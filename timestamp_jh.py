import numpy as np
from  S15lib.instruments import TimestampTDC1

# t_acq Aqusition Time: 가동시간 (단위 : s)
t_acq =0.01

# channel 구분
ch1 = 1
ch2 = 2
ch3 = 4
ch4 = 8

# TimestampTDC1 모듈로 timestamp 모드 (각 채널별 신호의 leading edge에 time 기록)
ts = TimestampTDC1()
ts.level = ts.TTL_LEVELS #use ts.NIM_LEVELS for nim signals
t,p = ts.get_timestamps(t_acq)
p_int = np.array([ int(T,2) for T in p])

t1 = t[p_int==ch1]
t2 = t[p_int==ch2]
t3 = t[p_int==ch3]
t4 = t[p_int==ch4]
# print(t1)
# print(p)

# Check time separation : 1.000042000000000000e+06 ns -> 1.000042ms
# tt1 = []
# for i in range(1,len(t1)-1):
#     tt1.append(t1[i+1]-t1[i])
# tt1.append(tt1[len(tt1)-1])
# print(tt1)
# np.savetxt('timestamp_separation_ch1.txt', tt1)

# tt3 = []
# for i in range(1,len(t3)-1):
#     tt3.append(t3[i+1]-t3[i])
# tt3.append(tt3[len(tt3)-1])
# print(tt3)
# np.savetxt('timestamp_separation_ch3.txt', tt3)

## txt 파일로 저장
# time
np.savetxt('timestamp_ch1.txt', t1)
np.savetxt('timestamp_ch2.txt', t2)
np.savetxt('timestamp_ch3.txt', t3)
np.savetxt('timestamp_ch4.txt', t4)
#event
np.savetxt('timestamp_event.txt', p,fmt='%s')



######################################
# c = ts.count_g2(t_acq =  0.5,
#                 bin_width = 2,
#                 bins=40,
#                 ch_stop_delay=2,
#                 ch_start=1,
#                 ch_stop=3,)

# histo = c['histogram']
# time_ax = c['time_bins']

# # 코드 실행 전에 histo와 time_ax 변수가 적절한 값으로 설정되어 있다고 가정
# # 저장할 파일의 경로를 지정
# save_directory = '/TimestampsData'

# # histo를 텍스트 파일에 저장
# histo_file_path = os.path.join(save_directory, 'histo.txt')
# np.savetxt(histo_file_path, histo)

# # time_ax를 텍스트 파일에 저장
# time_ax_file_path = os.path.join(save_directory, 'time_ax.txt')
# np.savetxt(time_ax_file_path, time_ax)