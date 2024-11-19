import tkinter as tk
from tkinter import ttk

class ECGMonitor(tk.Tk):
    def __init__(self):
        super().__init__()            #调用父类，初始化UI界面
        self.title("ECG Monitor")     #设置窗口标题
        self.geometry("1280x720")      #设置窗口大小

        # ECG Graph                   #心电图,根据数组绘制图形
        self.ecg_graph_label = ttk.Label(self, text = "ECG Graph: [Graph Placeholder]")
        self.ecg_graph_label.pack(pady = 10)
        self.ecg_canvas = tk.Canvas(self, width = 1024, height = 500, bg = "white")
        self.ecg_canvas.pack(pady=10)

        # Signal Quality              #信号质量
        self.signal_quality_label = ttk.Label(self, text = "Signal Quality: Good")
        self.signal_quality_label.pack(pady=10)

        # Heart Rate                 #心率
        self.heart_rate_label = ttk.Label(self, text = "Heart Rate: 72 BPM")
        self.heart_rate_label.pack(pady = 10)

        # Initialize data
        self.ecg_data = [0] * (512*2)    #显示2秒的数据

    def update_ecg_quality(self, quality):
        self.signal_quality_label.config(text = f"Signal Quality: {quality}")
        
    def update_ecg_heart_rate(self, heart_rate): 
        self.heart_rate_label.config(text = f"Heart Rate:{heart_rate} BPM")
        
    def update_ecg_graph(self, data):
        # Transform data to fit the canvas
        transformed_data = int((data / 65536.0) * 500)
        self.ecg_data.append(transformed_data)
        self.ecg_data.pop(0)
        #clear canvas
        self.ecg_canvas.delete("all")

        #Draw ECG Graph
        
        x1 = 0
        y1 = 250 - self.ecg_data[0]
        for i in range(len(self.ecg_data) - 1):
            # x1 = self.ecg_canvas.canvasx(700-i)
            # y1 = self.ecg_canvas.canvasy(300 - self.ecg_data[i])
            # x2 = self.ecg_canvas.canvasx(699-i)
            # y2 = self.ecg_canvas.canvasy(300 - self.ecg_data[i + 1])
            x2 = i + 1
            y2 = 250 - self.ecg_data[i + 1]
            self.ecg_canvas.create_line(x1, y1, x2, y2, fill="blue")
            x1, y1 = x2, y2

if __name__ == "__main__":
    import serial
    window = ECGMonitor()
    window.mainloop()
    
    # 初始化串口
    def init_serial():
        try:
            ser = serial.Serial('COM9', baudrate=57600, timeout=1)
            return ser
        except serial.SerialException as e:
            print(f"Error initializing serial port: {e}")
            return None
    
    ser = init_serial()

     #解码器
    def decode_data(data):       
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

    def read_serial():
        """读取串口数据"""
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
                            window.update_ecg_graph(value)


                        elif data == b'\x12':  # 检查是否是大数据包
                            data = ser.read(1)  # 02
                            if data == b'\x02':
                                print("senser on")
                            else:
                                print("senser off")
                            ser.read(2) #00 03
                            data = ser.read(1)
                            heart_rate = int.from_bytes(data, byteorder='big')  # 将心率数据转换为十进制数
                            window.update_ecg_heart_rate(heart_rate)
                            print(f"心率: {heart_rate}")
            except serial.SerialException as e:
                #print(f"Error reading from serial port: {e}")
                ser = None
            
