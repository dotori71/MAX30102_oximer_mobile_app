from posixpath import split
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from database import DataBase
import datetime
from matplotlib import pyplot as plt
import numpy as np
from kivy.garden.matplotlib import FigureCanvasKivyAgg
from kivy.clock import Clock
import subprocess
import time
import random
from kivymd.uix.datatables import MDDataTable
from kivy.metrics import dp
class CreateAccountWindow(Screen):
    namee = ObjectProperty(None)
    password = ObjectProperty(None)

    def submit(self):
        if self.namee.text != "":
            if self.password != "":
                k = db.add_user(self.password.text, self.namee.text)
                if k == -1:
                    usedname()
                self.reset()
                sm.current = "login"
            else:
                invalidForm()
        else:
            invalidForm()

    def login(self):
        self.reset()
        sm.current = "login"

    def reset(self):
        self.password.text = ""
        self.namee.text = ""

class LoginWindow(Screen):
    namee = ObjectProperty(None)
    password = ObjectProperty(None)

    def loginBtn(self):
        if db.validate(self.namee.text, self.password.text):
            MainWindow.current = self.namee.text
            RealTimeM.current = self.namee.text
            TodaysRecord.current = self.namee.text
            HRecord.current = self.namee.text
            Hrplot.current = self.namee.text
            Rtmq.current = self.namee.text
            self.reset()
            sm.current = "main"
        else:
            invalidLogin()

    def createBtn(self):
        self.reset()
        sm.current = "create"

    def reset(self):
        self.namee.text = ""
        self.password.text = ""


class MainWindow(Screen):
    n = ObjectProperty(None)
    created = ObjectProperty(None)
    current = ""

    def logOut(self):
        sm.current = "login"

    def on_enter(self, *args):
        self.n.text = "Hi," + self.current + "!"

