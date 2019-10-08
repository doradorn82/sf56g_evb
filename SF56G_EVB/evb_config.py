from evb_utils import *
class EVB_CONFIG(object):
    def __init__(self):
        self.version = 1.0
        self.data_rate = 53.125
        self.lane_en   = 0xf
        self.max_channel = 4
        self.ext_clk   = 0
        self.apb_delay = 0
        self.apb_poll_delay = 1
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
        self.ber_init_cnt = 0
        self.dump_path = '../dump/'
        self.histo_meastime = 5
        self.histo_zero_thld = 10
        self.b_use_old_meas_eye = False
        self.eom_zero_thld = 1000
        self.b_use_txeq_lut = False
        self.extra_ber_nrz_margin_list=[-12,-15,-17]
        self.extra_ber_pam4_margin_list=[-9,-12]
        self.log_ber_thld = 5*1e-1
        self.log_target   = ['tx','rx','cmn']
        self.extra_ber_h_phase = 90
        self.extra_ber_h_dump  = False
        self.extra_ber_h_plot  = False
        self.extra_ber_h_plot_raw = False
        self.extra_ber_h_accum_set = 10
        self.extra_ber_h_nrz_margin_list  = [-12,-15,-17]
        self.extra_ber_h_pam4_margin_list = [-9,-12]
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
        string = str(self.data_rate).replace('.','_')+'_'+self.process_corner
        return string
    def __repr__(self):
        s = ''
        for key,item in self.__dict__.items():
            s += ('%25s = %s\n' % (key,item))
        return s


