

"""
counter_FPGA_GUI.py is the GUI for continuous counting using the USB counter module
as a timestamp card.

Author: Lim Chin Chean 05/2019, S-Fifteen Instruments. Modded from QO Lab Script

"""
# from qitdevices.usb_counter import *
import usbcount_class as UC
import numpy as np
from tkinter import *
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
import serial.tools.list_ports

# sets the size of the font for the counters
ft_size = 42
# sets the trigger type of input signal, PLEASE CHECK THIS. 'nim' or 'ttl'
signal_type='ttl'


# Stop querying the timestamp function, close device and initiate selected device in pairs mode.
def InitDevice(*args):
    loop_flag.set(False)
    started = 1
    deviceAddress = ''
    for idx, device in enumerate(devicelist):
        if set_ports.get() == device:
            deviceAddress = addresslist[idx]
    print("SelectedPort " + deviceAddress)
    counter.startport(deviceAddress)
    counter.mode = 'pairs'
    print(set_ports.get(), "ready to go.")

def on_closing():
    counter.closeport()
    root.destroy()

# Function to change the integration time.
def change_counter_f(*args):
    loop_flag.set(True)
    counter.int_time=timer_00.get()

# Function to start the counter.
def start_f(*args):
    loop_flag.set(True)
    counter_100.set(0)
    counter_101.set(0)
    counter_102.set(0)
    while loop_flag.get():
        counter_value=counter.counts
        print(counter_value)
        counter_00.set('{:6.1f}'.format(counter_value[0]))
        counter_01.set('{:6.1f}'.format(counter_value[1]))
        counter_02.set('{:6.1f}'.format(counter_value[2]))
        counter_03.set('{:6.1f}'.format(counter_value[3]))
        counter_100.set('{:6.1f}'.format(counter_value[4]))
        counter_101.set('{:6.1f}'.format(counter_value[5]))
        counter_102.set('{:6.1f}'.format(counter_value[6]))
        counter_103.set('{:6.1f}'.format(counter_value[7]))
        root.update()

# Stop querying the counter function, resets counter display in GUI.
def stop_f(*args):
    counter_00.set(format(0))
    counter_01.set(format(0))
    counter_02.set(format(0))
    counter_03.set(format(0))
    counter_100.set(format(0))
    counter_101.set(format(0))
    counter_102.set(format(0))
    counter_103.set(format(0))
    loop_flag.set(False)

# Creates a graph for the GUI.
fig = plt.Figure(figsize=[9.4, 4.8])

# Initialize the counter value array for displayed graph.
xar = [0]
c00_yar = [0]
c01_yar = [0]
c02_yar = [0]
c03_yar = [0]
c100_yar = [0]
c101_yar = [0]
c102_yar = [0]
c103_yar = [0]

# Updates the graphs with new values, resizes the axes every loop. The x-axis is the UTC time in milliseconds since the epoch.
def animate(i):
    xar.append(int(round(time.time() * 1000)))
    c00_yar.append(float(counter_00.get()))
    c01_yar.append(float(counter_01.get()))
    c02_yar.append(float(counter_02.get()))
    c03_yar.append(float(counter_03.get()))
    c100_yar.append(float(counter_100.get()))
    c101_yar.append(float(counter_101.get()))
    c102_yar.append(float(counter_102.get()))
    c103_yar.append(float(counter_103.get()))
    if max(xar) - xar[0] > 5000:
        xar.pop(0)
        c00_yar.pop(0)
        c01_yar.pop(0)
        c02_yar.pop(0)
        c03_yar.pop(0)
        c100_yar.pop(0)
        c101_yar.pop(0)
        c102_yar.pop(0)
        c103_yar.pop(0)
    axes = fig.gca()
    axes.set_xlim([max(xar)-5000, max(xar)+5000])
    max_values = [max(c00_yar),max(c01_yar),max(c02_yar),max(c03_yar),max(c100_yar),max(c101_yar),max(c102_yar),max(c103_yar)]
    axes.set_ylim([1, max(max_values)+10])

    line1.set_xdata(xar)
    line1.set_ydata(c00_yar)  # update the data
    line2.set_xdata(xar)
    line2.set_ydata(c01_yar)  # update the data
    line3.set_xdata(xar)
    line3.set_ydata(c02_yar)  # update the data
    line4.set_xdata(xar)
    line4.set_ydata(c03_yar)  # update the data
    line5.set_xdata(xar)
    line5.set_ydata(c100_yar)  # update the data
    line6.set_xdata(xar)
    line6.set_ydata(c101_yar)  # update the data
    line7.set_xdata(xar)
    line7.set_ydata(c102_yar)  # update the data
    line8.set_xdata(xar)
    line8.set_ydata(c103_yar)  # update the data
    return line1, line2, line3, line4, line5, line6, line7, line8



"""Setting up the main window"""
root = Tk()
root.title("USB counter")
mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(0, weight=1)

counter = UC.FPGA_counter()
#counter.level=signal_type
#counter.mode = 'pairs'

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
ports_option.grid(row=7, padx=2, pady=5, column=2)
ports_option.configure(width=30)
loop_flag = BooleanVar()
loop_flag.set(False)

