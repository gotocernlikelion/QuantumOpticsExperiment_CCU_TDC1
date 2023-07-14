

"""
This is a script that provides a simple GUI to take snapshots of the signal events within the integration window.

Author: Lim Chin Chean 05/2019 Modded from QO Lab Script

Note: the data rate for USB read is <125 Mbps, take that into account when you are dealing with runs that has very high count rates!
     There is some room for improvement in terms of data rate as USB 2.0 protocol should be faster than 125 Mbps, work in progress.
"""

from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import csv
import usbcount_class as UC
import serial.tools.list_ports
import matplotlib.pyplot as plt
import time
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation

# sets the size of the font for the counters
ft_size = 20
# sets the trigger type of input signal, PLEASE CHECK THIS. 'nim' or 'ttl'
signal_type='ttl'

# Lists for stored timestamped events.
pattern_loop = []
timestamp_loop = []
Counter_loop = []
directory = ''

# set default path of CSV file for timestamp data. Note that the file gets overwritten when you restart the parsing.
timepath = 'Timeevents.dat'
histopath = 'Histo.dat'

# Initialize the counter value array for displayed graph.
xar = [0]
c00_yar = [0]
c01_yar = [0]
c12_yar = [0]

# This allows GUI user to create file path for histogram data.
def SetSave(*args):
    directory = filedialog.asksaveasfilename(initialdir="/", title="Select file",filetypes=(("dat files", "*.dat"), ("all files", "*.*")))
    print("New path: " + directory)
    global histopath
    histopath = directory

# single shot timestamp within integration time.
def change_snap_f(*args):
    loop_flag.set(True)
    print("Set Integration time:" + timer_00.get() + "ms")
    [timestamp,pattern] = counter.timestamp_acq_python(timer_00.get(),signal_type)
    [hist, histN, cnt1, cnt2, coincidence, binwidth, maxbins] = counter.g2(timestamp, pattern, CoincidenceWindow_00.get(),binwidth_00.get(),Maxbin_00.get())
    print("CH1 Count " +str(cnt1) + " /// CH2 Count " + str(cnt2))
    Counter = [binwidth,maxbins, cnt1,cnt2, coincidence]
    histogram = histN + hist
    Counter.extend(histogram)
    table = zip(pattern, timestamp)
    with open(timepath, 'w') as csvFile:
        writer = csv.writer(csvFile, delimiter=' ')
        writer.writerows(table)
        csvFile.close()
    with open(histopath, 'w') as csvFile:
        writer = csv.writer(csvFile, delimiter=' ')
        writer.writerow(Counter)
        csvFile.close()

# Function to start the parsing and concatenating timestamp lists from looped snapshots.
def start_f(*args):
    loop_flag.set(True)
    while loop_flag.get():
        [timestamp,pattern] = (counter.timestamp_acq_python(timer_00.get(),signal_type))
        [hist, histN, cnt1, cnt2, coincidence, binwidth, maxbins] = counter.g2(timestamp, pattern, CoincidenceWindow_00.get(),binwidth_00.get(),Maxbin_00.get())
        print("CH1 Count " + str(cnt1) + " /// CH2 Count " + str(cnt2))
        if savedata.get():
            Counter = [binwidth, maxbins, cnt1, cnt2, coincidence]
            histogram = histN + hist
            Counter.extend(histogram)
            Counter_loop.append(Counter)
            pattern_loop.extend(pattern)
            timestamp_loop.extend(timestamp)

        counter_00.set('{:6.1f}'.format(cnt1))
        counter_01.set('{:6.1f}'.format(cnt2))
        counter_12.set('{:6.1f}'.format(coincidence))
        if cnt1*cnt2 != 0:
            counter_ef1.set('{:6.1f}'.format(coincidence/cnt1*100))
            counter_ef2.set('{:6.1f}'.format(coincidence/cnt2*100))
        root.update()

# Stop querying the timestamp function, writes collected parsed timestamps into csv file.
def stop_f(*args):
    loop_flag.set(False)
    table = zip(pattern_loop, timestamp_loop)
    with open(timepath, 'w') as csvFile:
        writer = csv.writer(csvFile, delimiter=' ')
        writer.writerows(table)
        csvFile.close()
    with open(histopath, 'w') as csvFile:
        writer = csv.writer(csvFile, delimiter=' ')
        writer.writerows(Counter_loop)
        csvFile.close()
    pattern_loop.clear()
    timestamp_loop.clear()
    Counter_loop.clear()
    counter_00.set('{:6.1f}'.format(0))
    counter_01.set('{:6.1f}'.format(0))
    counter_12.set('{:6.1f}'.format(0))

