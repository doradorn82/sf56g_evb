import os
import sys
from time import time
evb_path = os.path.abspath('../SF56G_EVB')
os.environ['SF56G_EVB_PATH'] = evb_path
sys.path.insert(0,evb_path)
from LibSF56G import SF56G
from excel import save_to_xlsx

# test item
channel_list   = range(1)
data_rate_list = [53.125]
data_patt_list = ['PRBS13']
repeat         = 10

# build
chip = SF56G()
chip.SetConfig('max_channel',1)
#chip.SetConfig('media_mode','SLB')
chip.SetConfig('b_dbg_print',False)
chip.build()

# etc
r = chip.mApb.read
w = chip.mApb.write

# sequence
xls = save_to_xlsx('../dump/test_getstatus.xlsx')
xls.add_sheet('sim_01')
xls.write_head(['channel','repeat','rate','patt',
    'tx_pre2','tx_pre1','tx_post1','attenuation',
    'rx_pre2','rx_pre1','rx_main','rx_post1','rx_post2','rx_post3','rx_post4','rx_post5','rx_post6','rx_post7','rx_post8',
    'rx_ctle','rx_vga1','rx_vga2','rx_adcgain','cboost',
    'ber','eye01_height','eye01_width','eye12_height','eye12_width','eye23_height','eye23_width','time'
    ])

for ch in channel_list:
    for rate in data_rate_list:
        for patt in data_patt_list:
            for i in range(repeat):
                each_start = time()
                chip.init_evb()
                chip.set_datarate(rate)
                chip.act_chan_TX(patt)
                chip.act_chan_RX(patt)
                chip.mPmad.SetTxEqDecrease(0,3,0,ch)
                chip.tune_init()
                
                status = chip.get_status(HeightOnly=1)
                each_end = time()
                xls.write_data([ch,i,rate,patt,
                    status['tx_pre2'],status['tx_pre1'],status['tx_post1'],status['attenuation'],
                    status['rx_pre2'],status['rx_pre1'],status['rx_main'],status['rx_post1'],status['rx_post2'],status['rx_post3'],status['rx_post4'],status['rx_post5'],status['rx_post6'],status['rx_post7'],status['rx_post8'],
                    status['rx_ctle'],status['rx_vga1'],status['rx_vga2'],status['rx_adcgain'],status['cboost'],
                    status['ber'],status['eye01_height'],status['eye01_width'],status['eye12_height'],status['eye12_width'],status['eye23_height'],status['eye23_width'],(each_end-each_start)])
xls.close()
