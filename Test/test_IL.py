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
chip.build()

# sequence
chip.init_evb()
chip.set_datarate(53.125)
#chip.set_datarate(25.78125)
#chip.set_datarate(10.3125)
chip.act_chan_TX('PRBS13',channel=0)
chip.act_chan_RX('PRBS13',channel=0)
chip.mPmad.SetTxEqDecrease(0,3,0)
chip.tune_init(channel=0)
#chip.mPmad.PrintLaneState()
chip.display_rx_eq(channel=0)
ber= chip.meas_ber()
print("BER = %6.2g" % (ber))
ber= chip.meas_ber()
#chip.lin_fit_pulse()
print("BER = %6.2g" % (ber))
#chip.plot_256_samples()
chip.GetHistogram()
#if(ber==0):
#    estiBer=chip.get_extra_ber(2,0)
#    print('Estimated BER = %.2g'%estiBer)
#chip.mPmad.DumpRegFile(tag='before')
#chip.off_chan_RX(channel=0)
#chip.tune_init(channel=0)
#chip.act_chan_RX('PRBS13',channel=0)
#for i in range(    20):
#    chip.tune_rx(channel=0)
#    ber= chip.get_status('BER')
#    print("ber = %6.2g" % (ber))
#chip.display_rx_eq(channel=0)
#chip.mPmad.DumpRegFile(tag='after')
    