# Creates a graph for the GUI.
fig = plt.Figure(figsize=[9.9, 4.8])

# Looping for graph animation, the axis shifts by finding the max values.
def animate(i):
    xar.append(int(round(time.time() * 1000)))
    c00_yar.append(float(counter_00.get()))
    c01_yar.append(float(counter_01.get()))
    c12_yar.append(float(counter_12.get()))
    if max(xar)-xar[0] > 5000:
        xar.pop(0)
        c00_yar.pop(0)
        c01_yar.pop(0)
        c12_yar.pop(0)
    axes = fig.gca()
    axes.set_xlim([max(xar)-5000, max(xar)+5000])
    max_values = [max(c00_yar),max(c01_yar)]
    if loop_flag.get():
      ax.set_ylim([0, max(max_values)*1.1])
      ax2.set_ylim([0, max(c12_yar) * 1.1])
    line1.set_xdata(xar)
    line1.set_ydata(c00_yar)  # update the data
    line2.set_xdata(xar)
    line2.set_ydata(c01_yar)  # update the data
    line3.set_xdata(xar)
    line3.set_ydata(c12_yar)  # update the data
    return line1, line2, line3

# Stop querying the timestamp function, close device and initiate selected device in timestamp mode.
def InitDevice(*args):
    loop_flag.set(False)
    started = 1
    deviceAddress = ''
    for idx, device in enumerate(devicelist):
        if set_ports.get() == device:
            deviceAddress = addresslist[idx]
    print("SelectedPort " + deviceAddress)
    counter.startport(deviceAddress)
    counter.mode = 'timestamp'
    timestamp_loop.clear()
    print(set_ports.get(), "ready to go.")

def on_closing():
    counter.closeport()
    root.destroy()

"""Setting up the main window"""
root = Tk()
root.title("USB counter")
mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(0, weight=1)
loop_flag = BooleanVar()
loop_flag.set(False)
counter = UC.FPGA_counter()

# # 김준호의 코드 추가 (사이드바)
# scrollbar = ttk.Scrollbar(mainframe, orient="vertical")
# scrollbar.grid(row = 3, column=1, sticky = 'ns')

# Device option menu.
ttk.Label(mainframe, text='Select Device', font=("Helvetica", 12)).grid(row=2, padx=0, pady=2, column=1)
portslist = list(serial.tools.list_ports.comports())
devicelist = []
addresslist = []
for port in portslist:
    devicelist.append(port.device + " " + port.description)
    addresslist.append(port.device)
print(devicelist)
set_ports = StringVar(mainframe)
ports_option = ttk.OptionMenu(mainframe, set_ports, devicelist, *devicelist)
ports_option.grid(row=2, padx=2, pady=5, column=2)
ports_option.configure(width=30)


# buttons
ttk.Button(mainframe, text="Start", command=start_f).grid(
    column=1, row=6, sticky=W)
ttk.Button(mainframe, text="Stop", command=stop_f).grid(
    column=2, row=6, sticky=W)
ttk.Button(mainframe, text="Timestamp Snapshot", command=change_snap_f).grid(
    column=3, row=6, sticky=W)
ttk.Button(mainframe, text="Init Device", command=InitDevice).grid(
    column=4, row=2, sticky=W)
ttk.Button(mainframe, text="Histogram Path", command=SetSave).grid(
    column=4, row=4, sticky=W)

# checkbox
savedata = BooleanVar()
Checkbutton(mainframe, text="Record?", variable=savedata).grid(row=4,column=1, sticky = W)

# Spinbox variables.
timer_00 = IntVar()
CoincidenceWindow_00 = IntVar()
binwidth_00 = IntVar()
Maxbin_00 = IntVar()

# controls: Gate Time
time_entry = Spinbox(mainframe, width=7, from_=0.1, to=5,
                     increment=.1, textvariable=timer_00)
time_entry.grid(column=1, row=8, sticky=(W))
timer_00.set(400)
print(timer_00.get())

# controls: Coincidence Window
CoincidenceWindow_entry = Spinbox(mainframe, width=7, from_=0.1, to=5,
                     increment=.1, textvariable=CoincidenceWindow_00)
