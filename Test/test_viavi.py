import os
import sys
from time import time
evb_path = os.path.abspath('../SF56G_EVB')
os.environ['SF56G_EVB_PATH'] = evb_path
sys.path.insert(0,evb_path)
from LibSF56G import SF56G

# user
tx_channels = [0,1,2,3]
rx_channels = [0,1,2,3]

chip = SF56G()
chip.SetConfig('ext_clk',0)
#chip.SetConfig('b_dbg_print',True)
chip.build()

# sequence
if 0:
    chip.test_apb() 
if 1:
    if(chip.init_evb(tx_channels) >= 0):
        print("apb passed")
        chip.set_datarate(53.125)
    #chip.act_chan_TX('PRBS31', channel=0)
        for ch in tx_channels:
            chip.act_chan_TX('REMOTE', channel=ch)
        for ch in rx_channels:
            chip.act_chan_RX('REMOTE',channel=ch)
        for ch in tx_channels:
            chip.set_tx_pre_post(tx_pre1=-0.05,tx_post1=-0.15,attenuation=1,channel=ch)
        for ch in rx_channels:
            chip.tune_init(channel=ch)
        
        for ch in range(4):
            chip.mPmad.PrintLaneState(ch)
        for ch in range(4):
            chip.mPmad.PrintAllRxCoef(ch)
            chip.GetHistogram(ch)
    else:
        print("apb failed")
