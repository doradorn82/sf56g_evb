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
def test_0(chip):
    chip.init_evb()
    chip.mCs.WriteSlbVector()
    print (chip.mCs.GetBer())
    chip.mPmad.PrintAllRxCoef()

@functime_dec
def test_1(chip):
    chip.init_evb()
    print (hex(r(0x24000024)))
    chip.mCs.phyExtClkEn()
    print (hex(r(0x24000024)))
    chip.mCs.phyExtClkEn_pcs()
    print (hex(r(0x24000024)))
    chip.mCs.phyXoClkEn()
    print (hex(r(0x24000024)))

@functime_dec
def test_2(chip):
    chip.init_evb()
    chip.mCs.WriteSlbVector()
    chip.mCs.SweepGetBer()

@functime_dec
def test_3(chip):
    chip.init_evb()
    chip.SetConfig('data_rate',10.3125)
    chip.mCs.WriteElbVector()
    print (chip.mCs.GetBer())
    chip.mPmad.PrintAllRxCoef()
    chip.mCs.GetBerEom()
    chip.mCs.GetBathtub()

@functime_dec
def test_4(chip):
    chip.init_evb()
    chip.mCs.WriteElbVector_pcs_lb()
    print (chip.mCs.GetBer())
    chip.mPmad.PrintAllRxCoef()

@functime_dec
def test_5(chip):
    chip.init_evb()
    chip.mCs.WriteSineElbVector()
    print (chip.mCs.GetBer())
    chip.mPmad.PrintAllRxCoef()

@functime_dec
def test_6(chip):
    chip.init_evb()
    chip.mCs.WriteRxEvalVector()
    print (chip.mCs.GetBer())
    chip.mPmad.PrintAllRxCoef()
    chip.mPmad.PrintLaneState()

@functime_dec
def test_7(chip):
    chip.init_evb()
    chip.SetConfig('data_rate',53.125)
    chip.mCs.WriteSlbVector()
    print (chip.mCs.GetBer())
    chip.mPmad.PrintAllRxCoef()
    chip.mCs.GetBerEomPam4()
 
@functime_dec
def test_8(chip):
    chip.init_evb()
    chip.SetConfig('data_rate',25.78125)
    chip.mCs.WriteSlbVector()
    print (chip.mCs.GetBer())
    chip.mPmad.PrintAllRxCoef()
    chip.mCs.GetBerEomPam4()

@functime_dec
def test_9(chip):
    chip.init_evb()
    chip.SetConfig('data_rate',25.78125)
    chip.mCs.WriteSlbVector()
    print (chip.mCs.GetBer())
    chip.mPmad.PrintAllRxCoef()
    chip.mCs.GetHistogram()
@functime_dec
def test_10(chip):
    chip.init_evb()
    chip.SetConfig('data_rate',25.78125)
    chip.mCs.WriteSlbVector()
    print (chip.mCs.GetBer())
    chip.mPmad.PrintAllRxCoef()
    chip.mCs.GetAllChHistogram()
@functime_dec
def test_11(chip):
    chip.init_evb()
    chip.SetConfig('data_rate',25.78125)
    chip.mCs.WriteSlbVector()
    print (chip.mCs.GetBer())
    chip.mPmad.PrintAllRxCoef()
    chip.mCs.GetHistoEom()
@functime_dec
def test_12(chip):
    chip.init_evb()
    chip.SetConfig('data_rate',25.78125)
    chip.mCs.WriteSlbVector()
    print (chip.mCs.GetBer())
    chip.mPmad.PrintAllRxCoef()
    chip.mCs.GetBathtub()
@functime_dec
def test_13(chip):
    chip.init_evb()
    chip.SetConfig('data_rate',25.78125)
    chip.mCs.WriteSlbVector()
    print (chip.mCs.GetBer())
    chip.mPmad.PrintAllRxCoef()
    chip.mCs.GetCaloutMin()
    chip.mCs.GetCaloutMax()
    chip.mCs.GetCalMaxMin()
    chip.mCs.GetAdcMin8()
    chip.mCs.GetAdcMax8()
    chip.mCs.GetAdcMin()
    chip.mCs.GetAdcMax()
@functime_dec
def test_14(chip):
    chip.init_evb()
    chip.SetConfig('data_rate',25.78125)
    chip.mCs.WriteSlbVector()
@functime_dec
def test_me(chip):
    chip.init_evb()
    chip.set_datarate(53.125)
    chip.act_chan_TX()
    chip.act_chan_RX()
    print(chip.get_status())
    chip.mPmad.PrintAllAdcMinMax(mon_sel=0)
    chip.mPmad.PrintAllRxCoef()
    chip.mPmad.TuneChip()
    print(chip.get_status())
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
#test_0(chip)
#test_1(chip)
#test_2(chip)
#test_3(chip)
#test_4(chip)
#test_5(chip)
#test_6(chip)
#test_7(chip)
#test_8(chip)
#test_9(chip)
#test_10(chip)
#test_11(chip)
#test_12(chip)
#test_13(chip)
#chip.mCs.print_func_unused()
#test_me(chip)
#test_ber(chip)
#from evb_plot import *
#plot_ber_eom('../dump/ber_data_25_78125_reg_reg_NN_2_ln0.txt')

