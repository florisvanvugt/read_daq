
# Here we try the heroic task of reading just a single value!!



# Keep an eye on https://www.phas.ubc.ca/~halpern/309/programs/PC1710.py
# still also keep this: https://github.com/jhu-saw/sawJR3ForceSensor/wiki/Comedi-Notes

DEVICE    = '/dev/comedi0'
SUBDEVICE = 0
CHANNEL   = 0

import comedi as c

#open a comedi device
dev=c.comedi_open(DEVICE)
if not dev: raise Exception("Error opening Comedi device")


# get maxdata & range
#  - these values are used to convert integer to physical values

i = SUBDEVICE


maxdata = c.comedi_get_maxdata(dev,SUBDEVICE,0)
print("\tmax data value: %d" % (maxdata))



ranges = []
#n_ranges = c.comedi_get_n_ranges(dev,i,0)
print("\t\tall chans:")
n_ranges = c.comedi_get_n_ranges(dev,SUBDEVICE,0) # get how many range options we have
for j in range(n_ranges):
    rng = c.comedi_get_range(dev,SUBDEVICE,0,j)
    ranges.append(rng)
print([ (rng.min,rng.max) for rng in ranges])
    

# raw data
for CHANNEL in range(16):
    print("CHANNEL %d"%CHANNEL)
    for rn in range(n_ranges):
        ret,data = c.comedi_data_read(dev,
                                      SUBDEVICE,
                                      CHANNEL,
                                      rn,
                                      c.AREF_GROUND)
        phydata = c.comedi_to_phys(data, ranges[rn], maxdata)

        print("[%.3f,%.3f] Raw %d  --> voltage %f" %(ranges[rn].min,ranges[rn].max,data,phydata))


# convert to physical data
#  phydata = data * (max - min)/maxdata + min
phydata = c.comedi_to_phys(data, rng, maxdata)


print(phydata)
    
ret = c.comedi_close(dev)
if ret<0:
	raise Exception("ERROR executing comedi_close")


