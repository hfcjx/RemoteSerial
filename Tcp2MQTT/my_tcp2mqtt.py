from tcp2mqttapp import Tcp2MqttApp
import tkinter as tk
from tkinter import filedialog
import queue
from datetime import datetime
import threading
from threading import Thread
import ssl
from paho.mqtt import client as mqtt_client
import socket

# 自定义MQTT收发客户端
class MyMqttClient:
    def __init__(self, app=None,unique="",swap_pip = None):
        if unique == "":
            id = f'tcp2mqtt-mqtt_client'
        else:
            id = f'tcp2mqtt-mqtt_client-{unique}'
        self.my_client = mqtt_client.Client(id, userdata=app)
        self.swap_pip = swap_pip    #数据交互通信通道
        self.app = app
        self.sub_event = threading.Event()
        self.connecting = False

    def thread_is_run(self):
        # MQTT线程是否还在运行
        if self.my_client._thread is None:
            return False
        else:
            return True

    def my_mqtt_client_start(self,ip, port,r_topic,w_topic):
        self.sub_event.clear()
        self.connecting = False
        thread_my_mqtt = Thread(target=self.mqtt_connect,
                             args=(ip, port, r_topic, w_topic),
                             daemon=True)  # 建子线程处理新来的任务请求
        thread_my_mqtt.start()


    def my_mqtt_client_stop(self):
        self.my_client.disconnect()
        self.my_client.loop_stop()
        self.connecting = False
        self.sub_event.set()    #调用此函数停止任务，mqtt_connect在等待sub_event，触发事件，配合self.connecting，退出mqtt_connect线程

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
            self.connecting = True
            # 连接MQTT
            self.my_client.on_connect = mqtt_on_connect
            self.my_client.on_disconnect = mqtt_on_disconnect
            self.my_client.connect(ip, port)
            self.my_client.loop_start()
        except:
            self.app.add_log_line(f'MQTT Client failed to connect to the server.')
            self.app.widget_stop_state()
            self.connecting = False
            return
        if self.sub_event.wait(20):
            if self.connecting == False:
                self.app.add_log_line(f'MQTT Client stops connecting to the server.')
                return
            #启动publish线程
            thread_publish = Thread(target=self.thread_mqtt_publish,
                                    args=(w_topic,),
                                    daemon=True)  # 建子线程处理新来的任务请求
            thread_publish.start()

            #启动数据交换通道的线程
            if self.swap_pip is not None:
                self.swap_pip.tcp_server_start()
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
        self.connecting = False

    def mqtt_subscribe(self,r_topic,w_topic):
        def mqtt_on_subscribe(client, userdata, mid, granted_qos):
            app = userdata
            self.sub_event.set()
            app.add_log_line(f'MQTT Client subscribe "{r_topic}" successful.')

        def mqtt_on_message(client, userdata, msg):
            #收到数据从Tcp发出
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

