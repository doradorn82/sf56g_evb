import os
import sys
from time import time
evb_path = os.path.abspath('../SF56G_EVB')
os.environ['SF56G_EVB_PATH'] = evb_path
sys.path.insert(0,evb_path)
from LibSF56G import SF56G

chip = SF56G()
chip.SetConfig('lane_en',0x1)
chip.SetConfig('b_dbg_print',False)
chip.build()

# sequence
chip.init_evb()
chip.set_datarate(53.125)
chip.act_chan_TX('PRBS13',channel=0)
chip.act_chan_RX('PRBS13',channel=0)
chip.tune_rx(channel=0)
chip.display_rx_eq(channel=0)
ber= chip.get_status('BER')
print("ber = %6.2e" % (ber))
