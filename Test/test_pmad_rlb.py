import os
import sys
from time import time
evb_path = os.path.abspath('../SF56G_EVB')
os.environ['SF56G_EVB_PATH'] = evb_path
sys.path.insert(0,evb_path)
from LibSF56G import SF56G


def functime_dec(func):
    def decorator(*args,**kargs):
        print ("[%s] start" % (func.__name__))
        start = time()
        result = func(*args,**kargs)
        print ("[%s] done (time=%3.2fs)" % (func.__name__,(time()-start)))
        return result
    return decorator

#----------------------------------------------------------------------------------------------------
# test definition
#----------------------------------------------------------------------------------------------------
@functime_dec
def test_53g(chip):
    chip.init_evb()
    chip.set_datarate(53.125)
    chip.act_chan_TX()
    chip.act_chan_RX()
    print (chip.get_status('BER'))
    chip.mPmad.PrintAllRxCoef()
@functime_dec
def test_25g(chip):    
    chip.init_evb()
    chip.set_datarate(25.78125)
    chip.act_chan_TX()
    chip.act_chan_RX()
    print (chip.get_status('BER'))
    chip.mPmad.PrintAllRxCoef()
@functime_dec
def test_10g(chip):
    chip.init_evb()
    chip.set_datarate(10.3125)
    chip.act_chan_TX()
    chip.act_chan_RX()
    print (chip.get_status('BER'))
    chip.mPmad.PrintAllRxCoef()
@functime_dec
def test_me(chip):
    chip.init_evb()
    chip.set_datarate(53.125)
    chip.act_chan_TX('PRBS13')
    chip.act_chan_RX('PRBS13')
    print("BER= ", chip.get_status('BER'))
    chip.mPmad.PrintAllAdcMinMax(mon_sel=0)
    chip.mPmad.PrintAllRxCoef()
    chip.mPmad.TuneChip()
    chip.act_chan_TX('PRBS13')
    chip.act_chan_RX('PRBS13')
    ber=chip.get_status('BER')
    print("BER= ", ber)
    chip.mPmad.GetBerToTxt(ber)
    chip.mPmad.PrintAllAdcMinMax(mon_sel=0)
    chip.mPmad.PrintAllRxCoef()

@functime_dec
def test_ber(chip):
    test_25g(chip)
    chip.mCs.GetBerEom()  
#----------------------------------------------------------------------------------------------------
# test execution
#----------------------------------------------------------------------------------------------------

# test item
channel_list   = range(1)
data_rate_list = [10.3125,25.78125,53.125]
data_patt_list = ['PRBS7','PRBS13','PRBS31']
repeat         = 1

# build
chip = SF56G()
chip.SetConfig('max_channel',4)
chip.SetConfig('media_mode','RLB')
chip.SetConfig('phaseStep',1)

chip.build()

# alias
r = chip.mApb.read
w = chip.mApb.write
p = chip.mPmad

# test
test_me(chip)
test_me(chip)