class RealTimeM(Screen):
    n = ObjectProperty(None)
    n1 = ObjectProperty(None)
    n2 = ObjectProperty(None)
    n3 = ObjectProperty(None)
    n4 = ObjectProperty(None)
    layout = ObjectProperty(None)
    current = ""
    fig1 = ObjectProperty(None)
    ax = ObjectProperty(None)
    x = np.linspace(0, 200, 200)
    y = np.linspace(-2000, 2000, 200)
    x1 = [173.5, 174.6]
    y1 = [2014, 2014]
    x3 = [173.5, 174.6]
    y3 = [1905, 1905]
    l1= ObjectProperty(None)
    l3= ObjectProperty(None)
    l2x=173.5
    l2=ObjectProperty(None)
    l1t =ObjectProperty(None)
    l2t =ObjectProperty(None)
    l2t2=ObjectProperty(None)           
    line1=ObjectProperty(None)
    line2=ObjectProperty(None)
    mdot=ObjectProperty(None)
    timee=60
    process=0
    #receive data to present----------------
    ydata1=[]
    ydata2=[]
    mx=[]
    my=[]
    #xdata=[]
    xd=[]
    hrate=[]
    heartrate=[]
    SPO2=0
    s_p_o_2=[]
    message="waiting"
    kkk=-1
    flag=0
    ck=0
    for i in range(0, 200):#clear !!!!!!!!!
        ydata1 = ydata1 + [0]
        ydata2 = ydata2 + [0]
        xd=xd+[i]

    def on_enter(self, *args):
        hisrecord = db.get_user(self.current)[2]
        if hisrecord.count(str(datetime.datetime.now()).split(" ")[0]) == 1:    
            db.del_tr(self.current)
        self.layout.clear_widgets()
        plt.style.use('ggplot')
        self.fig1 = plt.figure(figsize=(11, 2), dpi=53)
        self.fig1.patch.set_facecolor('pink')
        self.fig1.patch.set_alpha(0.6)
        self.ax = self.fig1.add_subplot(111)
        self.ax.patch.set_facecolor('mistyrose')
        self.ax.patch.set_alpha(1)
        self.ax.set_title("Heart Rate & Pulse Oximeter", fontsize=19,
                    weight="bold", style="italic", color='darkred')
        self.ax.set_xlabel("Data Set Sequence Number", fontsize=10, color='darkred')
        self.ax.set_ylabel("Amplitude", fontsize=10, color='darkred')
        self.x1 = [173.5, 174.6]
        self.y1 = [2014, 2014]
        self.x3 = [173.5, 174.6]
        self.y3 = [1905, 1905]
        self.l1, = self.ax.plot(self.x, self.y, "lightcoral", linewidth=4, label='Smoothed IR Data')
        self.l3, = self.ax.plot(self.x, self.y, "red", linewidth=4, label='Smoothed RED Data')
        self.l1.set_data(self.x1, self.y1)
        self.l3.set_data(self.x3, self.y3)
        self.l2, = self.ax.plot(self.l2x, 1772, label='Gradient Peaks', marker="$•$", mfc="darkorange", mec="sienna", markersize=10,
                        linestyle='')
        self.l1t = self.ax.text(0.84, 0.95, '', transform=self.ax.transAxes, fontsize=7)
        self.l2t = self.ax.text(0.84, 0.9, '', transform=self.ax.transAxes, fontsize=7)
        self.l2t2 = self.ax.text(0.84, 0.925, '', transform=self.ax.transAxes, fontsize=7)                   
        self.l1t.set_text('   Smoothed IR Data')
        self.l2t.set_text('   Gradient Peaks')
        self.l2t2.set_text('   Smoothed RED Data')
        self.line1,= self.ax.plot(self.x, self.y, "lightcoral", linewidth=3, label='Smoothed IR Data')
        self.line2,= self.ax.plot(self.x, self.y, "red",        linewidth=3,label='Smoothed RED Data')
        self.mdot,=self.ax.plot([],[],label='Gradient Peaks',marker="$•$",mfc="darkorange",mec="sienna",markersize=10,linestyle='') 
        self.n.text =self.current
        self.ax.set_xlim(0,199)
        self.ax.set_ylim(-2000,2000)
        self.line1.set_data(self.xd,self.ydata1)
        self.line2.set_data(self.xd,self.ydata2)
        self.mdot.set_data(self.mx,self.my)
        self.l1.set_xdata(self.x1)
        self.l3.set_xdata(self.x3)
        self.l2.set_xdata(self.l2x)
        self.layout.add_widget(FigureCanvasKivyAgg(plt.gcf()))
        self.function_pwork=Clock.schedule_interval(self.pwork,0.0001)
        self.function_animation=Clock.schedule_interval(self.update_plot,0.0001)
        self.n2.text="60"
        self.function_counter=Clock.schedule_interval(self.timecount,1)
        self.process=subprocess.Popen('python rtm102ty1.py',stdin=subprocess.PIPE,stdout=subprocess.PIPE)

    def on_leave(self, *args):
        self.layout.clear_widgets()
        self.function_pwork.cancel()
        self.function_animation.cancel()
        self.function_counter.cancel()
        self.timee=60
        self.process.terminate()
        h_r_c=cal_hr(self.heartrate)
        if h_r_c!="X":
            h_r_c = round(h_r_c,1)#calculate an accurate hr after leave this page
        spo2t = round(np.mean(self.s_p_o_2),1) 
        # print("self.heartrate",self.heartrate)
        # print("h_r_c",h_r_c)
        # print("spo2t",spo2t)
        if h_r_c!="X" and spo2t!="X":
            db.add_tr(self.current,h_r_c,spo2t)
        #h_r_c and spo2's mean write to database!
        self.n.text = ""
        self.n1.text = ""
        self.n2.text = ""
        self.n3.text = ""
        self.n4.text = ""
        self.process=0
        #reset data to present----------------
        self.ydata1=[]
        self.ydata2=[]
        self.mx=[]
        self.my=[]
        self.xd=[]
        self.hrate=[]
        self.heartrate=[]
        self.SPO2=0
        self.s_p_o_2=[]
        self.message="waiting"
        self.kkk=-1
        self.flag=0
        self.ck=0
        for i in range(0, 200):#clear!
            self.ydata1 = self.ydata1 + [0]
            self.ydata2 = self.ydata2 + [0]
            self.xd=self.xd+[i]
        self.x1 = [173.5, 174.6]
        self.x3 = [173.5, 174.6]
        self.l2x= 173.5

    def pwork(self, *args):
        data =self.process.stdout.readline().decode("utf-8")
        if data.count(";")!=0:
            self.flag=0
            #print(data)
            task=data.split(";")
            if task[2]=="[]":
                cc=2
            else:
                cc=3
            kk=0
            for i in task[0:cc]:
                i=i.replace("[","").replace("]","").split(",")
                task[kk]=i
                kk=kk+1
            task1=[[],[],[],[],[]]
            kk=0
            for k in task[0:cc]:    
                for j in k:
                    try:
                        task1[kk].append(int(j))
                    except:
                        pass
                kk=kk+1
            if cc==3:
                self.hrate=task1[2]
            self.ydata1=self.ydata1[1:200] + [int(task[3])] 
            self.ydata2=self.ydata2[1:200] + [int(task[4])]
            self.ck=self.ck+1
            if self.ck>=200: 
                self.xd=self.xd[1:200] + [self.ck] 
                self.my=task1[1]
                for iii in range(len(task1[0])):
                    task1[0][iii]=task1[0][iii]+(self.ck-199)
                self.mx=task1[0]
                for iii in range(2):
                    self.x1[iii]=self.x1[iii]+1
                    self.x3[iii]=self.x3[iii]+1
                self.l2x=self.l2x+1    
            else:
                self.mx,self.my=task1[0],task1[1]
            self.SPO2=task[5]
            self.message=task[6]
            self.heartrate=self.heartrate+self.hrate
            self.s_p_o_2=self.s_p_o_2+[float(self.SPO2)]
            self.flag=1
        else:
            self.message=data

    def update_plot(self, *args):
        if self.flag==1:
            self.layout.clear_widgets()
            self.line1.set_data(self.xd,self.ydata1)
            self.line2.set_data(self.xd,self.ydata2)
            self.mdot.set_data(self.mx,self.my)
            self.l1.set_xdata(self.x1)
            self.l3.set_xdata(self.x3)
            self.l2.set_xdata(self.l2x)
            #plt.xticks(np.linspace(0,200,200),self.xdata)
            self.layout.add_widget(FigureCanvasKivyAgg(plt.gcf()))# adding plot to kivy boxlayout
            self.n1.text=str(self.hrate)
            if float(self.SPO2)!=-999 and self.SPO2!=0:
                self.n3.text=self.SPO2
            self.kkk=self.kkk+1
            if self.kkk>200:
                self.ax.set_xlim(self.kkk-200,self.kkk)
        self.n4.text=self.message

    def timecount(self, *args):
        if self.timee!=0:
            self.timee=self.timee-1
            timeee='{:02d}'.format(self.timee)
            self.n2.text=str(timeee)

