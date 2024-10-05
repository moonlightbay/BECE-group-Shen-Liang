import serial
import struct
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
import threading

# 初始化串口
def init_serial():
    try:
        ser = serial.Serial('COM9', baudrate=57600, timeout=1)
        return ser
    except serial.SerialException as e:
        print(f"Error initializing serial port: {e}")
        return None

ser = init_serial()

def decode_data(data):#解码器
    # 确保数据长度足够
    if len(data) < 2:
        raise ValueError("数据长度不足")

    value0 = data[0]
    value1 = data[1]

    # 计算raw值
    raw = value0 * 256 + value1

    # 如果raw大于等于32768，则减去65536
    if raw >= 32768:
        raw -= 65536

    return raw

# 创建一个全局变量来存储数据
data_values = []

def read_serial():
    """读取串口数据"""
    global ser, data_values
    while True:
        if ser is None:
            ser = init_serial()
            if ser is None:
                continue
        try:
            data = ser.read(1)  # 读取1个字节的数据包
            if data == b'\xAA':  # 检查数据包前缀
                data = ser.read(1)  # 读取1个字节的数据包
                #print(f"Received data: 1{data}")
                if data == b'\xAA':  # 检查数据包前缀
                    data = ser.read(1)  # 读取1个字节的数据包
                    #print(f"Received data: 2{data}")
                    if data == b'\x04':  # 检查是否是小数据包
                        data = ser.read(2)  # 02
                        #print(f"Received data: 02chu{data}")
                        data = ser.read(2)  # 数值
                        #print(f"Received data: 3{data}")
                        value = decode_data(data) # 解析数据包中的值（大端序）
                        #print(f"Parsed value: 数值{value}")
                        data_values.append(value)  # 将值添加到数据列表中
                        if len(data_values) > 512:
                            data_values.pop(0)  # 保持数据列表的长度为512

                    elif data == b'\x12':  # 检查是否是大数据包
                        data = ser.read(1)  # 02
                        if data == b'\x02':
                            print("senser on")
                        else:
                            print("senser off")
                        ser.read(2) #00 03
                        data = ser.read(1)
                        heart_rate = int.from_bytes(data, byteorder='big')  # 将心率数据转换为十进制数
                        print(f"心率: {heart_rate}")
        except serial.SerialException as e:
            #print(f"Error reading from serial port: {e}")
            ser = None

# 创建并启动读取串口数据的线程
serial_thread = threading.Thread(target=read_serial)
serial_thread.start()

# 创建一个图形窗口
fig, ax = plt.subplots()
xdata, ydata = [], []
ln, = plt.plot([], [], 'r-')

def init():
    ax.set_xlim(0, 512)
    ax.set_ylim(-5000, 5000)
    return ln,

def update(frame):
    xdata = np.arange(len(data_values))
    ydata = data_values
    ln.set_data(xdata, ydata)
    return ln,

ani = FuncAnimation(fig, update, frames=512, init_func=init, blit=True, interval=1)

plt.show()
