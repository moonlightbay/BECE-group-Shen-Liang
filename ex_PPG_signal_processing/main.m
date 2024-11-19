clc; clear; close all;
PPG_file = 'src/ppg.csv';% 读取CSV文件
opts = detectImportOptions(PPG_file, 'NumHeaderLines', 5); % 跳过前5行
data = readtable(PPG_file, opts);


r_amp = data{:, 6};    % 提取PPG数据    6;14
ir_amp = data{:, 14};
fs = 25;   %采样率
ts = ((0:length(r_amp)-1)/fs);      %根据采样率和数据长度计算时间序列

acc_file = 'src/acc.csv'; % 提取加速度数据
opts = detectImportOptions(acc_file, 'NumHeaderLines', 3); % 跳过前3行
data = readtable(acc_file, opts);
x_acc = data{:, 2};
y_acc = data{:, 3};
z_acc = data{:, 4};

x_acc = x_acc - mean(x_acc);%x,y,z去均值化
y_acc = y_acc - mean(y_acc);
z_acc = z_acc - mean(z_acc);
magnitude = sqrt(x_acc.^2 + y_acc.^2 + z_acc.^2); %计算合加速度

fs_acc = 25;
ts_acc = ((0:length(x_acc)-1)/fs_acc); %根据采样率和数据长度计算时间序列
figure;   % 绘制加速度数据
subplot(2, 1, 1);
plot(ts_acc, x_acc, 'r', 'LineWidth', 1.5);
hold on;
plot(ts_acc, y_acc, 'g', 'LineWidth', 1.5);
plot(ts_acc, z_acc, 'b', 'LineWidth', 1.5);
xlabel('Time (s)');
ylabel('Amplitude');
title('Acceleration Data');
legend('X', 'Y', 'Z');
grid on;
hold off;

subplot(2, 1, 2);
plot(ts_acc, magnitude, 'k', 'LineWidth', 1.5);
xlabel('Time (s)');
ylabel('Amplitude');
title('Magnitude of Acceleration');
grid on;

fc_low = 0.6;                          % 设计低通滤波器（用于提取DC成分）
[b_low, a_low] = butter(3, fc_low / (fs / 2), 'low');
r_dc = filtfilt(b_low, a_low, r_amp);
ir_dc = filtfilt(b_low, a_low, ir_amp);
r_ac = r_amp - r_dc;                 % 计算AC成分
ir_ac = ir_amp - ir_dc;

fc_low = 5;                          % 低通滤波
[b_low, a_low] = butter(2, fc_low / (fs / 2), 'low');
r_ac = filtfilt(b_low, a_low, r_ac);
ir_ac = filtfilt(b_low, a_low, ir_ac);



[r_pks,r_locs_pks] = findpeaks(r_ac,ts,'MinPeakHeight',100,'MinPeakDistance',10);    %寻找AC信号的峰值和谷值
[ir_pks,ir_locs_pks] = findpeaks(ir_ac,ts,'MinPeakHeight',100,'MinPeakDistance',10);
[r_valleys,r_locs_vlys] = findpeaks(-r_ac,ts,'MinPeakHeight',100,'MinPeakDistance',10);
[ir_valleys,ir_locs_vlys] = findpeaks(-ir_ac,ts,'MinPeakHeight',100,'MinPeakDistance',10);


r_ac_amp = mean(r_pks) - mean(r_valleys);%计算AC信号的峰谷值
ir_ac_amp = mean(ir_pks) - mean(ir_valleys);


r_ratio = r_ac_amp/ mean(r_dc); % 计算红光和红外光信号的AC/DC比值
ir_ratio = ir_ac_amp / mean(ir_dc);
R = r_ratio / ir_ratio;% 计算R值

% SpO2 = 110 - 25 * R;常见的SpO2计算公式
SpO2 = -45.060*R*R+30.354*R+94.845;  % MAX30102 经验证的SpO2计算公式


fprintf('Estimated SpO2: %.2f%%\n', SpO2);% 输出SpO2值

figure;% 绘制图形
plot(ts, r_amp, 'r', 'LineWidth', 1.5);
hold on;
plot(ts, ir_amp, 'b', 'LineWidth', 1.5);
xlabel('Time (s)');
ylabel('Amplitude');
title('Original PPG Signal');
legend('Red', 'IR');
grid on;
hold off;

figure;
subplot(2, 1, 1);
plot(ts, r_dc, 'r', 'LineWidth', 1.5);
hold on;
plot(ts, ir_dc, 'b', 'LineWidth', 1.5);
xlabel('Time (s)');
ylabel('Amplitude');
title('DC Component of PPG Signal');
legend('Red DC', 'IR DC');
grid on;
hold off;

subplot(2, 1, 2);
plot(ts, r_ac, 'r', 'LineWidth', 1.5);
hold on;
plot(ts, ir_ac, 'b', 'LineWidth', 1.5);
xlabel('Time (s)');
ylabel('Amplitude');
title('AC Component of PPG Signal');
legend('Red AC', 'IR AC');
grid on;
hold off;