class MyTCPServer:
    def __init__(self, app = None,addr ='0.0.0.0', port=34567):
        self.app = app
        self.host = addr
        self.port = port
        self.server_socket = None
        self.tcp_client = []
        self.lock = threading.Lock()
        self.recv_queue = queue.Queue()
        self.running_event = threading.Event()

    def thread_is_run(self):
        return self.running_event.is_set()

    def tcp_server_start(self):
        """启动服务器"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(10)  # 设置最大等待连接数
        except Exception as e:
            self.server_socket.close()
            self.app.add_log_line("Open TCP Server Socket Failed,Please Check.")
            return None
        self.running_event.set()
        # 启动接受客户端连接的线程
        accept_thread = threading.Thread(target=self._accept_clients, daemon=True)
        accept_thread.start()
        return accept_thread

    def tcp_server_stop(self):
        """停止服务器"""
        self.running_event.clear()
        if self.server_socket is not None:
            self.server_socket.close()
        try:
            for s in self.tcp_client:
                ip, port = s.getpeername()
                s.close()
        except Exception as e:
            self.app.add_log_line(f"close tcp client: ({ip}, {port}) error!")

    def write_data(self,data):
        for s in self.tcp_client:
            s.send(data)

    def _accept_clients(self):
        """接受客户端连接"""
        self.app.add_log_line(f"tcp server start: {self.host}:{self.port}")
        while self.running_event.is_set():
            try:
                client_socket, client_address = self.server_socket.accept()
                self.app.add_log_line(f"new tcp client: {client_address}")

                # 为每个客户端创建新线程
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket,),
                    daemon=True
                )
                self.tcp_client.append(client_socket)
                client_thread.start()

            except OSError as e:
                if self.running_event.is_set():
                    self.app.add_log_line(f"accept tcp client error: {e}")
                break
        self.app.add_log_line(f"tcp server stop: {self.host}:{self.port}")

    def _handle_client(self, client_socket):
        """处理单个客户端连接"""
        ip,port = client_socket.getpeername()
        self.app.add_log_line(f"tcp client: ({ip}, {port}) recv thread start.")
        try:
            while self.running_event.is_set():
                try:
                    # 接收数据
                    data = client_socket.recv(8192)
                    if not data:  # 客户端断开连接
                        break
                    # 处理数据 (这里简单打印)
                    self.lock.acquire()
                    try:
                        self.recv_queue.put(data)
                    finally:
                        self.lock.release()
                except ConnectionResetError:
                    self.app.add_log_line(f"tcp client: ({ip}, {port}) error closed.")
                    break
                except Exception as e:
                    self.app.add_log_line(f"tcp client: ({ip}, {port}) recv error: {e}")
                    break
        finally:
            self.app.add_log_line(f"tcp client: ({ip}, {port}) disconnect.")
            client_socket.close()
            if client_socket in self.tcp_client:
                self.tcp_client.remove(client_socket)
        self.app.add_log_line(f"tcp client: ({ip}, {port}) recv thread stop.")

class MyTcp2MqttApp(Tcp2MqttApp):
    read_topic_def = ""
    write_topic_def = ""
    log_queue = queue.Queue()
    my_tcp = None
    my_mqtt_client = None

    # 往队列中添加日志数据
    def add_log_line(self, log=''):
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
        self.mainwindow.after(50, self.show_log)

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
        self.read_topic_def = self.var_mqtt_read_topic.get()
        self.write_topic_def = self.var_mqtt_write_topic.get()
        self.var_mqtt_crt_file.trace_add("write", self.on_mqtt_crt_file_change)

        self.show_log()

        self.app_start_status()
        # 显示窗口
        windows.deiconify()

    # 重载Tcp2MqttApp的run函数
    def run(self, center=False):
        self.init_window(self.mainwindow)
        self.mainwindow.mainloop()

    def on_mqtt_unique_key_release(self, event=None):
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
        port = self.var_tcp_port.get()
        ip = self.var_tcp_ip.get()
        if(port == 0 or len(ip) == 0):
            return

        mqtt_ip = self.var_mqtt_ip.get()
        mqtt_port = self.var_mqtt_port.get()
        read_topic = self.var_mqtt_read_topic.get()
        write_topic = self.var_mqtt_write_topic.get()
        if(len(mqtt_ip) == 0 or mqtt_port == 0 or len(read_topic) == 0 or len(write_topic) == 0):
            return

        self.my_tcp = MyTCPServer(self, ip, port)
        self.my_mqtt_client = MyMqttClient(self, self.var_mqtt_unique.get(),self.my_tcp)

        if(len(self.var_mqtt_user.get()) != 0 and len(self.var_mqtt_pass.get()) != 0):
            self.my_mqtt_client.my_client.username_pw_set(self.var_mqtt_user.get(), self.var_mqtt_pass.get())
        if(len(self.var_mqtt_crt_file.get()) != 0):
            self.my_mqtt_client.my_client.tls_set(
                ca_certs=self.var_mqtt_crt_file.get(),  # CA 证书文件路径
                cert_reqs=ssl.CERT_REQUIRED  # 要求验证服务器证书
            )

        self.widget_start_state()
        self.clear_text_widget()

        self.my_mqtt_client.my_mqtt_client_start(mqtt_ip, mqtt_port, read_topic, write_topic)


    def on_btn_stop_press(self, event=None):
        self.widget_stop_state()

    def task_stop(self):
        self.my_tcp.tcp_server_stop()
        if isinstance(self.my_mqtt_client, MyMqttClient):
            self.my_mqtt_client.my_mqtt_client_stop()

    def on_destroy(self, event=None):
        self.task_stop()

    def app_start_status(self, ok=False):
        if ok:
            self.start_ok.configure(background='Green')
        else:
            self.start_ok.configure(background='Red')