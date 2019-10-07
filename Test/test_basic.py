import os
import sys
from time import time
evb_path = os.path.abspath('../SF56G_EVB')
os.environ['SF56G_EVB_PATH'] = evb_path
sys.path.insert(0,evb_path)
from LibSF56G import SF56G

chip = SF56G()
chip.SetConfig('lane_en',0x9)
chip.build()

# sequence
if 0:
    chip.test_apb() 
if 1:
    chip.init_evb()
    chip.set_datarate(53.125)
    #chip.set_datarate(25.78125)
    chip.act_chan_TX('PRBS31',channel=0)
    chip.act_chan_RX('PRBS31',channel=0)
    chip.set_tx_pre_post(tx_pre1=-0.15,tx_post1=-0,attenuation=1)
    
    chip.tune_init()
    #chip.tune_rx()
    #chip.mCs.GetHistogram()
    chip.display_rx_eq(channel=0)
    #chip.GetHistogram()
    ber= chip.get_status(measure_bits_db=34,HeightOnly=1,extra_ber_en=1,imp_eq_out=0)
    print(ber['ber'])
    print(ber['extra_ber'])
    #print(ber)
