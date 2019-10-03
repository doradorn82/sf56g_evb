from evb_utils import *

class EVB_CONFIG(object):
    def __init__(self):
        self.version = 1.0
        self.data_rate = 53.125
        self.lane_en   = 0xf
        self.max_channel = 4
        self.ext_clk   = 0
        self.apb_delay = 0
        self.b_dbg_apb_read = False
        self.b_dbg_apb_write = False
        self.b_dbg_print = False
        self.b_WA0 = True
        self.b_prot_en = False
        self.media_mode = 'RLB' #:= 'SLB'(internal channel),'ELB'(external channel),'RLB'(external long channel)
        self.adc_measure_time = 1
        self.ber_chk_period   = 500
        self.ber_chk_max      = 10
        self.process_corner = 'NN'
        self.chip_num = 2
        self.vdd08 = 'reg'
        self.vdd12 = 'reg'
        self.cb_pmad_pre = None
        self.phaseStep = 2
        self.b_init_boost_current = [True]*4
        #self.b_init_boost_current = True
        self.b_WA0 = True
        self.b_use_old_tune = False
        self.ber_fail_value = 0.5
        self.ber_init_cnt = 0
        self.dump_path = '../dump/'
        self.histo_meastime = 5
        self.histo_zero_thld = 10
        self.b_use_old_meas_eye = False
        self.eom_zero_thld = 1000
        self.b_use_txeq_lut = False
        self.gen_params()

    def gen_params(self):
        self.dump_abs_path = get_evb_path()+'\\'+self.dump_path

    def SetConfig(self,key,value):
        if key in self.__dict__.keys():
            self.__dict__[key] = value
            self.gen_params()

    def GetConfig(self,key):
        if key in self.__dict__.keys():
            return (self.__dict__[key])

    def GetCondition(self):
        string = str(self.data_rate).replace('.','_')+'_'+str(self.vdd08)+'_'+str(self.vdd12)+'_'+self.process_corner+'_'+str(self.chip_num)
        return string