def cal_hr(heart_rate):
    if len(heart_rate)!=0:
        n = 1.5
        q3 = np.percentile(heart_rate, 75)
        q1 = np.percentile(heart_rate, 25)
        IQR = q3 - q1 # IQR = Q3-Q1
        chr = []
        for i in range(len(heart_rate)):
            # outlier1 = Q3 + n*IQR ; outlier2 = Q1 - n*IQR
            if heart_rate[i] < q3 + n * IQR and heart_rate[i] > q1 - n * IQR:
                chr.append(heart_rate[i])
        hrc = np.mean(chr)
        return hrc
    else:
        return "X"
class Rtmq(Screen):
    current = ""

    def on_enter(self, *args):
        hisrecord = db.get_user(self.current)[2]
        if hisrecord.count(str(datetime.datetime.now()).split(" ")[0]) == 1:
            tryes()
        else:
            trnoyet()

class TodaysRecord(Screen):

    n = ObjectProperty(None)
    n1 = ObjectProperty(None)
    n2 = ObjectProperty(None)
    n3 = ObjectProperty(None)
    current = ""

    def on_enter(self, *args):
        password, created, hisrecord = db.get_user(self.current)
        num=hisrecord.count("/")+1
        if hisrecord.count(str(datetime.datetime.now()).split(" ")[0]) == 1:
            hisrecord=hisrecord.split("/")
            for i in range(num):
                if hisrecord[i].count(str(datetime.datetime.now()).split(" ")[0]) == 1:
                    trr=hisrecord[i].split(",")
                    self.n1.text = trr[1] + "bpm"
                    self.n.text = trr[2] + "%"
                    self.n3.text = ""
        else:
            self.n1.text =""
            self.n.text = ""
            self.n3.text="no record"
            notr()
        self.n2.text =str(datetime.datetime.now()).split(" ")[0]

