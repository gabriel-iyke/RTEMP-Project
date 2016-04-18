#!/usr/bin/env python
# Plot a graph distance vs time in real time using SPI and IR Sensor 
# Gabriel Soares

import pylab
import spidev
import time
from pylab import *
import matplotlib.pyplot as plt
from matplotlib.widgets import Cursor

spi = spidev.SpiDev()
spi.open(0, 0)


xAxisSet=pylab.arange(0,100,1)
yAxisSet=pylab.array([0]*100)

fig = pylab.figure(1)
ax = fig.add_subplot(111)
ax.grid(True)
ax.set_title("Realtime Plot")
ax.set_xlabel("Time ")
ax.set_ylabel("Distance [cm]")
ax.axis([0,100,0,150])
line=ax.plot(xAxisSet,yAxisSet,'-')

#widget to create a cursor in the screen in the horizontal position
cursor = Cursor(ax, horizOn=True, vertOn= False , useblit=True, color='r', linewidth=2)

manager = pylab.get_current_fig_manager()

#buffer to storage the data from the sensor to be plot 
buf=[]
buf = [0 for x in range(200)]

def movingAverage(x, k): # x is the numpy array. N is the window width
    acumulative = np.cumsum(np.insert(x, 0, 0))
    return (acumulative[k:] - acumulative[:-k]) / k

def readMCP3008(adcnum):
# read SPI data from MCP3008 chip, 8 possible adc's (0 thru 7)
    if adcnum > 7 or adcnum < 0:
        return -1
    r = spi.xfer2([1, 8 + adcnum << 4, 0])
    adcout = ((r[1] & 3) << 8) + r[2]
    #print"SPI data:",adcout
    time.sleep(0.02)
    return adcout

#function to convert the data from the adc to volts using round function to make some aproximation
def convertVolts(data,places):
  volts = (data * 3.3) / float(1023)
  volts = round(volts,places)
  return volts

# calculates the distance using a aproximation of the curve of the IR SHARP sensor (volts vs distance)
def distance(data):
  d=(16.2537 * data**4 - 129.893 * data**3 + 382.268 * data**2 - 512.611 * data + 306.439)/2 
  return d

def getData(arg):
  count=0
  global buf
  samples=1
  avg=np.zeros(1)
  aux=np.zeros(samples)

  #loop to create a average of n samples instead of crude data
  
  while (count <samples):
      aux[count]=distance(convertVolts(readMCP3008(0),2))
      #print"distance:", aux[count]
      time.sleep(0.04)
      count=count+1
  
  avg=movingAverage(aux, samples)
  buf.append(avg)
      
def plotData(arg):
  global buf
  CurrentXAxis=pylab.arange(len(buf)-100,len(buf),1)

  #print "buf",buf[-100:]
  line[0].set_data(CurrentXAxis,pylab.array(buf[-100:]))
  ax.axis([CurrentXAxis.min(),CurrentXAxis.max(),10,70])
  manager.canvas.draw()
 
#timers to sync the plot and the data acquisition by SPI  
timer = fig.canvas.new_timer(interval=10)
timer.add_callback(plotData, ())

timerData = fig.canvas.new_timer(interval=10)
timerData.add_callback(getData, ())

timer.start()
timerData.start()

pylab.show()
