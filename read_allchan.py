

from Tkinter import *

import ttk

master = Tk()

DEVICE    = '/dev/comedi0'
SUBDEVICE = 0
CHANNELS = [ c+1 for c in range(16) ]




import comedi as c

#open a comedi device
dev=c.comedi_open(DEVICE)
if not dev: raise Exception("Error opening Comedi device")


# get maxdata & range
#  - these values are used to convert integer to physical values

i = SUBDEVICE


maxdata = c.comedi_get_maxdata(dev,SUBDEVICE,0)
#print("\tmax data value: %d" % (maxdata))



ranges = []
#n_ranges = c.comedi_get_n_ranges(dev,i,0)
#print("\t\tall chans:")
n_ranges = c.comedi_get_n_ranges(dev,SUBDEVICE,0) # get how many range options we have
for j in range(n_ranges):
    rng = c.comedi_get_range(dev,SUBDEVICE,0,j)
    ranges.append(rng)
print([ (rng.min,rng.max) for rng in ranges])
    




class Meter(Frame):

    def __init__(self, master=None, maximum=100, **kw):
        Frame.__init__(self, master, **kw)
        self.maximum = maximum

        tv = StringVar()
        tv.set("something")
        label = Label( self, textvariable=tv, relief=RAISED )
        label.pack(side='left')
        
        pb = ttk.Progressbar(self,
                             orient="horizontal",
                             length=200,
                             maximum=maxdata,
                             mode="determinate")

        pb.pack(side='right') #.grid(row=0,column=0)
        self.pb = pb
        self.tv = tv
        
    def set_value(self,val,vol):
        self.pb['value']=val
        self.tv.set("%.3f"%vol)
    
        




pbs = []
for chan_i,ch in enumerate(CHANNELS):

    tv = StringVar()
    tv.set("CHANNEL %d"%ch)
    label = Label( master, textvariable=tv, relief=RAISED )
    label.grid(row=chan_i+1,column=0)
    
    thischan = []
    for range_i,ran in enumerate(range(n_ranges)):

        meter = Meter(master)
        meter.grid(row=chan_i+1,column=range_i+1)

        thischan.append(meter)
    pbs.append(thischan)



for range_i,ran in enumerate(ranges):
    
    tv = StringVar()
    tv.set("[%.3f,%.3f]"%(ran.min,ran.max))
    label = Label( master, textvariable=tv, relief=RAISED )
    label.grid(row=0,column=range_i+1)
    

# Code to add widgets will go here...
while True:
    master.update()
    master.update_idletasks()


    for chan_i,ch in enumerate(CHANNELS):
        for range_i,ran in enumerate(range(n_ranges)):
            ret,data = c.comedi_data_read(dev,
                                          SUBDEVICE,
                                          ch,
                                          ran,
                                          c.AREF_GROUND)
            phydata = c.comedi_to_phys(data, ranges[ran], maxdata)

            #print(phydata)
            pbs[chan_i][range_i].set_value(data,phydata) #['value'] = data
            #print("[%.3f,%.3f] Raw %d  --> voltage %f" %(ranges[rn].min,ranges[rn].max,data,phydata))
    


ret = c.comedi_close(dev)
if ret<0:
	raise Exception("ERROR executing comedi_close")


