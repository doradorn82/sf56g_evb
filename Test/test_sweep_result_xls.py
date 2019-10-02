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
data_rate_list = [10.3125,25.78125,53.125]
data_patt_list = ['PRBS7','PRBS13','PRBS31']
repeat         = 5

# build
chip = SF56G()
chip.SetConfig('max_channel',1)
chip.SetConfig('media_mode','SLB')
chip.build()

# etc
r = chip.mApb.read
w = chip.mApb.write

# sequence
f = save_to_xlsx('../dump/test_result.xlsx')
f.add_sheet('sim_01')
f.write_head(['channel','repeat','rate','patt','ber','time'])
for ch in channel_list:
    for rate in data_rate_list:
        for patt in data_patt_list:
            for i in range(repeat):
                each_start = time()
                chip.init_evb()
                chip.set_datarate(rate)
                chip.act_chan_TX(patt)
                chip.act_chan_RX(patt)
                ber = chip.get_status('BER')
                each_end = time()
                print("ch[%d-%d] rate[%10.4f] patt[%10s] > BER=%10.2e (%3.2fs)" % (ch,i,rate,patt,ber,(each_end-each_start)))
                f.write_data([ch,i,rate,patt,ber,(each_end-each_start)])
f.close()

