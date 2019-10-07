import os
import sys
from time import time
evb_path = os.path.abspath('../SF56G_EVB')
os.environ['SF56G_EVB_PATH'] = evb_path
sys.path.insert(0,evb_path)
from LibSF56G import SF56G

chip = SF56G()
chip.SetConfig('ext_clk',1)
chip.SetConfig('lane_en',1)
chip.build()

# sequence
if 0:
    chip.test_apb() 
if 1:
    if(chip.init_evb() < 0):
        print("apb failed")
        exit
    chip.set_datarate(53.125)
    #chip.act_chan_TX('PRBS31', channel=0)
    chip.act_chan_TX('REMOTE', channel=0)
    chip.act_chan_RX('PRBS31',channel=0)
    chip.set_tx_pre_post(tx_pre1=-0.05,tx_post1=-0.15,attenuation=1)
    
    chip.tune_init()
    
    #chip.tune_rx()
    chip.mCs.GetHistogram()
    chip.display_rx_eq(channel=0)
    chip.mPmad.PrintLaneState()
    #chip.GetHistogram()
    ber= chip.get_status(measure_bits_db=36,HeightOnly=1,extra_ber_en=1,imp_eq_out=0)
    print("ber=%6.2e" % (ber['ber']))
    #print(ber)
