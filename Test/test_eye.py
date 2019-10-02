import os
import sys
from time import time
evb_path = os.path.abspath('../SF56G_EVB')
os.environ['SF56G_EVB_PATH'] = evb_path
sys.path.insert(0,evb_path)
from LibSF56G import SF56G
#import evb_extra
import evb_plot
from evb_cs import *

chip = SF56G()
chip.SetConfig('lane_en',0x1)
chip.SetConfig('b_dbg_print',False)
chip.SetConfig('b_dbg_apb_read',False)
chip.SetConfig('histo_zero_thld',10)
chip.build()

# sequence
for i in range(1):
    #print("start")
    start = time()
    chip.init_evb()
    chip.set_datarate(53.125)
    chip.act_chan_TX('PRBS13',channel=0)
    chip.act_chan_RX('PRBS13',channel=0)
    chip.mPmad.SetTxEqDecrease(0,3,0)
    chip.tune_init(channel=0)
    #chip.display_rx_eq(channel=0)
    ber= chip.meas_ber()
    print("BER = %6.2g" % (ber))
    #chip.plot_histo_eom()
    #print(chip.meas_eye(0,0))
    print(chip.get_status())
    #print("time=%3.2fs" % (time()-start))