class HRecord(Screen):

    databasehr=ObjectProperty(None)
    current = ""
    dhr=[]
    table=ObjectProperty(None)
    rd=ObjectProperty(None)
    def on_enter(self, *args):
        hisrecord = db.get_user(self.current)[2]
        hisrecord = hisrecord.replace("[", "").replace("]", "").split("/")
        rd=[]
        for i in range(len(hisrecord)):
            kkk=[]
            k=hisrecord[i].split(",")
            kkk=[k[0]]
            if k[1]!="X":
                if float(k[1])>=60 and float(k[1])<=85:
                    kkk=kkk+[("checkbox-marked-circle",[39 / 256, 174 / 256, 96 / 256, 1],k[1],)]
                elif float(k[1])>85 and float(k[1])<100:
                    kkk=kkk+[("alert", [255 / 256, 165 / 256, 0, 1],k[1])]
                else:
                    kkk=kkk+[("alert-circle", [1, 0, 0, 1],k[1])]
            else:
                kkk=kkk+["[color=#FF4500]NaN[/color]"]
            if k[2]!="X":
                if float(k[2])>=95 and float(k[2])<=100:
                    kkk=kkk+[("checkbox-marked-circle",[39 / 256, 174 / 256, 96 / 256, 1],k[2],)]
                else:
                    kkk=kkk+[("alert-circle", [1, 0, 0, 1],k[2])]
            else:
                kkk=kkk+["[color=#FF4500]NaN[/color]"]
            kk=tuple(kkk)
            rd=rd+[kk]
        self.table=MDDataTable(
            column_data=[
                ("[color=#CD853F]Date[/color]",dp(30)),
                ("[color=#CD853F]HR[/color]",dp(13)),
                ("[color=#CD853F]SpO2[/color]",dp(13)),
            ],
            row_data=rd,
            pos_hint={"center_x":0.5,"center_y":0.575},
            size_hint=(0.95,0.53),
            use_pagination=True,
            rows_num=4,
            pagination_menu_height=dp(10),
            check=True
        )
        self.table.bind(on_check_press=self.checked)
        self.databasehr.add_widget(self.table)

    def checked(self,instance_table,current_row):
        k=0
        if self.dhr!=[]:
            for i in range(len(self.dhr)):
                if self.dhr[i]==current_row:
                    self.dhr.remove(current_row)
                    k=1
                    break
        if k==0:
            self.dhr=self.dhr+[current_row]

    def removehr(self):
        indextrd=[]
        for i in range(len(self.table.row_data)):
            for j in range(len(self.dhr)):
                if self.table.row_data[i][0]==self.dhr[j][0]:
                    indextrd=indextrd+[i]
        list=[]
        for k in range(len(indextrd)):
            list=list+[self.table.row_data[indextrd[k]]]
        for kk in range(len(list)): 
            self.table.row_data.remove(list[kk])
        self.rd=self.table.row_data
        db.del_hr(self.current,indextrd)
        self.dhr=[]
    def on_leave(self):
        self.dhr=[]
        self.databasehr.remove_widget(self.table)
        self.table=ObjectProperty(None)

class Ds(Screen):
    def on_enter(self, *args):
        pass

