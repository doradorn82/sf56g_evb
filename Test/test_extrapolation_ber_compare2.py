import os
import sys
import matplotlib.pyplot as plt
import time
from time import time
evb_path = os.path.abspath('../SF56G_EVB')
os.environ['SF56G_EVB_PATH'] = evb_path
sys.path.insert(0,evb_path)
from LibSF56G import SF56G
import numpy as np

chip = SF56G()
chip.SetConfig('lane_en',0x9)
chip.SetConfig('media_mode','ELB')
chip.build()
# sequence

if 0:
    chip.test_apb()
for i in range(1):
    chip.init_evb()
    # chip.set_datarate(56.25)
    # chip.set_datarate(53.125)
    chip.set_datarate(25.78125)
    # chip.set_datarate(10.3125)
    chip.act_chan_TX('PRBS31',channel=0)
    chip.act_chan_RX('PRBS31',channel=0)
    # chip.set_tx_pre_post(tx_pre1=-0.25,tx_post1=-0,attenuation=1)
    chip.set_tx_pre_post(tx_pre1=-0,tx_post1=-0,attenuation=1)
    chip.tune_init()
    # chip.mApb.write(0x60034,4<<6,0,0x7<<6)

    # chip.mApb.write(0x60028, 0x12 , 0, 0x1F )# vga2 forcing
    # chip.mApb.write(0x6002C, 0x38 , 0, 0x3F )# vga1 forcing

    # chip.mPmad.mApb.write(0x00060100, 0 << 5, 0, 1 << 5)
    # chip.mPmad.SetRxEqForce(-2,0,0)
    # chip.mPmad.SetRxEqForce(-1,0,0)
    # chip.mPmad.SetRxEqForce(2,0,0)
    # chip.mPmad.SetRxEqForce(3,0,0)
    # chip.mPmad.SetRxEqForce(4,0,0)
    # chip.mPmad.SetRxEqForce(5,0,0)
    # chip.mPmad.SetRxEqForce(6,0,0)
    # chip.mPmad.SetRxEqForce(7,0,0)
    # chip.mPmad.SetRxEqForce(8,0,0)
    # chip.mApb.write(0x61FF8, 0x4,0)
    channel=0
    histdata = np.zeros(128)
    chip.mApb.write(0x00060100, 1 << 6, channel, 1 << 6) # change monitoring point from EOM path to Data path
    chip.mApb.write(0x00060100, 0, channel, 0x1F)
    chip.mApb.write(0x00061000, 0x3 << 3, channel=channel, mask=0xf << 3)
    chip.mApb.write(0x00060100, 0 << 7, channel, 1 << 7)
    chip.mApb.write(0x00060100, 1 << 7, channel, 1 << 7)
    while (1):
        eom_done = (chip.mApb.read(0x62248, 0) & 1)
        if (eom_done == 1):
            break
    for mem_i in range(128):
        memAdd = 0x00063010 + mem_i * 4
        histdata[mem_i] = chip.mApb.read(memAdd, 0)

    histeom = np.zeros(128)
    chip.mApb.write(0x00060100, 0 << 6, channel, 1 << 6) # change monitoring point to EOM path
    chip.mApb.write(0x00060100, 0 << 7, channel, 1 << 7)
    chip.mApb.write(0x00060100, 1 << 7, channel, 1 << 7)
    while (1):
        eom_done = (chip.mApb.read(0x62248, 0) & 1)
        if (eom_done == 1):
            break
    for mem_i in range(128):
        memAdd = 0x00063010 + mem_i * 4
        histeom[mem_i] = chip.mApb.read(memAdd, 0)

    print("histdata :",histdata)
    print("histeom :",histeom)



    plt.plot(np.arange(-64, 64), histdata)
    plt.plot(np.arange(-64, 64), histeom)
    plt.grid(True)
    plt.savefig(chip.mCfg.dump_abs_path + "histo_compare_data_eom.png", dpi=200)
    plt.close()
