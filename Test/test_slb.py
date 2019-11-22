import os
import sys
from time import time
evb_path = os.path.abspath('../SF56G_EVB')
os.environ['SF56G_EVB_PATH'] = evb_path
sys.path.insert(0,evb_path)
from LibSF56G import SF56G

chip = SF56G()
chip.SetConfig('media_mode','SLB')
chip.SetConfig('lane_en',0x1)
chip.build()

#alias
r = chip.mApb.read
w = chip.mApb.write

# sequence
chip.init_evb()
chip.set_datarate(53.125)
chip.act_chan_TX('PRBS13',channel=0)
chip.act_chan_RX('PRBS13',channel=0)
chip.set_tx_pre_post(tx_pre1=-0.15, tx_post1=-0, attenuation=1)
chip.tune_init()
chip.display_rx_eq(channel=0)
chip.mPmad.get_extra_ber_vertical(1,0)
ber= chip.meas_ber()
print("ber = %6.2e" % (ber))
