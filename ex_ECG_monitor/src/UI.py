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
            

if __name__ == "__main__":      #测试UI界面，外部调用不会执行
    import math
    import time
    window = ECGMonitor()
    
    def generate_test_data():    #内部测试数据
        return int((math.sin(time.time()))* 32768)
    
    def update_test_data():      #更新数据
        new_data = generate_test_data()
        window.update_ecg_graph(new_data)
        window.after(2, update_test_data)   #每2ms更新一次数据
    
    update_test_data()
    window.mainloop()
    
    
    
    