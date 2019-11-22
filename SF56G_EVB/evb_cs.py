from evb_types import *
from evb_utils import *
import subprocess
import os
from evb_plot import *


class EVB_CS(object):
    def __init__(self):
        # port
        self.mCfg = None
        self.mApb = None
        self.evb_path = get_evb_path()
        self.dump_path = self.evb_path + '/../dump/'
        self.func_record = {'phyExtClkEn': 0, 'phyExtClkEn_pcs': 0, 'phyXoClkEn': 0, 'SwCm1Adap': 0, 'CheckOverGainAdc': 0, 'CheckOverGainCal': 0,
                            'txSlbBistEn': 0, 'txElbBistEn': 0, 'rxSlbBistEn': 0, 'rxElbBistEn': 0, 'WriteInitialRxEvalVector': 0, 'WritePostRxEvalVector': 0,
                            'AfeAdaptation': 0, 'AfeTuneScale': 0, 'AdcFineCalRestart': 0, 'SwVga2Adap': 0, 'SwOffsetCompensationCh': 0,
                            'writeLaneDefault25gVector': 0, 'WriteCmnVector': 0, 'phyEqC1Forcing': 0, 'phyEqCpre1Forcing': 0, 'phyEqOff': 0, 'phyEqOff4to8': 0,
                            'txRemoteLbEn': 0, 'gbe_1x200g_pcs_config': 0, 'gbe_1x100g_pcs_config': 0, 'gbe_1x25g_pcs_config': 0, 'gbe_1x40g_pcs_config': 0,
                            'WriteSlbVector': 0, 'SweepGetBer': 0, 'WriteElbVector': 0, 'WriteElbVector_pcs_lb': 0, 'WriteSineElbVector': 0,
                            'WriteRxEvalVector': 0, 'PCS_loopback': 0, 'PCS_200gx1_loopback': 0, 'PCS_100gx1_loopback': 0, 'PCS_25gx1_loopback': 0,
                            'PCS_40gx1_loopback': 0, 'WriteProtlbVector': 0, 'DefaultFfeWrite': 0, 'TxSineOut': 0, 'GetHistogram': 0, 'GetAllChHistogram': 0,
                            'GetHistoEom': 0, 'GetBerEom': 0, 'GetBerEomPam4': 0, 'GetBathtub': 0, 'getHorizontalCenter': 0, 'GetBer': 0, 'Plot256': 0,
                            'C1SweepAdap': 0, 'Cm1SweepAdap': 0, 'C1CtrlSweep': 0, 'GetCaloutMin': 0, 'GetCaloutMax': 0, 'GetAdcMaxMin': 0, 'GetCalMaxMin': 0,
                            'GetAdcMin8': 0, 'GetAdcMax8': 0, 'GetAdcMaxMin8': 0, 'GetAdcMin': 0, 'GetAdcMax': 0, 'VcoCharac': 0, 'GetHistogramOfBer': 0}

    def connect(self, mCfg, mApb):
        self.mCfg = mCfg
        self.mApb = mApb

    # ----------------------------------------------------------------------------------------------------
    # private functions
    # ----------------------------------------------------------------------------------------------------
    def is_lane_enabled(self, lane_index=0):
        return ((self.mCfg.lane_en >> lane_index) & 1 == 1)

    def print_func_recod(self):
        for key, item in self.func_record.items():
            print("[%s] = %d" % (key, item))

    def print_func_unused(self):
        string = ''
        for key, item in self.func_record.items():
            if item == 0:
                print("unused funcions = %s" % (key))
                string += ("unused funcions = %s\n" % (key))
        return string

    # ----------------------------------------------------------------------------------------------------
    # Config - Special
    # ----------------------------------------------------------------------------------------------------

    def phyExtClkEn(self):
        self.func_record['phyExtClkEn'] += 1
        self.mApb.write(0x24000004, 0x00000003)
        self.mApb.write(0x24000004, 0x00000000)
        lnEn = self.mCfg.lane_en
        self.mApb.write(0x24000024, 0x00000270 | lnEn)

    def phyExtClkEn_pcs(self):
        self.func_record['phyExtClkEn_pcs'] += 1
        self.mApb.write(0x24000004, 0x00000003)
        self.mApb.write(0x24000004, 0x00000000)
        lnEn = self.mCfg.lane_en
        self.mApb.write(0x24000024, 0x00000240 | lnEn)

    def phyXoClkEn(self):
        self.func_record['phyXoClkEn'] += 1
        self.mApb.write(0x24000004, 0x00000003)
        self.mApb.write(0x24000004, 0x00000000)
        lnEn = self.mCfg.lane_en
        self.mApb.write(0x24000024, 0x00000230 | lnEn)

    def WriteSlbVector(self):
        self.func_record['WriteSlbVector'] += 1
        self.phyXoClkEn()
        self.WriteCmnVector()
        for ln_i in range(4):
            if (((self.mCfg.lane_en >> ln_i) & 0x1) == 0x1):
                self.writeLaneDefault25gVector(ln_i)
                self.mApb.write(0x000640a8, 0x00000002, ln_i)
                self.mApb.write(0x0000004c, 0x00003FF3)
                self.mApb.write(0x00060010, 0x00000000, ln_i)
                self.mApb.write(0x00060014, 0x00000000, ln_i)
                self.mApb.write(0x00061008, 512 - 0, ln_i)

                self.phyEqCpre1Forcing(5, ln_i)
                self.mApb.write(0x00060090, 0x00000400, ln_i)

                if (self.mCfg.data_rate == 10.3125):
                    self.phyEqC1Forcing(0, ln_i)
                    self.mApb.write(0x00060500, 0x00008688, ln_i)
                    self.mApb.write(0x00050018, 0x00000001, ln_i)
                    self.mApb.write(0x00050100, 0x00000042, ln_i)
                    self.mApb.write(0x00063454, 0x00005390, ln_i)
                    self.mApb.write(0x0006345c, 0x0000fe20, ln_i)
                    self.mApb.write(0x00062004, 0x0000c0c0, ln_i)
                    self.mApb.write(0x00062008, 0x0000c0c0, ln_i)
                    self.mApb.write(0x0006200C, 0x0000c0c0, ln_i)
                    self.mApb.write(0x00062010, 0x0000c0c0, ln_i)
                    self.mApb.write(0x00060028, 0x0000001F, ln_i)
                    self.mApb.write(0x00060108, 0x00007A08, ln_i)
                if (self.mCfg.data_rate == 53.125):
                    self.phyEqC1Forcing(50, ln_i)
                    self.mApb.write(0x00060208, 0x00000180, ln_i)
                    self.mApb.write(0x00050084, 0x00000010, ln_i)
                    self.mApb.write(0x0006008C, 0x00000050, ln_i)
                self.mApb.write(0x00060088, 0x9, ln_i)
        self.mApb.write(0x00000064, 0x00000011)
        for ln_i in range(4):
            if (((self.mCfg.lane_en >> ln_i) & 0x1) == 0x1):
                self.mApb.write(0x00050000, 0x00000008, ln_i)
                self.mApb.write(0x00050000, 0x00000000, ln_i)
                self.mApb.write(0x00060088, 0x8, ln_i)
                if (self.mCfg.data_rate == 10.3125):
                    self.mApb.write(0x00050100, 0x00000002, ln_i)
                    self.mApb.write(0x00050100, 0x00000042, ln_i)
                self.mApb.write(0x00060060, 0x00000053, ln_i)
                self.mApb.write(0x00060090, 0x00000000, ln_i)
                self.txSlbBistEn(ln_i)
                self.rxSlbBistEn(ln_i)

    def SweepGetBer(self):
        self.func_record['SweepGetBer'] += 1
        filename = self.dump_path + "ber.txt"
        fs = open(filename, 'w')
        for i_1 in range(8):
            rs = 17 + i_1 * 2
            for i_2 in range(4):
                rl = 9 + i_2 * 2
                for i_3 in range(4):
                    ictrl = 8 + i_3 * 2
                    vga2Setting = (rs << 11) + (rl << 7) + (ictrl << 3)
                    for i_4 in range(4):
                        if (i_4 == 0):
                            slbvcm = 0
                        elif (i_4 == 1):
                            slbvcm = 1
                        elif (i_4 == 2):
                            slbvcm = 2
                        else:
                            slbvcm = 3

                        for ln_i in range(4):
                            if (((self.mCfg.lane_en >> ln_i) & 0x1) == 0x1):
                                self.phyXoClkEn()
                                self.WriteCmnVector()
                                self.writeLaneDefault25gVector(ln_i)
                                self.mApb.write(0x00062004, 0x0000C0C0, ln_i)
                                self.mApb.write(0x00062008, 0x0000C0C0, ln_i)
                                self.mApb.write(0x0006200c, 0x0000C0C0, ln_i)
                                self.mApb.write(0x00062010, 0x0000C0C0, ln_i)
                                self.mApb.write(0x000640a8, 0x00000002, ln_i)
                                self.mApb.write(0x0000004c, 0x00003FF3)
                                self.mApb.write(0x00063454, 0x00005150, ln_i)
                                self.mApb.write(0x00060054, 0x00007cc0, ln_i)
                                self.mApb.write(0x00060090, 0x00000400, ln_i)

                                if self.mCfg.data_rate == 53.125:
                                    self.phyEqC1Forcing(40, ln_i)
                                    self.mApb.write(0x00060208, 0x00000180, ln_i)
                                    self.mApb.write(0x00050084, 0x00000010, ln_i)
                                    self.mApb.write(0x0006008C, 0x00000050, ln_i)
                                    self.mApb.write(0x00060048, 0x0000888f | (slbvcm << 4), ln_i)
                                    self.mApb.write(0x00060054, vga2Setting, ln_i)
                                self.mApb.write(0x00060088, 0x9, ln_i)

                        self.mApb.write(0x00000064, 0x00000011)

                        for ln_i in range(4):
                            if self.is_lane_enabled(ln_i):
                                self.mApb.write(0x00050000, 0x00000008, ln_i)
                                self.mApb.write(0x00050000, 0x00000000, ln_i)
                                self.mApb.write(0x00060088, 0x8, ln_i)
                                if self.mCfg.data_rate == 10.3125:
                                    self.mApb.write(0x00050100, 0x00000002, ln_i)
                                    self.mApb.write(0x00050100, 0x00000042, ln_i)
                                self.mApb.write(0x00060060, 0x00000053, ln_i)
                                self.mApb.write(0x00060090, 0x00000000, ln_i)
                                self.txSlbBistEn(ln_i)
                                ber = self.GetBer(ln_i)
                                print("rs=%d,rl=%d,ictrl=%d,slbvcm=%d BER=%e" % (rs, rl, ictrl, slbvcm, ber))
                                fs.write("%d\t%d\t%d\t%d\t%e\n" % (rs, rl, ictrl, slbvcm, ber))
        print("Done")
        fs.close()

    def WriteElbVector(self):
        self.func_record['WriteElbVector'] += 1
        self.phyXoClkEn()
        self.WriteCmnVector()

        for ln_i in range(4):
            if self.is_lane_enabled(ln_i):
                self.writeLaneDefault25gVector(ln_i)
                self.phyEqCpre1Forcing(20)
                self.mApb.write(0x000640b4, 413, ln_i)
                self.mApb.write(0x00061008, 512 - 20, ln_i)
                # 10G
                if self.mCfg.data_rate == 10.3125:
                    self.mApb.write(0x00061008, 512 - 80, ln_i)
                    self.mApb.write(0x00060500, 0x00008688, ln_i)
                    self.mApb.write(0x00050018, 0x00000001, ln_i)
                    self.mApb.write(0x00050100, 0x00000042, ln_i)
                    self.mApb.write(0x00063454, 0x00005390, ln_i)
                    self.mApb.write(0x0006345c, 0x0000fe20, ln_i)
                    self.mApb.write(0x00062004, 0x0000c0c0, ln_i)
                    self.mApb.write(0x00062008, 0x0000c0c0, ln_i)
                    self.mApb.write(0x0006200C, 0x0000c0c0, ln_i)
                    self.mApb.write(0x00062010, 0x0000c0c0, ln_i)
                    self.mApb.write(0x00060054, ((15 << 11) + (13 << 7) + (14 << 3)), ln_i)
                    self.mApb.write(0x00060038, ((1 << 14) + (0 << 10) + (5 << 5) + 5), ln_i)
                    self.mApb.write(0x00060108, 0x00007A08, ln_i)
                # 53G
                if self.mCfg.data_rate == 53.125:
                    self.phyEqCpre1Forcing(20, ln_i)
                    self.mApb.write(0x00060208, 0x00000180, ln_i)
                    self.mApb.write(0x00050084, 0x00000010, ln_i)
                    self.mApb.write(0x0006008C, 0x00000050, ln_i)
                self.mApb.write(0x00060088, 0x9, ln_i)
                self.txElbBistEn(ln_i)
        self.mApb.write(0x00000064, 0x00000011)
        for ln_i in range(4):
            if self.is_lane_enabled(ln_i):
                self.mApb.write(0x00050000, 0x00000008, ln_i)
                self.mApb.write(0x00050000, 0x00000000, ln_i)
                self.mApb.write(0x00060088, 0x8, ln_i)
                if self.mCfg.data_rate == 10.3125:
                    self.mApb.write(0x00050100, 0x00000002, ln_i)
                    self.mApb.write(0x00050100, 0x00000042, ln_i)
                self.DefaultFfeWrite(0, 1, 3)
                self.rxElbBistEn(ln_i)
                self.txRemoteLbEn(ln_i)

    def WriteElbVector_pcs_lb(self):
        self.func_record['WriteElbVector_pcs_lb'] += 1
        self.phyXoClkEn()
        self.WriteCmnVector()

        for ln_i in range(4):
            if self.is_lane_enabled(ln_i):
                self.writeLaneDefault25gVector(ln_i)
                self.mApb.write(0x000640b4, 413, ln_i)
                self.mApb.write(0x00061008, 512 - 20, ln_i)

                if self.mCfg.data_rate == 10.3125:
                    self.mApb.write(0x00061008, 512 - 80, ln_i)
                    self.mApb.write(0x00060500, 0x00008688, ln_i)
                    self.mApb.write(0x00050018, 0x00000001, ln_i)
                    self.mApb.write(0x00050100, 0x00000042, ln_i)
                    self.mApb.write(0x00063454, 0x00005390, ln_i)
                    self.mApb.write(0x0006345c, 0x0000fe20, ln_i)
                    self.mApb.write(0x00062004, 0x0000c0c0, ln_i)
                    self.mApb.write(0x00062008, 0x0000c0c0, ln_i)
                    self.mApb.write(0x0006200C, 0x0000c0c0, ln_i)
                    self.mApb.write(0x00062010, 0x0000c0c0, ln_i)
                    self.mApb.write(0x00060054, ((15 << 11) + (13 << 7) + (14 << 3)), ln_i)
                    self.mApb.write(0x00060038, ((1 << 14) + (0 << 10) + (5 << 5) + 5), ln_i)
                    self.mApb.write(0x00060108, 0x00007A08, ln_i)

                if self.mCfg.data_rate == 53.125:
                    self.phyEqCpre1Forcing(10, ln_i)
                    self.phyEqOff4to8(ln_i)
                    self.mApb.write(0x00060208, 0x00000180, ln_i)
                    self.mApb.write(0x00050084, 0x00000010, ln_i)
                    self.mApb.write(0x0006008C, 0x00000050, ln_i)

                self.mApb.write(0x00060088, 0x9, ln_i)
                self.txElbBistEn(ln_i)
        self.mApb.write(0x00000064, 0x00000011)
        for ln_i in range(4):
            if self.is_lane_enabled(ln_i):
                self.mApb.write(0x00050000, 0x00000008, ln_i)
                self.mApb.write(0x00050000, 0x00000000, ln_i)
                self.mApb.write(0x00060088, 0x8, ln_i)
                if self.mCfg.data_rate == 10.3125:
                    self.mApb.write(0x00050100, 0x00000002, ln_i)
                    self.mApb.write(0x00050100, 0x00000042, ln_i)
                self.DefaultFfeWrite(0, 1, 3)

    def WriteSineElbVector(self):
        self.func_record['WriteSineElbVector'] += 1
        self.phyXoClkEn()
        self.WriteCmnVector()
        for ln_i in range(4):
            if self.is_lane_enabled(ln_i):
                self.writeLaneDefault25gVector(ln_i)
                self.phyEqOff(0, ln_i)
                self.mApb.write(0x00062004, 0x0000c0c0, ln_i)
                self.mApb.write(0x00062008, 0x0000c0c0, ln_i)
                self.mApb.write(0x0006200C, 0x0000c0c0, ln_i)
                self.mApb.write(0x00062010, 0x0000c0c0, ln_i)
                self.mApb.write(0x0006430c, 0x00000040, ln_i)
                self.mApb.write(0x00064310, 0x0000007f, ln_i)
                self.mApb.write(0x00064314, 0x00000040, ln_i)
                self.mApb.write(0x00064318, 0x0000007f, ln_i)
                self.mApb.write(0x0006431c, 0x0000007f, ln_i)
                self.mApb.write(0x000640a8, 0x00000003, ln_i)
                if self.mCfg.data_rate == 10.3125:
                    self.phyEqOff(0, ln_i)
                    self.mApb.write(0x00061008, 512 - 80, ln_i)
                    self.mApb.write(0x00060500, 0x00008688, ln_i)
                    self.mApb.write(0x00060038, 0x00007109, ln_i)
                    self.mApb.write(0x00050018, 0x00000001, ln_i)
                    self.mApb.write(0x00050100, 0x00000042, ln_i)
                    self.mApb.write(0x00063454, 0x00005390, ln_i)
                    self.mApb.write(0x0006345c, 0x0000fe20, ln_i)
                    self.mApb.write(0x00060020, 0x00000011, ln_i)
                    self.mApb.write(0x00060028, 0x00000011, ln_i)
                    self.mApb.write(0x0006002c, 0x00000021, ln_i)
                    self.mApb.write(0x00060108, 0x00007A08, ln_i)
                if self.mCfg.data_rate == 53.125:
                    self.phyEqOff(30, ln_i)
                    self.mApb.write(0x00060208, 0x00000180, ln_i)
                    self.mApb.write(0x00060054, ((23 << 11) + (15 << 7) + (14 << 3)), ln_i)
                    self.mApb.write(0x00060020, 0x00000014, ln_i)
                    self.mApb.write(0x00060028, 0x0000001f, ln_i)
                    self.mApb.write(0x0006002c, 0x00000028, ln_i)
                    self.mApb.write(0x00050084, 0x00000010, ln_i)
                    self.mApb.write(0x0006008C, 0x00000050, ln_i)

                if self.mCfg.b_WA0 == True:
                    dcc_code = self.mApb.read(0x50144, ln_i)
                    self.mApb.write(0x5000c, dcc_code, ln_i)
                    self.mApb.write(0x50000, 0x3 << 8, ln_i, 3 << 8)

                    self.mApb.write(0x60088, 1 << 0, ln_i, 1 << 0)  # rx_en
                    self.mApb.write(0x6008C, 0 << 0, ln_i, 1 << 0)  # rx_en
        self.mApb.write(0x00000064, 0x00000011)
        for ln_i in range(4):
            if self.is_lane_enabled(ln_i):
                if self.mCfg.b_WA0 == True:
                    self.mApb.write(0x50000, 0x1 << 3, ln_i, 1 << 3)
                    self.mApb.write(0x50000, 0x0 << 3, ln_i, 1 << 3)
                    self.mApb.write(0x6008C, 1 << 0, ln_i, 1 << 0)  # rx_en
                self.mApb.write(0x00063450, 0x0000102c, ln_i)
                self.txElbBistEn(ln_i)
                self.rxElbBistEn(ln_i)
        self.TxSineOut(3)

    def WriteRxEvalVector(self):
        self.func_record['WriteRxEvalVector'] += 1
        self.phyXoClkEn()
        self.WriteCmnVector()

        currentBoostSel = 0xf
        for ln_i in range(4):
            if self.is_lane_enabled(ln_i):
                self.WriteInitialRxEvalVector(0x1 & (currentBoostSel >> ln_i), ln_i)
                self.mApb.write(0x00060028, 0x00000013, ln_i)

        self.mApb.write(0x00000064, 0x00000011)
        for ln_i in range(4):
            if self.is_lane_enabled(ln_i):
                self.WritePostRxEvalVector(ln_i)
                if (self.CheckOverGainAdc(63, ln_i) == 1):
                    currentBoostSel -= (1 << ln_i)
                    print("LN%d turn off current boosting option" % (ln_i))

        self.phyXoClkEn()
        self.WriteCmnVector()
        for ln_i in range(4):
            if self.is_lane_enabled(ln_i):
                self.WriteInitialRxEvalVector(0x1 & (currentBoostSel >> ln_i), ln_i)
                self.mApb.write(0x000601dc, 0x00000001, ln_i)
        self.mApb.write(0x00000064, 0x00000011)
        for ln_i in range(4):
            if self.is_lane_enabled(ln_i):
                self.WritePostRxEvalVector(ln_i)
                ret = self.AfeAdaptation(ln_i)
                if (ret == -1):
                    return -1
                self.rxElbBistEn(ln_i)
        return 0

    def WriteInitialRxEvalVector(self, currentBoostSel, ln_i=0):
        self.func_record['WriteInitialRxEvalVector'] += 1
        cm1init = 30
        vga2Gain = 15
        ctleGain = 0
        self.writeLaneDefault25gVector(ln_i)
        self.mApb.write(0x00061008, 512 - 0, ln_i)
        self.phyEqCpre1Forcing(cm1init, ln_i)
        self.mApb.write(0x00060020, 0x0000001f - ctleGain, ln_i)
        self.mApb.write(0x00060028, 0x0000001f - vga2Gain, ln_i)
        self.mApb.write(0x0006002c, 0x0000003f, ln_i)

        self.mApb.write(0x00063454, 0x00006530, ln_i)
        self.mApb.write(0x00060054, ((0 << 15) + (31 << 11) + (15 << 7) + (14 << 3)), ln_i)
        self.mApb.write(0x00060050, ((15 << 7) + (15 << 3)), ln_i)
        self.mApb.write(0x00060038, ((0 << 10) + (11 << 5) + 11), ln_i)

        if (currentBoostSel == 1):
            self.mApb.write(0x00060054, ((0 << 15) + (15 << 11) + (15 << 7) + (15 << 3) + (0 << 2) + 0), ln_i)
            self.mApb.write(0x00060050, ((15 << 7) + (15 << 3) + (0 << 2) + 0), ln_i)
            self.mApb.write(0x00060038, ((0 << 10) + (15 << 5) + 15), ln_i)
            self.mApb.write(0x00050020, 0x00000001, ln_i)
            self.mApb.write(0x00060048, 0x00007b9f, ln_i)
        self.mApb.write(0x00060064, 0x0000120f, ln_i)
        self.mApb.write(0x00060040, 0x000000aa, ln_i)
        self.mApb.write(0x00060058, 0x00000128, ln_i)

        self.txElbBistEn(ln_i)

        if self.mCfg.data_rate == 10.3125:
            self.phyEqC1Forcing(60, ln_i)
            self.mApb.write(0x00060500, 0x00008688, ln_i)
            self.mApb.write(0x00060038, 0x00007109, ln_i)
            self.mApb.write(0x00050018, 0x00000001, ln_i)
            self.mApb.write(0x00050100, 0x00000042, ln_i)
            self.mApb.write(0x00063454, 0x0000578f, ln_i)
            self.mApb.write(0x0006345c, 0x0000fe20, ln_i)
            self.mApb.write(0x00062004, 0x0000c0c0, ln_i)
            self.mApb.write(0x00062008, 0x0000c0c0, ln_i)
            self.mApb.write(0x0006200C, 0x0000c0c0, ln_i)
            self.mApb.write(0x00062010, 0x0000c0c0, ln_i)
            self.mApb.write(0x00060028, 0x00000016, ln_i)
            self.mApb.write(0x00060108, 0x00007A08, ln_i)

        if self.mCfg.data_rate in [53.125, 56.25]:
            self.mApb.write(0x00060208, 0x00000180, ln_i)
            self.mApb.write(0x00050084, 0x00000010, ln_i)
            self.mApb.write(0x0006008C, 0x00000050, ln_i)
            self.DefaultFfeWrite(0, 0, 0)
        self.mApb.write(0x00060088, 0x9, ln_i)
        self.mApb.write(0x00060128, 0x100, ln_i)

    def WritePostRxEvalVector(self, ln_i):
        self.func_record['WritePostRxEvalVector'] += 1
        self.mApb.write(0x00050000, 0x00000008, ln_i)
        self.mApb.write(0x00050000, 0x00000000, ln_i)
        self.mApb.write(0x00060088, 0x8, ln_i)

        if self.mCfg.data_rate == 10.3125:
            self.mApb.write(0x00050100, 0x00000002, ln_i)
            self.mApb.write(0x00050100, 0x00000042, ln_i)
        if self.mCfg.data_rate == 10.3125:
            self.mApb.write(0x00063450, 0x0000100d, ln_i)
        elif self.mCfg.data_rate == 25.78125:
            self.mApb.write(0x00063450, 0x0000000d, ln_i)
        else:
            self.mApb.write(0x00063450, 0x0000000b, ln_i)

    def AfeAdaptation(self, ln_i):
        self.func_record['AfeAdaptation'] += 1
        maxLimit = 61
        minLimit = 58
        vga1Gain = self.mApb.read(0x0006002c, ln_i) - 32
        ctleGain = 15 - (self.mApb.read(0x00060020, ln_i) - 16)

        maxVal = self.GetAdcMaxMin8(ln_i) >> 8
        minVal = self.GetAdcMaxMin8(ln_i) & 0xff

        adcVrefSel = self.mApb.read(0x00060034, ln_i)
        if (maxVal < minLimit) and (minVal < minLimit):
            while ((maxVal < minLimit) and (minVal < minLimit) and ((adcVrefSel >> 6) > 0)):
                adcVrefSel -= (1 << 6)
                self.mApb.write(0x00060034, adcVrefSel, ln_i)
                maxVal = self.GetAdcMaxMin8(ln_i) >> 8
                minVal = self.GetAdcMaxMin8(ln_i) & 0xff
            print("adc vref sel update to 0x%x" % (adcVrefSel >> 6))

        elif (maxVal > maxLimit) and (minVal > maxLimit):
            while ((maxVal > maxLimit) and (minVal > maxLimit) and (vga1Gain > 0xf)):
                vga1Gain -= 8
                self.mApb.write(0x0006002c, 0x20 + vga1Gain, ln_i)
                maxVal = self.GetAdcMaxMin8(ln_i) >> 8
                minVal = self.GetAdcMaxMin8(ln_i) & 0xff
            if ((maxVal + minVal) < 120):
                vga1Gain += 8
                self.mApb.write(0x0006002c, 0x20 + vga1Gain, ln_i)
            print("vga1 update to 0x%x" % (vga1Gain))

        self.SwVga2Adap(ln_i)

        self.mApb.write(0x000601dc, 0x00000000, ln_i)
        data2230 = (self.mApb.read(0x00062230, ln_i) & 0xff)
        if (data2230 == 0xff or data2230 == 0):
            return -1

        self.mApb.write(0x00060128, 0x000, ln_i)
        self.SwVga2Adap(ln_i)
        self.SwCm1Adap(ln_i)
        self.AdcFineCalRestart(ln_i)

        c0 = self.mApb.read(0x6223C, ln_i)
        c1 = self.GetAvgCoeff(1, 4, ln_i)
        c2 = self.GetAvgCoeff(2, 4, ln_i)
        ctleUpdate = 0
        while (((c2 > 35 and -c1 < 50) or (-c1 >= 50 and -c1 < 80 and c2 > 25) or (-c1 >= 80 and c2 > 20)) and ctleGain < 15):
            ctleGain += 1
            self.mApb.write(0x00060020, 0x0000001f - ctleGain, ln_i)
            self.SwCm1Adap(ln_i)
            c2 = self.GetAvgCoeff(2, 4, ln_i)
            if (-c1 < 50):
                ctleUpdate = 1
            elif (-c1 < 80):
                ctleUpdate = 2
            else:
                ctleUpdate = 3

        if (ctleUpdate == 1):
            print("CTLE gain update(short) to 0x%x" % (15 - ctleGain))
        elif (ctleUpdate == 2):
            print("CTLE gain update(med) to 0x%x" % (15 - ctleGain))
        elif (ctleUpdate == 3):
            print("CTLE gain update(long) to 0x%x" % (15 - ctleGain))

        if (ctleUpdate != 0):
            self.SwVga2Adap(ln_i)
            self.AdcFineCalRestart(ln_i)
        self.mApb.write(0x00063450, 0x0000100b, ln_i)
        return 0

    def AfeTuneScale(self):
        self.func_record['AfeTuneScale'] += 1
        maxLimit = 61
        minLimit = 58
        for ln_i in range(4):
            if self.is_lane_enabled(ln_i):
                maxVal = self.GetAdcMaxMin8(ln_i) >> 8
                minVal = self.GetAdcMaxMin8(ln_i) & 0xff
                if (maxVal < minLimit and minVal < minLimit):
                    self.SwVga2Adap(ln_i)
                    maxVal = self.GetAdcMaxMin8(ln_i) >> 8
                    minVal = self.GetAdcMaxMin8(ln_i) & 0xff
                    adcVrefSel = self.mApb.read(0x00060034, ln_i)
                    if (maxVal < minLimit and minVal < minLimit and (adcVrefSel >> 6) > 0):
                        adcVrefSel -= (1 << 6)
                        self.mApb.write(0x00060034, adcVrefSel, ln_i)
                        print("adc vref sel update to 0x%x" % (adcVrefSel >> 6))
                maxVal = self.GetAdcMaxMin8(ln_i) >> 8
                minVal = self.GetAdcMaxMin8(ln_i) & 0xff
                if (maxVal > maxLimit and minVal > maxLimit):
                    adcVrefSel = self.mApb.read(0x00060034, ln_i)
                    if ((maxVal > maxLimit and minVal > maxLimit) and (adcVrefSel >> 6) < 4):
                        adcVrefSel += (1 << 6)
                        self.mApb.write(0x00060034, adcVrefSel, ln_i)
                        print("adc vref sel update to 0x%x" % (adcVrefSel >> 6))
                    self.SwVga2Adap(ln_i)
                self.SwCm1Adap(ln_i)
                self.AdcFineCalRestart(ln_i)

    def AdcFineCalRestart(self, ln_i):
        self.func_record['AdcFineCalRestart'] += 1
        self.mApb.write(0x0006347c, 0xd000, ln_i)
        self.mApb.write(0x000601AC, 1 << 1, ln_i, 1 << 1)
        Delay(10)

    def SwCm1Adap(self, ln_i):
        self.func_record['SwCm1Adap'] += 1
        cm1init = self.mApb.read(0x62270, ln_i)
        if (cm1init > 128):
            cm1init = cm1init - 256
        cm1 = cm1init
        cm2 = self.GetAvgCoeff(-2, 4, ln_i)
        if (-cm2 < -10 and -cm1 > 5):
            while (-cm2 < -10 and -cm1 > 5):
                cm1 += 1
                self.phyEqCpre1Forcing(-cm1, ln_i)
                cm2 = self.GetAvgCoeff(-2, 4, ln_i)
        c1 = self.GetAvgCoeff(1, 4, ln_i)
        if (c1 < cm1 - 50):
            while (c1 < cm1 - 50):
                cm1 -= 1
                self.phyEqCpre1Forcing(-cm1, ln_i)
                c1 = self.GetAvgCoeff(1, 4, ln_i)

    def CheckOverGainAdc(self, limit, ln_i=0):
        self.func_record['CheckOverGainAdc'] += 1
        maxMin = self.GetAdcMaxMin(0, ln_i)
        maxVal = (maxMin >> 8) - 64
        minVal = 64 - (maxMin & 0x7f)
        for i in range(3):
            maxMin = self.GetAdcMaxMin(i + 1, ln_i)
            maxVal += (maxMin >> 8) - 64
            minVal += 64 - (maxMin & 0x7f)
        maxVal /= 4
        minVal /= 4
        if (maxVal >= limit and minVal >= limit):
            return 1
        else:
            return 0

    def CheckOverGainCal(self, limit, ln_i=0):
        self.func_record['CheckOverGainCal'] += 1
        maxMin = self.GetCalMaxMin(0, ln_i)
        maxVal = (maxMin >> 8) - 128
        minVal = 128 - (maxMin & 0xff)
        for i in range(3):
            maxMin = self.GetCalMaxMin(i + 1, ln_i)
            maxVal += (maxMin >> 8) - 128
            minVal += 128 - (maxMin & 0xff)
        maxVal /= 4
        minVal /= 4

        if (maxVal >= limit or minVal >= limit):
            return 1
        else:
            return 0

    def SwVga2Adap(self, ln_i=0):
        self.func_record['SwVga2Adap'] += 1
        vga2Gain = 15 - (self.mApb.read(0x00060028, ln_i))

        maxVal = self.GetAdcMaxMin8(ln_i) >> 8
        minVal = self.GetAdcMaxMin8(ln_i) & 0xff
        maxLimit = 62

        if ((maxVal > maxLimit - 1 or minVal > maxLimit) and vga2Gain > 0):
            while ((maxVal > maxLimit - 1 or minVal > maxLimit) and vga2Gain > 0):
                vga2Gain -= 1
                self.mApb.write(0x00060028, 0x0000001f - vga2Gain, ln_i)
                maxVal = self.GetAdcMaxMin8(ln_i) >> 8
                minVal = self.GetAdcMaxMin8(ln_i) & 0xff
            print("vga2 gain update to 0x%x" % (vga2Gain))
        if (maxVal < maxLimit - 3 and minVal < maxLimit - 2 and vga2Gain < 0xf):
            while (maxVal < maxLimit - 3 and minVal < maxLimit - 2 and vga2Gain < 0xf):
                vga2Gain += 1
                self.mApb.write(0x00060028, 0x0000001f - vga2Gain, ln_i)
                maxVal = self.GetAdcMaxMin8(ln_i) >> 8
                minVal = self.GetAdcMaxMin8(ln_i) & 0xff
            print("vga2 gain update to 0x%x" % (vga2Gain))

    def SwOffsetCompensationCh(self, ln_i=0):
        self.func_record['SwOffsetCompensationCh'] += 1
        for rep_i in range(2):
            for adc_i in range(32):
                data = self.mApb.read(0x00060800 + adc_i * 4, ln_i)
                if (data > 127):
                    data -= 256
                data2 = self.mApb.read(0x00064100 + adc_i * 4, ln_i)
                if (data2 != 60 and data2 != 59):
                    if (adc_i >= 18):
                        data3 = self.mApb.read(0x00064184 + adc_i * 4 + 4, ln_i)
                    else:
                        data3 = self.mApb.read(0x00064184 + adc_i * 4, ln_i)
                    offset = -(data2 + data3 - 256) / 2
                    result = data + offset

                    if (result < 0):
                        result += 256
                    if (offset != 0 and data2 != 60 and data2 != 59 and (256 - data3) != 60 and (256 - data3) != 59):
                        self.mApb.write(0x00062014 + adc_i * 4, 0x8000 + result, ln_i)
                        self.mApb.write(0x00061FF8, 0x1, ln_i)

    def writeLaneDefault25gVector(self, ln_i=0):
        self.func_record['writeLaneDefault25gVector'] += 1
        self.mApb.write(0x00050000, 0x00000001, ln_i)
        self.mApb.write(0x00050004, 0x00000002, ln_i)
        self.mApb.write(0x00050008, 0x00000000, ln_i)
        self.mApb.write(0x0005000c, 0x00002040, ln_i)
        self.mApb.write(0x00050014, 0x00000401, ln_i)
        self.mApb.write(0x00050018, 0x00000000, ln_i)
        self.mApb.write(0x00050020, 0x00000002, ln_i)
        self.mApb.write(0x00050024, 0x00000000, ln_i)
        self.mApb.write(0x00050044, 0x00000000, ln_i)
        self.mApb.write(0x00050050, 0x00000000, ln_i)
        self.mApb.write(0x00050054, 0x00000000, ln_i)
        self.mApb.write(0x00050080, 0x00000008, ln_i)
        self.mApb.write(0x00050084, 0x00000000, ln_i)
        self.mApb.write(0x00050088, 0x00000000, ln_i)
        self.mApb.write(0x0005008c, 0x00000000, ln_i)
        self.mApb.write(0x00050090, 0x00000000, ln_i)
        self.mApb.write(0x00050100, 0x00000002, ln_i)
        self.mApb.write(0x00050104, 0x00000220, ln_i)
        self.mApb.write(0x00050108, 0x0000007f, ln_i)
        self.mApb.write(0x0005010c, 0x00001aa0, ln_i)
        self.mApb.write(0x00050110, 0x0000ffff, ln_i)
        self.mApb.write(0x00050114, 0x00007fff, ln_i)
        self.mApb.write(0x00050118, 0x0000aaaa, ln_i)
        self.mApb.write(0x0005011c, 0x0000aaaa, ln_i)
        self.mApb.write(0x00050120, 0x0000aaaa, ln_i)
        self.mApb.write(0x00050124, 0x0000aaaa, ln_i)
        self.mApb.write(0x00050128, 0x00000cd8, ln_i)
        self.mApb.write(0x0005012c, 0x00000018, ln_i)
        self.mApb.write(0x00050130, 0x0000000f, ln_i)
        self.mApb.write(0x00050134, 0x00000000, ln_i)
        self.mApb.write(0x00050138, 0x00000000, ln_i)
        self.mApb.write(0x00050150, 0x00000000, ln_i)
        self.mApb.write(0x00050154, 0x00000403, ln_i)
        self.mApb.write(0x00050158, 0x00000000, ln_i)
        self.mApb.write(0x0005015c, 0x00000064, ln_i)
        self.mApb.write(0x00050160, 0x00000000, ln_i)
        self.mApb.write(0x00050164, 0x0000000a, ln_i)
        self.mApb.write(0x00050400, 0x00000000, ln_i)
        self.mApb.write(0x00050500, 0x00000000, ln_i)
        self.mApb.write(0x00050504, 0x00000001, ln_i)
        self.mApb.write(0x0005050c, 0x00000002, ln_i)
        self.mApb.write(0x00050510, 0x00000002, ln_i)
        self.mApb.write(0x00050514, 0x00000002, ln_i)
        self.mApb.write(0x00050518, 0x00000002, ln_i)
        self.mApb.write(0x0005051c, 0x00000000, ln_i)
        self.mApb.write(0x00050600, 0x00000000, ln_i)
        self.mApb.write(0x00050604, 0x0000003c, ln_i)
        self.mApb.write(0x00050608, 0x00000006, ln_i)
        self.mApb.write(0x0005060c, 0x00000211, ln_i)
        self.mApb.write(0x00050610, 0x00000d7a, ln_i)
        self.mApb.write(0x00050614, 0x00000000, ln_i)
        self.mApb.write(0x00050618, 0x00000000, ln_i)
        self.mApb.write(0x0005061c, 0x000000c1, ln_i)
        self.mApb.write(0x00050620, 0x00000043, ln_i)
        self.mApb.write(0x00050624, 0x000000c1, ln_i)
        self.mApb.write(0x00050628, 0x00000043, ln_i)
        self.mApb.write(0x0005062c, 0x000000c1, ln_i)
        self.mApb.write(0x00050630, 0x00000043, ln_i)
        self.mApb.write(0x00050634, 0x000000c1, ln_i)
        self.mApb.write(0x00050638, 0x00000043, ln_i)
        self.mApb.write(0x0005063c, 0x00000075, ln_i)
        self.mApb.write(0x00050640, 0x00000880, ln_i)
        self.mApb.write(0x00050644, 0x00000075, ln_i)
        self.mApb.write(0x00050648, 0x00000280, ln_i)
        self.mApb.write(0x0005064c, 0x00000100, ln_i)
        self.mApb.write(0x00050650, 0x00000000, ln_i)
        self.mApb.write(0x00050654, 0x00000100, ln_i)
        self.mApb.write(0x00050658, 0x00000000, ln_i)
        self.mApb.write(0x0005065c, 0x00000100, ln_i)
        self.mApb.write(0x00050660, 0x00000000, ln_i)
        self.mApb.write(0x00050664, 0x00000100, ln_i)
        self.mApb.write(0x00050668, 0x00000000, ln_i)
        self.mApb.write(0x0005066c, 0x00000000, ln_i)
        self.mApb.write(0x00050670, 0x00000072, ln_i)
        self.mApb.write(0x00050674, 0x00000000, ln_i)
        self.mApb.write(0x00060000, 0x00000000, ln_i)
        self.mApb.write(0x00060004, 0x00000000, ln_i)
        self.mApb.write(0x00060008, 0x00000000, ln_i)
        self.mApb.write(0x0006000c, 0x00000000, ln_i)
        self.mApb.write(0x00060010, 0x00000080, ln_i)
        self.mApb.write(0x00060014, 0x00000080, ln_i)
        self.mApb.write(0x00060018, 0x00000080, ln_i)
        self.mApb.write(0x0006001c, 0x00000000, ln_i)
        self.mApb.write(0x00060020, 0x0000001e, ln_i)
        self.mApb.write(0x00060028, 0x00000010, ln_i)
        self.mApb.write(0x0006002c, 0x00000027, ln_i)
        self.mApb.write(0x00060034, 0x00000121, ln_i)
        self.mApb.write(0x00060038, ((1 << 14) + (0 << 10) + (9 << 5) + 9), ln_i)
        self.mApb.write(0x0006003c, 0x00000060, ln_i)
        self.mApb.write(0x00060040, 0x000000ff, ln_i)
        self.mApb.write(0x00060044, 0x0000000c, ln_i)
        self.mApb.write(0x00060048, 0x0000799f, ln_i)
        self.mApb.write(0x0006004c, 0x00000007, ln_i)
        self.mApb.write(0x00060050, ((0 << 7) + (0 << 3) + 4 + 3), ln_i)
        self.mApb.write(0x00060054, ((18 << 11) + (13 << 7) + (14 << 3)), ln_i)
        self.mApb.write(0x00060058, 0x00000000, ln_i)
        self.mApb.write(0x0006005c, 0x00000004, ln_i)
        self.mApb.write(0x00060060, 0x00000052, ln_i)
        self.mApb.write(0x00060064, 0x0000060c, ln_i)
        self.mApb.write(0x00060068, 0x00000000, ln_i)
        self.mApb.write(0x00060078, 0x00000000, ln_i)
        self.mApb.write(0x00060080, 0x00000000, ln_i)
        self.mApb.write(0x00060084, 0x00000000, ln_i)
        self.mApb.write(0x00060088, 0x00000008, ln_i)
        self.mApb.write(0x0006008c, 0x00000040, ln_i)
        self.mApb.write(0x00060090, 0x00000000, ln_i)
        self.mApb.write(0x00060094, 0x00000000, ln_i)
        self.mApb.write(0x00060098, 0x00000700, ln_i)
        self.mApb.write(0x00060100, 0x000000a0, ln_i)
        self.mApb.write(0x00060104, 0x00004202, ln_i)
        self.mApb.write(0x00060108, 0x00007b74, ln_i)
        self.mApb.write(0x0006010c, 0x00007420, ln_i)
        self.mApb.write(0x00060110, 0x00000000, ln_i)
        self.mApb.write(0x00060114, 0x0000700f, ln_i)
        self.mApb.write(0x00060118, 0x00000000, ln_i)
        self.mApb.write(0x0006011c, 0x00000000, ln_i)
        self.mApb.write(0x00060120, 0x00000000, ln_i)
        self.mApb.write(0x00060124, 0x00000000, ln_i)
        self.mApb.write(0x00060128, 0x00000000, ln_i)
        self.mApb.write(0x0006012c, 0x00000000, ln_i)
        self.mApb.write(0x00060130, 0x00000000, ln_i)
        self.mApb.write(0x00060134, 0x00000000, ln_i)
        self.mApb.write(0x00060138, 0x00000000, ln_i)
        self.mApb.write(0x0006013c, 0x00000000, ln_i)
        self.mApb.write(0x00060140, 0x00000000, ln_i)
        self.mApb.write(0x00060144, 0x00000000, ln_i)
        self.mApb.write(0x00060148, 0x00000000, ln_i)
        self.mApb.write(0x0006014c, 0x00000000, ln_i)
        self.mApb.write(0x00060150, 0x00000000, ln_i)
        self.mApb.write(0x00060154, 0x00000000, ln_i)
        self.mApb.write(0x00060158, 0x00000000, ln_i)
        self.mApb.write(0x0006015c, 0x00000000, ln_i)
        self.mApb.write(0x00060160, 0x00000000, ln_i)
        self.mApb.write(0x00060164, 0x00000000, ln_i)
        self.mApb.write(0x00060168, 0x00000000, ln_i)
        self.mApb.write(0x0006016c, 0x000006ff, ln_i)
        self.mApb.write(0x00060170, 0x00000000, ln_i)
        self.mApb.write(0x00060174, 0x00008220, ln_i)
        self.mApb.write(0x00060178, 0x0000ffff, ln_i)
        self.mApb.write(0x0006017c, 0x00000000, ln_i)
        self.mApb.write(0x00060180, 0x0000ffff, ln_i)
        self.mApb.write(0x00060184, 0x00000000, ln_i)
        self.mApb.write(0x00060188, 0x00000000, ln_i)
        self.mApb.write(0x0006018c, 0x00000383, ln_i)
        self.mApb.write(0x00060190, 0x00000000, ln_i)
        self.mApb.write(0x00060194, 0x0000f464, ln_i)
        self.mApb.write(0x00060198, 0x00001012, ln_i)
        self.mApb.write(0x000601a0, 0x00000010, ln_i)
        self.mApb.write(0x000601a4, 0x00000021, ln_i)
        self.mApb.write(0x000601a8, 0x00001000, ln_i)
        self.mApb.write(0x000601ac, 0x00000427, ln_i)
        self.mApb.write(0x000601b0, 0x0000ffff, ln_i)
        self.mApb.write(0x000601bc, 0x0000017d, ln_i)
        self.mApb.write(0x000601c0, 0x00000b7d, ln_i)
        self.mApb.write(0x000601c4, 0x00000010, ln_i)
        self.mApb.write(0x000601c8, 0x00002710, ln_i)
        self.mApb.write(0x000601cc, 0x000001fe, ln_i)
        self.mApb.write(0x000601d0, 0x00000082, ln_i)
        self.mApb.write(0x000601d4, 0x0000FFFF, ln_i)
        self.mApb.write(0x000601d8, 0x00000400, ln_i)
        self.mApb.write(0x000601dc, 0x00000000, ln_i)
        self.mApb.write(0x000601e0, 0x00000000, ln_i)
        self.mApb.write(0x000601e4, 0x00000020, ln_i)
        self.mApb.write(0x000601e8, 0x00000020, ln_i)
        self.mApb.write(0x000601ec, 0x00000000, ln_i)
        self.mApb.write(0x000601f0, 0x0000007f, ln_i)
        self.mApb.write(0x000601f4, 0x00000081, ln_i)
        self.mApb.write(0x000601f8, 0x00000efb, ln_i)
        self.mApb.write(0x00060200, 256 - 30, ln_i)
        self.mApb.write(0x00060204, 0x00000003, ln_i)
        self.mApb.write(0x00060208, 0x00000190, ln_i)
        self.mApb.write(0x00060400, 0x00000004, ln_i)
        self.mApb.write(0x00060500, 0x00008608, ln_i)
        self.mApb.write(0x00060504, 0x00000031, ln_i)
        self.mApb.write(0x00060508, 0x00000020, ln_i)
        self.mApb.write(0x0006050c, 0x00001000, ln_i)
        self.mApb.write(0x00060510, 0x00000000, ln_i)
        self.mApb.write(0x00060518, 0x00000400, ln_i)
        self.mApb.write(0x0006051c, 0x00000000, ln_i)
        self.mApb.write(0x00060520, 0x00008000, ln_i)
        self.mApb.write(0x00060524, 0x0000000f, ln_i)
        self.mApb.write(0x00060528, 0x00000400, ln_i)
        self.mApb.write(0x0006052c, 0x00000000, ln_i)
        self.mApb.write(0x00060530, 0x0000ffff, ln_i)
        self.mApb.write(0x00060534, 0x0000000f, ln_i)
        self.mApb.write(0x00060538, 0x00000000, ln_i)
        self.mApb.write(0x0006053c, 0x00000000, ln_i)

        self.mApb.write(0x00060540, 0x00000001, ln_i)
        self.mApb.write(0x00060544, 0x00000007, ln_i)
        self.mApb.write(0x00060548, 0x00000078, ln_i)
        self.mApb.write(0x00060550, 0x0000000e, ln_i)
        self.mApb.write(0x00060554, 0x0000000e, ln_i)
        self.mApb.write(0x00060558, 0x0000000d, ln_i)
        self.mApb.write(0x0006055c, 0x00000006, ln_i)
        self.mApb.write(0x00060560, 0x00000003, ln_i)
        self.mApb.write(0x00060564, 0x00000002, ln_i)
        self.mApb.write(0x00060568, 0x00000001, ln_i)
        self.mApb.write(0x0006056c, 0x00000000, ln_i)
        self.mApb.write(0x00060590, 0x00000f00, ln_i)
        self.mApb.write(0x000609b0, 0x00000400, ln_i)
        self.mApb.write(0x000609b4, 0x00000002, ln_i)
        self.mApb.write(0x00061000, 0x000001d8, ln_i)
        self.mApb.write(0x00061004, 0x00000000, ln_i)
        self.mApb.write(0x00061008, 0x00000000, ln_i)
        self.mApb.write(0x00061018, 0x00007017, ln_i)
        self.mApb.write(0x0006101c, 0x00000000, ln_i)
        self.mApb.write(0x00061020, 0x00000000, ln_i)
        self.mApb.write(0x00061024, 0x00000000, ln_i)
        self.mApb.write(0x00062000, 0x00000000, ln_i)
        self.mApb.write(0x00062004, 0x00000000, ln_i)
        self.mApb.write(0x00062008, 0x00000000, ln_i)
        self.mApb.write(0x0006200c, 0x00000000, ln_i)
        self.mApb.write(0x00062010, 0x00000000, ln_i)
        self.mApb.write(0x00062014, 0x00000000, ln_i)
        self.mApb.write(0x00062018, 0x00000000, ln_i)
        self.mApb.write(0x0006201c, 0x00000000, ln_i)
        self.mApb.write(0x00062020, 0x00000000, ln_i)
        self.mApb.write(0x00062024, 0x00000000, ln_i)
        self.mApb.write(0x00062028, 0x00000000, ln_i)
        self.mApb.write(0x0006202c, 0x00000000, ln_i)
        self.mApb.write(0x00062030, 0x00000000, ln_i)
        self.mApb.write(0x00062034, 0x00000000, ln_i)
        self.mApb.write(0x00062038, 0x00000000, ln_i)
        self.mApb.write(0x0006203c, 0x00000000, ln_i)
        self.mApb.write(0x00062040, 0x00000000, ln_i)
        self.mApb.write(0x00062044, 0x00000000, ln_i)
        self.mApb.write(0x00062048, 0x00000000, ln_i)
        self.mApb.write(0x0006204c, 0x00000000, ln_i)
        self.mApb.write(0x00062050, 0x00000000, ln_i)
        self.mApb.write(0x00062054, 0x00000000, ln_i)
        self.mApb.write(0x00062058, 0x00000000, ln_i)
        self.mApb.write(0x0006205c, 0x00000000, ln_i)
        self.mApb.write(0x00062060, 0x00000000, ln_i)
        self.mApb.write(0x00062064, 0x00000000, ln_i)
        self.mApb.write(0x00062068, 0x00000000, ln_i)
        self.mApb.write(0x0006206c, 0x00000000, ln_i)
        self.mApb.write(0x00062070, 0x00000000, ln_i)
        self.mApb.write(0x00062074, 0x00000000, ln_i)
        self.mApb.write(0x00062078, 0x00000000, ln_i)
        self.mApb.write(0x0006207c, 0x00000000, ln_i)
        self.mApb.write(0x00062080, 0x00000000, ln_i)
        self.mApb.write(0x00062084, 0x00000000, ln_i)
        self.mApb.write(0x00062088, 0x00000000, ln_i)
        self.mApb.write(0x0006208c, 0x00000000, ln_i)
        self.mApb.write(0x00062090, 0x00000000, ln_i)
        self.mApb.write(0x00062224, 0x00000000, ln_i)
        self.mApb.write(0x00062248, 0x00000004, ln_i)
        self.mApb.write(0x00063300, 0x0000ffff, ln_i)
        self.mApb.write(0x00063304, 0x0000ffff, ln_i)
        self.mApb.write(0x00063308, 0x00000010, ln_i)
        self.mApb.write(0x0006330c, 0x00000fff, ln_i)
        self.mApb.write(0x00063430, 0x00000040, ln_i)
        self.mApb.write(0x00063434, 0x00000040, ln_i)
        self.mApb.write(0x00063438, 0x00000040, ln_i)
        self.mApb.write(0x0006343c, 0x00000040, ln_i)
        self.mApb.write(0x00063440, 0x00000040, ln_i)
        self.mApb.write(0x00063444, 0x00000040, ln_i)
        self.mApb.write(0x00063448, 0x00000040, ln_i)
        self.mApb.write(0x0006344c, 0x00000040, ln_i)
        self.mApb.write(0x00063450, 0x0000000b, ln_i)
        self.mApb.write(0x00063454, 0x00005590, ln_i)

        self.mApb.write(0x00063458, 0x00000064, ln_i)
        self.mApb.write(0x0006345c, 0x0000ff00, ln_i)
        self.mApb.write(0x00063460, 0x000000c8, ln_i)
        self.mApb.write(0x00063464, 0x00000000, ln_i)
        self.mApb.write(0x00063468, 0x00000100, ln_i)
        self.mApb.write(0x0006346c, 0x00000060, ln_i)
        self.mApb.write(0x00063470, 0x00000000, ln_i)
        self.mApb.write(0x00063474, 0x000060ff, ln_i)
        self.mApb.write(0x00063478, 0x00000080, ln_i)
        self.mApb.write(0x0006347c, 0x00009000, ln_i)
        self.mApb.write(0x00063480, 0x00000000, ln_i)
        self.mApb.write(0x00063484, 0x00000000, ln_i)
        self.mApb.write(0x00063488, 0x00000000, ln_i)
        self.mApb.write(0x0006348c, 0x00000000, ln_i)
        self.mApb.write(0x00063490, 0x00000000, ln_i)
        self.mApb.write(0x00063494, 0x00000000, ln_i)
        self.mApb.write(0x00063498, 0x00000000, ln_i)
        self.mApb.write(0x0006349c, 0x00000000, ln_i)
        self.mApb.write(0x000634a0, 0x00000000, ln_i)
        self.mApb.write(0x000634a4, 0x00000000, ln_i)
        self.mApb.write(0x000634a8, 0x00000000, ln_i)
        self.mApb.write(0x000634ac, 0x00000000, ln_i)
        self.mApb.write(0x000634b0, 0x00000000, ln_i)
        self.mApb.write(0x000634b4, 0x00000000, ln_i)
        self.mApb.write(0x000634b8, 0x00000000, ln_i)
        self.mApb.write(0x000634bc, 0x00000000, ln_i)
        self.mApb.write(0x000634c0, 0x00000000, ln_i)
        self.mApb.write(0x000634c4, 0x00000000, ln_i)
        self.mApb.write(0x000634c8, 0x00000000, ln_i)
        self.mApb.write(0x000634cc, 0x00000000, ln_i)
        self.mApb.write(0x000634d0, 0x00000000, ln_i)
        self.mApb.write(0x000634d4, 0x00000000, ln_i)
        self.mApb.write(0x000634d8, 0x00000000, ln_i)
        self.mApb.write(0x000634dc, 0x00000000, ln_i)
        self.mApb.write(0x000634e0, 0x00000000, ln_i)
        self.mApb.write(0x000634e4, 0x00000000, ln_i)
        self.mApb.write(0x000634e8, 0x00000000, ln_i)
        self.mApb.write(0x000634ec, 0x00000000, ln_i)
        self.mApb.write(0x000634f0, 0x00000000, ln_i)
        self.mApb.write(0x000634f4, 0x00000000, ln_i)
        self.mApb.write(0x000634f8, 0x00000000, ln_i)
        self.mApb.write(0x000634fc, 0x00000000, ln_i)
        self.mApb.write(0x00063500, 0x00000000, ln_i)
        self.mApb.write(0x00063504, 0x00000000, ln_i)
        self.mApb.write(0x00063508, 0x00000101, ln_i)
        self.mApb.write(0x0006350c, 0x00000000, ln_i)
        self.mApb.write(0x00063510, 0x00000000, ln_i)
        self.mApb.write(0x00063514, 0x00000000, ln_i)
        self.mApb.write(0x00063518, 0x00000000, ln_i)
        self.mApb.write(0x0006351c, 0x00000000, ln_i)
        self.mApb.write(0x00063520, 0x00000000, ln_i)
        self.mApb.write(0x00063524, 0x00000000, ln_i)
        self.mApb.write(0x00063528, 0x00000000, ln_i)
        self.mApb.write(0x0006352c, 0x00000000, ln_i)
        self.mApb.write(0x00063530, 0x00000000, ln_i)
        self.mApb.write(0x00063534, 0x00000000, ln_i)
        self.mApb.write(0x00063538, 0x00000000, ln_i)
        self.mApb.write(0x0006353c, 0x00000000, ln_i)
        self.mApb.write(0x00063540, 0x00000000, ln_i)
        self.mApb.write(0x00063544, 0x00000000, ln_i)
        self.mApb.write(0x00063548, 0x00000000, ln_i)
        self.mApb.write(0x0006354c, 0x00000000, ln_i)
        self.mApb.write(0x00063550, 0x00000000, ln_i)
        self.mApb.write(0x00063554, 0x00000000, ln_i)
        self.mApb.write(0x00063558, 0x00000000, ln_i)
        self.mApb.write(0x0006355c, 0x00000000, ln_i)
        self.mApb.write(0x00063560, 0x00000000, ln_i)
        self.mApb.write(0x00063564, 0x00000000, ln_i)
        self.mApb.write(0x00063568, 0x00000000, ln_i)
        self.mApb.write(0x0006356c, 0x00000000, ln_i)
        self.mApb.write(0x00063570, 0x00000000, ln_i)
        self.mApb.write(0x00063574, 0x00000000, ln_i)
        self.mApb.write(0x00063578, 0x00000000, ln_i)
        self.mApb.write(0x0006357c, 0x00000000, ln_i)
        self.mApb.write(0x00063580, 0x00000000, ln_i)
        self.mApb.write(0x00063584, 0x00000000, ln_i)
        self.mApb.write(0x00063588, 0x00000000, ln_i)
        self.mApb.write(0x0006358c, 0x00000000, ln_i)
        self.mApb.write(0x000640a8, 0x00000000, ln_i)
        self.mApb.write(0x000640ac, 0x00000000, ln_i)
        self.mApb.write(0x000640b0, 0x00000000, ln_i)
        self.mApb.write(0x000640b4, 0x00000000, ln_i)
        self.mApb.write(0x0006420c, 0x00000018, ln_i)
        self.mApb.write(0x00064210, 0x00003333, ln_i)
        self.mApb.write(0x00064214, 0x00003333, ln_i)
        self.mApb.write(0x00064218, 0x00000000, ln_i)
        self.mApb.write(0x0006421c, 0x00000000, ln_i)
        self.mApb.write(0x00064224, 0x00000005, ln_i)
        self.mApb.write(0x00064300, 0x000004f7, ln_i)
        self.mApb.write(0x00064304, 0x00001000, ln_i)
        self.mApb.write(0x00064308, 0x00000005, ln_i)
        self.mApb.write(0x0006430c, 0x00000050, ln_i)
        self.mApb.write(0x00064310, 0x00000050, ln_i)
        self.mApb.write(0x00064314, 0x00000050, ln_i)
        self.mApb.write(0x00064318, 0x00000050, ln_i)
        self.mApb.write(0x00064320, 0x00000010, ln_i)
        self.mApb.write(0x00064324, 0x00000010, ln_i)
        self.mApb.write(0x00064328, 0x00000010, ln_i)
        self.mApb.write(0x0006432c, 0x00000010, ln_i)

    def WriteCmnVector(self):
        self.func_record['WriteCmnVector'] += 1
        self.mApb.write(0x00000000, 0x00000431)
        self.mApb.write(0x00000004, 0x00000024)
        self.mApb.write(0x00000008, 0x00000800)
        self.mApb.write(0x00000010, 0x000000a9)
        self.mApb.write(0x00000014, 0x00000005)
        self.mApb.write(0x00000018, 0x00000000)
        self.mApb.write(0x00000020, 0x00000001)
        self.mApb.write(0x00000028, 0x00000200)
        self.mApb.write(0x00000030, 0x000014FC)
        self.mApb.write(0x00000038, 0x00000000)
        self.mApb.write(0x00000048, 0x00000000)
        self.mApb.write(0x0000004c, 0x00002743)
        self.mApb.write(0x00000050, 0x00000f08)
        self.mApb.write(0x00000054, 0x00000000)
        self.mApb.write(0x00000058, 0x00000000)
        self.mApb.write(0x0000005c, 0x00000000)
        self.mApb.write(0x00000060, 0x00000000)
        self.mApb.write(0x00000064, 0x00000010)
        self.mApb.write(0x00000068, 0x000000ff)
        self.mApb.write(0x0000006c, 0x00000800)
        self.mApb.write(0x00000070, 0x00000800)
        self.mApb.write(0x00000074, 0x000000ff)
        self.mApb.write(0x00000078, 0x0000ffff)
        self.mApb.write(0x0000007c, 0x0000ffff)
        self.mApb.write(0x00000080, 0x0000002c)
        self.mApb.write(0x00000084, 0x00000000)
        self.mApb.write(0x0000008c, 0x00000000)
        self.mApb.write(0x000000a0, 0x00000000)
        self.mApb.write(0x000000a4, 0x00000000)
        self.mApb.write(0x000000a8, 0x00000000)
        self.mApb.write(0x000000ac, 0x00000000)
        self.mApb.write(0x000000b0, 0x00000000)
        self.mApb.write(0x000000b4, 0x00000000)
        self.mApb.write(0x000000b8, 0x00000000)
        self.mApb.write(0x000000d4, 0x0000000a)
        self.mApb.write(0x000000d8, 0x0000001a)
        self.mApb.write(0x000000dc, 0x00005252)
        self.mApb.write(0x000000e0, 0x00000000)
        self.mApb.write(0x000000e4, 0x00000004)
        self.mApb.write(0x000000e8, 0x00000201)
        self.mApb.write(0x000000ec, 0x00000040)
        self.mApb.write(0x000000f0, 0x00000000)
        self.mApb.write(0x000000f8, 0x00000342)
        self.mApb.write(0x00000100, 0x00000a66)
        self.mApb.write(0x00000104, 0x00000020)
        self.mApb.write(0x00000108, 0x000000c0)
        self.mApb.write(0x0000010c, 0x00000107)
        self.mApb.write(0x00000110, 0x00000000)
        self.mApb.write(0x00000114, 0x00000102)
        self.mApb.write(0x00000118, 0x00000759)
        self.mApb.write(0x0000011c, 0x00000000)
        self.mApb.write(0x00000120, 0x00000000)
        self.mApb.write(0x00000124, 0x000003c8)
        self.mApb.write(0x00000128, 0x00000001)
        self.mApb.write(0x0000012c, 0x000001a0)
        self.mApb.write(0x00000130, 0x00000111)
        self.mApb.write(0x00000134, 0x000000b0)
        self.mApb.write(0x00000138, 0x00000041)
        self.mApb.write(0x0000013c, 0x00001034)
        self.mApb.write(0x00000140, 0x00001034)
        self.mApb.write(0x00000144, 0x00000000)
        self.mApb.write(0x00000148, 0x0000036c)
        self.mApb.write(0x0000014c, 0x0000000c)
        self.mApb.write(0x00000300, 0x00000003)
        self.mApb.write(0x00000304, 0x0000000a)
        self.mApb.write(0x00000ffc, 0x00002001)
        if self.mCfg.data_rate == 10.3125:
            self.mApb.write(0x000000dc, 0x00004242)
            self.mApb.write(0x000000e4, 0x00000000)
            self.mApb.write(0x00000138, 0x00000001)
        if self.mCfg.data_rate == 53.125:
            self.mApb.write(0x000000dc, 0x00005555)
            self.mApb.write(0x000000e4, 0x00000000)
        if self.mCfg.data_rate == 56.25:
            self.mApb.write(0x000000dc, 0x00005a5a)
            self.mApb.write(0x000000e4, 0x00000000)

    def phyEqC1Forcing(self, forcingC1, ln_i=0):
        self.func_record['phyEqC1Forcing'] += 1
        if (forcingC1 == 0):
            self.mApb.write(0x00060130, 0x100, ln_i)
        else:
            self.mApb.write(0x00060130, 0x100 + 256 - forcingC1, ln_i)
        self.mApb.write(0x00061FF8, 0x4, ln_i)
        return 0

    def phyEqCpre1Forcing(self, forcingC1, ln_i=0):
        self.func_record['phyEqCpre1Forcing'] += 1
        if (forcingC1 == 0):
            self.mApb.write(0x00060120, 0x100, ln_i)
        else:
            self.mApb.write(0x00060120, 0x100 + 256 - forcingC1, ln_i)
        self.mApb.write(0x00061FF8, 0x4, ln_i)
        return 0

    def phyEqOff(self, forcingC1, ln_i=0):
        self.func_record['phyEqOff'] += 1
        startMemAdd = 0x00060120
        if self.mCfg.data_rate == 25.78125:
            for i in range(10):
                memAdd = startMemAdd + i * 8
                self.mApb.write(memAdd, 0x100, ln_i)

        self.mApb.write(0x00060130, 0x100 + 256 - forcingC1, ln_i)
        self.mApb.write(0x00061FF8, 0x4, ln_i)
        return 0

    def phyEqOff4to8(self, ln_i=0):
        self.func_record['phyEqOff4to8'] += 1
        startMemAdd = 0x00060150

        for i in range(4):
            memAdd = startMemAdd + i * 8
            self.mApb.write(memAdd, 0x100, ln_i)

        self.mApb.write(0x00061FF8, 0x4, ln_i)
        return 0

    def txSlbBistEn(self, ln_i=0):
        self.func_record['txSlbBistEn'] += 1
        self.mApb.write(0x00050118, 0x0000F0F0, ln_i)
        self.mApb.write(0x0005011C, 0x0000F0F0, ln_i)
        if self.mCfg.data_rate == 53.125:
            self.mApb.write(0x00050104, 0x00000225, ln_i)
        else:
            self.mApb.write(0x00050104, 0x00000205, ln_i)
        self.mApb.write(0x00050000, 1 << 0, ln_i, 1 << 0)
        self.mApb.write(0x00050004, 0 << 0, ln_i, 1 << 0)
        self.mApb.write(0x00050024, 1 << 0, ln_i, 1 << 0)

    def txElbBistEn(self, ln_i=0):
        self.func_record['txElbBistEn'] += 1
        if self.mCfg.data_rate == 53.125:
            self.mApb.write(0x00050104, 0x00000225, ln_i)
        else:
            self.mApb.write(0x00050104, 0x00000205, ln_i)
        self.mApb.write(0x00050000, 0 << 0, ln_i, 1 << 0)
        self.mApb.write(0x00050024, 0x00000000, ln_i)

    def rxSlbBistEn(self, ln_i=0):
        self.func_record['rxSlbBistEn'] += 1
        if self.mCfg.data_rate == 53.125:
            self.mApb.write(0x00060174, 0x00008225, ln_i)
        else:
            self.mApb.write(0x00060174, 0x00008205, ln_i)
        self.mApb.write(0x00060060, 0x00000053, ln_i)

    def rxElbBistEn(self, ln_i=0):
        self.func_record['rxElbBistEn'] += 1
        if self.mCfg.data_rate == 53.125:
            self.mApb.write(0x00060174, 0x00008225, ln_i)
        else:
            self.mApb.write(0x00060174, 0x00008205, ln_i)
        self.mApb.write(0x00060060, 0x00000052, ln_i)

    def txRemoteLbEn(self, ln_i=0):
        self.func_record['txRemoteLbEn'] += 1
        data = 0
        if self.mCfg.data_rate == 10.3125:
            self.mApb.write(0x00050100, data | 0x0040, ln_i)
            self.mApb.write(0x00050100, data | 0x0051, ln_i)
        else:
            self.mApb.write(0x00050100, data | 0x0010, ln_i)
            self.mApb.write(0x00050100, data | 0x0011, ln_i)

    def PCS_loopback(self):
        self.func_record['PCS_loopback'] += 1
        if self.mCfg.data_rate == 53.125:
            self.PCS_200gx1_loopback()
        elif self.mCfg.data_rate == 25.78125:
            self.PCS_100gx1_loopback()
        else:
            self.PCS_40gx1_loopback()

    def PCS_200gx1_loopback(self):
        self.func_record['PCS_200gx1_loopback'] += 1
        local_loopback = False
        phy_local_loopback_en = False

        self.WriteElbVector_pcs_lb()
        print("[gbe_200g_pcs_test begin]")

        if (phy_local_loopback_en):
            for i in range(4):
                self.mApb.write(0x00200000 + i * 0x40000 + 0x04, 1 << 5 | 1 << 3)

        self.gbe_1x200g_pcs_config()

        for ln_i in range(4):
            if self.is_lane_enabled(ln_i):
                self.mApb.write(0x00200000 + 0x0, 0x124, ln_i)
                if (local_loopback):
                    self.mApb.write(0x00200000 + 0x4, 0x28, ln_i)
                else:
                    self.mApb.write(0x00200000 + 0x4, 0x08, ln_i)

                self.mApb.write(0x00210000 + 0x0, 0x84, ln_i)
                self.mApb.write(0x00050100, 0x00000000, ln_i)
                self.mApb.write(0x00050080, 0x00000008, ln_i)
                self.mApb.write(0x00050084, 0x00000010, ln_i)
                self.mApb.write(0x00060088, 0x00000028, ln_i)
                self.mApb.write(0x0006008c, 0x00000010, ln_i)
                self.mApb.write(0x00200000 + 0x8, 0x66F | 1 << 8, ln_i)
        Delay(200)
        self.mApb.write(0x24010024, 0xf08040 | 1 << 24)
        Delay(200)
        data = self.mApb.read(0x2408001c)
        if ((data & 0xf) == 0xC):
            print("select 200G Base-R PCS type")
        else:
            print("select 400G Base-R PCS type")

        print("test results check")
        data = self.mApb.read(0x24080000 + 0x04)
        if ((data & 0x4) >> 2 == 1):
            print("pcs link pass")
        else:
            print("pcs link fail")

        data = self.mApb.read(0x240800c8)
        if ((data & 0x1000) >> 12 == 1):
            print("all receive lanes locked and aligned")

        print("Corrected codeword low %d" % (self.mApb.read(0x24040008)))
        print("Uncorrected codeword low %d" % (self.mApb.read(0x24040010)))
        print("Lane 0 to 7 alignment marker lock %d" % (self.mApb.read(0x240800d0)))
        print("[7:0] : Erroed blocks counter %d" % (self.mApb.read(0x24080084)))
        # self.mApb.read(0x24010080)
        print("[gbe_200g_pcs_test done]")

        while (False):
            data = self.mApb.read(0x24040010)
            if (data > 0):
                print("[gbe_200g_pcs_test] FAIL")
                break
            else:
                print("[gbe_200g_pcs_test] PASS ")
            Delay(10000)

    def gbe_1x200g_pcs_config(self):
        self.func_record['gbe_1x200g_pcs_config'] += 1
        self.mApb.write(0x24010020, 0xff)
        self.mApb.write(0x24010030, 1)
        self.mApb.write(0x24010034, 0xfff0)
        self.mApb.write(0x24010038, 0)
        self.mApb.write(0x2401003c, 0)
        self.mApb.write(0x24010040, 0)
        self.mApb.write(0x24010004, 0x0)
        self.mApb.write(0x24040000, 0x100)
        self.mApb.write(0x24040020, 0x100)
        self.mApb.write(0x24040040, 0x100)
        self.mApb.write(0x24040060, 0x100)
        self.mApb.write(0x24040180, 0xc0b3)
        self.mApb.write(0x24040184, 0x008c)
        self.mApb.write(0x240A0008, 0x1000)
        self.mApb.write(0x24080000, 0x2064 | 1 << 15)

    def PCS_100gx1_loopback(self):
        self.func_record['PCS_100gx1_loopback'] += 1
        self.WriteElbVector()
        print("[gbe_100g_pcs_test begin]")
        self.mApb.write(0x00000300, 0x00000003)
        self.gbe_1x100g_pcs_config()
        if (True):
            for ln_i in range(4):
                if self.is_lane_enabled(ln_i):
                    self.mApb.write(0x00200000 + 0x0, 0x120, ln_i)
                    self.mApb.write(0x00200000 + 0x4, 0x08, ln_i)
                    self.mApb.write(0x00200000 + 0x8, 0x66F | 1 << 8, ln_i)
                    self.mApb.write(0x00210000 + 0x0, 0x80, ln_i)
                    self.mApb.write(0x00050084, 0x00000000, ln_i)
                    self.mApb.write(0x00050080, 0x00000000, ln_i)
                    self.mApb.write(0x00050100, 0x00000000, ln_i)
                    self.mApb.write(0x0006008c, 0x00000000, ln_i)
                    self.mApb.write(0x00060088, 0x00000000, ln_i)
        self.mApb.write(0x24010028, 0x483018 | 1 << 24)
        self.mApb.write(0x240c0000 + 0x0, 0x2040 | 1 << 15)
        Delay(2000)
        print("pcs stautus check")
        data = self.mApb.read(0x240c0004)
        if ((data & 0x4) >> 2 == 1):
            print("pcs link pass")
        else:
            print("pcs link fail")
        data = self.mApb.read(0x240c00c8)
        if ((data & 0x1000) >> 12 == 1):
            print("xpcs all receive lanes locked and aligned")
        print("[gbe_1x100g_pcs_test done]")

    def gbe_1x100g_pcs_config(self):
        self.func_record['gbe_1x100g_pcs_config'] += 1
        self.mApb.write(0x24010020, 0xff)
        self.mApb.write(0x24010030, 0x0)
        self.mApb.write(0x24010034, 0 | 0 << 4 | 0 << 8 | 0xf << 12 | 0 << 16)
        self.mApb.write(0x24010038, 0 | 0 << 4 | 0 << 8 | 1 << 10 | 0 << 12)
        self.mApb.write(0x2401003C, 0 | 0 << 4)
        self.mApb.write(0x24010040, 0 | 0 << 4)
        self.mApb.write(0x24010004, 0x0)

    def gbe_1x25g_pcs_config(self):
        self.func_record['gbe_1x25g_pcs_config'] += 1
        self.mApb.write(0x24010020, 0x11)
        self.mApb.write(0x24010030, 0x0)
        self.mApb.write(0x24010034, 0 | 0 << 4 | 0 << 8 | 0x0 << 12 | 0 << 16)
        self.mApb.write(0x24010038, 0 | 0 << 4 | 0 << 8 | 0 << 10 | 0 << 12)
        self.mApb.write(0x2401003C, 0 | 0 << 4)
        self.mApb.write(0x24010040, 0 | 0 << 4)
        self.mApb.write(0x24010004, 0x0)

    def PCS_25gx1_loopback(self):
        self.func_record['PCS_25gx1_loopback'] += 1
        self.WriteElbVector()
        print("[gbe_25g_pcs_test begin]")
        self.mApb.write(0x00000300, 0x00000003)
        self.gbe_1x25g_pcs_config()
        if (True):
            for ln_i in range(4):
                if self.is_lane_enabled(ln_i):
                    self.mApb.write(0x00200000 + 0x0, 0x120, ln_i)
                    self.mApb.write(0x00200000 + 0x4, 0x08, ln_i)
                    self.mApb.write(0x00200000 + 0x8, 0x66F | 1 << 8, ln_i)
                    self.mApb.write(0x00210000 + 0x0, 0x80, ln_i)
                    self.mApb.write(0x00050084, 0x00000000, ln_i)
                    self.mApb.write(0x00050080, 0x00000000, ln_i)
                    self.mApb.write(0x00050100, 0x00000000, ln_i)
                    self.mApb.write(0x0006008c, 0x00000000, ln_i)
                    self.mApb.write(0x00060088, 0x00000000, ln_i)
        self.mApb.write(0x24010028, 0x483018 | 1 << 24)
        self.mApb.write(0x240c0000 + 0x0, 0x2040 | 1 << 15)
        Delay(2000)
        print("pcs stautus check")
        data = self.mApb.read(0x240c0004)
        if ((data & 0x4) >> 2 == 1):
            print("pcs link pass")
        else:
            print("pcs link fail")
        data = self.mApb.read(0x240c00c8)
        if ((data & 0x1000) >> 12 == 1):
            print("xpcs all receive lanes locked and aligned")
        print("[gbe_1x25g_pcs_test done]")

    def PCS_40gx1_loopback(self):
        self.func_record['PCS_40gx1_loopback'] += 1
        print("[gbe_40g_pcs_test begin]")
        self.mApb.write(0x00000300, 0x00000001)
        self.gbe_1x40g_pcs_config()
        if (True):
            for ln_i in range(4):
                if self.is_lane_enabled(ln_i):
                    self.mApb.write(0x00200000 + 0x0, 0x128, ln_i)
                    self.mApb.write(0x00200000 + 0x4, 0x08, ln_i)
                    self.mApb.write(0x00200000 + 0x8, 0x66F | 1 << 8, ln_i)
                    self.mApb.write(0x00210000 + 0x0, 0x88, ln_i)
                    self.mApb.write(0x00050084, 0x00000000, ln_i)
                    self.mApb.write(0x00050080, 0x00000008, ln_i)
                    self.mApb.write(0x00050100, 0x00000000, ln_i)
                    self.mApb.write(0x0006008c, 0x00000000, ln_i)
                    self.mApb.write(0x00060088, 0x00000008, ln_i)
        self.mApb.write(0x240c0000 + 0x0, 0x2040 | 1 << 15)
        Delay(2000)
        print("pcs stautus check")
        data = self.mApb.read(0x240c0004)
        if ((data & 0x4) >> 2 == 1):
            print("pcs link pass")
        else:
            print("pcs link fail")
        data = self.mApb.read(0x240c00c8)
        if ((data & 0x1000) >> 12 == 1):
            print("xpcs all receive lanes locked and aligned")
        print("[gbe_1x40g_pcs_test done]")
        self.mApb.read(0x24010038)
        self.mApb.read(0x240c0000)
        self.mApb.read(0x240c0004)
        self.mApb.read(0x240c001c)

    def gbe_1x40g_pcs_config(self):
        self.func_record['gbe_1x40g_pcs_config'] += 1
        self.mApb.write(0x24010020, 0xff)
        self.mApb.write(0x24010030, 0x0)
        self.mApb.write(0x24010034, 0xf | 0 << 4 | 0 << 8 | 0 << 12 | 0 << 16)
        self.mApb.write(0x24010038, 0x0 | 0x0 << 4 | 0 << 8 | 0 << 10 | 1 << 12)
        self.mApb.write(0x2401003C, 0 | 0 << 4)
        self.mApb.write(0x24010040, 0 | 0 << 4)
        self.mApb.write(0x24010004, 0x0)

    def WriteProtlbVector(self):
        self.func_record['WriteProtlbVector'] += 1
        for ln_i in range(4):
            if self.is_lane_enabled(ln_i):
                self.mApb.write(0x00200004, 0x00000008, ln_i)
                data = self.mApb.read(0x00050104, ln_i)
                if self.mCfg.data_rate == 53.125:
                    self.mApb.write(0x00200000, 0x0000016E, ln_i)
                else:
                    self.mApb.write(0x00200000, 0x0000016A, ln_i)

                self.mApb.read(0x00210900, ln_i)
                self.mApb.write(0x00200100, 0x00000209, ln_i)
                self.mApb.write(0x00050100, 0x00000000, ln_i)
                self.mApb.write(0x00050104, data & 0xfffe, ln_i)

                if self.mCfg.data_rate == 53.125:
                    self.mApb.write(0x00210000, 0x00000084, ln_i)
                else:
                    self.mApb.write(0x00210000, 0x00000080, ln_i)
                self.mApb.write(0x00210200, 0x00004209, ln_i)

        for ln_i in range(4):
            if self.is_lane_enabled(ln_i):
                data = self.mApb.read(0x00210900, ln_i)
                if ((data & 0x2) >> 1 == 1):
                    print("PROT LN%d Bist Error fail" % (ln_i))
                elif ((data & 0x1) == 1):
                    print("PROT LN%d Bist Pass" % (ln_i))
                else:
                    print("PROT LN%d Bist Sync Fail" % (ln_i))

    def DefaultFfeWrite(self, pre2, pre1, post1):
        self.func_record['DefaultFfeWrite'] += 1
        for ln_i in range(4):
            if self.is_lane_enabled(ln_i):
                self.mApb.write(0x0005063C, 0x1FC0, ln_i)
                self.mApb.write(0x00050640, 0x1FC0, ln_i)
                self.mApb.write(0x00050644, 0x1FC0, ln_i)
                self.mApb.write(0x00050648, 0x1FC0, ln_i)
                self.mApb.write(0x0005064C, 0x01FF, ln_i)
                self.mApb.write(0x00050654, 0x01FF, ln_i)
                self.mApb.write(0x0005065C, 0x01FF, ln_i)
                self.mApb.write(0x00050664, 0x01FF, ln_i)

                self.mApb.write(0x00050014, 1 << 0, ln_i, 1 << 0)
                self.mApb.write(0x00050080, 1 << 4, ln_i, 1 << 4)
                self.mApb.write(0x00050080, 1 << 2, ln_i, 1 << 2)
                self.mApb.write(0x00050084, 1 << 2, ln_i, 1 << 2)

                self.mApb.write(0x0005061C, 0x0182, ln_i)
                self.mApb.write(0x00050620, 0x0086, ln_i)
                self.mApb.write(0x00050624, 0x0182, ln_i)
                self.mApb.write(0x00050628, 0x0086, ln_i)
                self.mApb.write(0x0005062C, 0x0182, ln_i)
                self.mApb.write(0x00050630, 0x0086, ln_i)
                self.mApb.write(0x00050634, 0x0182, ln_i)
                self.mApb.write(0x00050638, 0x0086, ln_i)

                self.mApb.write(0x00050088, 0x1000, ln_i)
                for main_i in range(pre2 + pre1 + post1):
                    self.mApb.write(0x00050088, 0x0010, ln_i)
                    self.mApb.write(0x00050088, 0x0000, ln_i)

                for pre2_i in range(pre2):
                    self.mApb.write(0x00050088, 0x0800, ln_i)
                    self.mApb.write(0x00050088, 0x0000, ln_i)

                for pre1_i in range(pre1):
                    self.mApb.write(0x00050088, 0x0040, ln_i)
                    self.mApb.write(0x00050088, 0x0000, ln_i)

                for post1_i in range(post1):
                    self.mApb.write(0x00050088, 0x0020, ln_i)
                    self.mApb.write(0x00050088, 0x0000, ln_i)

    def TxSineOut(self, freq=3):
        self.func_record['TxSineOut'] += 1
        for ln_i in range(4):
            if self.is_lane_enabled(ln_i):
                self.mApb.write(0x00050014, 1 << 0, ln_i, 1 << 0)
                self.mApb.write(0x00050080, 1 << 4, ln_i, 1 << 4)
                self.mApb.write(0x00050080, 1 << 2, ln_i, 1 << 2)
                self.mApb.write(0x00050084, 1 << 2, ln_i, 1 << 2)
                self.mApb.write(0x00050674, 0x0003, ln_i)
                self.mApb.write(0x00050088, 0x1000, ln_i)

                for i in range(256):
                    if (freq == 3):
                        if (i == 0):
                            self.mApb.write(0x00051000 + i * 4, 0x7f, ln_i)
                        elif (i == 1):
                            self.mApb.write(0x00051000 + i * 4, 0x88, ln_i)
                        elif (i == 2):
                            self.mApb.write(0x00051000 + i * 4, 0x92, ln_i)
                        elif (i == 3):
                            self.mApb.write(0x00051000 + i * 4, 0x9b, ln_i)
                        elif (i == 4):
                            self.mApb.write(0x00051000 + i * 4, 0xa4, ln_i)
                        elif (i == 5):
                            self.mApb.write(0x00051000 + i * 4, 0xad, ln_i)
                        elif (i == 6):
                            self.mApb.write(0x00051000 + i * 4, 0xb5, ln_i)
                        elif (i == 7):
                            self.mApb.write(0x00051000 + i * 4, 0xbe, ln_i)
                        elif (i == 8):
                            self.mApb.write(0x00051000 + i * 4, 0xc6, ln_i)
                        elif (i == 9):
                            self.mApb.write(0x00051000 + i * 4, 0xcd, ln_i)
                        elif (i == 10):
                            self.mApb.write(0x00051000 + i * 4, 0xd5, ln_i)
                        elif (i == 11):
                            self.mApb.write(0x00051000 + i * 4, 0xdb, ln_i)
                        elif (i == 12):
                            self.mApb.write(0x00051000 + i * 4, 0xe1, ln_i)
                        elif (i == 13):
                            self.mApb.write(0x00051000 + i * 4, 0xe7, ln_i)
                        elif (i == 14):
                            self.mApb.write(0x00051000 + i * 4, 0xec, ln_i)
                        elif (i == 15):
                            self.mApb.write(0x00051000 + i * 4, 0xf1, ln_i)
                        elif (i == 16):
                            self.mApb.write(0x00051000 + i * 4, 0xf5, ln_i)
                        elif (i == 17):
                            self.mApb.write(0x00051000 + i * 4, 0xf8, ln_i)
                        elif (i == 18):
                            self.mApb.write(0x00051000 + i * 4, 0xfa, ln_i)
                        elif (i == 19):
                            self.mApb.write(0x00051000 + i * 4, 0xfc, ln_i)
                        elif (i == 20):
                            self.mApb.write(0x00051000 + i * 4, 0xfd, ln_i)
                        elif (i == 21):
                            self.mApb.write(0x00051000 + i * 4, 0xfe, ln_i)
                        elif (i == 22):
                            self.mApb.write(0x00051000 + i * 4, 0xfe, ln_i)
                        elif (i == 23):
                            self.mApb.write(0x00051000 + i * 4, 0xfd, ln_i)
                        elif (i == 24):
                            self.mApb.write(0x00051000 + i * 4, 0xfb, ln_i)
                        elif (i == 25):
                            self.mApb.write(0x00051000 + i * 4, 0xf9, ln_i)
                        elif (i == 26):
                            self.mApb.write(0x00051000 + i * 4, 0xf6, ln_i)
                        elif (i == 27):
                            self.mApb.write(0x00051000 + i * 4, 0xf3, ln_i)
                        elif (i == 28):
                            self.mApb.write(0x00051000 + i * 4, 0xef, ln_i)
                        elif (i == 29):
                            self.mApb.write(0x00051000 + i * 4, 0xea, ln_i)
                        elif (i == 30):
                            self.mApb.write(0x00051000 + i * 4, 0xe4, ln_i)
                        elif (i == 31):
                            self.mApb.write(0x00051000 + i * 4, 0xde, ln_i)
                        elif (i == 32):
                            self.mApb.write(0x00051000 + i * 4, 0xd8, ln_i)
                        elif (i == 33):
                            self.mApb.write(0x00051000 + i * 4, 0xd1, ln_i)
                        elif (i == 34):
                            self.mApb.write(0x00051000 + i * 4, 0xca, ln_i)
                        elif (i == 35):
                            self.mApb.write(0x00051000 + i * 4, 0xc2, ln_i)
                        elif (i == 36):
                            self.mApb.write(0x00051000 + i * 4, 0xba, ln_i)
                        elif (i == 37):
                            self.mApb.write(0x00051000 + i * 4, 0xb1, ln_i)
                        elif (i == 38):
                            self.mApb.write(0x00051000 + i * 4, 0xa8, ln_i)
                        elif (i == 39):
                            self.mApb.write(0x00051000 + i * 4, 0x9f, ln_i)
                        elif (i == 40):
                            self.mApb.write(0x00051000 + i * 4, 0x96, ln_i)
                        elif (i == 41):
                            self.mApb.write(0x00051000 + i * 4, 0x8d, ln_i)
                        elif (i == 42):
                            self.mApb.write(0x00051000 + i * 4, 0x84, ln_i)
                        elif (i == 43):
                            self.mApb.write(0x00051000 + i * 4, 0x7a, ln_i)
                        elif (i == 44):
                            self.mApb.write(0x00051000 + i * 4, 0x71, ln_i)
                        elif (i == 45):
                            self.mApb.write(0x00051000 + i * 4, 0x68, ln_i)
                        elif (i == 46):
                            self.mApb.write(0x00051000 + i * 4, 0x5f, ln_i)
                        elif (i == 47):
                            self.mApb.write(0x00051000 + i * 4, 0x56, ln_i)
                        elif (i == 48):
                            self.mApb.write(0x00051000 + i * 4, 0x4d, ln_i)
                        elif (i == 49):
                            self.mApb.write(0x00051000 + i * 4, 0x44, ln_i)
                        elif (i == 50):
                            self.mApb.write(0x00051000 + i * 4, 0x3c, ln_i)
                        elif (i == 51):
                            self.mApb.write(0x00051000 + i * 4, 0x34, ln_i)
                        elif (i == 52):
                            self.mApb.write(0x00051000 + i * 4, 0x2d, ln_i)
                        elif (i == 53):
                            self.mApb.write(0x00051000 + i * 4, 0x26, ln_i)
                        elif (i == 54):
                            self.mApb.write(0x00051000 + i * 4, 0x20, ln_i)
                        elif (i == 55):
                            self.mApb.write(0x00051000 + i * 4, 0x1a, ln_i)
                        elif (i == 56):
                            self.mApb.write(0x00051000 + i * 4, 0x14, ln_i)
                        elif (i == 57):
                            self.mApb.write(0x00051000 + i * 4, 0xf, ln_i)
                        elif (i == 58):
                            self.mApb.write(0x00051000 + i * 4, 0xb, ln_i)
                        elif (i == 59):
                            self.mApb.write(0x00051000 + i * 4, 0x8, ln_i)
                        elif (i == 60):
                            self.mApb.write(0x00051000 + i * 4, 0x5, ln_i)
                        elif (i == 61):
                            self.mApb.write(0x00051000 + i * 4, 0x3, ln_i)
                        elif (i == 62):
                            self.mApb.write(0x00051000 + i * 4, 0x1, ln_i)
                        elif (i == 63):
                            self.mApb.write(0x00051000 + i * 4, 0x0, ln_i)
                        elif (i == 64):
                            self.mApb.write(0x00051000 + i * 4, 0x0, ln_i)
                        elif (i == 65):
                            self.mApb.write(0x00051000 + i * 4, 0x1, ln_i)
                        elif (i == 66):
                            self.mApb.write(0x00051000 + i * 4, 0x2, ln_i)
                        elif (i == 67):
                            self.mApb.write(0x00051000 + i * 4, 0x4, ln_i)
                        elif (i == 68):
                            self.mApb.write(0x00051000 + i * 4 + 1, 0x6, ln_i)
                        elif (i == 69):
                            self.mApb.write(0x00051000 + i * 4, 0x9, ln_i)
                        elif (i == 70):
                            self.mApb.write(0x00051000 + i * 4, 0xd, ln_i)
                        elif (i == 71):
                            self.mApb.write(0x00051000 + i * 4, 0x12, ln_i)
                        elif (i == 72):
                            self.mApb.write(0x00051000 + i * 4, 0x17, ln_i)
                        elif (i == 73):
                            self.mApb.write(0x00051000 + i * 4, 0x1d, ln_i)
                        elif (i == 74):
                            self.mApb.write(0x00051000 + i * 4, 0x23, ln_i)
                        elif (i == 75):
                            self.mApb.write(0x00051000 + i * 4, 0x29, ln_i)
                        elif (i == 76):
                            self.mApb.write(0x00051000 + i * 4, 0x31, ln_i)
                        elif (i == 77):
                            self.mApb.write(0x00051000 + i * 4, 0x38, ln_i)
                        elif (i == 78):
                            self.mApb.write(0x00051000 + i * 4, 0x40, ln_i)
                        elif (i == 79):
                            self.mApb.write(0x00051000 + i * 4, 0x49, ln_i)
                        elif (i == 80):
                            self.mApb.write(0x00051000 + i * 4, 0x51, ln_i)
                        elif (i == 81):
                            self.mApb.write(0x00051000 + i * 4, 0x5a, ln_i)
                        elif (i == 82):
                            self.mApb.write(0x00051000 + i * 4, 0x63, ln_i)
                        elif (i == 83):
                            self.mApb.write(0x00051000 + i * 4, 0x6c, ln_i)
                        elif (i == 84):
                            self.mApb.write(0x00051000 + i * 4, 0x76, ln_i)
                        elif (i == 85):
                            self.mApb.write(0x00051000 + i * 4, 0x7f, ln_i)
                        elif (i == 86):
                            self.mApb.write(0x00051000 + i * 4, 0x88, ln_i)
                        elif (i == 87):
                            self.mApb.write(0x00051000 + i * 4, 0x92, ln_i)
                        elif (i == 88):
                            self.mApb.write(0x00051000 + i * 4, 0x9b, ln_i)
                        elif (i == 89):
                            self.mApb.write(0x00051000 + i * 4, 0xa4, ln_i)
                        elif (i == 90):
                            self.mApb.write(0x00051000 + i * 4, 0xad, ln_i)
                        elif (i == 91):
                            self.mApb.write(0x00051000 + i * 4, 0xb5, ln_i)
                        elif (i == 92):
                            self.mApb.write(0x00051000 + i * 4, 0xbe, ln_i)
                        elif (i == 93):
                            self.mApb.write(0x00051000 + i * 4, 0xc6, ln_i)
                        elif (i == 94):
                            self.mApb.write(0x00051000 + i * 4, 0xcd, ln_i)
                        elif (i == 95):
                            self.mApb.write(0x00051000 + i * 4, 0xd5, ln_i)
                        elif (i == 96):
                            self.mApb.write(0x00051000 + i * 4, 0xdb, ln_i)
                        elif (i == 97):
                            self.mApb.write(0x00051000 + i * 4, 0xe1, ln_i)
                        elif (i == 98):
                            self.mApb.write(0x00051000 + i * 4, 0xe7, ln_i)
                        elif (i == 99):
                            self.mApb.write(0x00051000 + i * 4, 0xec, ln_i)
                        elif (i == 100):
                            self.mApb.write(0x00051000 + i * 4, 0xf1, ln_i)
                        elif (i == 101):
                            self.mApb.write(0x00051000 + i * 4, 0xf5, ln_i)
                        elif (i == 102):
                            self.mApb.write(0x00051000 + i * 4, 0xf8, ln_i)
                        elif (i == 103):
                            self.mApb.write(0x00051000 + i * 4, 0xfa, ln_i)
                        elif (i == 104):
                            self.mApb.write(0x00051000 + i * 4, 0xfc, ln_i)
                        elif (i == 105):
                            self.mApb.write(0x00051000 + i * 4, 0xfd, ln_i)
                        elif (i == 106):
                            self.mApb.write(0x00051000 + i * 4, 0xfe, ln_i)
                        elif (i == 107):
                            self.mApb.write(0x00051000 + i * 4, 0xfe, ln_i)
                        elif (i == 108):
                            self.mApb.write(0x00051000 + i * 4, 0xfd, ln_i)
                        elif (i == 109):
                            self.mApb.write(0x00051000 + i * 4, 0xfb, ln_i)
                        elif (i == 110):
                            self.mApb.write(0x00051000 + i * 4, 0xf9, ln_i)
                        elif (i == 111):
                            self.mApb.write(0x00051000 + i * 4, 0xf6, ln_i)
                        elif (i == 112):
                            self.mApb.write(0x00051000 + i * 4, 0xf3, ln_i)
                        elif (i == 113):
                            self.mApb.write(0x00051000 + i * 4, 0xef, ln_i)
                        elif (i == 114):
                            self.mApb.write(0x00051000 + i * 4, 0xea, ln_i)
                        elif (i == 115):
                            self.mApb.write(0x00051000 + i * 4, 0xe4, ln_i)
                        elif (i == 116):
                            self.mApb.write(0x00051000 + i * 4, 0xde, ln_i)
                        elif (i == 117):
                            self.mApb.write(0x00051000 + i * 4, 0xd8, ln_i)
                        elif (i == 118):
                            self.mApb.write(0x00051000 + i * 4, 0xd1, ln_i)
                        elif (i == 119):
                            self.mApb.write(0x00051000 + i * 4, 0xca, ln_i)
                        elif (i == 120):
                            self.mApb.write(0x00051000 + i * 4, 0xc2, ln_i)
                        elif (i == 121):
                            self.mApb.write(0x00051000 + i * 4, 0xba, ln_i)
                        elif (i == 122):
                            self.mApb.write(0x00051000 + i * 4, 0xb1, ln_i)
                        elif (i == 123):
                            self.mApb.write(0x00051000 + i * 4, 0xa8, ln_i)
                        elif (i == 124):
                            self.mApb.write(0x00051000 + i * 4, 0x9f, ln_i)
                        elif (i == 125):
                            self.mApb.write(0x00051000 + i * 4, 0x96, ln_i)
                        elif (i == 126):
                            self.mApb.write(0x00051000 + i * 4, 0x8d, ln_i)
                        elif (i == 127):
                            self.mApb.write(0x00051000 + i * 4, 0x84, ln_i)
                        elif (i == 128):
                            self.mApb.write(0x00051000 + i * 4, 0x7a, ln_i)
                        elif (i == 129):
                            self.mApb.write(0x00051000 + i * 4, 0x71, ln_i)
                        elif (i == 130):
                            self.mApb.write(0x00051000 + i * 4, 0x68, ln_i)
                        elif (i == 131):
                            self.mApb.write(0x00051000 + i * 4, 0x5f, ln_i)
                        elif (i == 132):
                            self.mApb.write(0x00051000 + i * 4 + 2, 0x56, ln_i)
                        elif (i == 133):
                            self.mApb.write(0x00051000 + i * 4, 0x4d, ln_i)
                        elif (i == 134):
                            self.mApb.write(0x00051000 + i * 4, 0x44, ln_i)
                        elif (i == 135):
                            self.mApb.write(0x00051000 + i * 4, 0x3c, ln_i)
                        elif (i == 136):
                            self.mApb.write(0x00051000 + i * 4, 0x34, ln_i)
                        elif (i == 137):
                            self.mApb.write(0x00051000 + i * 4, 0x2d, ln_i)
                        elif (i == 138):
                            self.mApb.write(0x00051000 + i * 4, 0x26, ln_i)
                        elif (i == 139):
                            self.mApb.write(0x00051000 + i * 4, 0x20, ln_i)
                        elif (i == 140):
                            self.mApb.write(0x00051000 + i * 4, 0x1a, ln_i)
                        elif (i == 141):
                            self.mApb.write(0x00051000 + i * 4, 0x14, ln_i)
                        elif (i == 142):
                            self.mApb.write(0x00051000 + i * 4, 0xf, ln_i)
                        elif (i == 143):
                            self.mApb.write(0x00051000 + i * 4, 0xb, ln_i)
                        elif (i == 144):
                            self.mApb.write(0x00051000 + i * 4, 0x8, ln_i)
                        elif (i == 145):
                            self.mApb.write(0x00051000 + i * 4, 0x5, ln_i)
                        elif (i == 146):
                            self.mApb.write(0x00051000 + i * 4, 0x3, ln_i)
                        elif (i == 147):
                            self.mApb.write(0x00051000 + i * 4, 0x1, ln_i)
                        elif (i == 148):
                            self.mApb.write(0x00051000 + i * 4, 0x0, ln_i)
                        elif (i == 149):
                            self.mApb.write(0x00051000 + i * 4, 0x0, ln_i)
                        elif (i == 150):
                            self.mApb.write(0x00051000 + i * 4, 0x1, ln_i)
                        elif (i == 151):
                            self.mApb.write(0x00051000 + i * 4, 0x2, ln_i)
                        elif (i == 152):
                            self.mApb.write(0x00051000 + i * 4, 0x4, ln_i)
                        elif (i == 153):
                            self.mApb.write(0x00051000 + i * 4, 0x6, ln_i)
                        elif (i == 154):
                            self.mApb.write(0x00051000 + i * 4, 0x9, ln_i)
                        elif (i == 155):
                            self.mApb.write(0x00051000 + i * 4, 0xd, ln_i)
                        elif (i == 156):
                            self.mApb.write(0x00051000 + i * 4, 0x12, ln_i)
                        elif (i == 157):
                            self.mApb.write(0x00051000 + i * 4, 0x17, ln_i)
                        elif (i == 158):
                            self.mApb.write(0x00051000 + i * 4, 0x1d, ln_i)
                        elif (i == 159):
                            self.mApb.write(0x00051000 + i * 4, 0x23, ln_i)
                        elif (i == 160):
                            self.mApb.write(0x00051000 + i * 4, 0x29, ln_i)
                        elif (i == 161):
                            self.mApb.write(0x00051000 + i * 4, 0x31, ln_i)
                        elif (i == 162):
                            self.mApb.write(0x00051000 + i * 4, 0x38, ln_i)
                        elif (i == 163):
                            self.mApb.write(0x00051000 + i * 4, 0x40, ln_i)
                        elif (i == 164):
                            self.mApb.write(0x00051000 + i * 4, 0x49, ln_i)
                        elif (i == 165):
                            self.mApb.write(0x00051000 + i * 4, 0x51, ln_i)
                        elif (i == 166):
                            self.mApb.write(0x00051000 + i * 4, 0x5a, ln_i)
                        elif (i == 167):
                            self.mApb.write(0x00051000 + i * 4, 0x63, ln_i)
                        elif (i == 168):
                            self.mApb.write(0x00051000 + i * 4, 0x6c, ln_i)
                        elif (i == 169):
                            self.mApb.write(0x00051000 + i * 4, 0x76, ln_i)
                        elif (i == 170):
                            self.mApb.write(0x00051000 + i * 4, 0x7f, ln_i)
                        elif (i == 171):
                            self.mApb.write(0x00051000 + i * 4, 0x88, ln_i)
                        elif (i == 172):
                            self.mApb.write(0x00051000 + i * 4, 0x92, ln_i)
                        elif (i == 173):
                            self.mApb.write(0x00051000 + i * 4, 0x9b, ln_i)
                        elif (i == 174):
                            self.mApb.write(0x00051000 + i * 4, 0xa4, ln_i)
                        elif (i == 175):
                            self.mApb.write(0x00051000 + i * 4, 0xad, ln_i)
                        elif (i == 176):
                            self.mApb.write(0x00051000 + i * 4, 0xb5, ln_i)
                        elif (i == 177):
                            self.mApb.write(0x00051000 + i * 4, 0xbe, ln_i)
                        elif (i == 178):
                            self.mApb.write(0x00051000 + i * 4, 0xc6, ln_i)
                        elif (i == 179):
                            self.mApb.write(0x00051000 + i * 4, 0xcd, ln_i)
                        elif (i == 180):
                            self.mApb.write(0x00051000 + i * 4, 0xd5, ln_i)
                        elif (i == 181):
                            self.mApb.write(0x00051000 + i * 4, 0xdb, ln_i)
                        elif (i == 182):
                            self.mApb.write(0x00051000 + i * 4, 0xe1, ln_i)
                        elif (i == 183):
                            self.mApb.write(0x00051000 + i * 4, 0xe7, ln_i)
                        elif (i == 184):
                            self.mApb.write(0x00051000 + i * 4, 0xec, ln_i)
                        elif (i == 185):
                            self.mApb.write(0x00051000 + i * 4, 0xf1, ln_i)
                        elif (i == 186):
                            self.mApb.write(0x00051000 + i * 4, 0xf5, ln_i)
                        elif (i == 187):
                            self.mApb.write(0x00051000 + i * 4, 0xf8, ln_i)
                        elif (i == 188):
                            self.mApb.write(0x00051000 + i * 4, 0xfa, ln_i)
                        elif (i == 189):
                            self.mApb.write(0x00051000 + i * 4, 0xfc, ln_i)
                        elif (i == 190):
                            self.mApb.write(0x00051000 + i * 4, 0xfd, ln_i)
                        elif (i == 191):
                            self.mApb.write(0x00051000 + i * 4, 0xfe, ln_i)
                        elif (i == 192):
                            self.mApb.write(0x00051000 + i * 4, 0xfe, ln_i)
                        elif (i == 193):
                            self.mApb.write(0x00051000 + i * 4, 0xfd, ln_i)
                        elif (i == 194):
                            self.mApb.write(0x00051000 + i * 4, 0xfb, ln_i)
                        elif (i == 195):
                            self.mApb.write(0x00051000 + i * 4, 0xf9, ln_i)
                        elif (i == 196):
                            self.mApb.write(0x00051000 + i * 4, 0xf6, ln_i)
                        elif (i == 197):
                            self.mApb.write(0x00051000 + i * 4, 0xf3, ln_i)
                        elif (i == 198):
                            self.mApb.write(0x00051000 + i * 4, 0xef, ln_i)
                        elif (i == 199):
                            self.mApb.write(0x00051000 + i * 4, 0xea, ln_i)
                        elif (i == 200):
                            self.mApb.write(0x00051000 + i * 4, 0xe4, ln_i)
                        elif (i == 201):
                            self.mApb.write(0x00051000 + i * 4, 0xde, ln_i)
                        elif (i == 202):
                            self.mApb.write(0x00051000 + i * 4, 0xd8, ln_i)
                        elif (i == 203):
                            self.mApb.write(0x00051000 + i * 4, 0xd1, ln_i)
                        elif (i == 204):
                            self.mApb.write(0x00051000 + i * 4, 0xca, ln_i)
                        elif (i == 205):
                            self.mApb.write(0x00051000 + i * 4, 0xc2, ln_i)
                        elif (i == 206):
                            self.mApb.write(0x00051000 + i * 4, 0xba, ln_i)
                        elif (i == 207):
                            self.mApb.write(0x00051000 + i * 4, 0xb1, ln_i)
                        elif (i == 208):
                            self.mApb.write(0x00051000 + i * 4, 0xa8, ln_i)
                        elif (i == 209):
                            self.mApb.write(0x00051000 + i * 4, 0x9f, ln_i)
                        elif (i == 210):
                            self.mApb.write(0x00051000 + i * 4, 0x96, ln_i)
                        elif (i == 211):
                            self.mApb.write(0x00051000 + i * 4, 0x8d, ln_i)
                        elif (i == 212):
                            self.mApb.write(0x00051000 + i * 4, 0x84, ln_i)
                        elif (i == 213):
                            self.mApb.write(0x00051000 + i * 4, 0x7a, ln_i)
                        elif (i == 214):
                            self.mApb.write(0x00051000 + i * 4, 0x71, ln_i)
                        elif (i == 215):
                            self.mApb.write(0x00051000 + i * 4, 0x68, ln_i)
                        elif (i == 216):
                            self.mApb.write(0x00051000 + i * 4, 0x5f, ln_i)
                        elif (i == 217):
                            self.mApb.write(0x00051000 + i * 4, 0x56, ln_i)
                        elif (i == 218):
                            self.mApb.write(0x00051000 + i * 4, 0x4d, ln_i)
                        elif (i == 219):
                            self.mApb.write(0x00051000 + i * 4, 0x44, ln_i)
                        elif (i == 220):
                            self.mApb.write(0x00051000 + i * 4, 0x3c, ln_i)
                        elif (i == 221):
                            self.mApb.write(0x00051000 + i * 4, 0x34, ln_i)
                        elif (i == 222):
                            self.mApb.write(0x00051000 + i * 4, 0x2d, ln_i)
                        elif (i == 223):
                            self.mApb.write(0x00051000 + i * 4, 0x26, ln_i)
                        elif (i == 224):
                            self.mApb.write(0x00051000 + i * 4, 0x20, ln_i)
                        elif (i == 225):
                            self.mApb.write(0x00051000 + i * 4, 0x1a, ln_i)
                        elif (i == 226):
                            self.mApb.write(0x00051000 + i * 4, 0x14, ln_i)
                        elif (i == 227):
                            self.mApb.write(0x00051000 + i * 4, 0xf, ln_i)
                        elif (i == 228):
                            self.mApb.write(0x00051000 + i * 4, 0xb, ln_i)
                        elif (i == 229):
                            self.mApb.write(0x00051000 + i * 4, 0x8, ln_i)
                        elif (i == 230):
                            self.mApb.write(0x00051000 + i * 4, 0x5, ln_i)
                        elif (i == 231):
                            self.mApb.write(0x00051000 + i * 4, 0x3, ln_i)
                        elif (i == 232):
                            self.mApb.write(0x00051000 + i * 4, 0x1, ln_i)
                        elif (i == 233):
                            self.mApb.write(0x00051000 + i * 4, 0x0, ln_i)
                        elif (i == 234):
                            self.mApb.write(0x00051000 + i * 4, 0x0, ln_i)
                        elif (i == 235):
                            self.mApb.write(0x00051000 + i * 4, 0x1, ln_i)
                        elif (i == 236):
                            self.mApb.write(0x00051000 + i * 4, 0x2, ln_i)
                        elif (i == 237):
                            self.mApb.write(0x00051000 + i * 4, 0x4, ln_i)
                        elif (i == 238):
                            self.mApb.write(0x00051000 + i * 4, 0x6, ln_i)
                        elif (i == 239):
                            self.mApb.write(0x00051000 + i * 4, 0x9, ln_i)
                        elif (i == 240):
                            self.mApb.write(0x00051000 + i * 4, 0xd, ln_i)
                        elif (i == 241):
                            self.mApb.write(0x00051000 + i * 4, 0x12, ln_i)
                        elif (i == 242):
                            self.mApb.write(0x00051000 + i * 4, 0x17, ln_i)
                        elif (i == 243):
                            self.mApb.write(0x00051000 + i * 4, 0x1d, ln_i)
                        elif (i == 244):
                            self.mApb.write(0x00051000 + i * 4, 0x23, ln_i)
                        elif (i == 245):
                            self.mApb.write(0x00051000 + i * 4, 0x29, ln_i)
                        elif (i == 246):
                            self.mApb.write(0x00051000 + i * 4, 0x31, ln_i)
                        elif (i == 247):
                            self.mApb.write(0x00051000 + i * 4, 0x38, ln_i)
                        elif (i == 248):
                            self.mApb.write(0x00051000 + i * 4, 0x40, ln_i)
                        elif (i == 249):
                            self.mApb.write(0x00051000 + i * 4, 0x49, ln_i)
                        elif (i == 250):
                            self.mApb.write(0x00051000 + i * 4, 0x51, ln_i)
                        elif (i == 251):
                            self.mApb.write(0x00051000 + i * 4, 0x5a, ln_i)
                        elif (i == 252):
                            self.mApb.write(0x00051000 + i * 4, 0x63, ln_i)
                        elif (i == 253):
                            self.mApb.write(0x00051000 + i * 4, 0x6c, ln_i)
                        elif (i == 254):
                            self.mApb.write(0x00051000 + i * 4, 0x76, ln_i)

    # ----------------------------------------------------------------------------------------------------
    # Test Item
    # ----------------------------------------------------------------------------------------------------
    def GetHistogram(self):
        self.func_record['GetHistogram'] += 1
        memSize = 128
        for ln_i in range(4):
            if self.is_lane_enabled(ln_i):
                dataTemp = self.mApb.read(0x00060100, ln_i)
                #dataTemp = dataTemp & 0xbf
                dataTemp = dataTemp | 0x40
                self.mApb.write(0x00060100, dataTemp & 0x7F, ln_i)
                self.mApb.write(0x00060100, dataTemp | 0x80, ln_i)
                Delay(100)

                countnum = ((self.mApb.read(0x00061000, ln_i) & 0x7f) >> 3) + 14
                filename = self.dump_path + "histo_data_" + self.mCfg.GetCondition() + "_ln" + str(ln_i) + "_count" + str(countnum) + ".txt"
                fs = open(filename, 'w')

                for mem_i in range(memSize):
                    memAdd = 0x00063010 + mem_i * 4
                    data = self.mApb.read(memAdd, ln_i)
                    fs.write("%s %s\n" % (str(mem_i), str(data)))

                fs.close()
                PlotHisto(filename)
        if (self.mCfg.b_dbg_print):
            print("Histogram Done!")

    def GetAllChHistogram(self):
        self.func_record['GetAllChHistogram'] += 1
        memSize = 128
        for ln_i in range(4):
            if self.is_lane_enabled(ln_i):
                self.mApb.write(0x00060100, 1 << 6, ln_i, 1 << 6)  # eom_data_path_sel=data (not need this)
                filename = self.dump_path + "ch_histo_data_" + self.mCfg.GetCondition() + "_ln" + str(ln_i) + ".txt"
                fs = open(filename, 'w')
                for ch_i in range(32):
                    self.mApb.write(0x00060100, ch_i | 1 << 6 | 0 << 7, ln_i, 0x1f | 1 << 6 | 1 << 7)  # eom_en=0, ch=i, path=real-data
                    self.mApb.write(0x00060100, 1 << 7, ln_i, 1 << 7)  # eom_en=1
                    for mem_i in range(memSize):
                        memAdd = 0x00063010 + mem_i * 4
                        if (mem_i == 0):
                            data = self.mApb.read(memAdd, ln_i)
                        else:
                            data = self.mApb.read(memAdd, ln_i)
                        fs.write("%d %d %d\n" % (ch_i, mem_i, data))
                    print("ADC CH%d FOM :%d" % (ch_i, self.mApb.read(0x00061010, ln_i)))
                self.mApb.write(0x00060100, 0 << 6, ln_i, 1 << 6)
                fs.close()
                plot_ch_histo(filename)
        print("Done")
        return 0

    def GetHistoEom(self):
        self.func_record['GetHistoEom'] += 1
        memSize = 128
        memStartAdd = 0x00063010
        totalPhase = 128
        phaseStep = self.mCfg.phaseStep

        if self.mCfg.data_rate == 10.3125:
            totalPhase *= 2
            phaseStep *= 2

        for ln_i in range(4):
            if self.is_lane_enabled(ln_i):
                centerPosition = self.getHorizontalCenter(ln_i)
                filename = self.dump_path + "eom_data_" + self.mCfg.GetCondition() + "_ln" + str(ln_i) + ".txt"
                fs = open(filename, 'w')
                self.mApb.write(0x00060100, 0 << 6, ln_i, 1 << 6)

                for phase_i in range(0, totalPhase, phaseStep):
                    if (phase_i < totalPhase - centerPosition):
                        phase = phase_i + (512 - totalPhase) + centerPosition
                    else:
                        phase = phase_i - (totalPhase - centerPosition)
                    self.set_eom_position(phase, ln_i)
                    self.mApb.write(0x00060100, 0 << 7, ln_i, 1 << 7)
                    self.mApb.write(0x00060100, 1 << 7, ln_i, 1 << 7)
                    for mem_i in range(memSize):
                        memAdd = memStartAdd + mem_i * 4
                        data = self.mApb.read(memAdd)
                        fs.write("%d %d %d\n" % (phase_i, mem_i, data))

                        if (mem_i == memSize / 2):
                            print("phase: %d\t%d" % (phase, data))
                self.set_eom_position(0, ln_i)

                fs.close()
                if self.mCfg.data_rate == 10.3125:
                    plot_eom_10g(filename)
                else:
                    plot_eom(filename)
        print("EOM Done")
        return 0

    def GetBerEom(self):
        self.func_record['GetBerEom'] += 1
        totalPhase = 128
        phaseStep = self.mCfg.phaseStep

        if self.mCfg.data_rate == 10.3125:
            totalPhase *= 2
            phaseStep *= 2

        for ln_i in range(4):
            if self.is_lane_enabled(ln_i):
                centerPosition = self.getHorizontalCenter(ln_i)
                curPhase = self.mApb.read(0x00061008, ln_i)

                filename = self.dump_path + "ber_data_" + self.mCfg.GetCondition() + "_ln" + str(ln_i) + ".txt"
                fs = open(filename, 'w')

                self.mApb.write(0x00060100, 0 << 6, ln_i, 1 << 6)
                for phase_i in range(0, totalPhase, phaseStep):
                    if (phase_i < totalPhase - centerPosition):
                        phase = phase_i + (512 - totalPhase) + centerPosition
                    else:
                        phase = phase_i - (totalPhase - centerPosition)
                    if (phase_i == 0):
                        while (curPhase != phase):
                            if ((curPhase < 256 and phase > 256) or curPhase > phase):
                                curPhase -= 1
                                if (curPhase < 0):
                                    curPhase += 512
                            else:
                                curPhase += 1
                                if (curPhase >= 512):
                                    curPhase -= 512
                            self.mApb.write(0x00061008, curPhase, ln_i)
                    self.mApb.write(0x00061008, phase, ln_i)
                    # for alpha_i in range(1):
                    for alpha_i in range(-128, 128, 2):
                        # if alpha_i%64 == 0:
                        #	print("[EOM] (%3d.%4d) get info " % (phase_i,alpha_i))
                        if (alpha_i < -50 or alpha_i > 50):
                            data = 1 << 21
                        else:
                            if (alpha_i < 0):
                                alpha = alpha_i + 256
                            else:
                                alpha = alpha_i
                            self.mApb.write(0x00061020, alpha, ln_i)  # set eom_vref_alpha_1_2
                            self.mApb.write(0x00060100, 0 << 7, ln_i, 1 << 7)  # eom off/on
                            self.mApb.write(0x00060100, 1 << 7, ln_i, 1 << 7)
                            data = self.mApb.read(0x00063428, ln_i)
                            while ((data & 0x2) != 2):
                                data = self.mApb.read(0x00063428, ln_i)
                                Delay(1)
                            data1 = self.mApb.read(0x00063418, ln_i)
                            data2 = self.mApb.read(0x0006341C, ln_i)
                            data = data1 + (data2 << 16)
                        if (alpha_i == 0):
                            print("phase: %d\t%d" % (phase, data))
                        fs.write("%d %d %d\n" % (phase_i, alpha_i, data))
                # print("%d %d %d" %(phase_i, alpha_i, data))

                fs.close()
                if self.mCfg.data_rate == 10.3125:
                    plot_ber_eom_10g(filename)
                elif self.mCfg.data_rate == 25.78125:
                    plot_ber_eom(filename)

            print("BER EOM Done")
            return 0

    def GetBerEomPam4(self, accum_set=7, y_step=1):
        self.func_record['GetBerEomPam4'] += 1
        totalPhase = 128
        phaseStep = self.mCfg.phaseStep

        for ln_i in range(4):
            if self.is_lane_enabled(ln_i):
                centerPosition = self.getHorizontalCenter(ln_i)
                curPhase = self.mApb.read(0x00061008, ln_i)

                filename = self.dump_path + "ber_data_" + self.mCfg.GetCondition() + "_ln" + str(ln_i) + "_12.txt"
                filename0 = self.dump_path + "ber_data_" + self.mCfg.GetCondition() + "_ln" + str(ln_i) + "_01.txt"
                filename2 = self.dump_path + "ber_data_" + self.mCfg.GetCondition() + "_ln" + str(ln_i) + "_23.txt"
                filename3 = self.dump_path + "ber_data_" + self.mCfg.GetCondition() + "_ln" + str(ln_i) + "_vref.txt"

                fs = open(filename, 'w')
                fs0 = open(filename0, 'w')
                fs2 = open(filename2, 'w')
                fs_vref = open(filename3, 'w')

                self.mApb.write(0x00061018, 0x0017 | accum_set << 12, ln_i)
                self.mApb.write(0x00060100, 0 << 6, ln_i, 1 << 6)
                vref = self.mApb.read(0x609A4, ln_i)
                fs_vref.write("%d\n" % (vref))
                fs_vref.close()

                for phase_i in range(0, totalPhase, phaseStep):
                    if (phase_i < totalPhase - centerPosition):
                        phase = phase_i + (512 - totalPhase) + centerPosition
                    else:
                        phase = phase_i - (totalPhase - centerPosition)
                    if (phase_i == 00):
                        while (curPhase != phase):
                            if ((curPhase < 256 and phase > 256) or curPhase > phase):
                                curPhase -= 1
                                if (curPhase < 0):
                                    curPhase += 512
                            else:
                                curPhase += 1
                                if (curPhase >= 512):
                                    curPhase -= 512
                            self.mApb.write(0x00061008, curPhase, ln_i)
                    self.mApb.write(0x00061008, phase, ln_i)
                    for alpha_i in range(int(-vref / 2) - 10, int(vref / 2) + 10, y_step):
                        if (alpha_i < 0):
                            alpha = alpha_i + 256
                        else:
                            alpha = alpha_i
                        self.mApb.write(0x0006101C, alpha, ln_i)
                        self.mApb.write(0x00061020, alpha, ln_i)
                        self.mApb.write(0x00061024, alpha, ln_i)
                        self.mApb.write(0x00060100, 0 << 7, ln_i, 1 << 7)
                        self.mApb.write(0x00060100, 1 << 7, ln_i, 1 << 7)
                        data = self.mApb.read(0x00063428, ln_i)
                        while ((data & 0x2) != 2):
                            data = self.mApb.read(0x00063428, ln_i)
                        # Delay(1)

                        data1 = self.mApb.read(0x00063420, ln_i)
                        data2 = self.mApb.read(0x00063424, ln_i)
                        data = data1 + (data2 << 16)
                        fs2.write("%d %d %d\n" % (phase_i, alpha_i, data))
                        data1 = self.mApb.read(0x00063410, ln_i)
                        data2 = self.mApb.read(0x00063414, ln_i)
                        data = data1 + (data2 << 16)
                        fs0.write("%d %d %d\n" % (phase_i, alpha_i, data))
                        data1 = self.mApb.read(0x00063418, ln_i)
                        data2 = self.mApb.read(0x0006341C, ln_i)
                        data = data1 + (data2 << 16)
                        fs.write("%d %d %d\n" % (phase_i, alpha_i, data))
                        print("[GetBerEomPam4] %d %d %d" % (phase_i, alpha_i, data))
                        if (((vref / 2) % 2 == 1 and alpha_i == 1) or ((vref / 2) % 2 == 0 and alpha_i == 0)):
                            print("phase: %d\t%d" % (phase, data))

                fs.close()
                fs0.close()
                fs2.close()
                plot_ber_eom_pam4(filename)
            print("BER EOM Done")
            return 0

    def GetBathtub(self):
        self.func_record['GetBathtub'] += 1
        totalPhase = 128
        phaseStep = self.mCfg.phaseStep

        if self.mCfg.data_rate == 10.3125:
            totalPhase *= 2
            phaseStep *= 2
        for ln_i in range(4):
            if self.is_lane_enabled(ln_i):
                curPhase = self.mApb.read(0x00061008, ln_i)
                centerPosition = self.getHorizontalCenter(ln_i)
                print("center : %d\r\n" % (centerPosition))
                filename = self.dump_path + "bathtub_" + self.mCfg.GetCondition() + "_ln" + str(ln_i) + ".txt"
                fs = open(filename, 'w')
                self.mApb.write(0x00061020, 0, ln_i)
                self.mApb.write(0x00061018, 0x7017, ln_i)
                self.mApb.write(0x00060100, 0 << 6, ln_i, 1 << 6)
                for phase_i in range(0, totalPhase - 0, phaseStep):
                    if (phase_i < totalPhase - centerPosition):
                        phase = phase_i + (512 - totalPhase) + centerPosition
                    else:
                        phase = phase_i - (totalPhase - centerPosition)
                    if (phase_i == 0):
                        while (curPhase != phase):
                            if (curPhase < 256 and phase > 256 or curPhase > phase):
                                curPhase -= 1
                                if (curPhase < 0):
                                    curPhase += 512
                            else:
                                curPhase += 1
                                if (curPhase >= 512):
                                    curPhase -= 512
                            self.mApb.write(0x00061008, curPhase, ln_i)
                    self.mApb.write(0x00061008, phase, ln_i)
                    self.mApb.write(0x00060100, 0 << 7, ln_i, 1 << 7)
                    self.mApb.write(0x00060100, 1 << 7, ln_i, 1 << 7)
                    data = self.mApb.read(0x00063428, ln_i)
                    while ((data & 0x2) != 2):
                        data = self.mApb.read(0x00063428, ln_i)
                        Delay(1)
                    data1 = self.mApb.read(0x00063418, ln_i)
                    data2 = self.mApb.read(0x0006341C, ln_i)
                    data = data1 + (data2 << 16)
                    print("phase: %d\t%d" % (phase, data))
                    fs.write("%d %d\n" % (phase_i, data))
                fs.close()

        print("Bathtub Done")
        return 0

    def set_eom_position(self, target=0, channel=0):
        curPhase = self.mApb.read(0x61008, channel)
        if(target < 0):
            unsigned_target = target + 512
        elif(target > 511):
            unsigned_target = target - 512
        else:
            unsigned_target = target
        if unsigned_target > curPhase:
            direction = 1 if abs(unsigned_target - curPhase) < abs(512 + curPhase - unsigned_target) else 0
        else:
            direction = 1 if abs(curPhase - unsigned_target) > abs(512 + unsigned_target - curPhase) else 0
        while (curPhase != unsigned_target):
            if direction == 1:
                curPhase += 1
                curPhase = 0 if curPhase == 512 else curPhase
            else:
                curPhase -= 1
                curPhase = 511 if curPhase == -1 else curPhase
            self.mApb.write(0x61008, curPhase, channel)

    # verified
    def getHorizontalCenter(self, ln_i=0):
        self.func_record['getHorizontalCenter'] += 1
        minData = 1 << 30
        minDataPosition = 64
        thres = 100

        self.mApb.write(0x00061020, 0, ln_i)
        self.mApb.write(0x00060100, 0 << 6, ln_i, 1 << 6)
        zeroRight = 0
        zeroLeft = 1000
        totalPhase = 128
        phaseStep = self.mCfg.phaseStep

        if self.mCfg.data_rate == 10.3125:
            totalPhase *= 2
            phaseStep *= 2
        phase_i_init = -40
        for phase_i in range(phase_i_init, totalPhase + 50, phaseStep):
            if (phase_i < totalPhase / 2):
                phase = phase_i + 512 - totalPhase / 2
            else:
                phase = phase_i - totalPhase / 2

            phase = int(phase)
            self.set_eom_position(phase,ln_i)
            self.mApb.write(0x00061008, phase, ln_i)
            self.mApb.write(0x00060100, 0 << 7, ln_i, 1 << 7)
            self.mApb.write(0x00060100, 1 << 7, ln_i, 1 << 7)

            data = self.mApb.read(0x00063428, ln_i)
            while ((data & 0x2) != 2):
                data = self.mApb.read(0x00063428, ln_i)
                Delay(1)
            data1 = self.mApb.read(0x00063418, ln_i)
            data2 = self.mApb.read(0x0006341C, ln_i)
            data = data1 + (data2 << 16)
            # print("%d\t%d"%(phase, data))
            if (data < minData):
                minData = data
                minDataPosition = phase_i
            if (zeroLeft == 1000 and data <= thres):
                zeroLeft = phase_i
            if (zeroLeft != 1000 and data > thres):
                zeroRight = phase_i
                break
        # print("left right : %d\t%d" % (zeroLeft, zeroRight))
        if (zeroLeft != 1000 and zeroRight == 0):
            return int(zeroLeft + totalPhase / 2)
        elif (zeroLeft == 1000 and zeroRight == 0):
            return int(minDataPosition)

        return int((zeroRight + zeroLeft) / 2)

    def GetBer(self, ln_i=0):
        self.func_record['GetBer'] += 1
        if ((self.mApb.read(0x0006008C, ln_i) >> 4 & 0x1) == 1):  # PAM4
            self.mApb.write(0x00060208, 0x000001a0, ln_i)
            self.mApb.write(0x00060174, 0x00008224, ln_i)
            self.mApb.write(0x00060174, 0x00008225, ln_i)
        else:
            self.mApb.write(0x00060208, 0x000001b0, ln_i)
            self.mApb.write(0x00060174, 0x00008204, ln_i)
            self.mApb.write(0x00060174, 0x00008205, ln_i)
        data = self.mApb.read(0x00060700, ln_i)
        if ((data & 0x2) >> 1 == 1 or (data & 0x1) == 1):
            errorCnt = 0
            Delay(250)
            errorCnt += self.mApb.read(0x00060704, ln_i)
            errorCnt += self.mApb.read(0x00060708, ln_i)
            ber = errorCnt / (1 << 30) / (1 << 2)

            errorCnt = self.mApb.read(0x0006070C, ln_i)
            errorCnt += self.mApb.read(0x00060710, ln_i)
            ber += (errorCnt / (1 << 10) / (1 << 2))

            if ((self.mApb.read(0x0006008C, ln_i) >> 4 & 0x1) == 1):  # PAM4
                self.mApb.write(0x00060208, 0x00000180, ln_i)
                self.mApb.write(0x00060174, 0x00008224, ln_i)
                self.mApb.write(0x00060174, 0x00008225, ln_i)
            else:
                self.mApb.write(0x00060208, 0x00000190, ln_i)
                self.mApb.write(0x00060174, 0x00008204, ln_i)
                self.mApb.write(0x00060174, 0x00008205, ln_i)
        else:
            ber = 0.5
        return ber

    def Plot256(self, mon_sel=1):
        self.func_record['Plot256'] += 1
        for ln_i in range(4):
            if self.is_lane_enabled(ln_i):
                filename = self.dump_path + "dump_256_" + self.mCfg.GetCondition() + "_ln" + str(ln_i) + ".txt"
                fs = open(filename, 'w')
                self.mApb.write(0x00060190, 0x00000000 | mon_sel, ln_i)
                self.mApb.write(0x00060190, 0x00000002 | mon_sel, ln_i)
                for i in range(256):
                    addr = 0x00065000 + +i * 4
                    if (addr == 0x65110):
                        addr = 0x65111
                    elif (addr == 0x65210):
                        addr = 0x65212
                    fs.write("%d\t%d\n" % (i, self.mApb.read(addr, ln_i)))
                fs.close()
                plot_256(filename)
        print("Dump done!")

    def C1SweepAdap(self):
        self.func_record['C1SweepAdap'] += 1
        StartCode = 90
        for ln_i in range(4):
            if self.is_lane_enabled(ln_i):
                self.mApb.write(0x00062004, 0x0000C0C0, ln_i)
                self.mApb.write(0x00062008, 0x0000c0c0, ln_i)
                self.mApb.write(0x0006200c, 0x0000c0c0, ln_i)
                self.mApb.write(0x00062010, 0x0000c0c0, ln_i)
                filename = self.dump_path + "coeff_" + self.mCfg.GetCondition() + "_ln" + str(ln_i) + ".txt"
                fs = open(filename, 'w')

                for eq_i in range(40):
                    if (eq_i == 0):
                        c1int = self.mApb.read(0x62250, ln_i)
                        self.mApb.write(0x00060130, 0x000, ln_i)
                        if (c1int > 128):
                            c1int = c1int - 256
                        c1int = -c1int
                        writeC1 = c1int
                        if (c1int > StartCode):
                            while (writeC1 != StartCode):
                                writeC1 -= 1
                                self.mApb.write(0x00060130, 0x100 + 256 - writeC1, ln_i)
                                self.mApb.write(0x00061FF8, 0x4, ln_i)
                        else:
                            while (writeC1 != StartCode):
                                writeC1 += 1
                                self.mApb.write(0x00060130, 0x100 + 256 - writeC1, ln_i)
                                self.mApb.write(0x00061FF8, 0x4, ln_i)

                    self.phyEqC1Forcing(StartCode - eq_i * 2, ln_i)
                    cdrCode = self.mApb.read(0x000640BC, ln_i)
                    cm2 = self.mApb.read(0x62274, ln_i)
                    cm1 = self.mApb.read(0x62270, ln_i)
                    c0 = self.mApb.read(0x6223C, ln_i)
                    c1 = self.mApb.read(0x62250, ln_i)
                    c2 = self.mApb.read(0x62254, ln_i)
                    c3 = self.mApb.read(0x62258, ln_i)
                    c4 = self.mApb.read(0x6225C, ln_i)
                    c5 = self.mApb.read(0x62260, ln_i)
                    c6 = self.mApb.read(0x62264, ln_i)
                    c7 = self.mApb.read(0x62268, ln_i)
                    c8 = self.mApb.read(0x6226C, ln_i)
                    if (cm2 > 128): cm2 = cm2 - 256
                    if (cm1 > 128): cm1 = cm1 - 256
                    if (c1 > 128): c1 = c1 - 256
                    if (c2 > 128): c2 = c2 - 256
                    if (c3 > 128): c3 = c3 - 256
                    if (c4 > 128): c4 = c4 - 256
                    if (c5 > 128): c5 = c5 - 256
                    if (c6 > 128): c6 = c6 - 256
                    if (c7 > 128): c7 = c7 - 256
                    if (c8 > 128): c8 = c8 - 256
                    ber = GetBer(ln_i)
                    if (ber > 0.1):
                        break
                    fs.write(
                        "%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\n" % (cdrCode % 128, -cm2, -cm1, c0, -c1, -c2, -c3, -c4, -c5, -c6, -c7, -c8, ber))
                    print("%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\n" % (cdrCode % 128, -cm2, -cm1, c0, -c1, -c2, -c3, -c4, -c5, -c6, -c7, -c8, ber))

                fs.close()
                plot_coeff(filename)
        print("Sweep Done!")
        return 0

    def Cm1SweepAdap(self):
        self.func_record['Cm1SweepAdap'] += 1
        StartCode = 2
        for ln_i in range(4):
            if self.is_lane_enabled(ln_i):
                self.mApb.write(0x00062004, 0x0000C0C0, ln_i)
                self.mApb.write(0x00062008, 0x0000c0c0, ln_i)
                self.mApb.write(0x0006200c, 0x0000c0c0, ln_i)
                self.mApb.write(0x00062010, 0x0000c0c0, ln_i)
                filename = self.dump_path + "coeff_" + self.mCfg.GetCondition() + "_ln" + str(ln_i) + ".txt"
                fs = open(filename, 'w')

                for eq_i in range(40):
                    if (eq_i == 0):
                        c1int = self.mApb.read(0x62250, ln_i)
                        c1int = self.mApb.read(0x62270, ln_i)
                        self.mApb.write(0x00060130, 0x000, ln_i)
                        if (c1int > 128):
                            c1int = c1int - 256
                        c1int = -c1int
                        writeC1 = c1int
                        if (c1int > StartCode):
                            while (writeC1 != StartCode):
                                writeC1 -= 1
                                self.mApb.write(0x00060120, 0x100 + 256 - writeC1, ln_i)
                                self.mApb.write(0x00061FF8, 0x4, ln_i)
                        else:
                            while (writeC1 != StartCode):
                                writeC1 += 1
                                self.mApb.write(0x00060120, 0x100 + 256 - writeC1, ln_i)
                                self.mApb.write(0x00061FF8, 0x4, ln_i)

                    self.mApb.write(0x00060120, 0x100 + 256 - (StartCode + eq_i * 2), ln_i)
                    self.mApb.write(0x00061FF8, 0x4, ln_i)
                    cdrCode = self.mApb.read(0x000640BC, ln_i)
                    cm2 = self.mApb.read(0x62274, ln_i)
                    cm1 = self.mApb.read(0x62270, ln_i)
                    c0 = self.mApb.read(0x6223C, ln_i)
                    c1 = self.mApb.read(0x62250, ln_i)
                    c2 = self.mApb.read(0x62254, ln_i)
                    c3 = self.mApb.read(0x62258, ln_i)
                    c4 = self.mApb.read(0x6225C, ln_i)
                    c5 = self.mApb.read(0x62260, ln_i)
                    c6 = self.mApb.read(0x62264, ln_i)
                    c7 = self.mApb.read(0x62268, ln_i)
                    c8 = self.mApb.read(0x6226C, ln_i)
                    if (cm2 > 128): cm2 = cm2 - 256
                    if (cm1 > 128): cm1 = cm1 - 256
                    if (c1 > 128): c1 = c1 - 256
                    if (c2 > 128): c2 = c2 - 256
                    if (c3 > 128): c3 = c3 - 256
                    if (c4 > 128): c4 = c4 - 256
                    if (c5 > 128): c5 = c5 - 256
                    if (c6 > 128): c6 = c6 - 256
                    if (c7 > 128): c7 = c7 - 256
                    if (c8 > 128): c8 = c8 - 256
                    ber = GetBer(ln_i);
                    if (ber > 0.1):
                        break
                    fs.write(
                        "%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t\n" % (cdrCode % 128, -cm2, -cm1, c0, -c1, -c2, -c3, -c4, -c5, -c6, -c7, -c8, ber))
                    print("%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t" % (cdrCode % 128, -cm2, -cm1, c0, -c1, -c2, -c3, -c4, -c5, -c6, -c7, -c8, ber))
                fs.close()
                plot_coeff(filename)
        print("Sweep Done!")
        return 0

    def C1CtrlSweep(self):
        self.func_record['C1CtrlSweep'] += 1
        StartCode = 31
        for ln_i in range(4):
            if self.is_lane_enabled(ln_i):
                self.mApb.write(0x00062004, 0x0000C0C0, ln_i)
                self.mApb.write(0x00062008, 0x0000c0c0, ln_i)
                self.mApb.write(0x0006200c, 0x0000c0c0, ln_i)
                self.mApb.write(0x00062010, 0x0000c0c0, ln_i)
                filename = self.dump_path + "c1_ctrl_coeff_" + self.mCfg.GetCondition() + "_ln" + str(ln_i) + ".txt"
                fs = open(filename, 'w')

                for eq_i in range(62):
                    cdrCode = self.mApb.read(0x000640BC, ln_i)
                    cm2 = self.mApb.read(0x62274, ln_i)
                    cm1 = self.mApb.read(0x62270, ln_i)
                    c0 = self.mApb.read(0x6223C, ln_i)
                    c1 = self.mApb.read(0x62250, ln_i)
                    c2 = self.mApb.read(0x62254, ln_i)
                    c3 = self.mApb.read(0x62258, ln_i)
                    c4 = self.mApb.read(0x6225C, ln_i)
                    c5 = self.mApb.read(0x62260, ln_i)
                    c6 = self.mApb.read(0x62264, ln_i)
                    c7 = self.mApb.read(0x62268, ln_i)
                    c8 = self.mApb.read(0x6226C, ln_i)
                    c1ctrlDone = self.mApb.read(0x6400C, ln_i)
                    if (self.mApb.read(0x63590, ln_i) >= 1024):
                        c1MinusCm1 = (2048 - self.mApb.read(0x63590, ln_i)) / 4.0
                    else:
                        c1MinusCm1 = (2048 - self.mApb.read(0x63590, ln_i)) / 4.0
                    if (cm2 > 128): cm2 = cm2 - 256
                    if (cm1 > 128): cm1 = cm1 - 256
                    if (c1 > 128): c1 = c1 - 256
                    if (c2 > 128): c2 = c2 - 256
                    if (c3 > 128): c3 = c3 - 256
                    if (c4 > 128): c4 = c4 - 256
                    if (c5 > 128): c5 = c5 - 256
                    if (c6 > 128): c6 = c6 - 256
                    if (c7 > 128): c7 = c7 - 256
                    if (c8 > 128): c8 = c8 - 256
                    ber = GetBer(ln_i)
                    fs.write("%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%e\t%d\t\n" % (
                        StartCode - eq_i, -cm2, -cm1, c0, -c1, -c2, -c3, -c4, -c5, -c6, -c7, -c8, ber, c1MinusCm1))
                    print("%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%e\t%d\t" % (
                        StartCode - eq_i, -cm2, -cm1, c0, -c1, -c2, -c3, -c4, -c5, -c6, -c7, -c8, ber, c1MinusCm1))
                fs.close()
                plot_coeff(filename)
        print("Sweep Done!")
        return 0

    def GetCaloutMin(self, ln_i=0):
        self.func_record['GetCaloutMin'] += 1
        minData = 128
        self.mApb.write(0x0006051c, 0x00000000, ln_i)
        for i in range(32):
            self.mApb.write(0x00062248, (i << 4) | 4, ln_i)
            self.mApb.write(0x00062248, (i << 4) | 5, ln_i)
            data = self.mApb.read(0x0006224C, ln_i) & 0xFF;
            if (minData > data):
                minData = data
        return 128 - minData

    def GetCaloutMax(self, ln_i=0):
        self.func_record['GetCaloutMax'] += 1
        maxData = 0
        self.mApb.write(0x0006051c, 0x00000000, ln_i)
        for i in range(32):
            self.mApb.write(0x00062248, (i << 4) | 4, ln_i)
            self.mApb.write(0x00062248, (i << 4) | 5, ln_i)
            data = (self.mApb.read(0x0006224C, ln_i) & 0xFF00) >> 8;
            if (maxData < data):
                maxData = data
        return maxData - 128

    def GetAdcMaxMin(self, ch=0, ln_i=0):
        self.func_record['GetAdcMaxMin'] += 1
        self.mApb.write(0x0006051c, 0x00000000, ln_i)
        self.mApb.write(0x00062248, (ch << 4) | 0, ln_i)
        self.mApb.write(0x00062248, (ch << 4) | 1, ln_i)
        data = self.mApb.read(0x0006224C, ln_i);
        return data

    def GetCalMaxMin(self, ch=0, ln_i=0):
        self.func_record['GetCalMaxMin'] += 1
        self.mApb.write(0x0006051c, 0x00000000, ln_i)
        self.mApb.write(0x00062248, (ch << 4) | 0x4, ln_i)
        self.mApb.write(0x00062248, (ch << 4) | 0x5, ln_i)
        data = self.mApb.read(0x0006224C, ln_i)
        return data

    def GetAdcMin8(self, ln_i=0):
        self.func_record['GetAdcMin8'] += 1
        minData = 64;
        self.mApb.write(0x0006051c, 0x00000000, ln_i)
        for i in range(8):
            self.mApb.write(0x00062248, (i << 4) | 0, ln_i)
            self.mApb.write(0x00062248, (i << 4) | 1, ln_i)
            data = self.mApb.read(0x0006224C, ln_i) & 0xFF
            if (minData > data):
                minData = data
        return 64 - minData

    def GetAdcMax8(self, ln_i=0):
        self.func_record['GetAdcMax8'] += 1
        maxData = 0;
        self.mApb.write(0x0006051c, 0x00000000, ln_i)
        for i in range(8):
            self.mApb.write(0x00062248, (i << 4) | 0, ln_i)
            self.mApb.write(0x00062248, (i << 4) | 1, ln_i)
            data = (self.mApb.read(0x0006224C, ln_i) & 0xFF00) >> 8;

            if (maxData < data):
                maxData = data
        return maxData - 64

    def GetAdcMaxMin8(self, ln_i=0):
        self.func_record['GetAdcMaxMin8'] += 1
        maxData = 0;
        minData = 64;
        self.mApb.write(0x0006051c, 0x00000000, ln_i)
        for i in range(8):
            self.mApb.write(0x00062248, (i << 4) | 0, ln_i)
            self.mApb.write(0x00062248, (i << 4) | 1, ln_i)
            data = self.mApb.read(0x0006224C, ln_i);

            if (maxData < (data & 0xff00) >> 8):
                maxData = (data & 0xff00) >> 8
            if (minData > (data & 0xff)):
                minData = data & 0xff
        return ((maxData - 64) << 8) + (64 - minData)

    def GetAdcMin(self, ln_i=0):
        self.func_record['GetAdcMin'] += 1
        minData = 64;
        self.mApb.write(0x0006051c, 0x00000000, ln_i)
        for i in range(32):
            self.mApb.write(0x00062248, (i << 4) | 0, ln_i)
            self.mApb.write(0x00062248, (i << 4) | 1, ln_i)
            data = self.mApb.read(0x0006224C, ln_i) & 0xFF;

            if (minData > data):
                minData = data
        return 64 - minData

    def GetAdcMax(self, ln_i=0):
        self.func_record['GetAdcMax'] += 1
        maxData = 0;
        self.mApb.write(0x0006051c, 0x00000000, ln_i)
        for i in range(32):
            self.mApb.write(0x00062248, (i << 4) | 0, ln_i)
            self.mApb.write(0x00062248, (i << 4) | 1, ln_i)
            data = (self.mApb.read(0x0006224C, ln_i) & 0xFF00) >> 8;

            if (maxData < data):
                maxData = data
        return maxData - 64

    def VcoCharac(self):
        self.func_record['VcoCharac'] += 1
        filename = self.dump_path + "vco_14g_" + self.mCfg.process_corner + "_" + str(self.mCfg.chip_num) + ".txt"
        fs = open(filename, 'w')
        for afcValue in range(31, -1, -1):
            for vciValue in range(8):
                self.mApb.write(0x24000004, 0x00000003)
                self.mApb.write(0x24000004, 0x00000000)
                self.mApb.write(0x24000024, 0x00000231)
                self.mApb.write(0x00000000, 0x00000431)
                self.mApb.write(0x00000138, 0x00000041)
                self.mApb.write(0x00000104, 0x0000004F)
                self.mApb.write(0x00000100, 0x00000A67)
                self.mApb.write(0x0000010c, 0x00000107)

                if (afcValue % 2 == 1):
                    self.mApb.write(0x000000F8, 0x00000306 | (int(afcValue / 2) << 4))
                else:
                    self.mApb.write(0x000000F8, 0x00000006 | (int(afcValue / 2) << 4))
                self.mApb.write(0x00000110, 0x00000001 | (vciValue << 1))
                self.mApb.write(0x00000064, 0x00000011)
                self.mApb.write(0x0000014C, 0x00000020)
                self.mApb.write(0x0000014C, 0x00000030)
                data = self.mApb.read(0x00000150)
                fs.write("%d\t%d\t%f\n" % (afcValue, vciValue, data / 10.0 * 156.25 / 1000.0))
        fs.close()
        plot_vco(filename)
        filename = self.dump_path + "vco_10g_" + self.mCfg.process_corner + "_" + str(self.mCfg.chip_num) + ".txt"
        fs = open(filename, 'w')
        for afcValue in range(31, -1, -1):
            for vciValue in range(8):
                self.mApb.write(0x24000004, 0x00000003)
                self.mApb.write(0x24000004, 0x00000000)
                self.mApb.write(0x24000024, 0x00000231)
                self.mApb.write(0x00000138, 0x00000001)
                if (afcValue % 2 == 1):
                    self.mApb.write(0x000000F8, 0x00000306 | (int(afcValue / 2) << 4))
                else:
                    self.mApb.write(0x000000F8, 0x00000006 | (int(afcValue / 2) << 4))
                self.mApb.write(0x00000110, 0x00000001 | (vciValue << 1))
                self.mApb.write(0x00000104, 0x0000004F)
                self.mApb.write(0x00000100, 0x00000A67)
                self.mApb.write(0x00000000, 0x00000431)
                self.mApb.write(0x0000010c, 0x00000107)
                self.mApb.write(0x00000108, 0x0000014F)
                self.mApb.write(0x00000064, 0x00000011)
                self.mApb.write(0x0000014C, 0x00000020)
                self.mApb.write(0x0000014C, 0x00000030)
                data = self.mApb.read(0x00000150)
                fs.write("%d\t%d\t%f\n" % (afcValue, vciValue, data / 10.0 * 156.25 / 1000.0))
        fs.close()
        plot_vco(filename)
        print("VCO Test Done!\r\n")
        self.mApb.write(0x00000038, 0x00000010)

    def GetHistogramOfBer(self, filename):
        self.func_record['GetHistogramOfBer'] += 1
        memSize = 128;
        for ln_i in range(4):
            if self.is_lane_enabled(ln_i):
                plot_histo_ber(filename)
        print("Histogram Done!")

    def GetAvgCoeff(self, tap, avgNum, ln_i=0):
        result = 0
        temp = 0
        if (avgNum < 1):
            return 0xffff
        if (tap > 0 and tap < 8):
            addr = 0x62250 + (tap - 1) * 4
        elif (tap < 0 and tap > -3):
            addr = 0x62270 + (-tap - 1) * 4
        elif (tap == 0):
            addr = 0x6223c
        else:
            return 0xffff

        for i in range(avgNum):
            temp = self.mApb.read(addr, ln_i)
            if (temp > 128):
                result = result + temp - 256
            else:
                result += temp
        result /= avgNum
        return result
