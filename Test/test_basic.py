import os
import sys
from time import time
evb_path = os.path.abspath('../SF56G_EVB')
os.environ['SF56G_EVB_PATH'] = evb_path
sys.path.insert(0,evb_path)
from LibSF56G import SF56G

chip = SF56G()
chip.SetConfig('lane_en',0x1)
chip.build()

# sequence
chip.init_evb(True)
chip.set_datarate(53.125)
chip.act_chan_TX('PRBS13',channel=0)
chip.act_chan_RX('PRBS13',channel=0)
chip.set_tx_pre_post(0,-0.15,0)
chip.tune_init()
chip.tune_rx()
for key,data in chip.get_status(HeightOnly=1).items():
    print("["+key+"] =>",data)
