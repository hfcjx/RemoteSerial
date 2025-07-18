from com2mqttapp import Com2MqttApp
import tkinter as tk
from tkinter import filedialog
import queue
from datetime import datetime
import threading
from threading import Thread
import ssl
import serial
import serial.tools.list_ports
import secrets
from paho.mqtt import client as mqtt_client

# 自定义MQTT收发客户端
class MyMqttClient:
    def __init__(self, app=None,unique="",swap_pip = None):
        self.my_client = mqtt_client.Client(f'com2mqtt-mqtt_client-{unique}', userdata=app)
        self.swap_pip = swap_pip    #数据交互通信通道
        self.app = app
        self.sub_event = threading.Event()

    def thread_is_run(self):
        # MQTT线程是否还在运行
        if self.my_client._thread is None:
            return False
        else:
            return True

    def my_mqtt_client_start(self,ip, port,r_topic,w_topic):
        self.sub_event.clear()
        thread_my_mqtt = Thread(target=self.mqtt_connect,
                             args=(ip, port, r_topic, w_topic),
                             daemon=True)  # 建子线程处理新来的任务请求
        thread_my_mqtt.start()


    def my_mqtt_client_stop(self):
        self.my_client.disconnect()
        self.my_client.loop_stop()

    def mqtt_connect(self,ip, port,r_topic,w_topic):
        def mqtt_on_connect(client, userdata, flags, rc):
            app = userdata
            if rc == 0:
                app.add_log_line('MQTT Client: "'+client._client_id.decode('utf-8')+'" Connected Successful!')
                self.mqtt_subscribe(r_topic,w_topic)
            else:
                app.add_log_line(f'MQTT Client: "'+client._client_id.decode('utf-8')+ f'" Failed to Connect,return code {rc}')

        def mqtt_on_disconnect(client, userdata, rc):
            app = userdata
            if rc == 0:
                app.add_log_line(f'MQTT Client: "'+client._client_id.decode('utf-8')+'" DisConnected Successful!')
            else:
                app.add_log_line(f'MQTT Client: "'+client._client_id.decode('utf-8')+f'" Failed to DisConnect,return code {rc}')
        try:
            # 连接MQTT
            self.my_client.on_connect = mqtt_on_connect
            self.my_client.on_disconnect = mqtt_on_disconnect
            self.my_client.connect(ip, port)
            self.my_client.loop_start()
        except:
            self.app.add_log_line(f'MQTT Client failed to connect to the server.')
            self.app.widget_stop_state()
            return
        if self.sub_event.wait(20):
            #启动publish线程
            thread_publish = Thread(target=self.thread_mqtt_publish,
                                    args=(w_topic,),
                                    daemon=True)  # 建子线程处理新来的任务请求
            thread_publish.start()

            #启动数据交换通道的线程
            if self.swap_pip is not None:
                self.swap_pip.serial_start()
                if self.swap_pip.running_event.wait(2):
                    thread_mon = Thread(target=self.threda_monitor,
                                             daemon=True)  # 建子线程处理新来的任务请求
                    thread_mon.start()
                    self.app.app_start_status(True)
                else:
                    self.app.widget_stop_state()
            else:
                self.app.widget_stop_state()
        else:
            self.app.add_log_line(f'MQTT Client subscribe timeout.')
            self.app.widget_stop_state()

    def mqtt_subscribe(self,r_topic,w_topic):
        def mqtt_on_subscribe(client, userdata, mid, granted_qos):
            app = userdata
            self.sub_event.set()
            app.add_log_line(f'MQTT Client subscribe "{r_topic}" successful.')

        def mqtt_on_message(client, userdata, msg):
            app = userdata
            #收到数据从COM发出
            app.com_tx_inc()
            self.swap_pip.write_data(msg.payload)

        self.my_client.subscribe(topic=r_topic,qos=2)
        self.my_client.on_message = mqtt_on_message
        self.my_client.on_subscribe = mqtt_on_subscribe

    def thread_mqtt_publish(self, w_topic):
        self.app.add_log_line(f'MQTT Client publish Thread start.')
        event = threading.Event()
        while self.thread_is_run() == True:
            while not self.swap_pip.recv_queue.empty():
                p = self.my_client.publish(topic=w_topic, payload=self.swap_pip.recv_queue.get(), qos=2)
                p.wait_for_publish()
            event.wait(0.001)
        self.app.add_log_line(f'MQTT Client publish Thread exit.')

    def threda_monitor(self):
        event = threading.Event()
        self.app.add_log_line(f'Thread monitor start.')
        while True:
            if (self.thread_is_run() == False) or (self.swap_pip.thread_is_run() == False):
                self.app.widget_stop_state()
                break
            event.wait(0.5)
        self.app.add_log_line(f'Thread monitor exit.')

