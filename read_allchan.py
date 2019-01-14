

from Tkinter import *

import ttk

#from Tkinter import font
#fnt = font.nametofont("TkFixedFont").actual()

master = Tk()
#default_font = tkFont.nametofont("Courier New")
#default_font.configure(size=12)
#master.option_add("*Font", fnt)

fixed = ttk.Style()
#fixed.configure('Fixed.TButton', font='TkFixedFont')
fixed.configure("Courier.TButton", font=("Courier", 16))
#fixed.theme_use('default')
master.style=fixed

DEVICE    = '/dev/comedi0'
SUBDEVICE = 0
CHANNELS = [ c+1 for c in range(16) ]



N_FORCES = 6

dumpf = open('dump.txt','w')



import numpy as np
sens_to_f = np.genfromtxt('sensor_transf_matrix_FT4714.csv',delimiter=',')
# read the matrix that transforms sensor data into force data.
# note: the columns here are the sensor dimensions, the rows are the force dimensions.




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
        label.configure(font=('Courier',16))
        
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

        v = "%.3f"%vol
        if v[0]!='-': v="+"+v
        if v=='+nan': v=' nan  '
        
        self.tv.set(v)
    
  



pbs = []
fram = Frame(master)
fram.pack(side='top',anchor=W)
for chan_i,ch in enumerate(CHANNELS):

    tv = StringVar()
    tv.set("CHANNEL %d"%ch)
    label = Label( fram, textvariable=tv, relief=RAISED )
    label.grid(row=chan_i+1,column=0)
    
    thischan = []
    for range_i,ran in enumerate(range(n_ranges)):

        meter = Meter(fram)
        meter.grid(row=chan_i+1,column=range_i+1)

        thischan.append(meter)
    pbs.append(thischan)



 

for range_i,ran in enumerate(ranges):
    
    tv = StringVar()
    tv.set("[%.3f,%.3f]"%(ran.min,ran.max))
    label = Label( fram, textvariable=tv, relief=RAISED )
    label.grid(row=0,column=range_i+1)




force_labels = []
for f in range(N_FORCES):

    fsth = StringVar()
    fsth.set("SOMETHING")
    label = Label( fram, textvariable=fsth, relief=RAISED )
    label.grid(row=len(CHANNELS)+f+3,column=1,sticky=W)
    label.configure(font=('Courier',20))
    #label.pack(side='bottom',anchor=W)
    force_labels.append(fsth)


    


      
def capture_all():
    captured = [ [ None for _ in range(n_ranges) ] for _ in CHANNELS ]
    for chan_i,ch in enumerate(CHANNELS):
        for range_i,ran in enumerate(range(n_ranges)):
            ret,data = c.comedi_data_read(dev,
                                          SUBDEVICE,
                                          ch,
                                          ran,
                                          c.AREF_GROUND)
            phydata = c.comedi_to_phys(data, ranges[ran], maxdata)

            captured[chan_i][range_i] = (data,phydata)
    return captured



biases = [ [ (0,0) for _ in range(n_ranges) ] for _ in CHANNELS ]

def zero_bias():
    global biases
    biases = capture_all()
    print('zero bias!')
        
fram = Frame(master)
fram.pack(side='bottom')
b = Button(fram, text="Zero bias", command=zero_bias)
b.pack(side='top')





def compute_forces(channels,biases):

    channels = np.array(channels)
    biases   = np.array(biases)

    # Subtract the bias
    ref = channels-biases

    # Multiply with the sensor matrix
    forces = sens_to_f.dot(ref[:6])
    #print(forces)
    return forces
    
    



SELECTED_RANGE = 0 # in the list of ranges (e.g. 1 corresponds to [-5V,+5V]
    

def formulate_f(f):
    s= "%.3f"%f
    if not f<0: s="+"+s
    return s
    

    
# Code to add widgets will go here...
while True:
    master.update()
    master.update_idletasks()


    captured = capture_all()

    for chan_i,ch in enumerate(CHANNELS):
        for range_i,ran in enumerate(range(n_ranges)):

            #print(phydata)
            data,phydata = captured[chan_i][range_i]

            _,zero_phydata = biases[chan_i][range_i]
            
            pbs[chan_i][range_i].set_value(data,phydata-zero_phydata) #['value'] = data
            #print("[%.3f,%.3f] Raw %d  --> voltage %f" %(ranges[rn].min,ranges[rn].max,data,phydata))
    


    channels = [ captured[ch][SELECTED_RANGE][1] for ch,_ in enumerate(CHANNELS) ]
    bias     = [ biases[ch][SELECTED_RANGE][1]   for ch,_ in enumerate(CHANNELS) ]

    forces = compute_forces(channels,bias)
    for i,force in enumerate(forces):
        #f = str([ '%.2f'%fn for fn in forces])
        
        force_labels[i].set('f%d -- %s N'%(i,formulate_f(force)))
        #allf.set(f)

    dumpf.write(" ".join([ str(x) for x in channels])+"\n")

    

dumpf.close()
            
ret = c.comedi_close(dev)
if ret<0:
	raise Exception("ERROR executing comedi_close")


