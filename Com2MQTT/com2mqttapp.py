#!/usr/bin/python3
import tkinter as tk
import tkinter.ttk as ttk


class Com2MqttApp:
    def __init__(self, master=None, translator=None):
        _ = translator
        if translator is None:
            def _(x): return x
        # build ui
        self.top_main = tk.Tk() if master is None else tk.Toplevel(master)
        self.top_main.configure(height=400, width=600)
        self.top_main.resizable(False, False)
        self.top_main.title("COM2MQTT")
        self.frame_main = ttk.Frame(self.top_main, name="frame_main")
        self.frame_main.configure(height=400, width=600)
        self.mqtt_group = ttk.Labelframe(self.frame_main, name="mqtt_group")
        self.mqtt_group.configure(height=170, text=_('MQTT'), width=480)
        self.label14 = ttk.Label(self.mqtt_group)
        self.label14.configure(text=_('IP'))
        self.label14.grid(
            column=0,
            ipadx=1,
            ipady=1,
            padx=1,
            pady=1,
            row=0,
            sticky="w")
        self.mqtt_ip = ttk.Entry(self.mqtt_group, name="mqtt_ip")
        self.var_mqtt_ip = tk.StringVar(value=_('broker.emqx.io'))
        self.mqtt_ip.configure(
            justify="left",
            state="normal",
            takefocus=False,
            textvariable=self.var_mqtt_ip,
            validate="none",
            width=40)
        _text_ = _('broker.emqx.io')
        self.mqtt_ip.delete("0", "end")
        self.mqtt_ip.insert("0", _text_)
        self.mqtt_ip.grid(
            column=1,
            columnspan=3,
            ipadx=1,
            ipady=1,
            padx=1,
            pady=1,
            row=0,
            sticky="w")
        self.label15 = ttk.Label(self.mqtt_group)
        self.label15.configure(text=_('Port'))
        self.label15.grid(
            column=4,
            ipadx=1,
            ipady=1,
            padx=1,
            pady=1,
            row=0,
            sticky="w")
        self.mqtt_port = ttk.Entry(self.mqtt_group, name="mqtt_port")
        self.var_mqtt_port = tk.IntVar(value=1883)
        self.mqtt_port.configure(
            takefocus=False,
            textvariable=self.var_mqtt_port,
            validate="none",
            width=10)
        _text_ = _('1883')
        self.mqtt_port.delete("0", "end")
        self.mqtt_port.insert("0", _text_)
        self.mqtt_port.grid(
            column=5,
            ipadx=1,
            ipady=1,
            padx=1,
            pady=1,
            row=0,
            sticky="w")
        self.label16 = ttk.Label(self.mqtt_group)
        self.label16.configure(text=_('User'))
        self.label16.grid(
            column=0,
            ipadx=1,
            ipady=1,
            padx=1,
            pady=1,
            row=1,
            sticky="w")
        self.mqtt_user = ttk.Entry(self.mqtt_group, name="mqtt_user")
        self.var_mqtt_user = tk.StringVar()
        self.mqtt_user.configure(
            takefocus=False,
            textvariable=self.var_mqtt_user,
            validate="none",
            width=12)
        self.mqtt_user.grid(
            column=1,
            ipadx=1,
            ipady=1,
            padx=1,
            pady=1,
            row=1,
            sticky="w")
        self.label17 = ttk.Label(self.mqtt_group)
        self.label17.configure(text=_('Password'), width=9)
        self.label17.grid(
            column=2,
            ipadx=1,
            ipady=1,
            padx=1,
            pady=1,
            row=1,
            sticky="w")
        self.mqtt_pass = ttk.Entry(self.mqtt_group, name="mqtt_pass")
        self.var_mqtt_pass = tk.StringVar()
        self.mqtt_pass.configure(
            takefocus=False,
            textvariable=self.var_mqtt_pass,
            validate="none",
            width=12)
        self.mqtt_pass.grid(
            column=3,
            ipadx=1,
            ipady=1,
            padx=1,
            pady=1,
            row=1,
            sticky="w")
        self.label19 = ttk.Label(self.mqtt_group)
        self.label19.configure(
            relief="flat",
            takefocus=False,
            text=_('Read Topic'),
            width=14)
        self.label19.grid(column=0, row=2, sticky="w")
        self.mqtt_read_topic = ttk.Entry(
            self.mqtt_group, name="mqtt_read_topic")
        self.var_mqtt_read_topic = tk.StringVar(
            value=_('/remote_serial/tcp2mqtt/write/'))
        self.mqtt_read_topic.configure(
            textvariable=self.var_mqtt_read_topic, width=55)
        _text_ = _('/remote_serial/tcp2mqtt/write/')
        self.mqtt_read_topic.delete("0", "end")
        self.mqtt_read_topic.insert("0", _text_)
        self.mqtt_read_topic.grid(column=1, columnspan=5, row=2, sticky="w")
        self.mqtt_write_topic = ttk.Label(
            self.mqtt_group, name="mqtt_write_topic")
        self.mqtt_write_topic.configure(
            relief="flat",
            takefocus=False,
            text=_('Write Topic'),
            width=14)
        self.mqtt_write_topic.grid(column=0, row=3, sticky="w")
        self.mqtt_w_topic = ttk.Entry(self.mqtt_group, name="mqtt_w_topic")
        self.var_mqtt_write_topic = tk.StringVar(
            value=_('/remote_serial/com2mqtt/write/'))
        self.mqtt_w_topic.configure(
            state="readonly",
            textvariable=self.var_mqtt_write_topic,
            width=55)
        _text_ = _('/remote_serial/com2mqtt/write/')
        self.mqtt_w_topic["state"] = "normal"
        self.mqtt_w_topic.delete("0", "end")
        self.mqtt_w_topic.insert("0", _text_)
        self.mqtt_w_topic["state"] = "readonly"
        self.mqtt_w_topic.grid(column=1, columnspan=5, row=3, sticky="w")
        self.label21 = ttk.Label(self.mqtt_group)
        self.label21.configure(text=_('CRT File'))
        self.label21.grid(column=0, row=4, sticky="w")
        self.mqtt_crt_file = ttk.Entry(self.mqtt_group, name="mqtt_crt_file")
        self.var_mqtt_crt_file = tk.StringVar()
        self.mqtt_crt_file.configure(
            textvariable=self.var_mqtt_crt_file,
            validate="focus",
            width=43)
        self.mqtt_crt_file.grid(column=1, columnspan=4, row=4, sticky="w")
        self.btn_browse = ttk.Button(self.mqtt_group, name="btn_browse")
        self.btn_browse.configure(text=_('Browse'), width=10)
        self.btn_browse.grid(column=5, row=4, sticky="w")
        self.btn_browse.bind(
            "<ButtonPress>",
            self.on_btn_browse_press,
            add="+")
        self.mqtt_unique_ck = ttk.Checkbutton(
            self.mqtt_group, name="mqtt_unique_ck")
        self.var_mqtt_unique_ck = tk.BooleanVar()
        self.mqtt_unique_ck.configure(
            text=_('Unique'),
            variable=self.var_mqtt_unique_ck,
            width=8)
        self.mqtt_unique_ck.grid(
            column=4,
            ipadx=1,
            ipady=1,
            padx=1,
            pady=1,
            row=1,
            sticky="w")
        self.mqtt_unique_ck.bind(
            "<ButtonPress>",
            self.on_mqtt_unique_ck_press,
            add="+")
        self.mqtt_unique = ttk.Entry(self.mqtt_group, name="mqtt_unique")
        self.var_mqtt_unique = tk.StringVar()
        self.mqtt_unique.configure(
            state="readonly",
            textvariable=self.var_mqtt_unique,
            width=10)
        self.mqtt_unique.grid(
            column=5,
            ipadx=1,
            ipady=1,
            padx=1,
            pady=1,
            row=1,
            sticky="w")
        self.mqtt_group.grid(
            column=0,
            ipadx=1,
            ipady=1,
            padx=1,
            pady=1,
            row=1,
            sticky="new")
        self.mqtt_group.grid_propagate(0)
        self.mqtt_group.rowconfigure("all", pad=1, weight=1)
        self.mqtt_group.columnconfigure("all", pad=1, weight=1)
        self.com_group = ttk.Labelframe(self.frame_main, name="com_group")
        self.com_group.configure(height=60, text=_('Serial'), width=590)
        self.label11 = ttk.Label(self.com_group)
        self.label11.configure(
            relief="flat",
            state="disabled",
            text=_('Port'),
            width=6)
        self.label11.grid(
            column=1,
            ipadx=1,
            ipady=1,
            padx=1,
            pady=1,
            row=0,
            sticky="w")
        self.label12 = ttk.Label(self.com_group)
        self.label12.configure(text=_('Baud'))
        self.label12.grid(
            column=3,
            ipadx=1,
            ipady=1,
            padx=1,
            pady=1,
            row=0,
            sticky="w")
        self.label13 = ttk.Label(self.com_group)
        self.label13.configure(text=_('Parity'))
        self.label13.grid(
            column=5,
            ipadx=1,
            ipady=1,
            padx=1,
            pady=1,
            row=0,
            sticky="w")
        self.com_port = ttk.Combobox(self.com_group, name="com_port")
        self.com_port.configure(width=8)
        self.com_port.grid(
            column=2,
            ipadx=1,
            ipady=1,
            padx=1,
            pady=1,
            row=0,
            sticky="w")
        self.com_port.bind("<Button-1>", self.com_port_Lbtn_press, add="+")
        self.com_baud = ttk.Entry(self.com_group, name="com_baud")
        self.var_com_baud = tk.IntVar(value=115200)
        self.com_baud.configure(textvariable=self.var_com_baud, width=10)
        _text_ = _('115200')
        self.com_baud.delete("0", "end")
        self.com_baud.insert("0", _text_)
        self.com_baud.grid(
            column=4,
            ipadx=1,
            ipady=1,
            padx=1,
            pady=1,
            row=0,
            sticky="w")
        self.com_parity = ttk.Combobox(self.com_group, name="com_parity")
        self.com_parity.configure(values='None Even Odd', width=8)
        self.com_parity.grid(
            column=6,
            ipadx=1,
            ipady=1,
            padx=1,
            pady=1,
            row=0,
            sticky="w")
        self.label_1 = ttk.Label(self.com_group)
        self.label_1.configure(text=_('Tx'), width=2)
        self.label_1.grid(column=7, row=0)
        self.com_tx = ttk.Label(self.com_group, name="com_tx")
        self.var_com_tx = tk.IntVar()
        self.com_tx.configure(textvariable=self.var_com_tx, width=8)
        self.com_tx.grid(column=8, row=0)
        self.label_3 = ttk.Label(self.com_group)
        self.label_3.configure(text=_('Rx'), width=2)
        self.label_3.grid(column=9, row=0)
        self.com_rx = ttk.Label(self.com_group, name="com_rx")
        self.var_com_rx = tk.IntVar()
        self.com_rx.configure(textvariable=self.var_com_rx, width=8)
        self.com_rx.grid(column=10, row=0)
        self.com_group.grid(
            column=0,
            ipadx=1,
            ipady=1,
            padx=1,
            pady=1,
            row=0,
            sticky="new")
        self.com_group.grid_propagate(0)
        self.com_group.rowconfigure("all", pad=1, weight=1)
        self.com_group.columnconfigure("all", pad=1, weight=1)
        self.labelframe13 = ttk.Labelframe(self.frame_main)
        self.labelframe13.configure(height=150, text=_('Log'), width=490)
        self.log_text = tk.Text(self.labelframe13, name="log_text")
        self.log_text.configure(
            height=10,
            insertunfocussed="none",
            relief="flat",
            setgrid=False,
            state="disabled",
            takefocus=True,
            undo=False,
            width=40,
            wrap="char")
        self.log_text.pack(
            expand=True,
            fill="both",
            ipadx=1,
            ipady=1,
            padx=1,
            pady=1,
            side="top")
        self.labelframe13.grid(
            column=0,
            columnspan=2,
            ipadx=1,
            ipady=1,
            padx=1,
            pady=1,
            row=2,
            sticky="ew")
        self.labelframe13.pack_propagate(0)
        self.frame2 = ttk.Frame(self.frame_main)
        self.frame2.configure(height=36, width=490)
        self.btn_start = ttk.Button(self.frame2, name="btn_start")
        self.btn_start.configure(text=_('Start'))
        self.btn_start.grid(column=1, ipadx=1, ipady=1, padx=1, pady=1, row=0)
        self.btn_start.bind("<ButtonPress>", self.on_btn_start_press, add="+")
        self.btn_stop = ttk.Button(self.frame2, name="btn_stop")
        self.btn_stop.configure(state="disabled", text=_('Stop'))
        self.btn_stop.grid(
            column=2,
            ipadx=1,
            ipady=1,
            padx=1,
            pady=1,
            row=0,
            sticky="e")
        self.btn_stop.bind("<ButtonPress>", self.on_btn_stop_press, add="+")
        self.start_ok = ttk.Label(self.frame2, name="start_ok")
        self.start_ok.configure(background="#ff0000", width=2)
        self.start_ok.grid(
            column=0,
            ipadx=1,
            ipady=1,
            padx=1,
            pady=1,
            row=0,
            sticky="w")
        self.frame2.grid(
            column=0,
            columnspan=2,
            ipadx=1,
            ipady=1,
            padx=1,
            pady=1,
            row=3,
            sticky="sew")
        self.frame2.grid_propagate(0)
        self.frame2.columnconfigure(0, pad=1, weight=1)
        self.frame2.columnconfigure(1, pad=1, weight=1)
        self.frame2.columnconfigure(2, pad=10)
        self.frame_main.grid(column=0, row=0, sticky="sw")
        self.frame_main.grid_propagate(0)
        self.frame_main.rowconfigure("all", pad=1, weight=1)
        self.frame_main.columnconfigure("all", pad=1, weight=1)
        self.frame_main.bind("<Destroy>", self.on_destroy, add="+")

        # Main widget
        self.mainwindow = self.top_main

    def center(self, event):
        wm_min = self.mainwindow.wm_minsize()
        wm_max = self.mainwindow.wm_maxsize()
        screen_w = self.mainwindow.winfo_screenwidth()
        screen_h = self.mainwindow.winfo_screenheight()
        """ `winfo_width` / `winfo_height` at this point return `geometry` size if set. """
        x_min = min(screen_w, wm_max[0],
                    max(self.main_w, wm_min[0],
                        self.mainwindow.winfo_width(),
                        self.mainwindow.winfo_reqwidth()))
        y_min = min(screen_h, wm_max[1],
                    max(self.main_h, wm_min[1],
                        self.mainwindow.winfo_height(),
                        self.mainwindow.winfo_reqheight()))
        x = screen_w - x_min
        y = screen_h - y_min
        self.mainwindow.geometry(f"{x_min}x{y_min}+{x // 2}+{y // 2}")
        self.mainwindow.unbind("<Map>", self.center_map)

    def run(self, center=False):
        if center:
            """ If `width` and `height` are set for the main widget,
            this is the only time TK returns them. """
            self.main_w = self.mainwindow.winfo_reqwidth()
            self.main_h = self.mainwindow.winfo_reqheight()
            self.center_map = self.mainwindow.bind("<Map>", self.center)
        self.mainwindow.mainloop()

    def on_btn_browse_press(self, event=None):
        pass

    def on_mqtt_unique_ck_press(self, event=None):
        pass

    def com_port_Lbtn_press(self, event=None):
        pass

    def on_btn_start_press(self, event=None):
        pass

    def on_btn_stop_press(self, event=None):
        pass

    def on_destroy(self, event=None):
        pass


# if __name__ == "__main__":
#     app = Com2MqttApp()
#     app.run()
