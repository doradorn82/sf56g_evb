import os
import sys
from time import time
evb_path = os.path.abspath('../SF56G_EVB')
os.environ['SF56G_EVB_PATH'] = evb_path
sys.path.insert(0,evb_path)
from LibSF56G import SF56G

# user
tx_channels = [0]
rx_channels = [0]
data_patt   = 'PRBS31'

chip = SF56G()
chip.SetConfig('ext_clk',1)
#chip.SetConfig('b_dbg_print',True)
chip.build()
def post_setting(chip):
    chip.mApb.write(0x601cc,0x1ff)
    chip.act_chan_RX('PRBS31',channel=0)
    chip.mApb.write(0x60174, 0<<15, 0, 1<<15)
    ber = chip.mPmad.GetBer(measure_bits_db=32)
    print('ber=%.3g'%ber)

# sequence
if 0:
    chip.test_apb() 
if 1:
    if(chip.init_evb(tx_channels) >= 0):
        print("apb passed")
        chip.set_datarate(53.125)    
        for ch in tx_channels:
            chip.act_chan_TX('REMOTE',channel=ch)
            if data_patt == 'PRBS31':
                chip.mApb.write(0x50104, 0<<9, ch, 1<<9)
        for ch in rx_channels:
            chip.act_chan_RX('PRBS31',channel=ch)
            if data_patt == 'PRBS31':
                chip.mApb.write(0x60174, 0<<15, ch, 1<<15)
        for ch in tx_channels:
            chip.set_tx_pre_post(tx_pre1=-0.05,tx_post1=-0.15,attenuation=1,channel=ch)
        for ch in rx_channels:
            chip.tune_init(channel=ch)
            #chip.tune_rx(channel=ch)
        
        for ch in range(1):
            chip.mPmad.PrintLaneState(ch)
        for ch in range(1):
            chip.mPmad.PrintAllRxCoef(ch)
            chip.GetHistogram(ch)
        while True:
            ber = chip.mPmad.GetBer(measure_bits_db=32)
            print('ber=%.3g'%ber)
    else:
        print("apb failed")


