import os
import sys
import time
from time import time
evb_path = os.path.abspath('../SF56G_EVB')
os.environ['SF56G_EVB_PATH'] = evb_path
sys.path.insert(0,evb_path)
from LibSF56G import SF56G
import numpy as np

chip = SF56G()
chip.SetConfig('lane_en',0x9)
# chip.SetConfig('media_mode','SLB')
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
    chip.set_tx_pre_post(tx_pre1=-0.25,tx_post1=-0,attenuation=1)
    # chip.set_tx_pre_post(tx_pre1=-0,tx_post1=-0,attenuation=1)

    chip.tune_init()
    # print("origital vsel status = %d" % ((chip.mApb.read(0x60034, 0) >> 6) & 0x7))
    # chip.mApb.write(0x60034,5<<6,0,0x7<<6)
    # chip.mPmad.mCfg.dump_abs_path=chip.mPmad.mCfg.dump_abs_path.strip(str(i-1))+str(i)

    #
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

    #
    # ber= chip.meas_ber(40)
    # ber= chip.meas_ber()
    # print(" BER_status = %.3g"%ber)

    status = chip.get_status(lin_fit_en=0, vertical_analysis_en=0, horizontal_analysis_en=1)
    # chip.plot_histo_eom()
    # print("vsel status = %d" % ((chip.mApb.read(0x60034, 0) >> 6) & 0x7))


    # chip.mCs.GetAllChHistogram()


    VerticalBerList=np.array(status['extra_ber_vertical'])
    pam4=(chip.mCfg.data_rate>50)
    if (pam4==1):
        histBer=VerticalBerList[:,:2].sum()/2
        # histBer=VerticalBerList[0,2]+VerticalBerList[2,2]+VerticalBerList[1,2]
        #histBer=VerticalBerList[0,2]+VerticalBerList[2,2]+np.average(VerticalBerList[1,:2])
    else:
        histBer=VerticalBerList[1,:2].sum()/2
        # histBer=VerticalBerList[1,2]
        # histBer=np.average(VerticalBerList[1,:2])
    print('Bathtub cross BER = %.3g' % histBer)