# String Variables used
counter_00 = StringVar()
counter_00.set(format(0))
counter_01 = StringVar()
counter_01.set(format(0))
counter_02 = StringVar()
counter_02.set(format(0))
counter_03 = StringVar()
counter_03.set(format(0))
counter_100 = StringVar()
counter_100.set(format(0))
counter_101 = StringVar()
counter_101.set(format(0))
counter_102 = StringVar()
counter_102.set(format(0))
counter_103 = StringVar()
counter_103.set(format(0))

timer_00 = StringVar()

# Basic setup for the displayed graph.
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().grid(column=0,row=1)

ax = fig.add_subplot(111)
line1, = ax.plot(xar, c00_yar)
line2, = ax.plot(xar, c01_yar)
line3, = ax.plot(xar, c02_yar)
line4, = ax.plot(xar, c03_yar)
line5, = ax.plot(xar, c100_yar)
line6, = ax.plot(xar, c101_yar)
line7, = ax.plot(xar, c102_yar)
line8, = ax.plot(xar, c103_yar)
fig.legend(['C1', 'C2', 'C3', 'C4','P13','P14','P23','P24'], loc='upper right')
fig.suptitle('Counts (TTL) vs Current Time')
ax.set_xlabel('Time')
ax.set_ylabel('Counts')
ani = animation.FuncAnimation(fig, animate, interval=100, blit=False)

# buttons
ttk.Button(mainframe, text="Start", command=start_f).grid(
    column=1, row=1, sticky=W)
ttk.Button(mainframe, text="Stop", command=stop_f).grid(
    column=2, row=1, sticky=W)
ttk.Button(mainframe, text="Set Gate Time", command=change_counter_f).grid(
    column=3, row=1, sticky=W)
ttk.Button(mainframe, text="Init Device", command=InitDevice).grid(
    column=4, row=7, sticky=W)

# controls
time_entry = Spinbox(mainframe, width=7, from_=0.1, to=5,
                     increment=.1, textvariable=timer_00)
time_entry.grid(column=5, row=6, sticky=(W, E))
timer_00.set(400)
print(timer_00.get())

# title
ttk.Label(mainframe, text='Counting Rate',
          font=("Helvetica", 28)).grid(column=4, row=1, sticky=(W, E))


# labels
ttk.Label(mainframe, text='Channel 1',
          font=("Helvetica", 28)).grid(column=1, row=2, sticky=(W, E))
ttk.Label(mainframe, text='Channel 2',
          font=("Helvetica", 28)).grid(column=1, row=3, sticky=(W, E))
ttk.Label(mainframe, text='Channel 3',
          font=("Helvetica", 28)).grid(column=1, row=4, sticky=(W, E))
ttk.Label(mainframe, text='Channel 4',
          font=("Helvetica", 28)).grid(column=1, row=5, sticky=(W, E))
ttk.Label(mainframe, text='Pair C1-C3',
          font=("Helvetica", 28)).grid(column=3, row=2, sticky=(W, E))
ttk.Label(mainframe, text='Pair C1-C4',
          font=("Helvetica", 28)).grid(column=3, row=3, sticky=(W, E))
ttk.Label(mainframe, text='Pair C2-C3',
          font=("Helvetica", 28)).grid(column=3, row=4, sticky=(W, E))
ttk.Label(mainframe, text='Pair C2-C4',
          font=("Helvetica", 28)).grid(column=3, row=5, sticky=(W, E))
ttk.Label(mainframe, text='Gate Time / ms',
          font=("Helvetica", 12)).grid(column=4, row=6, sticky=(E))
ttk.Label(mainframe, text='Select Device',
          font=("Helvetica", 12)).grid(column=1, row=7, sticky=(W))



# outputs
ttk.Label(mainframe, textvariable=counter_00, width=7, anchor=E,
          font=("Helvetica", ft_size)).grid(column=2, row=2, sticky=(W, E))
ttk.Label(mainframe, textvariable=counter_01, width=7, anchor=E,
          font=("Helvetica", ft_size)).grid(column=2, row=3, sticky=(W, E))
ttk.Label(mainframe, textvariable=counter_02, width=7, anchor=E,
          font=("Helvetica", ft_size)).grid(column=2, row=4, sticky=(W, E))
ttk.Label(mainframe, textvariable=counter_03, anchor=E,
          font=("Helvetica", ft_size)).grid(column=2, row=5, sticky=(W, E))

ttk.Label(mainframe, textvariable=counter_100, width=7, anchor=E,
          font=("Helvetica", ft_size)).grid(column=4, row=2, sticky=(W, E))
ttk.Label(mainframe, textvariable=counter_101, width=7, anchor=E,
          font=("Helvetica", ft_size)).grid(column=4, row=3, sticky=(W, E))
ttk.Label(mainframe, textvariable=counter_102, width=7, anchor=E,
          font=("Helvetica", ft_size)).grid(column=4, row=4, sticky=(W, E))
ttk.Label(mainframe, textvariable=counter_103, anchor=E,
          font=("Helvetica", ft_size)).grid(column=4, row=5, sticky=(W, E))


# padding the space surrounding all the widgets
for child in mainframe.winfo_children():
    child.grid_configure(padx=10, pady=10)

root.protocol("WM_DELETE_WINDOW",on_closing)

# finally we run it!
root.mainloop()

