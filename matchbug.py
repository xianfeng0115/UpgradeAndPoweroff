#coding=utf-8
import os, uiautomation
from time import sleep
from pykeyboard import PyKeyboard
from pymouse import PyMouse
import tkinter as tk
import tkinter.messagebox
from tkinter import scrolledtext
import threading
from SendMail import SendMail
from tkinter import END
from Stopthreading import *
import serial.tools.list_ports

k = PyKeyboard()
m = PyMouse()


class matchbug(tk.Tk):
    def __init__(self):
        # 使用'uiautomation'先定位总窗口
        self.window = uiautomation.WindowControl(searchDepth=1, AutomationId='MainForm')
        self.count = 0
        self.passed = 0
        self.failed = 0
        self.ispass = True
        self.num = 1
        super().__init__()
        self.title('Monitor(测试一部)')
        self.geometry('500x400')

        # 判断脚本暂停恢复的标志位，默认是FALSE
        self.singal = threading.Event()
        self.singal.set()

        # 标题区域
        self.var2 = tk.StringVar(self)
        self.var2.set('软件烧录中途断电测试')
        self.heading_label = tk.Label(self, textvariable=self.var2, bg='green', fg='white', font=('Arial', 12),
                                      width=55,
                                      height=3)
        self.heading_label.pack()

        # 进度条控制区域
        self.wait = tk.StringVar(self)
        self.progress = tk.Label(self, bg='green', fg='white', width=18, text='升级断电时间设置')
        self.progress.place(x=20, y=90)
        self.scale = tk.Scale(self, label='下电时间调整', from_=44, to=46, orient=tk.HORIZONTAL, length=130, showvalue=0,
                              tickinterval=1, resolution=0.1, variable=self.wait, command=self.print_selection)
        self.scale.place(x=20, y=120)

        # 监控控制区域
        self.monitor_father = tk.LabelFrame(self, text="控制区", padx=10, pady=10)
        self.monitor_father.place(x=30, y=200)
        self.begin_button = tk.Button(self.monitor_father, text='开始测试', width=10, height=1, padx=5, pady=5,
                                      command=self.monitorbutton)
        self.begin_button.pack()
        self.pause_button = tk.Button(self.monitor_father, text='暂停测试', width=10, height=1, padx=5, pady=5,command=self.button2)
        self.pause_button.pack()

        # 结果显示区域
        self.var = tk.StringVar(self)
        self.Information_father = tk.LabelFrame(self, text="日志信息", padx=10, pady=10)  # 创建子容器，水平，垂直方向上的边距均为10
        self.Information_father.place(x=160, y=80)
        self.Information_text = scrolledtext.ScrolledText(self.Information_father, width=33, height=15, padx=5, pady=10,
                                                          wrap=tk.WORD, font=('Arial', 12))
        self.Information_text.grid()

    def print_selection(self, v):
        self.progress.config(text='升级%s秒后下电' % v)

    def monitorbutton(self):
        answer = tkinter.messagebox.askokcancel('提示', '请确保已经打开MFIL升级工具，并正确连接端口')
        if answer == True:
            self.begin_button.configure(text='正在监控')
            self.begin_button.configure(state='disabled')  # 将按钮设置为灰色状态，不可使用状态
            # 此处需要用到线程
            self.t = threading.Thread(target=self.test)
            self.t.setDaemon(True)
            self.t.start()
        else:
            pass

    def button2(self):
        self.num += 1
        if self.num % 2 == 0:
            self.pause()
            self.pause_button.configure(text='恢复测试')
        else:
            self.restart()
            self.pause_button.configure(text='暂停测试')

    def pause(self):
        self.Information_text.insert('end', '测试pause\n')
        self.singal.clear()

    def restart(self):
        self.Information_text.insert('end', '测试continue\n')
        self.singal.set()

    def test(self):
        while True:
            self.var2.set('总共测试%s次,通过%s次\n' % (self.count, self.passed))
            # 判断端口是否存在
            os.popen("adb shell usb_composition_switch 902D n n y y")
            sleep(5)
            port_list = serial.tools.list_ports.comports()
            print(port_list)
            try:
                if 'Qualcomm' in str(port_list[0]):
                    self.Information_text.insert('end', '端口正常\n')
                else:
                    tkinter.messagebox.showwarning('错误', '未检测到端口')
                    break
            except:
                tkinter.messagebox.showwarning('错误', '未检测到端口')
                break
            num3 = 30
            for i in range(30):
                self.singal.wait()
                self.Information_text.insert('end', '%ss后进入测试\n' % num3)
                self.Information_text.see(END)
                sleep(1)
                num3 -= 1
            self.count += 1
            self.Information_text.insert('end', '正在检测，第%s次测试即将开始\n' % self.count)
            self.Information_text.see(END)
            sleep(3)
            try:
                self.window.TextControl(ClassName="TextBlock", Name='Download').Click()
            except LookupError:
                tkinter.messagebox.showwarning('错误', '未检测到MFIL升级工具')
                break
            self.Information_text.insert('end', '开始MFIL升级\n')
            self.Information_text.see(END)
            num = 24
            for i in range(24):
                self.singal.wait()
                self.Information_text.insert('end', '%ss后进入9008模式\n' % num)
                self.Information_text.see(END)
                sleep(1)
                num -= 1
            os.popen("adb shell sys_reboot edl")
            self.Information_text.insert('end', '正在进入9008模式\n')
            sleep(1)
            self.Information_text.insert('end', '开始升级\n')
            sleep(float(self.wait.get()))
            os.popen('D:\pythonCode\MyTools\\NationStandard\\PowerOff/M2MdiagnosticPlatform.Power.exe')
            self.Information_text.insert('end', 'KL30下电\n')
            self.Information_text.see(END)
            sleep(2)
            os.popen('D:\pythonCode\MyTools\\NationStandard\\Poweron/M2MdiagnosticPlatform.Power.exe')
            self.Information_text.insert('end', 'KL30上电\n')
            self.Information_text.insert('end', '正在等待TBOX重启完成\n')
            self.Information_text.see(END)
            sleep(20)
            try:
                window2 = uiautomation.WindowControl(searchDepth=1, AutomationId='DownloadStatusForm')
                window2.ButtonControl(ClassName="Button", AutomationId='PART_Close').Click()
            except LookupError:
                pass
            os.system("taskkill /F /IM M2MdiagnosticPlatform.Power.exe")
            num2 = 25
            for i in range(25):
                self.singal.wait()
                self.Information_text.insert('end', '%ss后开始导出etc/data文件\n' % num2)
                self.Information_text.see(END)
                sleep(1)
                num2 -= 1
            os.popen("adb pull etc/data d:logs")
            self.Information_text.insert('end', '已经导出最新etc/data 文件\n')
            self.Information_text.see(END)
            list = ['ddclient.conf', 'dnsmasq.conf', 'dsi_config.xml', 'factory_l2tp_cfg.xml',
                    'factory_mobileap_cfg.xml', 'factory_mobileap_firewall.xml',
                    'factory_qti_socksv5_auth.xml', 'factory_qti_socksv5_conf.xml', 'l2tp_cfg.xml', 'mbim_mode',
                    'mux_mode', 'netmgr_config.xml']
            for i in list:
                b = os.path.getsize('logs\%s' % i)
                if b == 0:
                    self.Information_text.insert('end', '%s检测失败\n' % i)
                    self.Information_text.see(END)
                    self.ispass = False
                    break
                else:
                    self.Information_text.insert('end', '%s检测成功\n' % i)
                    self.Information_text.see(END)
                    self.ispass = True
            self.check()
            self.Information_text.insert('end', '总共测试%s次,通过%s次\n' % (self.count, self.passed))
            self.Information_text.insert('end', '正在等待下一次测试\n')
            self.Information_text.insert('end', '******************************\n')
            self.Information_text.see(END)

    def check(self):
        if self.ispass == True:
            self.passed += 1
        elif self.ispass == False:
            self.var2.set('问题已经复现')
            self.heading_label.configure(bg='red')
            self.failed += 1
            m = SendMail(
                username='1091238794@qq.com',
                passwd='ccunnyoypajyhjgf',
                recv=['xianfeng.liu@m2motive.com.cn'],
                title='H7问题复现通知',
                content='H7问题已经复现，请回到挂机现场查看分析',
                # file=r'E:\\testpy\\python-mpp\\day7\\作业\\data\\mpp.xls',
                ssl=True,
            )
            m.send_mail()
            self.Information_text.insert('end', '邮件已经发送\n')
            self.Information_text.see(END)
            stop_thread(self.t)

if __name__ == '__main__':
    match = matchbug()
    match.mainloop()
