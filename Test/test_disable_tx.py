import os
import sys
from time import time
evb_path = os.path.abspath('../SF56G_EVB')
os.environ['SF56G_EVB_PATH'] = evb_path
sys.path.insert(0,evb_path)
from LibSF56G import SF56G

def cb_pmad_pre(self):
    self.SetRxEqReleaseAll()

chip = SF56G()
chip.SetConfig('cb_pmad_pre',cb_pmad_pre)
chip.SetConfig('media_mode','ELB')
chip.build()

#alias
r=chip.mApb.read
w=chip.mApb.write

# init
for rate in [10.3125,25.78125,53.125]:
    for coef in range(-70,0,5): 
        chip.init_evb()
        chip.set_datarate(rate)
        chip.set_rx_ffe(-1,coef)
        chip.act_chan_TX('PRBS13')
        chip.act_chan_RX('PRBS13')
        #chip.mPmad.PrintAllAdcMinMax()
        #chip.display_rx_eq()
        init_ber= chip.get_status('BER')
        #print("initial ber = %6.2e" % (ber))
    # disable
        chip.dis_chan_TX()
        #chip.mPmad.PrintAllAdcMinMax()
        #chip.display_rx_eq()
        #ber= chip.get_status('BER')
        #print("ber = %6.2e" % (ber))
    # enable
        chip.ena_chan_TX()
        #chip.mPmad.PrintAllAdcMinMax()
        #chip.display_rx_eq()
        react_ber= chip.get_status('BER')
        print("rate=%f coef=%d, init=%6.2e, react=%6.2e"%(rate,coef,init_ber,react_ber))
        
