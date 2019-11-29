if __name__ == '__main__':
    import os
    import sys

    evb_path = os.path.abspath('../SF56G_EVB')
    os.environ['SF56G_EVB_PATH'] = evb_path
    sys.path.insert(0, evb_path)
from evb_types import *
from evb_utils import *
from evb_config import EVB_CONFIG
from evb_apb import EVB_APB
from evb_cs import EVB_CS
from evb_pmad import EVB_PMAD


class SF56G(object):
    def __init__(self, auto_build=True):
        self.version = 1.0
        self.mCfg = EVB_CONFIG()
        self.mApb = EVB_APB()
        self.mCs = EVB_CS()
        self.mPmad = EVB_PMAD()
        # function remap
        self.GetConfig = self.mCfg.GetConfig
        self.SetConfig = self.mCfg.SetConfig
        if auto_build:
            self.build()

    def build(self):
        self.mApb.connect(self.mCfg)
        self.mCs.connect(self.mCfg, self.mApb)
        self.mPmad.connect(self.mCfg, self.mApb)

    # ----------------------------------------------------------------------------------------------------
    # functions
    # ----------------------------------------------------------------------------------------------------
    def get_type_with_string(self, data_type):
        if (data_type == "PRBS7"):
            return 0
        elif (data_type == "PRBS13"):
            return 1
        elif (data_type == "PRBS31"):
            return 2
        else:
            return 3;

    # ----------------------------------------------------------------------------------------------------
    # PCS - Config
    # ----------------------------------------------------------------------------------------------------
    # def PCS_EnableClk(self):
    #  self.ApbWrite(0x300,3)
    # ----------------------------------------------------------------------------------------------------
    # API
    # ----------------------------------------------------------------------------------------------------
    def Delay(self, ms):
        Delay(ms)

    def init_evb(self, channels=[0]):
        lane_en = 0
        for c in channels:
            lane_en += 1 << c
        self.mCfg.lane_en = lane_en
        self.mApb.init_evb()
        self.mPmad.Init()
        rdata0 = self.mApb.read(0)
        rdata1 = self.mApb.read(4)
        if rdata0 == rdata1:
            return -1
        else:
            return 0

    def set_datarate(self, data_rate=25.78125):
        self.SetConfig('data_rate', data_rate)
        self.mPmad.Start()

    def act_chan_TX(self, data_patt="PRBS31", channel=0):
        if (data_patt == "CLK"):
            self.mPmad.SetTxUserPattern([0x3333, 0x3333, 0x3333, 0x3333], channel)
        if (data_patt == "REMOTE"):
            self.mPmad.SetTxRemote(channel=channel)
        else:
            self.mPmad.SetTxBist(data_patt=self.get_type_with_string(data_patt), en=1, channel=channel)
        self.mPmad.SetTxOn(channel)

    def act_chan_RX(self, data_patt="PRBS31", channel=0):
        if (data_patt == "CLK"):
            self.mPmad.SetRxUserPattern([0x3333, 0x3333, 0x3333, 0x3333], channel)
        if (data_patt != "REMOTE"):
            self.mPmad.SetRxBist(data_patt=self.get_type_with_string(data_patt), en=1, channel=channel)
        self.mPmad.SetRxOn(channel)

    def off_chan_TX(self, channel=0):
        self.mPmad.SetTxOff(channel)

    def off_chan_RX(self, channel=0):
        self.mPmad.SetRxOff(channel=channel)

    def dis_chan_TX(self, channel=0):
        self.mPmad.SetTxDisable(channel)

    def ena_chan_TX(self, channel=0):
        self.mPmad.SetTxInitP1(channel)

    def swap_dpdn_TX(self, en=1, channel=0):
        self.mPmad.SetTxSwap(en, channel)

    def swap_dpdn_RX(self, en=1, channel=0):
        self.mPmad.SetRxSwap(en, channel)

    def tx_setting(self, graycoding=0, precoding=0, channel=0):
        self.mPmad.SetTxCoding(graycoding, precoding, channel)

    def rx_setting(self, graycoding=0, precoding=0, channel=0):
        self.mPmad.SetRxCoding(graycoding, precoding, channel)

    def tune_rx(self, channel=0):
        self.mPmad.TuneRx(channel)

    def tune_init(self, channel=0):
        self.mPmad.SetRxTuneInit(channel)

    def meas_eye(self, height_only=1, channel=0):
        return self.mPmad.meas_eye(height_only, channel)

    def meas_ber(self, measure_bits_db=34, channel=0):
        return self.mPmad.GetBer(measure_bits_db, channel)

    def get_status(self, measure_bits_db=34, vertical_analysis_en=1, horizontal_analysis_en=0, lin_fit_en=1, lin_fit_point=41,
                   lin_fit_main=10, tag='', channel=0,lin_fit_pulse_plot_en=1,bathtub_plot_en=1,filename=''):
        return self.mPmad.GetStatus(measure_bits_db=measure_bits_db, vertical_analysis_en=vertical_analysis_en, horizontal_analysis_en=horizontal_analysis_en,
                                    lin_fit_en=lin_fit_en, lin_fit_point=lin_fit_point, lin_fit_main=lin_fit_main,
                                    tag=tag, channel=channel,lin_fit_pulse_plot_en=lin_fit_pulse_plot_en,bathtub_plot_en=bathtub_plot_en,filename=filename)

    def set_tx_pre_post(self, tx_pre2=0, tx_pre1=0, tx_post1=0, attenuation=1.0, channel=0):
        self.mPmad.SetTxEq(tx_pre2, tx_pre1, tx_post1, attenuation, channel)

    def set_rx_ffe(self, tap=1, coef=0, channel=0):
        coef_value = int(coef * 127.0)
        self.mPmad.SetRxEqForce(tap, coef_value, channel)

    def display_rx_eq(self, channel=0):
        self.mPmad.PrintAllRxCoef(channel)

    def lin_fit_pulse(self, num_point=41, main=10, eq_out=0, lin_fit_pulse_plot_en=1, channel=0,filename=''):
        return self.mPmad.lin_fit_pulse(num_point, main, eq_out, lin_fit_pulse_plot_en, channel,filename)

    def get_impulse(self, patternwidth=16, channel=0):
        print(self.mPmad.get_impulse(patternwidth, channel))

    def GetHistogram(self, channel=0):
        self.mCs.GetHistogram()

    def get_extra_ber(self, nBit=1, channel=0):
        return self.mCs.get_extra_ber(nBit, channel)

    def plot_histo_eom(self):
        self.mCs.GetHistoEom()

    def plot_histo_allch(self):
        self.mCs.GetAllChHistogram()

    def plot_ber_eom(self):
        if self.mCfg.data_rate >= 53.125:
            self.mCs.GetBerEomPam4()
        else:
            self.mCs.GetBerEom()

    def plot_256_samples(self, mon_sel=0):
        self.mCs.Plot256(mon_sel)

    # ----------------------------------------------------------------------------------------------------
    # Self-Test
    # ----------------------------------------------------------------------------------------------------
    def test_apb(self):
        print("[test_apb] start")
        self.mApb.init_evb()
        self.mPmad.Init()
        rdata0 = self.mApb.read(0)
        rdata1 = self.mApb.read(4)
        if rdata0 == rdata1:
            print("test fail")
        else:
            print("test success")

    def test_smoke_mCs(self):
        print("[test_smoke_mCs] start")
        self.mApb.init_evb()
        self.mCs.WriteElbVector()
        ber = self.mCs.GetBer()
        if ber > 1e-2:
            print("test fail")
        else:
            print("test success")

    def test_smoke_mPmad(self):
        print("[test_smoke_mPmad] start")
        self.init_evb()
        self.set_datarate(25.78125)
        self.act_chan_TX('PRBS13')
        self.act_chan_RX('PRBS13')
        ber = self.meas_ber()
        if ber > 1e-2:
            print("test fail")
        else:
            print("test success")


if __name__ == '__main__':
    chip = SF56G()
    chip.SetConfig('b_dbg_apb_read', True)
    chip.SetConfig('media_mode', 'SLB')
    chip.SetConfig('data_rate', 25.78125)
    chip.build()
    # alias
    w = chip.mApb.write
    r = chip.mApb.read
    i = chip.init_evb
    # run
    if 0:
        chip.test_smoke_mCs()
    if 1:
        chip.test_smoke_mPmad()
