import os
import sys
import time
from time import time
evb_path = os.path.abspath('../SF56G_EVB')
os.environ['SF56G_EVB_PATH'] = evb_path
sys.path.insert(0,evb_path)
from LibSF56G import SF56G
from evb_cs import EVB_CS
import numpy as np
import evb_plot

chip = SF56G()
chip.SetConfig('lane_en',0x1)
chip.SetConfig('data_rate',25.78125)
# chip.SetConfig('b_WA0',False)
chip.SetConfig('media_mode','ELB')
chip.build()

channel=0
# sequence
if 0:
    chip.test_apb()
for i in range(10):
    print("repeat : %d"%i)
    chip.init_evb()
    # chip.set_datarate(53.125)
    chip.mCs.WriteSineElbVector()
    chip.mPmad.SetTxOff(0)
    chip.mPmad.SetRxOff(b_keep_clk='TRUE', channel=0)
    chip.mPmad.SetTxOn(channel=0)
    chip.mPmad.SetRxOn(channel=0, b_tune='false')

    # chip.mApb.write(0x5000C, 0x2000)
    # dcd_data = 0x2000
    # for i in range(128):
    #     chip.mApb.write(0x5000C, dcd_data)
    #     print("%x", dcd_data & 0x7F)
    #     dcd_data += 1
    # chip.mApb.write(0x5000C, 0x207F)
    # chip.mApb.write(0x5000C, 0x2040)

    chip.plot_256_samples()

