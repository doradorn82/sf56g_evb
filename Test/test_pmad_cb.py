import os
import sys
from time import time
evb_path = os.path.abspath('../SF56G_EVB')
os.environ['SF56G_EVB_PATH'] = evb_path
sys.path.insert(0,evb_path)
from LibSF56G import SF56G

def cb_pmad_pre(self):
    print("cb start")
    print("ip version=%x" % self.mApb.read(0xffc))
    self.mApb.write(0xffc,0xdead)
    print("ip version=%x" % self.mApb.read(0xffc))
    print("cb end")

# test
rate = 25.78125
lane_strb = 1
max_channel = 1
repeat = 1

# build
chip = SF56G()
chip.SetConfig('media_mode','ELB')
chip.SetConfig('cb_pmad_pre',cb_pmad_pre)
chip.build()
# etc
r = chip.mApb.read
w = chip.mApb.write
# run
chip.init_evb()
if 1:
    chip.set_datarate(rate)
    chip.act_chan_TX('PRBS13')
    chip.act_chan_RX('PRBS13')
else:
    chip.mCs.WriteElbVector()
chip.mPmad.PrintAllADCMinMax()
chip.mPmad.PrintAllRxCoef()
chip.mPmad.PrintADCSkewCode()
print("BER=%e" % (chip.get_status("BER")))
#chip.mCs.GetBerEomPam4()