# 自定义串口发送
class MyCom:
    def __init__(self, app=None, com_port = "",baud = 0,parity = ""):
        self.app = app
        self.my_serial = None
        self.err = False
        self.recv_queue = queue.Queue()
        self.port = com_port
        self.baud = baud
        self.parity = parity
        self.running_event = threading.Event()

    def thread_is_run(self):
        if self.my_serial is None:
            return not self.err
        else:
            return self.running_event.is_set()

    def serial_start(self):
        thread_swap_pip = Thread(target=self.thread_recv,
                                 daemon=True)  # 建子线程处理新来的任务请求
        thread_swap_pip.start()

    def serial_stop(self):
        self._close_serial()

    def set_serial(self,com_port = "",baud = 0,parity = ""):
        self.port = com_port
        self.baud = baud
        self.parity = parity

    # 列出系统中可用的COM口
    def find_sys_COM(self):
        ports = []
        for port in serial.tools.list_ports.comports():
            ports.append(port.name)
        return ports

    def open_serial(self,port = "", baud = 0, parity = ""):
        if port == "" :
            port = self.port
        if baud == 0:
            baud = self.baud
        if parity == "":
            parity = self.parity
        try:
            if parity == 'Even':
                par = serial.PARITY_EVEN
            elif parity == 'Odd':
                par = serial.PARITY_ODD
            else:
                par = serial.PARITY_NONE
            self.my_serial = serial.Serial(port=port, baudrate=baud, parity=par, timeout=0)
            return True
        except Exception as e:
            self.err = True
            return False

    def write_data(self,data):
        return self.my_serial.write(data)

    def _close_serial(self):
        if isinstance(self.my_serial, serial.Serial):
            self.my_serial.close()

    def thread_recv(self):
        event = threading.Event()
        if self.open_serial(self.port, self.baud, self.parity) == True:
            self.app.add_log_line(f'{self.port} open successful!')
            self.running_event.set()
            while True:
                try:
                    if isinstance(self.my_serial, serial.Serial):
                        if self.my_serial.isOpen() == False:
                            self.app.add_log_line(f'{self.port} closed!')
                            break
                        if self.my_serial.in_waiting > 0:
                            data = self.my_serial.read(self.my_serial.in_waiting)
                            self.recv_queue.put(data)
                            self.app.com_rx_inc()
                    event.wait(0.001)
                except:
                    self.my_serial.close()
                    self.app.add_log_line(f"{self.port} closed!")
                    break
            self.running_event.clear()
        else:
            self.app.add_log_line(f'{self.port} open fail!')

