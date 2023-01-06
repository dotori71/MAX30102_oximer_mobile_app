# import socket
import time
import json
import numpy as np
import threading
import sys

def DCRemover(x, w, alpha):
    w_n = x + alpha * w
    return [w_n, w_n - w]


class FindPT():
    def __init__(self):
        self.filter1 = [0.02879, 0.03346, 0.0488, 0.06485, 0.07991,
                        0.09225, 0.10035, 0.10317, 0.10035, 0.09225,
                        0.07991, 0.06485, 0.0488, 0.03346, 0.0288]
        self.window1 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    def FindP(self, data1):
        self.window1 = [data1] + self.window1[0:14]
        self.rawData1 = self.window1[0] * self.filter1[0] + self.window1[1] * self.filter1[1] + self.window1[2] * \
                        self.filter1[2] + self.window1[3] * self.filter1[3] + self.window1[4] * self.filter1[4] + \
                        self.window1[5] * self.filter1[5] + self.window1[6] * self.filter1[6] + self.window1[7] * \
                        self.filter1[7] + self.window1[8] * self.filter1[8] + self.window1[9] * self.filter1[9] + \
                        self.window1[10] * self.filter1[10] + self.window1[11] * self.filter1[11] + self.window1[12] * \
                        self.filter1[12] + self.window1[13] * self.filter1[13] + self.window1[14] * self.filter1[14]


def calc_spo2(ir_data, red_data, ir_valley_locs, n_peaks):
    """
    By detecting  peaks of PPG cycle and corresponding AC/DC
    of red/infra-red signal, the an_ratio for the SPO2 is computed.
    """
    # find precise min near ir_valley_locs (???)
    exact_ir_valley_locs_count = n_peaks
    # find ir-red DC and ir-red AC for SPO2 calibration ratio
    # find AC/DC maximum of raw
    i_ratio_count = 0
    ratio = []
    # find max between two valley locations
    # and use ratio between AC component of Ir and Red DC component of Ir and Red for SpO2
    red_dc_max_index = -1
    ir_dc_max_index = -1
    for k in range(exact_ir_valley_locs_count - 1):
        red_dc_max = -16777216
        ir_dc_max = -16777216
        if ir_valley_locs[k + 1] - ir_valley_locs[k] > 3:
            for i in range(ir_valley_locs[k], ir_valley_locs[k + 1]):
                if ir_data[i] > ir_dc_max:
                    ir_dc_max = ir_data[i]
                    ir_dc_max_index = i
                if red_data[i] > red_dc_max:
                    red_dc_max = red_data[i]
                    red_dc_max_index = i

            red_ac = int((red_data[ir_valley_locs[k + 1]] - red_data[ir_valley_locs[k]]) * (
                    red_dc_max_index - ir_valley_locs[k]))
            red_ac = red_data[ir_valley_locs[k]] + int(red_ac / (ir_valley_locs[k + 1] - ir_valley_locs[k]))
            red_ac = red_data[red_dc_max_index] - red_ac  # subtract linear DC components from raw

            ir_ac = int(
                (ir_data[ir_valley_locs[k + 1]] - ir_data[ir_valley_locs[k]]) * (ir_dc_max_index - ir_valley_locs[k]))
            ir_ac = ir_data[ir_valley_locs[k]] + int(ir_ac / (ir_valley_locs[k + 1] - ir_valley_locs[k]))
            ir_ac = ir_data[ir_dc_max_index] - ir_ac  # subtract linear DC components from raw

            nume = red_ac * ir_dc_max
            denom = ir_ac * red_dc_max
            if (denom > 0 and i_ratio_count < 5) and nume != 0:
                # original cpp implementation uses overflow intentionally.
                # but at 64-bit OS, Pyhthon 3.X uses 64-bit int and nume*100/denom does not trigger overflow
                # so using bit operation ( &0xffffffff ) is needed
                ratio.append(int(((nume * 100) & 0xffffffff) / denom))
                i_ratio_count += 1

    # choose median value since PPG signal may vary from beat to beat
    ratio = sorted(ratio)  # sort to ascending order
    mid_index = int(i_ratio_count / 2)

    ratio_ave = 0
    if mid_index > 1:
        ratio_ave = int((ratio[mid_index - 1] + ratio[mid_index]) / 2)
    else:
        if len(ratio) != 0:
            ratio_ave = ratio[mid_index]

    if ratio_ave > 2 and ratio_ave < 184:
        spo2 = -45.060 * (ratio_ave ** 2) / 10000.0 + 30.054 * ratio_ave / 100.0 + 94.845
        spo2_valid = True
    else:
        spo2 = -999
        spo2_valid = False

    return spo2, spo2_valid