CoincidenceWindow_entry.grid(column=2, row=8, sticky=(W))
CoincidenceWindow_00.set(100)
print(CoincidenceWindow_00.get())

# controls: Binwidth
binwidth_entry = Spinbox(mainframe, width=7, from_=0.1, to=5,
                     increment=.1, textvariable=binwidth_00)
binwidth_entry.grid(column=3, row=8, sticky=(W))
binwidth_00.set(1)
print(binwidth_00.get())

# controls: Maximum bins.
Maxbin_entry = Spinbox(mainframe, width=7, from_=0.1, to=5,
                     increment=.1, textvariable=Maxbin_00)
Maxbin_entry.grid(column=4, row=8, sticky=(W))
Maxbin_00.set(100)
print(Maxbin_00.get())

# title
ttk.Label(mainframe, text='Timestamp',
          font=("Helvetica", 18)).grid(column=2, row=1, sticky=(W, E))

# Text display variables.
counter_00 = StringVar()
counter_00.set(format(0))
counter_01 = StringVar()
counter_01.set(format(0))
counter_12 = StringVar()
counter_12.set(format(0))
counter_ef1 = StringVar()
counter_ef1.set(format(0))
counter_ef2 = StringVar()
counter_ef2.set(format(0))

# labels
ttk.Label(mainframe, text='Gate Time /ms',
          font=("Helvetica", 8)).grid(column=1, row=9, sticky=(W))
ttk.Label(mainframe, text='Coincidence Window /ns',
          font=("Helvetica", 8)).grid(column=2, row=9, sticky=(W))
ttk.Label(mainframe, text='Binwidth /ns',
          font=("Helvetica", 8)).grid(column=3, row=9, sticky=(W))
ttk.Label(mainframe, text='Maxbins',
          font=("Helvetica", 8)).grid(column=4, row=9, sticky=(W))
ttk.Label(mainframe, text='Channel 1',
          font=("Helvetica", 10)).grid(column=5, row=2, sticky=(E))
ttk.Label(mainframe, text='Channel 2',
          font=("Helvetica", 10)).grid(column=5, row=3, sticky=(E))
ttk.Label(mainframe, text='Pairs',
          font=("Helvetica", 10)).grid(column=5, row=4, sticky=(E))
ttk.Label(mainframe, text='Eff 1 %',
          font=("Helvetica", 10)).grid(column=5, row=5, sticky=(E))
ttk.Label(mainframe, text='Eff 2 %',
          font=("Helvetica", 10)).grid(column=5, row=6, sticky=(E))
ttk.Label(mainframe, textvariable=counter_00, width=7, anchor=E,
          font=("Helvetica", 10)).grid(column=6, row=2, sticky=(W, E))
ttk.Label(mainframe, textvariable=counter_01, width=7, anchor=E,
          font=("Helvetica", 10)).grid(column=6, row=3, sticky=(W, E))
ttk.Label(mainframe, textvariable=counter_12, width=7, anchor=E,
          font=("Helvetica", 10)).grid(column=6, row=4, sticky=(W, E))
ttk.Label(mainframe, textvariable=counter_ef1, width=7, anchor=E,
          font=("Helvetica", 10)).grid(column=6, row=5, sticky=(W, E))
ttk.Label(mainframe, textvariable=counter_ef2, width=7, anchor=E,
          font=("Helvetica", 10)).grid(column=6, row=6, sticky=(W, E))

# Basic setup for the displayed graph.
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().grid(column=0,row=1)

ax = fig.add_subplot(111)
ax2 = ax.twinx()
line1, = ax.plot(xar, c00_yar, color='blue')
line2, = ax.plot(xar, c01_yar, color='green')
line3, = ax2.plot(xar, c12_yar, color='red', linestyle = '--')
box = ax.get_position()
ax.set_position([box.x0, box.y0, box.width * 0.9, box.height])
fig.legend(['C1', 'C2', 'C12'], loc='upper right', bbox_to_anchor = [1.0, 1])
fig.suptitle('Counts (TTL) vs Current Time')
ax.set_xlabel('Time / ms')
ax.set_ylabel('Counts')
ax.grid(True)
ani = animation.FuncAnimation(fig, animate, interval=100, blit=False)


# padding the space surrounding all the widgets
for child in mainframe.winfo_children():
    child.grid_configure(padx=10, pady=10)

root.protocol("WM_DELETE_WINDOW",on_closing)

# finally we run it!
root.mainloop()