class Hrplot(Screen):
    layout = ObjectProperty(None)
    layout1 = ObjectProperty(None)
    n1 = ObjectProperty(None)
    current = ""
    def on_enter(self, *args):
        hisrecord = db.get_user(self.current)[2].split("/")
        hrd=[]
        for i in range(len(hisrecord)):
            kk=(hisrecord[i]).split(",")
            kkk=[kk[0]]+[float(kk[1])]+[float(kk[2])]
            hrd=hrd+[kkk]
        xdata=[]
        yhr=[]
        yspo2=[]
        for i in range(len(hrd)):
            xdata=xdata+[i]
            yhr=yhr+[hrd[i][1]]
            yspo2=yspo2+[hrd[i][2]]
        xhr=[]
        xspo2=[]
        for i in range(len(hrd)):
            xhr=xhr+[i]
            xspo2=xspo2+[i]
        x = np.linspace(0,len(hrd)-1,len(hrd))
        y = np.linspace(50,135,len(hrd))
        y1 = np.linspace(90,100,len(hrd))
        plt.style.use('ggplot')
        fig1 = plt.figure(figsize=(11, 2), dpi=45)
        fig1.patch.set_facecolor('lavender')
        fig1.patch.set_alpha(0.8)
        ax = fig1.add_subplot(111)
        ax.patch.set_facecolor('k')
        ax.patch.set_alpha(1)
        ax.set_title("Run chart (heart rate)", fontsize=19,
                        weight="bold", style="italic", color='slateblue')
        ax.set_xlabel("Data Set Sequence Number", fontsize=13, color='indigo')
        ax.set_ylabel("heart rate (bpm)", fontsize=15, color='indigo')
        l1, = ax.plot(x, y, "mediumpurple", linewidth=4,marker='o', markersize=10,  mfc="chartreuse",markeredgecolor='lemonchiffon')
        l1.set_data(xhr,yhr)
        plt.xticks(x,xdata)
        self.layout.add_widget(FigureCanvasKivyAgg(plt.gcf()))
        fig2 = plt.figure(figsize=(11, 2), dpi=45)
        fig2.patch.set_facecolor('lavender')
        fig2.patch.set_alpha(0.8)
        ax1 = fig2.add_subplot(111)
        ax1.patch.set_facecolor('k')
        ax1.patch.set_alpha(1)
        ax1.set_title("Run chart (SpO2)", fontsize=19,
                        weight="bold", style="italic", color='slateblue')
        ax1.set_xlabel("Data Set Sequence Number", fontsize=13, color='indigo')
        ax1.set_ylabel("SpO2 (%)", fontsize=15, color='indigo')
        l2, = ax1.plot(x, y1, "mediumpurple", linewidth=4,marker='o', mfc="chartreuse",markersize=10, markeredgecolor='lemonchiffon')
        l2.set_data(xspo2,yspo2)
        plt.xticks(x,xdata)
        self.layout1.add_widget(FigureCanvasKivyAgg(plt.gcf()))
    def on_leave(self, *args):
        self.layout.clear_widgets()
        self.layout1.clear_widgets()

class WindowManager(ScreenManager):
    pass

def invalidLogin():
    pop = Popup(title='Invalid Login',
                  content=Label(text='Invalid username or password.'),
                  size_hint=(None, None), size=(320, 300))
    pop.open()
def notr():
    pop = Popup(title='No record',
                  content=Label(text="You haven't measured today!"),
                  size_hint=(None, None), size=(320, 300))
    pop.open()

def usedname():
    pop = Popup(title='Used Name',
                  content=Label(text='Try another name!'),
                  size_hint=(None, None), size=(320, 300))
    pop.open()

def invalidForm():
    pop = Popup(title='Invalid Form',
                  content=Label(text='Please fill in all inputs with valid information.'),
                  size_hint=(None, None), size=(320, 300))

    pop.open()

def trnoyet():
    pop = Popup(title='Notice',
                  content=Label(text=" You haven't taken a measurement today,\n please put your finger on the oximeter device \n and press the green button to start the\n measurement when you are ready.\n Or leave."),
                  size_hint=(None, None), size=(320, 300))

    pop.open()

def tryes():
    pop = Popup(title='Notice',
                  content=Label(text=" You have already measured today.\n You can press the green button to delete\n the previous record and measure a new one.\n Or leave."),
                  size_hint=(None, None), size=(320, 300))

    pop.open()
kv = Builder.load_file("my.kv")
sm = WindowManager()
db = DataBase("users.txt")

screens = [LoginWindow(name="login"), CreateAccountWindow(name="create")
           , MainWindow(name="main"), RealTimeM(name="rtm"),
           TodaysRecord(name="tr"), HRecord(name="hr"),
           Hrplot(name="hrp"),Ds(name="ds"),Rtmq(name="rq")]
for screen in screens:
    sm.add_widget(screen)

sm.current = "login"

class MyMainApp(MDApp):
    def build(self):
        return sm

if __name__ == "__main__":
    MyMainApp().run()