class Work102:
    def __init__(self):
        self.js = [list()]
        self.xdata1 = []
        self.ydata1 = []
        self.ydata2 = []
        self.socketFlag = 0
        self.Datalist = []
        self.mx = []
        self.my = []
        self.hrate = []
        self.SPO2 = 0
        self.message = "waiting"
    def socket_client(self, *args):
        i = 0
        # HOST = '192.168.10.121'
        # PORT = 2049
        # s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # s.connect((HOST, PORT))
        #print('Connect Success!')
        while True:
            str1 = "success"
            # s.send(str1.encode())
            self.socketFlag = 1
            self.js = [[np.random.uniform(-4000, 2000), np.random.uniform(-4000, 2000), i]]
            if self.js != []:
                self.Datalist = self.Datalist + self.js
            i = i + 1
        # s.close()

    def decoding(self, *args):
        irraw = []
        redraw = []
        dca = []
        kk = 0
        w = 0
        w2 = 0
        xxx = []
        for i in range(200):
            xxx = xxx + [i]
        A = FindPT()
        B = FindPT()
        for i in range(0, 200):
            self.ydata1 = self.ydata1 + [0]
            self.ydata2 = self.ydata2 + [0]
            self.xdata1 = self.xdata1 + [0]
            irraw = irraw + [0]
            redraw = redraw + [0]
        while True:
            if self.socketFlag == 1:
                if self.Datalist != [] and kk < len(self.Datalist):
                    #print(self.Datalist[kk])
                    #if self.Datalist[kk][1] > 120000:  # detect finger at the correct position
                    if self.Datalist[kk][1] > -4000:  # detect finger at the correct position
                        self.message = "successful detection"
                        irraw = irraw[1:200] + [self.Datalist[kk][1]]
                        redraw = redraw[1:200] + [self.Datalist[kk][0]]
                        self.mx = []
                        self.my = []
                        # remove dc value,remain ac value
                        dca = DCRemover(self.Datalist[kk][1], w, 0.95)
                        iracvalue = dca[1]
                        w = dca[0]
                        A.FindP(iracvalue)
                        dca2 = DCRemover(self.Datalist[kk][0], w2, 0.95)
                        redacvalue = dca2[1]
                        w2 = dca2[0]
                        B.FindP(redacvalue)
                        yd1=int(-A.rawData1)
                        yd2=int(-B.rawData1)
                        self.ydata1 = self.ydata1[1:200] + [yd1]  # smoothed ir value serial and invert signal
                        self.ydata2 = self.ydata2[1:200] + [yd2]  # smoothed red value serial and invert signal
                        self.xdata1 = self.xdata1[1:200] + [self.Datalist[kk][2]]  # time serial
                        ir_grad = np.gradient(self.ydata1, xxx)
                        for k in range(199):
                            if self.ydata1[k] > 10:  # threshold of peak detection
                                if ir_grad[k] >= 0 and ir_grad[k + 1] < 0:  # peak location
                                    self.mx.append(k)  # put index of peaks in mx
                                    self.my.append(self.ydata1[k])
                        self.hrate = []
                        if len(self.mx) >= 2 and  kk%200==0:
                            for i in range(len(self.mx) - 1):
                                if (self.xdata1[self.mx[i + 1]] - self.xdata1[self.mx[i]]) != 0:
                                    self.hrate.append(
                                        int(60 / ((self.xdata1[self.mx[i + 1]] - self.xdata1[self.mx[i]]) / 1000)))
                        #self.SPO2, SPO2_valid = calc_spo2(irraw, redraw, self.mx, len(self.mx))
                        self.SPO2=np.random.uniform(90,100)
                        self.SPO2=round(self.SPO2,1)
                        kk = kk + 1
                        text=str(self.mx)+";"+str(self.my)+";"+str(self.hrate)+";"+str(yd1)+";"+str(yd2)+";"+str(self.SPO2)+";"+str(self.message)
                        print("")
                        sys.stdout.write(text)
                        sys.stdout.flush()
                    else:
                        self.message = "!!!wrong finger placement!!!"
                        text=self.message
                        print("")
                        sys.stdout.write(text)
                        sys.stdout.flush()
                        kk = kk + 1
                else:
                    time.sleep(0.001)
            else:
                time.sleep(0.01)
                print('...wait for connection...')


if __name__=="__main__":
    w=Work102()
    threading.Thread(target=w.socket_client,args=()).start()
    threading.Thread(target=w.decoding,args=()).start()
