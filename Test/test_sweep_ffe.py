import os
import sys
from time import time
evb_path = os.path.abspath('../SF56G_EVB')
os.environ['SF56G_EVB_PATH'] = evb_path
sys.path.insert(0,evb_path)
from LibSF56G import SF56G

# test item
channel_list   = range(1)
data_rate_list = [53.125]
data_patt_list = ['PRBS7','PRBS13','PRBS31']
repeat         = 5
rate = 53.125
patt = 'PRBS13'
filename = '../dump/result_sweep_ffe.txt'

# build
chip = SF56G()
chip.SetConfig('lane_en',1)
chip.build()
f = open(filename,'w')

# etc
r = chip.mApb.read
w = chip.mApb.write

f.write("rate=%s, patt=%s, mode=%s\n" % (str(rate),patt,chip.mCfg.media_mode))
best_result = {}
for tap in [-2,-1,1,2,3]:
    best_coef = -90
    best_ber  = 1.0
    for coef in range(-90,95,5):
        chip.init_evb()
        chip.set_datarate(rate)
        chip.set_rx_ffe(tap,coef)
        chip.act_chan_TX(patt)
        chip.act_chan_RX(patt)
        ber = chip.get_status('BER')

        if ber < best_ber:
            best_ber  = ber
            best_coef = coef
        f.write("tap=%d, coef=%d, ber=%6.2e\n" % (tap,coef,ber))

    f.write("==================================================\n")
    f.write("tap=%d, best_coef=%d, best_ber=%6.2e\n" % (tap,best_coef,best_ber))
    best_result['tap'+str(tap)] = best_coef

f.write("==================================================\n")
for tap, coef in best_result.items():
    f.write("tap=%d, coef=%d\n" % (tap,coef))
f.close()
