import tkinter as tk
from tkinter import ttk
import threading
import serial
import struct
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation

# 初始化串口
def init_serial():
    try:
        ser = serial.Serial('COM3', baudrate=57600, timeout=1)
        return ser
    except serial.SerialException as e:
        print(f"Error initializing serial port: {e}")
        return None

ser = init_serial()

def decode_data(data):  # 解码器
    if len(data) < 2:
        raise ValueError("数据长度不足")
    value0 = data[0]
    value1 = data[1]
    raw = value0 * 256 + value1
    if raw >= 32768:
        raw -= 65536
    return raw

# 创建一个全局变量来存储数据
data_values = []
heart_rate = 0
signal_quality = "Unknown"
signal_good = True  # 新增变量，记录信号质量是否为Good

def read_serial():
    global ser, data_values, heart_rate, signal_quality, signal_good
    while True:
        if ser is None:
            ser = init_serial()
            if ser is None:
                continue
        try:
            data = ser.read(1)  # 读取1个字节的数据包
            if data == b'\xAA':  # 检查数据包前缀
                data = ser.read(1)  # 读取1个字节的数据包
                if data == b'\xAA':  # 检查数据包前缀
                    data = ser.read(1)  # 读取1个字节的数据包
                    if data == b'\x04':  # 检查是否是小数据包
                        data = ser.read(2)  # 02
                        data = ser.read(2)  # 数值
                        value = decode_data(data)  # 解析数据包中的值（大端序）
                        if signal_good:
                            data_values.append(value)  # 将值添加到数据列表中
                        else:
                            data_values.append(0)  # 信号质量为Bad时，添加0
                        if len(data_values) > 512:
                            data_values.pop(0)  # 保持数据列表的长度为512
                    elif data == b'\x12':  # 检查是否是大数据包
                        ser.read(1)  # 02
                        data = ser.read(1)
                        if data == b'\xC8':
                            signal_quality = "Good"
                            signal_good = True
                        else:
                            signal_quality = "Bad"
                            signal_good = False
                        ser.read(1)  #03
                        data = ser.read(1)
                        heart_rate = int.from_bytes(data, byteorder='big')  # 将心率数据转换为十进制数
        except serial.SerialException as e:
            ser = None

# 创建并启动读取串口数据的线程
serial_thread = threading.Thread(target=read_serial)
serial_thread.start()

# 创建一个图形窗口
class ECGMonitor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ECG Monitor")
        self.geometry("1280x720")

        # 心率
        self.heart_rate_label = ttk.Label(self, text="心率: 0 BPM")
        self.heart_rate_label.pack(pady=10)

        # 信号质量
        self.signal_quality_label = ttk.Label(self, text="信号质量: Unknown")
        self.signal_quality_label.pack(pady=10)

        # 导联脱落
        self.lead_off_label = ttk.Label(self, text="", foreground="red", font=("Helvetica", 16))
        self.lead_off_label.pack(pady=10)

        # 创建一个图形窗口（matplotlib）
        self.fig, self.ax = plt.subplots()    #创建一个图形窗口,fig是画布，ax是坐标轴
        self.xdata, self.ydata = [], []
        self.ln, = plt.plot([], [], 'r-')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)  #matplotlib图形嵌入到tkinter中
        self.canvas.get_tk_widget().pack()
        # 动画
        self.ani = FuncAnimation(self.fig, self.update_plot, frames=512, init_func=self.init_plot, blit=True, interval=1)

        self.update_ui()

    def init_plot(self):                 #初始化画布
        self.ax.set_xlim(0, 512)
        self.ax.set_ylim(-5000, 5000)
        return self.ln,

    def update_plot(self, frame):        #更新画布
        self.xdata = np.arange(len(data_values))
        self.ydata = data_values
        self.ln.set_data(self.xdata, self.ydata)
        return self.ln,

    def update_ui(self):                   #更新UI界面（tkinter）
        self.heart_rate_label.config(text=f"心率: {heart_rate} BPM")
        self.signal_quality_label.config(text=f"信号质量: {signal_quality}")
        if signal_quality == "Bad":
            self.lead_off_label.config(text="导联脱落")
        else:
            self.lead_off_label.config(text="")
        self.after(1000, self.update_ui)

if __name__ == "__main__":               #运行主程序
    window = ECGMonitor()
    window.mainloop()