class MyCom2MqttApp(Com2MqttApp):
    sread_topic_def = ""
    write_topic_def = ""
    log_queue = queue.Queue()
    my_mqtt_client = None
    my_com = None

    def generate_int_random(self):
        # 生成32位随机整数（范围：0 到 4,294,967,295）
        random_int = secrets.randbelow(2 ** 32)
        # 不带前缀的版本
        hex_string_no_prefix = hex(random_int)[2:]  # 去掉 '0x' 前缀
        return hex_string_no_prefix

    # 往队列中添加日志数据
    def add_log_line(self, log = ''):
        if len(log) != 0:
            t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            text = f'[{t}] ' + log + "\r\n"
            self.log_queue.put(text)

    # 把队列的日志数据打印在Text控件中
    def show_log(self):
        if not self.log_queue.empty():
            self.log_text.configure(state=tk.NORMAL)
            while not self.log_queue.empty():
                self.log_text.insert('end', self.log_queue.get())
            self.log_text.configure(state=tk.DISABLED)
            self.log_text.update_idletasks()
            self.log_text.see(tk.END)
        self.mainwindow.after(100, self.show_log)

    # 清空Text控件中的日志
    def clear_text_widget(self):
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.delete('1.0', tk.END)
        self.log_text.configure(state=tk.DISABLED)

    # 初始化窗口控件的默认值
    def init_window(self,windows):
        # 先隐藏窗口
        windows.withdraw()
        """将窗口居中显示"""
        windows.update_idletasks()
        width = windows.winfo_width()
        height = windows.winfo_height()
        screen_width = windows.winfo_screenwidth()
        screen_height = windows.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        windows.geometry(f"+{x}+{y}")
        #初始化控件
        self.my_com = MyCom(self)
        self.com_port['value'] = self.my_com.find_sys_COM()
        if self.com_port['value']:
            self.com_port.current(0)
        if self.com_parity['value']:
            self.com_parity.current(0)

        self.var_mqtt_unique_ck.set(False)
        self.var_mqtt_unique.set(self.generate_int_random())
        self.read_topic_def = self.var_mqtt_read_topic.get()
        self.write_topic_def = self.var_mqtt_write_topic.get()
        self.var_mqtt_crt_file.trace_add("write", self.on_mqtt_crt_file_change)

        self.show_log()

        self.app_start_status()

        # 显示窗口
        windows.deiconify()

    def com_rx_inc(self):
        rx = self.var_com_rx.get()
        rx = rx + 1
        self.var_com_rx.set(rx)

    def com_tx_inc(self):
        tx = self.var_com_tx.get()
        tx = tx + 1
        self.var_com_tx.set(tx)

    # 重载Com2MqttApp的run函数
    def run(self, center=False):
        self.init_window(self.mainwindow)
        self.mainwindow.mainloop()

    def on_mqtt_unique_ck_press(self, event=None):
        if(self.var_mqtt_unique_ck.get()):
            self.var_mqtt_unique.set(self.generate_int_random())
            self.var_mqtt_read_topic.set(self.read_topic_def)
            self.var_mqtt_write_topic.set(self.write_topic_def)
        else:   #从未选到勾选
            self.var_mqtt_read_topic.set(self.read_topic_def + self.var_mqtt_unique.get())
            self.var_mqtt_write_topic.set(self.write_topic_def + self.var_mqtt_unique.get())

    def on_mqtt_crt_file_change(self,*args):
        if len(self.var_mqtt_crt_file.get()) == 0:
            self.var_mqtt_port.set(1883)
        else:
            self.var_mqtt_port.set(8883)

    def on_btn_browse_press(self, event=None):
        file_path = filedialog.askopenfilename(
            title="Select a file",  # 对话框标题
            initialdir="/",  # 初始目录
            filetypes=[  # 文件类型过滤
                ("CRT File", "*.crt"),
                ("All File", "*.*")
            ]
        )
        if len(file_path) != 0:
            self.var_mqtt_crt_file.set(file_path)

    def widget_start_state(self):
        self.btn_stop.configure(state=tk.NORMAL)
        self.btn_start.configure(state=tk.DISABLED)

    def widget_stop_state(self):
        self.btn_stop.configure(state=tk.DISABLED)
        self.btn_start.configure(state=tk.NORMAL)
        self.task_stop()
        self.app_start_status()

    def on_btn_start_press(self, event=None):
        port = self.com_port.get()
        baud = self.var_com_baud.get()
        parity = self.com_parity.get()
        if(len(port) == 0 or len(parity) == 0):
            return
        self.my_com.set_serial(port,baud,parity)

        self.my_mqtt_client = MyMqttClient(self, self.var_mqtt_unique.get(),self.my_com)
        mqtt_ip = self.var_mqtt_ip.get()
        mqtt_port = self.var_mqtt_port.get()
        read_topic = self.var_mqtt_read_topic.get()
        write_topic = self.var_mqtt_write_topic.get()
        if(len(mqtt_ip) == 0 or mqtt_port == 0 or len(read_topic) == 0 or len(write_topic) == 0):
            return
        if(len(self.var_mqtt_user.get()) != 0 and len(self.var_mqtt_pass.get()) != 0):
            self.my_mqtt_client.my_client.username_pw_set(self.var_mqtt_user.get(), self.var_mqtt_pass.get())
        if(len(self.var_mqtt_crt_file.get()) != 0):
            self.my_mqtt_client.my_client.tls_set(
                ca_certs=self.var_mqtt_crt_file.get(),  # CA 证书文件路径
                cert_reqs=ssl.CERT_REQUIRED  # 要求验证服务器证书
            )

        self.widget_start_state()
        self.clear_text_widget()
        self.var_com_rx.set(0)
        self.var_com_tx.set(0)

        self.my_mqtt_client.my_mqtt_client_start(mqtt_ip, mqtt_port, read_topic,write_topic)

    def on_btn_stop_press(self, event=None):
        self.widget_stop_state()

    def task_stop(self):
        self.my_com.serial_stop()
        if isinstance(self.my_mqtt_client, MyMqttClient):
            self.my_mqtt_client.my_mqtt_client_stop()

    def on_destroy(self, event=None):
        self.task_stop()


    def com_port_Lbtn_press(self, event=None):
        self.com_port['value'] = self.my_com.find_sys_COM()

    def app_start_status(self,ok=False):
        if ok :
            self.start_ok.configure(background='Green')
        else:
            self.start_ok.configure(background='Red')