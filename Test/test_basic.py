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
chip.SetConfig('lane_en',0x1)
chip.SetConfig('media_mode','ELB')
chip.build()

# sequence
if 0:
    chip.test_apb() 
for i in range(1):
    chip.init_evb()
    # chip.set_datarate(56.25)
    chip.set_datarate(53.125)
    # chip.set_datarate(25.78125)
    # chip.set_datarate(10.3125)
    chip.act_chan_TX('PRBS31',channel=0)
    chip.act_chan_RX('PRBS31',channel=0)
    chip.set_tx_pre_post(tx_pre1=-0.25,tx_post1=-0.0,attenuation=1)

    chip.tune_init()
    #chip.tune_rx()
    #chip.mCs.GetHistogram()
    chip.display_rx_eq(channel=0)
    chip.GetHistogram()
    # status = chip.get_status(lin_fit_en=1, vertical_analysis_en=1, horizontal_analysis_en=1)
    status = chip.get_status(lin_fit_en=1, vertical_analysis_en=0,horizontal_analysis_en=0)
    print(status)
    ber = status['ber']
    print("BER_status = %.3g"%ber)
    # ber = chip.meas_ber()
    # print("BER = %.3g"%ber)
    # ber = chip.meas_ber()
    # print("BER = %.3g"%ber)
    # ber = chip.meas_ber()
    # print("BER = %.3g"%ber)
    # for order in range(8,13):
    #     measure_bits_db = int(round(np.log2(10**order)+0.5))
    #     t_beg = time()
    #     ber= chip.meas_ber(measure_bits_db)
    #     t_end = time()
    #     print("order=%d, bits=%d, time(%4.2f), ber=%4.2e" % (order,measure_bits_db,(t_end-t_beg),ber))
    #print(ber)
