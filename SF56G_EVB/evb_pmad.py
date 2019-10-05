from evb_types import *
from evb_utils import *
import numpy as np
from evb_plot import plot_256
import matplotlib.pyplot as plt
from matplotlib import rcParams
from evb_plot import *
import evb_extra
class EVB_PMAD(object):
    def __init__(self):
        # port
        self.mCfg  = None
        self.mApb  = None
        # shared vars
    def connect(self,mCfg,mApb):
        self.mCfg = mCfg
        self.mApb = mApb
        self.init_vars()
#----------------------------------------------------------------------------------------------------
# private functions
#----------------------------------------------------------------------------------------------------
    def init_vars(self):
        self.tx_pre2 = [0]*self.mCfg.max_channel
        self.tx_pre1 = [0]*self.mCfg.max_channel
        self.tx_post1 = [0]*self.mCfg.max_channel
        self.attenuation = [1.0]*self.mCfg.max_channel
        self.cboost = [0]*self.mCfg.max_channel
  
    def is_bbpd_rate(self,data_rate):
        if data_rate in [10.3125]:
            return True
        else:
            return False
    def is_pam4_rate(self,data_rate):
        if data_rate in [56.25,53.125,21.25,22.5]:
            return True
        else:
            return False
    def is_lane_enabled(self,lane_index=0):
        return ((self.mCfg.lane_en >> lane_index) & 1 == 1)
    def get_active_lane(self):
        result = []
        for i in range(self.mCfg.max_channel):
            if ((self.mCfg.lane_en >> i) & 1 == 1):
                result.append(i)
        return result
    def get_signed_code(self, unsigned):
        return (unsigned if unsigned < 128 else unsigned-256)
    def get_unsigned_code(self, signed):
        return (signed if signed >= 0 else signed+256)
    def get_coef_lvl(self, symbol):
        if symbol == 0:
            return -3
        elif symbol == 1:
            return -1
        elif symbol == 2:
            return  1
        elif symbol == 3:
            return  3
        else:
            return 0
#----------------------------------------------------------------------------------------------------
# Debug
#----------------------------------------------------------------------------------------------------
    #{{{
    def DumpRegs(self,fh,start=0x0,end=0x4,channel=0):
        addr = start
        while (addr <= end):
            data = self.mApb.read(addr,channel)
            fh.writelines('[ln%d] 0x%x => 0x%x\n' % (channel,addr,data))
            addr += 4
    def DumpRegFile(self,target='rx',tag='',channel=0):
        file_name = self.mCfg.dump_path+'regdump'+tag+'.txt'
        fh = open(file_name,'w')
        print ("DumpRegFile ln%d - (%s)" % (channel,target))
        if ((target == 'tx') or (target == 'all')):
            self.DumpRegs(fh,0x50000,0x50164,channel)
            self.DumpRegs(fh,0x50500,0x5051C,channel)
            self.DumpRegs(fh,0x50600,0x5066C,channel)
            self.DumpRegs(fh,0x51000,0x51BFC,channel) #TXDSP_LUT
            self.DumpRegs(fh,0x54000,0x5400C,channel)
        if ((target == 'rx') or (target == 'all')):
            self.DumpRegs(fh,0x60000,0x601F8,channel)
            self.DumpRegs(fh,0x60500,0x605CC,channel)
            self.DumpRegs(fh,0x60700,0x60710,channel)
            self.DumpRegs(fh,0x60800,0x609C0,channel)
            self.DumpRegs(fh,0x61000,0x61024,channel)
            self.DumpRegs(fh,0x61FF8,0x6224C,channel)
            self.DumpRegs(fh,0x63010,0x6320C,channel) #EOM_VCNT
            self.DumpRegs(fh,0x63410,0x6358C,channel) #EOM_ERROR/MMCDR/ADC_IOC/CAL/INIT_FORCE
            self.DumpRegs(fh,0x64000,0x640F0,channel) #FSM/CAL_FSM/MMCDR_SKEW_CODE/MMCDR_CONFIGs/etc
            self.DumpRegs(fh,0x64100,0x64208,channel) #ADC_CAL_xx
            self.DumpRegs(fh,0x6420C,0x6421C,channel) #BUBBLE,VITERBI_CTRL
        if ((target == 'cmn') or (target == 'all')):
            self.DumpRegs(fh,0x0000,0x0148,0)
            self.DumpRegs(fh,0x0FFC,0x0FFC,0)
        fh.close()
    def PrintCmnState(self):
        rdata = self.mApb.read(0xC0)
        print ("PLL Lock Done = %s" % (rdata & 1 == 1))
    def PrintLaneState(self,channel=0):
        rxstate = self.mApb.read(0x64000,channel)
        rxstate |= ((self.mApb.read(0x64004,channel) & 0x1ff) << 16)
        txstate = self.mApb.read(0x54000,channel)
        print ("LN[%d] %-20s %-20s" % (channel,PMAD_RxState(rxstate),PMAD_TxState(txstate)))
    def PrintIocCalState(self,channel=0):
        rdata = self.mApb.read(0x64010,channel)
        state = rdata&0xf
        substate = (rdata>>4)&0xf
        print ("LN[%d] IocCalState: %-20s , %-20s" % (channel,PMAD_IocState(state),PMAD_IocSubState(substate)))
    def PrintInitCalState(self,channel=0):
        for i in range(33):
            rdata = self.mApb.read(0x64014+i*4,channel)
            state = (rdata>>3)&0x3
            print ("LN[%d] adc(%2d) InitCalState: %-20s" % (channel,i,PMAD_InitCalState(state)))
    def PrintMainCalState(self,channel=0):
        for i in range(33):
            rdata = self.mApb.read(0x64014+i*4,channel)
            state = rdata&0x7
            print ("LN[%d] adc(%2d) MainCalState: %-20s" % (channel,i,PMAD_MainCalState(state)))
    def PrintAllRxCoef(self,channel=0):
        cm2 = self.get_signed_code(self.mApb.read(0x62274,channel))
        cm1 = self.get_signed_code(self.mApb.read(0x62270,channel))
        c0h = self.mApb.read(0x6223C,channel)
        c0l = self.mApb.read(0x62240,channel)
        c1  = self.get_signed_code(self.mApb.read(0x62250,channel))
        c2  = self.get_signed_code(self.mApb.read(0x62254,channel))
        c3  = self.get_signed_code(self.mApb.read(0x62258,channel))
        c4  = self.get_signed_code(self.mApb.read(0x6225C,channel))
        c5  = self.get_signed_code(self.mApb.read(0x62260,channel))
        c6  = self.get_signed_code(self.mApb.read(0x62264,channel))
        c7  = self.get_signed_code(self.mApb.read(0x62268,channel))
        c8  = self.get_signed_code(self.mApb.read(0x6226C,channel))
        print ("LN[%d] C[-2]: %-10.2f" % (channel,round(-cm2/128.0,2)))
        print ("LN[%d] C[-1]: %-10.2f" % (channel,round(-cm1/128.0,2)))
        print ("LN[%d] C[0H]: %-10.2f" % (channel,(c0h)))
        print ("LN[%d] C[0L]: %-10.2f" % (channel,(c0l)))
        print ("LN[%d] C[ 1]: %-10.2f" % (channel,round(-c1 /128.0,2)))
        print ("LN[%d] C[ 2]: %-10.2f" % (channel,round(-c2 /128.0,2)))
        print ("LN[%d] C[ 3]: %-10.2f" % (channel,round(-c3 /128.0,2)))
        print ("LN[%d] C[ 4]: %-10.2f" % (channel,round(-c4 /128.0,2)))
        print ("LN[%d] C[ 5]: %-10.2f" % (channel,round(-c5 /128.0,2)))
        print ("LN[%d] C[ 6]: %-10.2f" % (channel,round(-c6 /128.0,2)))
        print ("LN[%d] C[ 7]: %-10.2f" % (channel,round(-c7 /128.0,2)))
        print ("LN[%d] C[ 8]: %-10.2f" % (channel,round(-c8 /128.0,2)))
    def PrintAllAdcMinMax(self,channel=0,mon_sel=0):
        for adc_channel in range(32):
            (minval,maxval) = self.GetAdcMinMax(adc_channel,channel,mon_sel,1)
            print ("LN[%d] adc(%2d) min=%d, max=%d" % (channel,adc_channel,minval,maxval))
    def PrintAdcSkewCode(self,channel=0):
        for i in range(4):
            code = self.mApb.read(0x64098+i*4,channel)
            print ("LN[%d] skewcode%d=%d" % (channel,i,code))
    def PrintAdcCalC0p(self,channel=0):
        for i in range(33):
            code = self.mApb.read(0x64100+i*4,channel)
            print ("LN[%d] adc<%2d> c0p=%d" % (channel,i,code))
    def PrintAdcCalC0m(self,channel=0):
        for i in range(33):
            code = self.get_signed_code(self.mApb.read(0x64184+(i*4 if i<18 else i*4+4),channel))
            print ("LN[%d] adc<%2d> c0m=%d" % (channel,i,code))
    def PrintDataPathConfig(self,channel=0):
        tx_018 = self.mApb.read(0x50018,channel)
        tx_084 = self.mApb.read(0x50084,channel)
        tx_100 = self.mApb.read(0x50100,channel)
        tx_104 = self.mApb.read(0x50104,channel)
        rx_08c = self.mApb.read(0x6008c,channel)
        rx_174 = self.mApb.read(0x60174,channel)
        print("[%d] ana_10g_mode=%d, tx_enc=%d, tx_10g_en=%d, tx_data_sel=%d, tx_bist_width=%d"% (channel,tx_018&1,(tx_084>>3)&3,(tx_100>>6)&1,tx_100&3,(tx_104>>5)&1))
        print("[%d] rx_enc=%d, rx_bist_width=%d"% (channel,(rx_08c>>3)&3,(rx_174>>5)&1))
#}}}
#----------------------------------------------------------------------------------------------------
# Monitor
#----------------------------------------------------------------------------------------------------
#{{{
    def GetEye(self,HeightOnly=0,channel=0):
        # get reference
        c0h = min(63,int((self.mApb.read(0x6223C,channel)+3)/2.0)) #25
        c0l = min(63,int((self.mApb.read(0x62240,channel)+1)/2.0)) #9
        pam4 = (c0l != 0)
        # get histo data
        height_data = self.GetEye_HeightData(target=range(128),channel=channel)
        # find Height and Center
        if pam4:
            h01,c01 = self.GetEye_HnC(height_data,64-c0h,64-c0l)
            h12,c12 = self.GetEye_HnC(height_data,64-c0l,64+c0l)
            h23,c23 = self.GetEye_HnC(height_data,64+c0l,64+c0h)
        else:
            h01,c01 = 0,0
            h12,c12 = self.GetEye_HnC(height_data,64-c0h,64+c0h)
            h23,c23 = 0,0
        # collect width data
        w01,w12,w23 = 0,0,0
        if not HeightOnly:
            # find center phase with eom base
            p01 = self.GetEye_GetCenterPhase(c01,channel)
            p12 = self.GetEye_GetCenterPhase(c12,channel)
            p23 = self.GetEye_GetCenterPhase(c23,channel)
            # find effective thld with eom base
            t01 = self.GetEye_GetEomThld(c01,h01,p01,channel)
            t12 = self.GetEye_GetEomThld(c12,h12,p12,channel)
            t23 = self.GetEye_GetEomThld(c23,h23,p23,channel)
            width_data  = self.GetEye_WidthData(c01,c12,c23,channel)
            if pam4:
                w01 = self.GetEye_Width(width_data[0],t01)
            w12 = self.GetEye_Width(width_data[1],t12)
            if pam4:
                w23 = self.GetEye_Width(width_data[2],t23)
        # convert height to voltage scale
        h01s = h01/63.0
        h12s = h12/63.0
        h23s = h23/63.0
        w01s = w01/128.0
        w12s = w12/128.0
        w23s = w23/128.0
        return [h01s,w01s,h12s,w12s,h23s,w23s]
 
    def GetEye_Width(self,width_data,thld=0):
        if width_data[0] <= thld:
            state = 'PREV_EYE'
        else:
            state = 'WALL'
        ptr_beg,ptr_end = 0,0
        for i,data in enumerate(width_data):
            if state == 'PREV_EYE':
                if data > thld:
                    state = 'WALL'
            elif state == 'WALL':
                if data <= thld:
                    state = 'CURR_EYE'
                    ptr_beg = i
            elif state == 'CURR_EYE':
                if data > thld:
                    state = 'END'
                    ptr_end = i
        return max(0,(ptr_end-ptr_beg))
    def GetEye_WidthData(self,c01,c12,c23,channel=0):
        ui_interval = 128
        # move to left boundary
        phase = self.mApb.read(0x61008,channel)
        self.SetEomPosition(-int(ui_interval/2),channel)
        # collect
        w01 = []
        w12 = []
        w23 = []
        self.mApb.write(0x60100, 0<<6, channel, 1<<6) # eom_data
        phase = self.mApb.read(0x61008,channel)
        for i in range(0,int(1.5*ui_interval),1):
            # set PI
            phase = phase+1
            phase = phase-512 if phase>=512 else phase
            self.mApb.write(0x61008,phase,channel)
            # collect eom
            self.mApb.write(0x60100, 0<<7, channel, 1<<7) # turn off
            self.mApb.write(0x60100, 1<<7, channel, 1<<7) # turn on
            Delay(10)
            w01.append(self.mApb.read(0x63010+4*c01,channel))
            w12.append(self.mApb.read(0x63010+4*c12,channel))
            w23.append(self.mApb.read(0x63010+4*c23,channel))
        return w01,w12,w23
    def GetEye_HnC(self,height_data,bot,top):
        zero_min = -1
        zero_max = -1
        if len(height_data) < top:
            return 0,0
        for i in range(max(0,bot),max(0,top)):
            if (zero_min < 0) and height_data[i] <= self.mCfg.histo_zero_thld:
                zero_min = i
            if (zero_min >= 0) and (zero_max < 0) and height_data[i] > self.mCfg.histo_zero_thld:
                zero_max = i
        height = zero_max-zero_min
        center = int((zero_max+zero_min)/2)
        return (height,center)
    def GetEye_HeightData(self,target=range(128),channel=0):
        data = []
        self.mApb.write(0x60100, 1<<6|0<<7, channel, 1<<6|1<<7) # turn off, data_path(1:normal,0:eom)
        self.mApb.write(0x60100, 1<<7, channel, 1<<7) # turn on
        Delay(10)
        for i in target:
            data.append(self.mApb.read(0x63010+4*i,channel))
        return data
    def SetEomZeroPosition(self,channel=0):
        curPhase = self.mApb.read(0x61008,channel)
        self.mApb.write(0x61018,0xc017,channel) #?
        while (curPhase !=0 and curPhase != 512):
            if (curPhase > 256):
                curPhase += 1
            else:
                curPhase -= 1
            self.mApb.write(0x61008,curPhase,channel)
    def SetEomPosition(self,target=0,channel=0):
        curPhase = self.mApb.read(0x61008,channel)
        self.mApb.write(0x61018,0xc017,channel) #?
        unsigned_target = target if target >= 0 else target+512
        if unsigned_target > curPhase:
            direction = 1 if abs(unsigned_target-curPhase) < abs(512+curPhase-unsigned_target) else 0
        else:
            direction = 1 if abs(curPhase-unsigned_target) > abs(512+unsigned_target-curPhase) else 0
        while (curPhase != unsigned_target):
            if direction == 1:
                curPhase += 1
                curPhase = 0 if curPhase==512 else curPhase
            else:
                curPhase -= 1
                curPhase = 511 if curPhase==-1 else curPhase
            self.mApb.write(0x61008,curPhase,channel)
    def GetEye_GetCenterPhase(self,height_center=64,channel=0):
        center_data = []
        eom_beg_ptr = -64
        self.mApb.write(0x60100, 0<<6, channel, 1<<6) # eom_data
        self.SetEomPosition(eom_beg_ptr,channel)
        phase = self.mApb.read(0x61008,channel)
        for i in range(0,128,1):
            phase += 1
            phase = phase-512 if phase>=512 else phase
            self.mApb.write(0x61008,phase,channel)
            # collect eom
            self.mApb.write(0x60100, 0<<7, channel, 1<<7) # turn off
            self.mApb.write(0x60100, 1<<7, channel, 1<<7) # turn on
            Delay(10)
            center_data.append(self.mApb.read(0x63010+4*height_center,channel))
        phase_beg = 0
        phase_len = 0
        state   = 'IDLE'
        for i,cnt in enumerate(center_data):
            phase = i+eom_beg_ptr
            if phase >= 512:
                phase -=512
            elif phase < 0:
                phase += 512
            if state == 'IDLE':
                if cnt <= self.mCfg.eom_zero_thld:
                    phase_beg = phase
                    phase_len += 1
                    state = 'FOUND_BEG'
            elif state == 'FOUND_BEG':
                if cnt > self.mCfg.eom_zero_thld:
                    state = 'FOUND_END'
                else:
                    phase_len += 1
        center = phase_beg + int(phase_len/2)
        center = center-512 if center >= 512 else center
        return center
    def GetEye_GetEomThld(self,center,height,phase,channel=0):
        self.SetEomPosition(phase,channel)
        self.mApb.write(0x60100, 0<<6, channel, 1<<6) # eom_data
        self.mApb.write(0x60100, 0<<7, channel, 1<<7) # turn off
        self.mApb.write(0x60100, 1<<7, channel, 1<<7) # turn on
        Delay(10)
        height_half = int(height/2)
        thld_data = []
        for i in range(max(0,center-height_half),center+height_half+1):
            thld_data.append(self.mApb.read(0x63010+4*i,channel))
        if len(thld_data) > 0:
            return max(thld_data)
        else:
            return 0
    def GetStatus(self,measure_bits_db=30,extra_ber_en=1,HeightOnly=1,lin_fit_en=1,lin_fit_point=41,lin_fit_main=10,imp_eq_out=0,channel=0):
        result = {}
        # TxEQ
        result['tx_pre2'] = self.tx_pre2[channel]
        result['tx_pre1'] = self.tx_pre1[channel]
        result['tx_post1'] = self.tx_post1[channel]
        result['attenuation'] = self.attenuation[channel]
        # RxEQ
        for rx_tap in range(-2,0):
            result['rx_pre'+str(abs(rx_tap))] = round(self.GetRxEqCoef(rx_tap,channel)/128.0,2)
        result['rx_main'] = round(self.GetRxEqCoef(0,channel)/128.0,2)
        for rx_tap in range(1,9):
            result['rx_post'+str(rx_tap)] = round(self.GetRxEqCoef(rx_tap,channel)/128.0,2)
        # AMP
        result['rx_ctle'] = 15-(self.mApb.read(0x60020,channel)&0xf)
        result['rx_vga1'] = (self.mApb.read(0x6002c,channel)&0x1f)
        result['rx_vga2'] = 15-(self.mApb.read(0x60028,channel)&0xf)
        result['rx_adcgain'] = 7-((self.mApb.read(0x60034,channel)>>6) & 0x7)
        result['cboost'] = self.cboost[channel]
        # BER/EYE
        result['ber'] = self.GetBer(measure_bits_db,channel)
        if(extra_ber_en==1):
            result['voltage_margin'],result['extra_ber']=self.get_extra_ber(pam4=self.is_pam4_rate(self.mCfg.data_rate),ln_i=channel)
        else:
            result['voltage_margin'],result['extra_ber']=[[0]],[[0,0,0]]
        eye = self.meas_eye(HeightOnly,channel)
        #eye = (0,0,0,0,0,0)
        result['eye01_height'] = eye[0]
        result['eye01_width']  = eye[1]
        result['eye12_height'] = eye[2]
        result['eye12_width']  = eye[3]
        result['eye23_height'] = eye[4]
        result['eye23_width']  = eye[5]
        # linear fit
        if lin_fit_en==1:
            result['lin_fit_x'],result['lin_fit_y'] = self.lin_fit_pulse(num_point=lin_fit_point,main=lin_fit_main,eq_out=imp_eq_out,channel=channel)

        return result
    def get_extra_ber(self, pam4, ln_i):
        memSize = 128
        curPhase = self.mApb.read(0x00061008, ln_i)
        self.mApb.write(0x00061018, 0xc017, ln_i)
        while (curPhase != 0 and curPhase != 512):
            if (curPhase > 256):
                curPhase += 1
            else:
                curPhase -= 1
            self.mApb.write(0x00061008, curPhase, ln_i)
        countNumOrg = (self.mApb.read(0x00061000, ln_i) & 0x7f) >> 3
        self.mApb.write(0x00061000, 0xf<<3, channel=ln_i, mask=0xf<<3)
        countNum = 29
        filename = self.mCfg.dump_abs_path + "histo_data_" +self.mCfg.GetCondition()+ "_ln" + str(ln_i) + "_count" + str(countNum) + ".txt"
        dataTemp = self.mApb.read(0x00060100, ln_i)
        dataTemp = dataTemp & 0xBF
        dataTemp = dataTemp | 0x40
        self.mApb.write(0x00060100, dataTemp & 0x7F, ln_i)
        self.mApb.write(0x00060100, dataTemp | 0x80, ln_i)
        Delay(100)
        fs = open(filename, 'w')
        for mem_i in range(memSize):
            memAdd = 0x00063010 + mem_i * 4
            data = self.mApb.read(memAdd, ln_i)
            fs.write("%s %s\n" % (str(mem_i), str(data)))
        fs.close()
        if self.is_bbpd_rate(self.mCfg.data_rate):
            countNum = 16
            self.mApb.write(0x00061000, 0x2<<3, channel=ln_i, mask=0xf<<3)
        else:
            countNum = 18
            self.mApb.write(0x00061000, 0x4<<3, channel=ln_i, mask=0xf<<3)
        filename2 = self.mCfg.dump_abs_path + "histo_data_" +self.mCfg.GetCondition()+ "_ln" + str(ln_i) + "_count" + str(countNum) + ".txt"
        dataTemp = self.mApb.read(0x00060100, ln_i)
        dataTemp = dataTemp & 0xBF
        dataTemp = dataTemp | 0x40
        self.mApb.write(0x00060100, dataTemp & 0x7F, ln_i)
        self.mApb.write(0x00060100, dataTemp | 0x80, ln_i)
        Delay(100)
        fs = open(filename2, 'w')
        for mem_i in range(memSize):
            memAdd = 0x00063010 + mem_i * 4
            data = self.mApb.read(memAdd, ln_i)
            fs.write("%s %s\n" % (str(mem_i), str(data)))
        fs.close()
        self.mApb.write(0x00061000, countNumOrg<<3, channel=ln_i, mask=0xf<<3)
        vrefSel= ((self.mApb.read(0x60034,ln_i)>>6) & 0x7)
        if (pam4== 1):
            return evb_extra.bathtub_extrapolation_vertical(filename, filename2, 29, countNum,1,vrefSel,self.mCfg.extra_ber_pam4_margin_list)
        else:
            return evb_extra.bathtub_extrapolation_vertical(filename, filename2, 29, countNum,0,vrefSel,self.mCfg.extra_ber_nrz_margin_list)
    def GetAdcMinMax(self,adc_channel=0,channel=0,mon_sel=0,repeat=1):
        # to disable the use by h/w(rx_main)
        org_value = self.mApb.read(0x6051C,channel)
        self.mApb.write(0x6051C,0,channel)
        # measure
        minval = 0
        maxval = 0
        for i in range(repeat):
            self.mApb.write(0x62248,adc_channel<<4|mon_sel<<2|1,channel)
            Delay(self.mCfg.adc_measure_time)
            rdata = self.mApb.read(0x6224C,channel)
            minval += (rdata&0xff)
            maxval += ((rdata>>8)&0xff)
            self.mApb.write(0x62248,0,channel)
        minval = int(minval/repeat)
        maxval = int(maxval/repeat)
        # rollback
        self.mApb.write(0x6051C,org_value,channel)
        if mon_sel==1:
            minval = minval-128
            maxval = maxval-128
        return (minval,maxval)
    def GetBer(self, measure_bits_db=30 ,channel=0):
        # calculate measure time
        if self.is_bbpd_rate(self.mCfg.data_rate):
            sfr_measure = measure_bits_db - 4
        elif self.is_pam4_rate(self.mCfg.data_rate):
            sfr_measure = measure_bits_db - 6
        else:
            sfr_measure = measure_bits_db - 5
        sfr_measure = max(1,sfr_measure)
        sfr_measure = min(31,sfr_measure)
        measure_time = 250 * (2**(max(27,sfr_measure)-26))
        # set measure time, restart
        self.mApb.write(0x60174, 0, channel, mask=1)
        self.mApb.write(0x60208, sfr_measure<<4, channel, mask=0x1f<<4)
        self.mApb.write(0x60174, 1, channel, mask=1)
        # calculate ber
        Delay(measure_time)
        data = self.mApb.read(0x00060700,channel)
        if ((data & 0x3) != 0):
            cnt  = self.mCfg.ber_init_cnt
            cnt += self.mApb.read(0x00060704,channel)
            cnt += (self.mApb.read(0x00060708,channel) << 10)
            cnt += (self.mApb.read(0x0006070C,channel) << 20)
            cnt += (self.mApb.read(0x00060710,channel) << 30)
            if self.mCfg.b_dbg_print:
                print ("cnt=%d,bits=%d"%(cnt,measure_bits_db))
            ber = cnt / (1<<measure_bits_db)
        else:
            ber  = self.mCfg.ber_fail_value
        return ber
    def GetRxEqCoef(self,tap,channel=0,repeat=1):
        regmap = ([0x2274,0x2270,0x223C] + [0x2250+4*i for i in range(8)])
        addr   = regmap[(tap+2)]+0x60000
        coef_sum = 0
        for i in range(repeat):
            coef_sum += self.get_signed_code(self.mApb.read(addr,channel))
        return int(coef_sum/repeat)
#}}}
#----------------------------------------------------------------------------------------------------
# Config - base
#----------------------------------------------------------------------------------------------------
#{{{
    def SetCmnStart(self):
        self.mApb.write(0x00064, 0x0011)
    def SetCmnBase(self):
        self.mApb.write(0x00000000, 0x00000431)
        self.mApb.write(0x00000004, 0x00000024)  #[DIFF] 2c
        self.mApb.write(0x00000008, 0x00000800)
        self.mApb.write(0x00000010, 0x000000a9)
        self.mApb.write(0x00000014, 0x00000005)
        self.mApb.write(0x00000018, 0x00000000)
        self.mApb.write(0x00000020, 0x00000001)
        self.mApb.write(0x00000028, 0x00000200)
        self.mApb.write(0x00000030, 0x000014fc)
        self.mApb.write(0x00000038, 0x00000000)
        self.mApb.write(0x00000048, 0x00000000)
        self.mApb.write(0x0000004c, 0x00002743)  #[DIFF] 3ff3
        self.mApb.write(0x00000050, 0x00000f08)
        self.mApb.write(0x00000054, 0x00000000)
        self.mApb.write(0x00000058, 0x00000000)
        self.mApb.write(0x0000005c, 0x00000000)
        self.mApb.write(0x00000060, 0x00000000)
        self.mApb.write(0x00000064, 0x00000010)
        self.mApb.write(0x00000068, 0x000000ff)
        self.mApb.write(0x0000006c, 0x00000800) #[DIFF] 320
        self.mApb.write(0x00000070, 0x00000800) #[DIFF] 320
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
        self.mApb.write(0x00000300, 0x00000003) #[DIFF] 0
        self.mApb.write(0x00000304, 0x0000000a)
    def SetTxBase(self, channel=0):
        en_10g = 1 if self.is_bbpd_rate(self.mCfg.data_rate) else 0
        dw_64b = 1 if self.is_pam4_rate(self.mCfg.data_rate) else 0
        self.mApb.write(0x50000, 0x0001, channel)   # force dcc i code -> @ 201 force dcc ib_code
        self.mApb.write(0x50004, 0x0002, channel)
        self.mApb.write(0x50008, 0x0000, channel)
        self.mApb.write(0x5000c, 0x2040, channel)   # @ dcc force code value -> 1040
        self.mApb.write(0x50014, 0x0401, channel)   # tx drv cap en [0]
        self.mApb.write(0x50018, en_10g<<0, channel)
        self.mApb.write(0x50020, 0x0002, channel)   # lane bias
        self.mApb.write(0x50024, 0x0000, channel)
        self.mApb.write(0x50044, 0x0000, channel)
        self.mApb.write(0x50050, 0x0000, channel)
        self.mApb.write(0x50054, 0x0000, channel)
        if not self.mCfg.b_prot_en:
            self.mApb.write(0x50080, 0x001e, channel)
        self.mApb.write(0x50084, 0x0000, channel)
        self.mApb.write(0x50088, 0x0000, channel)
        self.mApb.write(0x5008c, 0x0000, channel)
        self.mApb.write(0x50090, 0x0000, channel)
        self.mApb.write(0x50100, 0x0002| en_10g<<6, channel)
        self.mApb.write(0x50104, 0x0200| dw_64b<<5, channel)
        self.mApb.write(0x50108, 0x007f, channel)
        self.mApb.write(0x5010c, 0x1aa0, channel)
        self.mApb.write(0x50110, 0xffff, channel)
        self.mApb.write(0x50114, 0x7fff, channel)
        self.mApb.write(0x50118, 0xaaaa, channel)
        self.mApb.write(0x5011c, 0xaaaa, channel)
        self.mApb.write(0x50120, 0xaaaa, channel)
        self.mApb.write(0x50124, 0xaaaa, channel)
        self.mApb.write(0x50128, 0x0cd8, channel)   # DCC Cal 1 option cd8
        self.mApb.write(0x5012c, 0x0018, channel)   # dcc ib en [4] @ off-> cal i only
        self.mApb.write(0x50130, 0x000f, channel)
        self.mApb.write(0x50134, 0x0000, channel)   # dcc add code en [8]
        self.mApb.write(0x50138, 0x0000, channel)   # dcc i add code [3:0]
        self.mApb.write(0x50150, 0x0000, channel)
        self.mApb.write(0x50154, 0x0403, channel)
        self.mApb.write(0x50158, 0x0000, channel)
        self.mApb.write(0x5015c, 0x0064, channel)
        self.mApb.write(0x50160, 0x0000, channel)
        self.mApb.write(0x50164, 0x000a, channel)
        self.mApb.write(0x50400, 0x0000, channel)
        self.mApb.write(0x50500, 0x0000, channel)   # tx dcc cal skip [0]
        self.mApb.write(0x50504, 0x0001, channel)   # an_bypass
        self.mApb.write(0x5050c, 0x0002, channel)   # ser_clk_en_time default 2
        self.mApb.write(0x50510, 0x0002, channel)   # comp_cal_en_time default 2
        self.mApb.write(0x50514, 0x0002, channel)   # an_ser_d_rstn_time default 2
        self.mApb.write(0x50518, 0x0002, channel)   # tx_an_en_dis_time
        self.mApb.write(0x5051c, 0x0000, channel)
        self.mApb.write(0x50600, 0x0000, channel)
        self.mApb.write(0x50604, 0x003c, channel)
        self.mApb.write(0x50608, 0x0006, channel)
        self.mApb.write(0x5060c, 0x0211, channel)
        self.mApb.write(0x50610, 0x0d7a, channel)
        self.mApb.write(0x50614, 0x0000, channel)
        self.mApb.write(0x50618, 0x0000, channel)
        self.mApb.write(0x5061c, 0x00c1, channel)
        self.mApb.write(0x50620, 0x0043, channel)
        self.mApb.write(0x50624, 0x00c1, channel)
        self.mApb.write(0x50628, 0x0043, channel)
        self.mApb.write(0x5062c, 0x00c1, channel)
        self.mApb.write(0x50630, 0x0043, channel)
        self.mApb.write(0x50634, 0x00c1, channel)
        self.mApb.write(0x50638, 0x0043, channel)
        self.mApb.write(0x5063c, 0x0075, channel)
        self.mApb.write(0x50640, 0x0880, channel)
        self.mApb.write(0x50644, 0x0075, channel)
        self.mApb.write(0x50648, 0x0280, channel)
        self.mApb.write(0x5064c, 0x0100, channel)
        self.mApb.write(0x50650, 0x0000, channel)
        self.mApb.write(0x50654, 0x0100, channel)
        self.mApb.write(0x50658, 0x0000, channel)
        self.mApb.write(0x5065c, 0x0100, channel)
        self.mApb.write(0x50660, 0x0000, channel)
        self.mApb.write(0x50664, 0x0100, channel)
        self.mApb.write(0x50668, 0x0000, channel)
        self.mApb.write(0x5066c, 0x0000, channel)
        self.mApb.write(0x50670, 0x0072, channel)
        self.mApb.write(0x50674, 0x0000, channel)
    def SetRxBase(self, channel=0):
        en_10g = 1 if self.is_bbpd_rate(self.mCfg.data_rate) else 0
        dw_64b = 1 if self.is_pam4_rate(self.mCfg.data_rate) else 0
        self.mApb.write(0x60000, 0x0000, channel)
        self.mApb.write(0x60004, 0x0000, channel)
        self.mApb.write(0x60008, 0x0000, channel)
        self.mApb.write(0x6000c, 0x0000, channel)
        self.mApb.write(0x60010, 0x0080, channel)   # vga3 offset code force [8] en [7:0] val debugging by who 190909
        self.mApb.write(0x60014, 0x0080, channel)   # vga2 offset code force [8] en [7:0] val debugging by who 190909
        self.mApb.write(0x60018, 0x0080, channel)   # vga1 offset code force [8] en [7:0] val debugging by who 190909
        self.mApb.write(0x6001c, 0x0000, channel)
        self.mApb.write(0x60020, 0x001e, channel)   # hfeq r sel force [4] en [3:0] value high -> gain low
        self.mApb.write(0x60028, 0x0010, channel)   # vga2 r sel force [4] en [3:0] value high -> gain low
        self.mApb.write(0x6002C, 0x0027, channel)   # vga1 r sel force [5] en [4:0] value high -> gain high
        self.mApb.write(0x60034, 0x0121, channel)   # adc vref sel [8:6]
        self.mApb.write(0x60038, ((1 << 14) + (0 << 10) + (9 << 5) + 9), channel)   # hfef c sel [13:10] i ctrl [9:5], rl ctrl [4:0]
        self.mApb.write(0x6003c, 0x00000060, channel)   # adc i ctrl
        self.mApb.write(0x60040, 0x000000ff, channel)   # 0x30 -> 0xff by who 190906
        self.mApb.write(0x60044, 0x0000000c, channel)
        self.mApb.write(0x60048, 0x0000799f, channel)   # afe cm ctrl [15:12] peq [11:8] acc,adc 0x7690 -> 0x799f by who 190906
        self.mApb.write(0x6004c, 0x00000007, channel)   # slb term ctrl [1:0]
        self.mApb.write(0x60050, ((0 << 7) + (0 << 3) + 4+3), channel)   # vga1 dac lsb ctrl [1:0] 0->3, i ctrl [6:3], dac pull up [2] 40
        self.mApb.write(0x60054, ((18 << 11) + (13 << 7) + (14 << 3)), channel)   # vga2 dac lsb ctrl [1:0] 0->3, rs [15:11] i ctrl [6:3], dac pull up [2] 40
        self.mApb.write(0x60058, 0x00000000, channel)   # peq c sel [11:8], peq r sel [7:2]
        self.mApb.write(0x6005c, 0x00000004, channel)
        self.mApb.write(0x60060, 0x00000052, channel)   # hfeq eq en [4]
        self.mApb.write(0x60064, 0x0000060C, channel)   # pi slew ctrl 7->1 [12:10] pi str [3:0] 0x60f -> 0x60c by who 190906
        self.mApb.write(0x60068, 0x00000000, channel)
        self.mApb.write(0x60078, 0x00000000, channel)
        self.mApb.write(0x60080, 0x00000000, channel)
        self.mApb.write(0x60084, 0x00000000, channel)
        if not self.mCfg.b_prot_en:
            self.mApb.write(0x60088, 0x0000007f, channel)
        #self.mApb.write(0x60088, 0x00000008, channel)   # debugging by who 190909
        self.mApb.write(0x6008c, 0x00000040, channel)
        self.mApb.write(0x60090, 0x00000000, channel)
        self.mApb.write(0x60094, 0x00000000, channel)
        self.mApb.write(0x60098, 0x00000700, channel)
        self.mApb.write(0x60100, 0x000000a0, channel)
        self.mApb.write(0x60104, 0x00004202, channel)   # c else lock thres [13:8] c0 lock thres [5:0]
        self.mApb.write(0x60108, 0x00007b74, channel)   # u value change after lock [15] 0x7b7d -> 0x7b74 by who 190906
        self.mApb.write(0x6010c, 0x00007420, channel)   # c0_h init [7:0] c0_h u value [12:10]
        self.mApb.write(0x60110, 0x00000000, channel)
        self.mApb.write(0x60114, 0x0000700f, channel)   # c0_l init [7:0] c0_h u value [12:10]
        self.mApb.write(0x60118, 0x00000000, channel)
        self.mApb.write(0x6011c, 0x00000000, channel)
        self.mApb.write(0x60120, 0x00000000, channel)
        self.mApb.write(0x60124, 0x00000000, channel)
        self.mApb.write(0x60128, 0x00000000, channel)
        self.mApb.write(0x6012c, 0x00000000, channel)   # c_post1_init  0xc0 -> 0x00 by who 190906
        self.mApb.write(0x60130, 0x00000000, channel)
        self.mApb.write(0x60134, 0x00000000, channel)
        self.mApb.write(0x60138, 0x00000000, channel)
        self.mApb.write(0x6013c, 0x00000000, channel)
        self.mApb.write(0x60140, 0x00000000, channel)
        self.mApb.write(0x60144, 0x00000000, channel)
        self.mApb.write(0x60148, 0x00000000, channel)
        self.mApb.write(0x6014c, 0x00000000, channel)
        self.mApb.write(0x60150, 0x00000000, channel)
        self.mApb.write(0x60154, 0x00000000, channel)
        self.mApb.write(0x60158, 0x00000000, channel)
        self.mApb.write(0x6015c, 0x00000000, channel)
        self.mApb.write(0x60160, 0x00000000, channel)
        self.mApb.write(0x60164, 0x00000000, channel)
        self.mApb.write(0x60168, 0x00000000, channel)
        self.mApb.write(0x6016c, 0x000006ff, channel)   # c1 ctrl cond sel [9:8], ctrl set [15:10]
        self.mApb.write(0x60170, 0x00000000, channel)   # c1 control disable [12]
        self.mApb.write(0x60174, 0x00008200|dw_64b<<5, channel)
        self.mApb.write(0x60178, 0x0000ffff, channel)
        self.mApb.write(0x6017c, 0x00000000, channel)
        self.mApb.write(0x60180, 0x0000ffff, channel)
        self.mApb.write(0x60184, 0x00000000, channel)
        self.mApb.write(0x60188, 0x00000000, channel)
        self.mApb.write(0x6018c, 0x00000383, channel)
        self.mApb.write(0x60190, 0x00000000, channel)
        self.mApb.write(0x60194, 0x0000f464, channel)
        self.mApb.write(0x60198, 0x00001012, channel)   # sq thres [14:8], ch sel [7:2], duration [1:0] # 812 0x612 -> 0x1012 by who 190906
        self.mApb.write(0x601a0, 0x00000010, channel)   # adc cal stable cnt
        self.mApb.write(0x601a4, 0x00000021, channel)
        self.mApb.write(0x601a8, 0x00001000, channel)   # adc cal lock cnt
        self.mApb.write(0x601ac, 0x00000427, channel)   # adc bg cal en [1] adc sleep mode en[2] fine cal bw 0x421 -> 0x427 by who 190906
        self.mApb.write(0x601b0, 0x0000ffff, channel)   # adc bg cal counter 0x2000 -> 0xffff by who 190906
        self.mApb.write(0x601bc, 0x0000017d, channel)
        self.mApb.write(0x601c0, 0x00000b7d, channel)
        self.mApb.write(0x601c4, 0x00000013, channel)   # [JC] to coef reinit when restart
       #self.mApb.write(0x601c4, 0x00000010, channel)   # [JC] to coef reinit when restart debugging by who 190909
        self.mApb.write(0x601c8, 0x00002710, channel)
        self.mApb.write(0x601cc, 0x000001fe, channel)   # power rdc en [0]
        self.mApb.write(0x601d0, 0x00000082, channel)   # c else lock init [11:6] c0 lock init [5:0]
        self.mApb.write(0x601d4, 0x0000FFFF, channel)
        self.mApb.write(0x601d8, 0x00000400, channel)
        self.mApb.write(0x601dc, 0x00000000, channel)
        self.mApb.write(0x601e0, 0x00000000, channel)  # detect force en / value
        self.mApb.write(0x601e4, 0x00000020, channel)
        self.mApb.write(0x601e8, 0x00000020, channel)
        self.mApb.write(0x601ec, 0x00000000, channel)
        self.mApb.write(0x601f0, 0x0000007f, channel)
        self.mApb.write(0x601f4, 0x00000081, channel)
        self.mApb.write(0x601f8, 0x00000efb, channel)   # c else lock cnt set
        self.mApb.write(0x60200, 256 - 30, channel)     # c1 compare offset 256-26 -> 256-30 by who 190906
        self.mApb.write(0x60204, 0x00000003, channel)   # bist error ind
        self.mApb.write(0x60208, 0x00000190, channel)   # bist measure time [8:4] 0x19 => 10^9 in 25/10G
        self.mApb.write(0x60400, 0x00000004, channel)   # coef no mux 10g [2]
        self.mApb.write(0x60500, 0x00008608, channel)   # fine cal skip
        self.mApb.write(0x60504, 0x00000031, channel)   # an bypass [0], skew on fine [12]
        self.mApb.write(0x60508, 0x00000020, channel)   # ioc full skip E2? 20? 0xc0 -> 0x20 by who 190906
        self.mApb.write(0x6050c, 0x00001000, channel)   # dsp eq wait time
        self.mApb.write(0x60510, 0x00000000, channel)
        self.mApb.write(0x60518, 0x00000400, channel)   # adc_pi_clk_en_time
        self.mApb.write(0x6051c, 0x00000000, channel)   # adc mon wait cnt (if '0' adc mon =0 @ normal)
        self.mApb.write(0x60520, 0x00008000, channel)
        self.mApb.write(0x60524, 0x0000000f, channel)   # 0x40 -> 0x0f by who 190906
        self.mApb.write(0x60528, 0x00000400, channel)
        self.mApb.write(0x6052c, 0x00000000, channel)
        self.mApb.write(0x60530, 0x0000ffff, channel)
        self.mApb.write(0x60534, 0x0000000f, channel)
        self.mApb.write(0x60538, 0x00000000, channel)
        self.mApb.write(0x6053c, 0x00000000, channel)   # skew cal skip [15:8], bypass [7:0]
        self.mApb.write(0x60540, 0x00000001, channel)   # pi in skew cal skip
        self.mApb.write(0x60544, 0x00000007, channel)
        self.mApb.write(0x60548, 0x00000078, channel)   # 0x68 -> 0x78 by who 190906
        self.mApb.write(0x60550, 0x0000000e, channel)
        self.mApb.write(0x60554, 0x0000000e, channel)
        self.mApb.write(0x60558, 0x0000000d, channel)
        self.mApb.write(0x6055c, 0x00000006, channel)
        self.mApb.write(0x60560, 0x00000003, channel)
        self.mApb.write(0x60564, 0x00000002, channel)
        self.mApb.write(0x60568, 0x00000001, channel)
        self.mApb.write(0x6056c, 0x00000000, channel)
        self.mApb.write(0x60590, 0x00000f00, channel)
        self.mApb.write(0x609b0, 0x00000400, channel)   # skew lock cnt
        self.mApb.write(0x609b4, 0x00000002, channel)   # skew lock tol
        self.mApb.write(0x61000, 0x00000180|self.mCfg.histo_meastime<<3, channel)   # eom accu time
        self.mApb.write(0x61004, 0x00000000, channel)   # eom pi sel [0] 0: addition 1: absolute
        self.mApb.write(0x61008, 0x00000000, channel)
        self.mApb.write(0x61018, 0x00007017, channel)
        self.mApb.write(0x6101c, 0x00000000, channel)
        self.mApb.write(0x61020, 0x00000000, channel)
        self.mApb.write(0x61024, 0x00000000, channel)
        self.mApb.write(0x62000, 0x00000000, channel)
        self.mApb.write(0x62004, 0x00000000, channel)
        self.mApb.write(0x62008, 0x00000000, channel)
        self.mApb.write(0x6200c, 0x00000000, channel)
        self.mApb.write(0x62010, 0x00000000, channel)
        self.mApb.write(0x62014, 0x00000000, channel)
        self.mApb.write(0x62018, 0x00000000, channel)
        self.mApb.write(0x6201c, 0x00000000, channel)
        self.mApb.write(0x62020, 0x00000000, channel)
        self.mApb.write(0x62024, 0x00000000, channel)
        self.mApb.write(0x62028, 0x00000000, channel)
        self.mApb.write(0x6202c, 0x00000000, channel)
        self.mApb.write(0x62030, 0x00000000, channel)
        self.mApb.write(0x62034, 0x00000000, channel)
        self.mApb.write(0x62038, 0x00000000, channel)
        self.mApb.write(0x6203c, 0x00000000, channel)
        self.mApb.write(0x62040, 0x00000000, channel)
        self.mApb.write(0x62044, 0x00000000, channel)
        self.mApb.write(0x62048, 0x00000000, channel)
        self.mApb.write(0x6204c, 0x00000000, channel)
        self.mApb.write(0x62050, 0x00000000, channel)
        self.mApb.write(0x62054, 0x00000000, channel)
        self.mApb.write(0x62058, 0x00000000, channel)
        self.mApb.write(0x6205c, 0x00000000, channel)
        self.mApb.write(0x62060, 0x00000000, channel)
        self.mApb.write(0x62064, 0x00000000, channel)
        self.mApb.write(0x62068, 0x00000000, channel)
        self.mApb.write(0x6206c, 0x00000000, channel)
        self.mApb.write(0x62070, 0x00000000, channel)
        self.mApb.write(0x62074, 0x00000000, channel)
        self.mApb.write(0x62078, 0x00000000, channel)
        self.mApb.write(0x6207c, 0x00000000, channel)
        self.mApb.write(0x62080, 0x00000000, channel)
        self.mApb.write(0x62084, 0x00000000, channel)
        self.mApb.write(0x62088, 0x00000000, channel)
        self.mApb.write(0x6208c, 0x00000000, channel)
        self.mApb.write(0x62090, 0x00000000, channel)
        self.mApb.write(0x62224, 0x00000000, channel)   # debugging by who 190909
        self.mApb.write(0x62248, 0x00000004, channel)   # adc mon sel [2] 1: cal out, debugging by who 190909
        self.mApb.write(0x63300, 0x0000ffff, channel)
        self.mApb.write(0x63304, 0x0000ffff, channel)
        self.mApb.write(0x63308, 0x00000010, channel)  # full cal vga sel [4] 1 : vga2 0: vga1 0x02 -> 0x10 by who 190906
        self.mApb.write(0x6330c, 0x00000fff, channel)  # ioc_wait_cnt2  0x001 -> 0xfff by who 190906
        self.mApb.write(0x63430, 0x00000040, channel)
        self.mApb.write(0x63434, 0x00000040, channel)
        self.mApb.write(0x63438, 0x00000040, channel)
        self.mApb.write(0x6343c, 0x00000040, channel)
        self.mApb.write(0x63440, 0x00000040, channel)
        self.mApb.write(0x63444, 0x00000040, channel)
        self.mApb.write(0x63448, 0x00000040, channel)
        self.mApb.write(0x6344c, 0x00000040, channel)
        self.mApb.write(0x63450, 0x0000000b, channel)   # skew hold en [12]
        self.mApb.write(0x63454, 0x00005590, channel)   # bbpd en[9] / pd_sel[15:14]
        self.mApb.write(0x63458, 0x00000064, channel)
        self.mApb.write(0x6345c, 0x0000ff00, channel) # [15:8] skew cal en 0x0000 -> 0xff00 by who 190906
        self.mApb.write(0x63460, 0x000000c8, channel)
        self.mApb.write(0x63464, 0x00000000, channel)
        self.mApb.write(0x63468, 0x00000100, channel)
        self.mApb.write(0x6346c, 0x00000060, channel)
        self.mApb.write(0x63470, 0x00000000, channel)
        self.mApb.write(0x63474, 0x000060ff, channel) # ioc compare done num[13:8] (0813 : 10 -> 20) ioc wait cnt [7:0] (0813 : 40 -> ff)  0x5040 -> 0x60ff by who 190906
        self.mApb.write(0x63478, 0x00000080, channel) # default 0x80, cal bypass [6:1] ([1] : VGA2 / [2] : VGA3 / [3] : VGA1 / [4] : FULL CAL) 0xf0 -> 0x80 by who 190906
        self.mApb.write(0x6347c, 0x00009000, channel) # check num [13:10]
        self.mApb.write(0x63480, 0x00000000, channel)
        self.mApb.write(0x63484, 0x00000000, channel)
        self.mApb.write(0x63488, 0x00000000, channel)
        self.mApb.write(0x6348c, 0x00000000, channel)
        self.mApb.write(0x63490, 0x00000000, channel)
        self.mApb.write(0x63494, 0x00000000, channel)
        self.mApb.write(0x63498, 0x00000000, channel)
        self.mApb.write(0x6349c, 0x00000000, channel)
        self.mApb.write(0x634a0, 0x00000000, channel)
        self.mApb.write(0x634a4, 0x00000000, channel)
        self.mApb.write(0x634a8, 0x00000000, channel)
        self.mApb.write(0x634ac, 0x00000000, channel)
        self.mApb.write(0x634b0, 0x00000000, channel)
        self.mApb.write(0x634b4, 0x00000000, channel)
        self.mApb.write(0x634b8, 0x00000000, channel)
        self.mApb.write(0x634bc, 0x00000000, channel)
        self.mApb.write(0x634c0, 0x00000000, channel)
        self.mApb.write(0x634c4, 0x00000000, channel)
        self.mApb.write(0x634c8, 0x00000000, channel)
        self.mApb.write(0x634cc, 0x00000000, channel)
        self.mApb.write(0x634d0, 0x00000000, channel)
        self.mApb.write(0x634d4, 0x00000000, channel)
        self.mApb.write(0x634d8, 0x00000000, channel)
        self.mApb.write(0x634dc, 0x00000000, channel)
        self.mApb.write(0x634e0, 0x00000000, channel)
        self.mApb.write(0x634e4, 0x00000000, channel)
        self.mApb.write(0x634e8, 0x00000000, channel)
        self.mApb.write(0x634ec, 0x00000000, channel)
        self.mApb.write(0x634f0, 0x00000000, channel)
        self.mApb.write(0x634f4, 0x00000000, channel)
        self.mApb.write(0x634f8, 0x00000000, channel)
        self.mApb.write(0x634fc, 0x00000000, channel)
        self.mApb.write(0x63500, 0x00000000, channel)
        self.mApb.write(0x63504, 0x00000000, channel)   # main cal force
        self.mApb.write(0x63508, 0x00000101, channel)
        self.mApb.write(0x6350c, 0x00000000, channel)
        self.mApb.write(0x63510, 0x00000000, channel)
        self.mApb.write(0x63514, 0x00000000, channel)
        self.mApb.write(0x63518, 0x00000000, channel)
        self.mApb.write(0x6351c, 0x00000000, channel)
        self.mApb.write(0x63520, 0x00000000, channel)
        self.mApb.write(0x63524, 0x00000000, channel)
        self.mApb.write(0x63528, 0x00000000, channel)
        self.mApb.write(0x6352c, 0x00000000, channel)
        self.mApb.write(0x63530, 0x00000000, channel)
        self.mApb.write(0x63534, 0x00000000, channel)
        self.mApb.write(0x63538, 0x00000000, channel)
        self.mApb.write(0x6353c, 0x00000000, channel)
        self.mApb.write(0x63540, 0x00000000, channel)
        self.mApb.write(0x63544, 0x00000000, channel)
        self.mApb.write(0x63548, 0x00000000, channel)
        self.mApb.write(0x6354c, 0x00000000, channel)
        self.mApb.write(0x63550, 0x00000000, channel)
        self.mApb.write(0x63554, 0x00000000, channel)
        self.mApb.write(0x63558, 0x00000000, channel)
        self.mApb.write(0x6355c, 0x00000000, channel)
        self.mApb.write(0x63560, 0x00000000, channel)
        self.mApb.write(0x63564, 0x00000000, channel)
        self.mApb.write(0x63568, 0x00000000, channel)
        self.mApb.write(0x6356c, 0x00000000, channel)
        self.mApb.write(0x63570, 0x00000000, channel)
        self.mApb.write(0x63574, 0x00000000, channel)
        self.mApb.write(0x63578, 0x00000000, channel)
        self.mApb.write(0x6357c, 0x00000000, channel)
        self.mApb.write(0x63580, 0x00000000, channel)
        self.mApb.write(0x63584, 0x00000000, channel)
        self.mApb.write(0x63588, 0x00000000, channel)
        self.mApb.write(0x6358c, 0x00000000, channel)
        self.mApb.write(0x640a8, 0x00000000, channel)   # pi (cdr) force en
        self.mApb.write(0x640ac, 0x00000000, channel)
        self.mApb.write(0x640b0, 0x00000000, channel)
        self.mApb.write(0x640b4, 0x00000000, channel)   # pi force code
        self.mApb.write(0x6420c, 0x00000018, channel)
        self.mApb.write(0x64210, 0x00003333, channel)
        self.mApb.write(0x64214, 0x00003333, channel)
        self.mApb.write(0x64218, 0x00000000, channel)
        self.mApb.write(0x6421c, 0x00000000, channel)
        self.mApb.write(0x64224, 0x00000005, channel)   # pi skew control code
        self.mApb.write(0x64300, 0x000004f7, channel)   # pi skew thres [7:4] pi skew en [3:0] hold en [9] pd sel[11:10]
        self.mApb.write(0x64304, 0x00001000, channel)
        self.mApb.write(0x64308, 0x00000005, channel)
        self.mApb.write(0x6430c, 0x00000050, channel)   # pi in skew force
        self.mApb.write(0x64310, 0x00000050, channel)
        self.mApb.write(0x64314, 0x00000050, channel)
        self.mApb.write(0x64318, 0x00000050, channel)
        self.mApb.write(0x64320, 0x00000010, channel)   # pi in skew init
        self.mApb.write(0x64324, 0x00000010, channel)
        self.mApb.write(0x64328, 0x00000010, channel)
        self.mApb.write(0x6432c, 0x00000010, channel)
    def SetPll(self):
        if (self.mCfg.data_rate == 10.3125) :
            self.mApb.write(0x000000d8, 0x0000001a)  #pll sdiv [4]
            self.mApb.write(0x000000dc, 0x00004242)  # pll mdiv
            self.mApb.write(0x000000e4, 0x00000000)  # sdm en
            self.mApb.write(0x00000138, 0x00000001)  # 14g_en [6]
        elif (self.mCfg.data_rate == 25.78125) :
            self.mApb.write(0x000000d8, 0x0000001a)  #pll sdiv [4]
            self.mApb.write(0x000000dc, 0x00005252)  # pll mdiv
            self.mApb.write(0x000000e4, 0x00000004)  # sdm en
            self.mApb.write(0x00000138, 0x00000041)  # 14g_en [6]
        elif (self.mCfg.data_rate == 53.125) :
            self.mApb.write(0x000000d8, 0x0000001a)  #pll sdiv [4]
            self.mApb.write(0x000000dc, 0x00005555)  # pll mdiv 5555
            self.mApb.write(0x000000e4, 0x00000000)  # sdm en
            self.mApb.write(0x00000138, 0x00000041)  # 14g_en [6]
        elif (self.mCfg.data_rate == 56.25) :
            self.mApb.write(0x000000d8, 0x0000001a)  #pll sdiv [4]
            self.mApb.write(0x000000dc, 0x00005a5a)  # pll mdiv 5555
            self.mApb.write(0x000000e4, 0x00000000)  # sdm en
            self.mApb.write(0x00000138, 0x00000041)  # 14g_en [6]
        elif (self.mCfg.data_rate == 21.25) :
            self.mApb.write(0x000000d8, 0x0000002a)  #pll sdiv [4]
            self.mApb.write(0x000000dc, 0x00004444)  # pll mdiv
            self.mApb.write(0x000000e4, 0x00000000)  # sdm en
            self.mApb.write(0x00000138, 0x00000041)  # 14g_en [6]
        elif (self.mCfg.data_rate == 22.5) :
            self.mApb.write(0x000000d8, 0x0000002a)  #pll sdiv [4]
            self.mApb.write(0x000000dc, 0x00004848)  # pll mdiv
            self.mApb.write(0x000000e4, 0x00000000)  # sdm en
            self.mApb.write(0x00000138, 0x00000041)  # 14g_en [6]
    def SetTxBist(self, data_patt=0, en=1, channel=0):
        self.mApb.write(0x50104, data_patt<<2|en<<0, channel, 3<<2|1<<0)
        if self.mCfg.media_mode == 'SLB':
            self.mApb.write(0x60060, 1<<0, channel, 1<<0)
            self.mApb.write(0x50000, 1, channel, 1<<0)
            self.mApb.write(0x50004, 0, channel, 1<<0)
            self.mApb.write(0x50024, 1, channel, 1<<0)
    def SetTxRemote(self,en=1,channel=0):
        self.mApb.write(0x50100,en<<0|en<<4,channel,3<<0|1<<4)
    def SetRxBist(self, data_patt=0, en=1, channel=0):
        self.mApb.write(0x60174, data_patt<<2|en<<0, channel, 3<<2|1<<0)
        if self.mCfg.media_mode == 'SLB':
            self.mApb.write(0x60060, 1<<0, channel, 1<<0)
    def SetTxEqCmax(self, pre2=0x1FC0, pre1=0x1FC0,main=0x1FC0,post1=0x1FC0,channel=0):
        # c1, c0, cn1, cn2 max=0x3f(+max), min=0x40 (-max)
        self.mApb.write(0x0005063C, 0x1FC0, channel)
        self.mApb.write(0x00050640, 0x1FC0, channel)
        self.mApb.write(0x00050644, 0x1FC0, channel)
        self.mApb.write(0x00050648, 0x1FC0, channel)
    def SetTxEqEmax(self, pre2=0x1FC0, pre1=0x1FC0,main=0x1FC0, post1=0x1FC0,channel=0):
        # eq_max = 0x1ff (default 0x100),
        self.mApb.write(0x5064C, 0x01FF, channel)
        self.mApb.write(0x50654, 0x01FF, channel)
        self.mApb.write(0x5065C, 0x01FF, channel)
        self.mApb.write(0x50664, 0x01FF, channel)
    def SetTxEqStep(self,channel=0):
        self.mApb.write(0x5061C, 0x0182, channel)                 # [11:6] c1_step_size_3  [5:0] c1_step_size_2
        self.mApb.write(0x50620, 0x0086, channel)                 # [11:6] c1_step_size_1  [5:0] c1_step_size_0
        self.mApb.write(0x50624, 0x0182, channel)                 # [11:6] c0_step_size_3  [5:0] c0_step_size_2
        self.mApb.write(0x50628, 0x0086, channel)                 # [11:6] c0_step_size_1  [5:0] c0_step_size_0
        self.mApb.write(0x5062C, 0x0182, channel)                 # [11:6] cn1_step_size_3 [5:0] cn1_step_size_2
        self.mApb.write(0x50630, 0x0086, channel)                 # [11:6] cn1_step_size_1 [5:0] cn1_step_size_0
        self.mApb.write(0x50634, 0x0182, channel)                 # [11:6] cn2_step_size_3 [5:0] cn2_step_size_2
        self.mApb.write(0x50638, 0x0086, channel)                 # [11:6] cn2_step_size_1 [5:0] cn2_step_size_0
    def SetTxEqDecrease(self, pre2, pre1, post1, attenuation=1.0, channel=0):
        self.mApb.write(0x50014, 1<<0, channel, mask= 0x1<<0)   # TODO: something strange
        self.mApb.write(0x50088, 0x1000, channel)
        self.mApb.write(0x50088, 0x0000, channel)
        # decrease main as others are changed
        main = pre2+pre1+post1+round((1.0-attenuation)/0.05)
        for i in range(main):
            self.mApb.write(0x50088, 0x0010, channel)
            self.mApb.write(0x50088, 0x0000, channel)
        for i in range(pre2):
            self.mApb.write(0x50088, 0x0800, channel)
            self.mApb.write(0x50088, 0x0000, channel)
        for i in range(pre1):
            self.mApb.write(0x50088, 0x0040, channel)
            self.mApb.write(0x50088, 0x0000, channel)
        for i in range(post1):
            self.mApb.write(0x50088, 0x0020, channel)
            self.mApb.write(0x50088, 0x0000, channel)
    def SetTxEqLut(self, pre2=0, pre1=0, post1=0, attenuation=1.0, channel=0):
        main   = 1.0 - (abs(pre2) + abs(pre1) + abs(post1))
        for i in range(256):
            coef_x_pre2  = self.get_coef_lvl(((i >> 6) & 0x3)) * pre2 * 127 / 3
            coef_x_pre1  = self.get_coef_lvl(((i >> 4) & 0x3)) * pre1 * 127 / 3
            coef_x_main  = self.get_coef_lvl(((i >> 2) & 0x3)) * main * 127 / 3
            coef_x_post1 = self.get_coef_lvl(((i >> 0) & 0x3)) * post1 * 127 / 3
            ffe_val = coef_x_pre2 + coef_x_pre1 + coef_x_main + coef_x_post1;
            if (ffe_val >= 0):
                ffe_lvl = int(attenuation * (ffe_val + 128))
            else:
                ffe_lvl = int(attenuation * (ffe_val + 127))
            self.mApb.write(0x00051000 + (i*4), ffe_lvl, channel)
        # preset1 req
        self.mApb.write(0x50088, 0x1000, channel)
        self.mApb.write(0x50088, 0x0000, channel)
    def SetTxEq(self,tx_pre2=0,tx_pre1=0,tx_post1=0,attenuation=1.0,channel=0):
        self.tx_pre2[channel] = tx_pre2
        self.tx_pre1[channel] = tx_pre1
        self.tx_post1[channel] = tx_post1
        self.attenuation[channel] = attenuation
        if self.mCfg.b_use_txeq_lut:
            self.SetTxEqLut(tx_pre2,tx_pre1,tx_post1,attenuation,channel)
        else:
            pre2 = round(abs(tx_pre2) / 0.05)
            pre1 = round(abs(tx_pre1) / 0.05)
            post1= round(abs(tx_post1) / 0.05)
            self.SetTxEqDecrease(pre2,pre1,post1,attenuation,channel)
    def SetRxEqForce(self, tap=1, coef=0, channel=0):
        # pre2, pre1, c0h, c1,...
        regmap = [0x128,0x120]+[0x110]+[0x130+8*i for i in range(8)]
        addr   = regmap[(tap+2)]+0x60000
        value = (0x100-abs(coef)) if (coef < 0) else coef
        self.mApb.write(addr, 1<<8|value, channel)
        # set c0_l with 1/3*c0_h
        if tap == 0:
            self.mApb.write(0x60118, int(value/3), channel)
        self.mApb.write(0x61FF8, 0x4, channel) # update
    def SetRxEqReleaseAll(self, channel=0):
        regmap = [0x128,0x120]+[0x110]+[0x118]+[0x130+8*i for i in range(8)]
        for reg in regmap:
            self.mApb.write(0x60000+reg,0<<8,channel,1<<8)
    def SetTxUserPattern(self,pattern, channel=0):
        self.mApb.write(0x50118, pattern[0], channel)
        self.mApb.write(0x5011C, pattern[1], channel)
        self.mApb.write(0x50120, pattern[2], channel)
        self.mApb.write(0x50124, pattern[3], channel)
    def SetRxUserPattern(self, pattern, channel=0):
        self.mApb.write(0x60178, pattern[0], channel)
        self.mApb.write(0x6017C, pattern[1], channel)
        self.mApb.write(0x60180, pattern[2], channel)
        self.mApb.write(0x60184, pattern[3], channel)
    def SetTxDisable(self,channel=0):
        for i in range(128):
            self.mApb.write(0x51000 + ((i*2+0)*4), 0x0080, channel)
            self.mApb.write(0x51000 + ((i*2+1)*4), 0x007f, channel)
        # preset1 req
        self.mApb.write(0x50088, 0x1000, channel)
        self.mApb.write(0x50088, 0x0000, channel)
    def SetTxInitP1(self,channel=0):
        p1 = [0x0,0x0,0x0,0x0,0x54,0x54,0x54,0x54,0xAB,0xAB,0xAB,0xAB,0xFF,0xFF,0xFF,0xFF,0x0,0x0,0x0,0x0,0x54,0x54,0x54,0x54,0xAB,0xAB,0xAB,0xAB,0xFF,0xFF,0xFF,0xFF,0x0,0x0,0x0,0x0,0x54,0x54,0x54,0x54,0xAB,0xAB,0xAB,0xAB,0xFF,0xFF,0xFF,0xFF,0x0,0x0,0x0,0x0,0x54,0x54,0x54,0x54,0xAB,0xAB,0xAB,0xAB,0xFF,0xFF,0xFF,0xFF,0x0,0x0,0x0,0x0,0x54,0x54,0x54,0x54,0xAB,0xAB,0xAB,0xAB,0xFF,0xFF,0xFF,0xFF,0x0,0x0,0x0,0x0,0x54,0x54,0x54,0x54,0xAB,0xAB,0xAB,0xAB,0xFF,0xFF,0xFF,0xFF,0x0,0x0,0x0,0x0,0x54,0x54,0x54,0x54,0xAB,0xAB,0xAB,0xAB,0xFF,0xFF,0xFF,0xFF,0x0,0x0,0x0,0x0,0x54,0x54,0x54,0x54,0xAB,0xAB,0xAB,0xAB,0xFF,0xFF,0xFF,0xFF,0x0,0x0,0x0,0x0,0x54,0x54,0x54,0x54,0xAB,0xAB,0xAB,0xAB,0xFF,0xFF,0xFF,0xFF,0x0,0x0,0x0,0x0,0x54,0x54,0x54,0x54,0xAB,0xAB,0xAB,0xAB,0xFF,0xFF,0xFF,0xFF,0x0,0x0,0x0,0x0,0x54,0x54,0x54,0x54,0xAB,0xAB,0xAB,0xAB,0xFF,0xFF,0xFF,0xFF,0x0,0x0,0x0,0x0,0x54,0x54,0x54,0x54,0xAB,0xAB,0xAB,0xAB,0xFF,0xFF,0xFF,0xFF,0x0,0x0,0x0,0x0,0x54,0x54,0x54,0x54,0xAB,0xAB,0xAB,0xAB,0xFF,0xFF,0xFF,0xFF,0x0,0x0,0x0,0x0,0x54,0x54,0x54,0x54,0xAB,0xAB,0xAB,0xAB,0xFF,0xFF,0xFF,0xFF,0x0,0x0,0x0,0x0,0x54,0x54,0x54,0x54,0xAB,0xAB,0xAB,0xAB,0xFF,0xFF,0xFF,0xFF,0x0,0x0,0x0,0x0,0x54,0x54,0x54,0x54,0xAB,0xAB,0xAB,0xAB,0xFF,0xFF,0xFF,0xFF]
        for i,dac in enumerate(p1):
            self.mApb.write(0x51000 + (i*4), dac, channel)
        # preset1 req
        self.mApb.write(0x50088, 0x1000, channel)
        self.mApb.write(0x50088, 0x0000, channel)
    def SetTxOff(self,channel=0):
        self.mApb.write(0x50504, 1<<5, channel, mask=1<<5) #ser_clk_done_bypass=1
        self.mApb.write(0x50004, 0x18<<0, channel, mask=0x18<<0) #ser_clk_rstn,dcc_clk_en=1
        self.mApb.write(0x50000, 0x18<<0, channel, mask=0x18<<0)
        self.mApb.write(0x50084, 0<<0, channel, mask=1<<0)
        self.mApb.write(0x50080, 1<<0, channel, mask=1<<0)
    def SetTxOn(self,channel=0):
       #self.mApb.write(0x50504, 1<<5, channel, mask=1<<5) #ser_clk_done_bypass=1
        self.mApb.write(0x50084, 1<<2|1<<0, channel, mask=1<<2|1<<0) # train=1, prot_en=1
        if self.mCfg.media_mode == 'SLB':
            self.mApb.write(0x50024, 1, channel)
        if False:
            self.mApb.write(0x50000, 0x0008, channel, 1<<3) # WA0-2 dcc code forcing -> 300 [9] forcing ib code [8] forcing i code   @ 208, tx ser clk rstn
            self.mApb.write(0x50000, 0x0000, channel, 1<<3) # WA0-3 dcc code forcing -> 300 [9] forcing ib code [8] forcing i code   @ 200
            if(mCfg.data_rate==10.3125) :
                # WA0-5 toggle tx_10g_en to flush dtoa buffer
                self.mApb.write(0x50100, 0<<6, channel, 1<<6)
                self.mApb.write(0x50100, 1<<6, channel, 1<<6)
    def SetRxOff(self,b_keep_clk=True,channel=0):
        #self.mApb.write(0x63478, 0xf<<1, channel,0x1f<<1) # default 0x80, cal bypass [6:1] ([1] : VGA2 / [2] : VGA3 / [3] : VGA1 / [4] : FULL CAL) 0xf0 -> 0x80 by who 190906
        #self.mApb.write(0x60500, 0x1f<<2, channel, 0x1f<<2)   #
        #self.mApb.write(0x60508, 0x000000e2, channel)   # ioc full skip E2? 20? 0xc0 -> 0x20 by who 190906
        #self.mApb.write(0x60094, 0x0<<10, channel,0x1<<10)
        #self.mApb.write(0x60090, 0x1<<10, channel,0x1<<10)
        #self.mApb.write(0x60094, 0x1<<10, channel,0x1<<10)
        if self.mCfg.b_dbg_print:
            self.PrintIocCalState()
        # rx_pi=Active
        if b_keep_clk:
            self.mApb.write(0x6000C, 0xf<<6|1<<1, channel, mask=0xf<<6|1<<1)
            self.mApb.write(0x60004, 0xf<<6|1<<1, channel, mask=0xf<<6|1<<1)
        self.mApb.write(0x601dc, 0x00000001, channel) # sq force
        # prot_rx_en=0
        self.mApb.write(0x6008C, 0<<0, channel, mask=1<<0)
        #self.mApb.write(0x63478, 0x0<<1, channel,0x1f<<1)
        #self.mApb.write(0x60090, 0x0<<10, channel,0x1<<10)
        #self.mApb.write(0x60500, 0x0<<2, channel, 0x1f<<2)   #
        #self.mApb.write(0x60508, 0x00000020, channel)   # ioc full skip E2? 20? 0xc0 -> 0x20 by who 190906
    def SetRxOn(self,channel=0,b_tune=False):
        self.mApb.write(0x6008C, 1<<0, channel, mask=1<<0)
        #self.mApb.write(0x601dc, 0, channel)
    def SetTxCoding(self,graycoding=0,precoding=0,channel=0):
        if precoding == 1:
            self.mApb.write(0x50084,3<<3,channel,3<<3)
        elif graycoding == 1:
            self.mApb.write(0x50084,2<<3,channel,3<<3) # PAM4
        elif self.is_pam4_rate(self.mCfg.data_rate): # 64bit
            self.mApb.write(0x50084,1<<3,channel,3<<3) # bypass
        else:
            self.mApb.write(0x50084,0<<3,channel,3<<3) # PAM2
    def SetRxCoding(self,graycoding=0,precoding=0,channel=0):
        if precoding == 1:
            self.mApb.write(0x6008C,3<<3,channel,3<<3)
        elif graycoding == 1:
            self.mApb.write(0x6008C,2<<3,channel,3<<3) # PAM4
        elif self.is_pam4_rate(self.mCfg.data_rate): # 64bit
            self.mApb.write(0x6008C,1<<3,channel,3<<3) # bypass
        else:
            self.mApb.write(0x6008C,0<<3,channel,3<<3) # PAM2
    def SetTxSwap(self,en=1,channel=0):
        self.mApb.write(0x50400,en,channel)
    def SetRxSwap(self,en=1,channel=0):
        self.mApb.write(0x60400,en<<1,channel,1<<1)
#}}}
#----------------------------------------------------------------------------------------------------
# Config - Tune
#----------------------------------------------------------------------------------------------------
#{{{
    def TuneVga1(self,channel=0,thld=124):
        repeat = 4
        gain = (self.mApb.read(0x6002C,channel) & 0x1f)
        (minval,maxval) = self.GetAdcMinMax(adc_channel=0,channel=channel,mon_sel=1,repeat=repeat)
        while ((abs(maxval) > thld) or (abs(minval) > thld)) and (gain > 8):
            gain -= 2
            self.mApb.write(0x6002C,1<<5|gain,channel)
            (minval,maxval) = self.GetAdcMinMax(adc_channel=0,channel=channel,mon_sel=1,repeat=repeat)
     
    def TuneVga2(self,channel=0,thld=120):
        repeat = 4
        gain = (self.mApb.read(0x60028,channel) & 0xf)
        (minval,maxval) = self.GetAdcMinMax(adc_channel=0,channel=channel,mon_sel=1,repeat=repeat)
        while ((abs(maxval) > thld) or (abs(minval) > thld)):
            gain += 1
            self.mApb.write(0x60028,1<<4|gain,channel)
            (minval,maxval) = self.GetAdcMinMax(adc_channel=0,channel=channel,mon_sel=1,repeat=repeat)
    def TuneCm1(self,channel=0,c1max=85,c1min=50):
        cm1 = self.GetRxEqCoef(tap=-1,channel=channel,repeat=1)
        c1  = self.GetRxEqCoef(tap=1,channel=channel,repeat=4)
        if ((c1 < -c1max) and (cm1 > -45)) or (c1 < cm1-55):
            while ((c1 < -c1max) and (cm1 > -45)) or (c1 < cm1-55):
                cm1 -= 1
                self.SetRxEqForce(tap=-1,coef=cm1,channel=channel)
                c1  = self.GetRxEqCoef(tap=1,channel=channel,repeat=4)
        elif (c1 > -c1min) and (cm1 < -5):
            while (c1 > -c1min) and (cm1 < -5):
                cm1 += 1
                self.SetRxEqForce(tap=-1,coef=cm1,channel=channel)
    def TuneCtle(self,channel=0):
        c0 = self.GetRxEqCoef(0,channel,1)
        c1 = self.GetRxEqCoef(1,channel,4)
        c2 = self.GetRxEqCoef(2,channel,4)
        c3 = self.GetRxEqCoef(3,channel,4)
        gain = 0xf - (self.mApb.read(0x60020,channel) & 0xf)
        ch_length = 'none'
        while (((c2+c3 > 10 and -c1 < 50) or (-c1 >= 50 and -c1 < 75 and c2 > 30) or (-c1 >= 75 and c2 > 25) or (c0 < 25)) and gain < 15):
            if (-c1 < 50):
                gain += 1
                self.mApb.write(0x60020,1<<4|(0xf-gain))
                self.TuneVga2(channel)
                self.TuneCm1(channel)
                c2 = self.GetRxEqCoef(2,channel,4)
                c3 = self.GetRxEqCoef(3,channel,4)
                ch_length = 'short'
            else:
                gain += 1
                self.mApb.write(0x60020,1<<4|(0xf-gain))
                self.TuneVga2(channel)
                self.TuneCm1(channel)
                c0 = self.GetRxEqCoef(0,channel,4)
                c2 = self.GetRxEqCoef(2,channel,4)
                if -c1 < 75:
                    ch_length = 'medium'
                else :
                    ch_length = 'long'
        print ("CTLE gain update(%s) to %d" % (ch_length,(15-gain)))
    def CompAdcOffset(self,channel=0,max_loop=1000):
        for rep in range(3):
            # wait to avoid the error is not in 0.4~0.6*avg
            loop = 0
            while True:
                c0p_cnt   = 0
                c0p_total = 0
                loop += 1
                for ch in range(32):
                    c0p = self.mApb.read(0x64100+0x4*ch,channel)
                    if c0p != 60:
                        c0p_cnt += 1
                        c0p_total += c0p
                if not (((c0p_total%c0p_cnt) < (c0p_cnt*0.6)) and ((c0p_total%c0p_cnt) > (c0p_cnt*0.4))):
                    break
                if loop >= max_loop:
                    break
            if loop >= max_loop:
                break
            # wait to avoid the error is not in 0.4~0.6*avg
            loop = 0
            while True:
                c0m_cnt   = 0
                c0m_total = 0
                for ch in range(32):
                    c0m = self.mApb.read(0x64184+0x4*ch+(0 if ch < 18 else 4),channel)
                    if c0m != (256-60):
                        c0m_cnt += 1
                        c0m_total += (256-c0m)
                if not (((c0m_total%c0m_cnt) < (c0m_cnt*0.6)) and ((c0m_total%c0m_cnt) > (c0m_cnt*0.4))):
                    break
                if loop >= max_loop:
                    break
            if loop >= max_loop:
                break
            # compensate offset
            offset = -(((c0p_total + c0p_cnt/2)/c0p_cnt) - ((c0m_total+c0m_cnt/2)/c0m_cnt))
            offset = offset/2 if abs(offset) > 2 else 0
            #print("offset=%d, c0p_total=%d, c0m_total=%d" % (offset,c0p_total, c0m_total))
            if offset != 0:
                for ch in range(32):
                    code = self.get_signed_code(self.mApb.read(0x60800+4*ch,channel))
                    code = self.get_unsigned_code(code+offset)
                    self.mApb.write(0x62014+4*ch,code|1<<15,channel)
                    self.mApb.write(0x61FF8,1,channel)
            else:
                break
    def SetRxTuneInit(self, channel=0):
        #self.SetRxOff(channel=channel)
        self.mApb.write(0x6008C, 1<<0, channel, mask=1<<0)
        if self.mCfg.media_mode == 'RLB':
            self.mApb.write(0x60028, 0x11, channel)
            if (self.CheckOverGainAdc(63,channel) == 1):
                self.UnsetBoostCurrent(channel)
            self.mApb.write(0x60028, 0x10, channel)
        # self.mApb.write(0x00060034, 0x121, channel)
        # self.mApb.write(0x0006002c, 0x20 + 23, channel)
        # self.mApb.write(0x00060028, 0x17, channel)
        # self.mApb.write(0x00060020, 0x1f, channel)
        # self.mApb.write(0x000601dc, 0x00000000, channel)
        self.AfeAdaptation(ln_i=channel)
    def AfeAdaptation(self, ln_i=0):
        #self.DumpRegFile()
        if self.mCfg.b_dbg_print:
            self.PrintTuneRegs(ln_i)
        maxLimit = 61
        minLimit = 58
        vga1Gain = self.mApb.read(0x0006002c,ln_i) - 32
        ctleGain = 15 - (self.mApb.read(0x00060020,ln_i) - 16)
        maxVal = self.GetAdcMaxMin8(ln_i) >> 8
        minVal = self.GetAdcMaxMin8(ln_i) & 0xff
        adcVrefSel = self.mApb.read(0x00060034,ln_i)
        if (maxVal < minLimit) and (minVal < minLimit):
            while ((maxVal < minLimit) and (minVal < minLimit) and ((adcVrefSel >> 6) > 0)):
                adcVrefSel -= (1 << 6)
                self.mApb.write(0x00060034, adcVrefSel, ln_i)
                maxVal = self.GetAdcMaxMin8(ln_i) >> 8
                minVal = self.GetAdcMaxMin8(ln_i) & 0xff
            if self.mCfg.b_dbg_print:
                print("adc vref sel update to 0x%x" % (adcVrefSel >> 6))

        elif (maxVal+minVal > maxLimit*2):
            while ((maxVal+minVal > maxLimit*2) and (vga1Gain > 0xf)):
                vga1Gain -= 8
                self.mApb.write(0x0006002c, 0x20 + vga1Gain, ln_i)
                maxVal = self.GetAdcMaxMin8(ln_i) >> 8
                minVal = self.GetAdcMaxMin8(ln_i) & 0xff
            if ((maxVal+minVal) < 110):
                 vga1Gain += 8
                 self.mApb.write(0x0006002c, 0x20 + vga1Gain, ln_i)
            if self.mCfg.b_dbg_print:
                print("vga1gain= %d" %vga1Gain)
                print("Max= %d" %maxVal)
                print("Min= %d" %minVal)
                print("vga1 update to 0x%x"%( vga1Gain))
        self.SwVga2Adap(ln_i)
        self.mApb.write(0x000601dc, 0x00000000, ln_i)
        data2230 = (self.mApb.read(0x00062230,ln_i) & 0xff)
        if (data2230 == 0xff or data2230 == 0):
            return -1
        self.mApb.write(0x00060128, 0x000,ln_i)
        self.SwCm1Adap(ln_i)
        self.AdcFineCalRestart(ln_i)
        if self.mCfg.b_dbg_print:
            maxVal = self.GetAdcMaxMin8(ln_i) >> 8
            minVal = self.GetAdcMaxMin8(ln_i) & 0xff
            print("Max= %d" %maxVal)
            print("Min= %d" %minVal)
        c0 = self.mApb.read(0x6223C,ln_i)
        c1 = self.GetAvgCoeff(1, 4,ln_i)
        c2 = self.GetAvgCoeff(2, 4,ln_i)
        ctleUpdate = 0
        while (((c2 > 35 and -c1 < 50) or (-c1 >= 50 and -c1 < 80 and c2 > 25) or (-c1 >= 80 and c2 > 20)) and ctleGain < 15):
            ctleGain += 1
            self.mApb.write(0x00060020, 0x0000001f - ctleGain, ln_i)
            self.SwCm1Adap(ln_i)
            c2 = self.GetAvgCoeff(2, 4,ln_i)
            if (-c1 < 50):
                ctleUpdate = 1
            elif (-c1 < 80):
                ctleUpdate = 2
            else:
                ctleUpdate = 3
        if self.mCfg.b_dbg_print:
            if (ctleUpdate == 1):
                print("CTLE gain update(short) to 0x%x" % (15 - ctleGain))
            elif (ctleUpdate == 2):
                print("CTLE gain update(med) to 0x%x" % (15 - ctleGain))
            elif (ctleUpdate == 3):
                print("CTLE gain update(long) to 0x%x" % (15 - ctleGain))
        if (ctleUpdate != 0):
            self.SwVga2Adap(ln_i)
            self.AdcFineCalRestart(ln_i)
        if self.mCfg.b_dbg_print:
            self.PrintTuneRegs(ln_i)
            maxVal = self.GetAdcMaxMin8(ln_i) >> 8
            minVal = self.GetAdcMaxMin8(ln_i) & 0xff
            print("Max= %d" %maxVal)
            print("Min= %d" %minVal)
        return 0
    def AfeTuneScale(self, ln_i=0):
        rxstate = self.mApb.read(0x64000,ln_i)
        rxstate |= ((self.mApb.read(0x64004,ln_i) & 0x1ff) << 16)
        if (rxstate >> 18) & 1 != 1:
            return -1
        maxLimit = 61
        minLimit = 58
        maxVal = self.GetAdcMaxMin8(ln_i) >> 8
        minVal = self.GetAdcMaxMin8(ln_i) & 0xff
        if (maxVal < minLimit and minVal < minLimit):
            self.SwVga2Adap(ln_i)
            maxVal = self.GetAdcMaxMin8(ln_i) >> 8
            minVal = self.GetAdcMaxMin8(ln_i) & 0xff
            adcVrefSel = self.mApb.read(0x00060034,ln_i)
            if (maxVal < minLimit and minVal < minLimit and (adcVrefSel >> 6) > 0):
                adcVrefSel -= (1 << 6)
                self.mApb.write(0x00060034, adcVrefSel, ln_i)
                print("adc vref sel update to 0x%x" % (adcVrefSel >> 6))
        maxVal = self.GetAdcMaxMin8(ln_i) >> 8
        minVal = self.GetAdcMaxMin8(ln_i) & 0xff
        if (maxVal > maxLimit and minVal > maxLimit):
            adcVrefSel = self.mApb.read(0x00060034,ln_i)
            if ((maxVal > maxLimit and minVal > maxLimit) and (adcVrefSel >> 6) < 4):
                adcVrefSel += (1 << 6)
                self.mApb.write(0x00060034, adcVrefSel, ln_i)
                print("adc vref sel update to 0x%x"% (adcVrefSel >> 6))
            self.SwVga2Adap(ln_i)
        self.SwCm1Adap(ln_i)
        self.AdcFineCalRestart(ln_i)
        return 0;
    def AdcFineCalRestart(self, channel=0):
        self.mApb.write(0x0006347c, 0xd000, channel)
        self.mApb.write(0x000601AC, 0<<1, channel,1<<1)
        self.mApb.write(0x000601AC, 1<<1, channel,1<<1)
     
        if self.mCfg.b_dbg_print:
            print("AdcFineCalRestart")
        #Delay(10)
    def GetAdcMaxMin8(self, ln_i=0):
        maxData = 0;
        minData = 64;
        self.mApb.write(0x0006051c, 0x00000000, ln_i)
        for i in range(16):
                self.mApb.write(0x00062248, (i << 4) | 0, ln_i)
                self.mApb.write(0x00062248, (i << 4) | 1, ln_i)
                data = self.mApb.read(0x0006224C ,ln_i);
                #print("max ch : %d data: %d" %(i, data-64))
             
                if (maxData < (data & 0xff00) >> 8):
                        maxData = (data & 0xff00) >> 8
                if (minData > (data & 0xff)):
                        minData = data & 0xff
        return ((maxData - 64) << 8) + (64 - minData)
    def SwVga2Adap(self,ln_i=0):
        vga2Gain = 15 - (self.mApb.read(0x00060028,ln_i)-16)
        maxVal = self.GetAdcMaxMin8(ln_i) >> 8
        minVal = self.GetAdcMaxMin8(ln_i) & 0xff
        maxLimit = 62
        if self.mCfg.b_dbg_print:
            print ("<SwVga2Adap> start")
        if ((maxVal > maxLimit - 1 or minVal > maxLimit) and vga2Gain > 0):
            while ((maxVal > maxLimit - 1 or minVal > maxLimit) and vga2Gain > 0):
                vga2Gain -= 1
                self.mApb.write(0x00060028, 0x0000001f - vga2Gain, ln_i)
                maxVal = self.GetAdcMaxMin8(ln_i) >> 8
                minVal = self.GetAdcMaxMin8(ln_i) & 0xff
            if self.mCfg.b_dbg_print:
                print("vga2 gain update to 0x%x"%( vga2Gain))
        if (maxVal < maxLimit - 3 and minVal < maxLimit - 2 and vga2Gain < 0xf):
            while (maxVal < maxLimit - 3 and minVal < maxLimit - 2 and vga2Gain < 0xf):
                vga2Gain += 1
                self.mApb.write(0x00060028, 0x0000001f - vga2Gain, ln_i)
                maxVal = self.GetAdcMaxMin8(ln_i) >> 8
                minVal = self.GetAdcMaxMin8(ln_i) & 0xff
            if self.mCfg.b_dbg_print:
                print("vga2 gain update to 0x%x"%( vga2Gain))
        if self.mCfg.b_dbg_print:
            print ("<SwVga2Adap> done")
    def SwCm1Adap(self, ln_i):
        cm1init = self.mApb.read(0x62270,ln_i)
        if (cm1init > 128):
            cm1init = cm1init - 256
        cm1 = cm1init
        cm2 = self.GetAvgCoeff(-2, 4,ln_i)
        if (-cm2 < -10 and -cm1 > 5):
            while (-cm2 < -10 and -cm1 > 5):
                cm1 += 1
                self.phyEqCpre1Forcing(-cm1,ln_i)
                cm2 = self.GetAvgCoeff(-2, 4,ln_i)
        c1 = self.GetAvgCoeff(1, 4,ln_i)
        if (c1 < cm1 - 50):
            while (c1 < cm1 - 50):
                cm1 -= 1
                self.phyEqCpre1Forcing(-cm1,ln_i)
                c1 = self.GetAvgCoeff(1, 4,ln_i)
    def GetAvgCoeff(self, tap, avgNum, ln_i=0):
        result=0
        temp=0
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
            temp = self.mApb.read(addr,ln_i)
            if (temp > 128):
                result = result + temp - 256
            else:
                result += temp
        result /= avgNum
        return int(result)
    def phyEqCpre1Forcing(self,forcingC1,ln_i=0):
        if (forcingC1 == 0):
            self.mApb.write(0x00060120, 0x100, ln_i)
        else:
            self.mApb.write(0x00060120, 0x100 + 256 - forcingC1, ln_i)
        self.mApb.write(0x00061FF8, 0x4, ln_i)
        return 0
    def PrintCtleRegs(self,channel=0):
        r20 = self.mApb.read(0x00060020,channel)
        r38 = self.mApb.read(0x00060038,channel)
        r2c = self.mApb.read(0x0006002c,channel)
        r50 = self.mApb.read(0x00060050,channel)
        r28 = self.mApb.read(0x00060028,channel)
        r54 = self.mApb.read(0x00060054,channel)
        print("hfeq rsel(%d), bypass(%d), csel(%d), i_ctrl(%d), rl_ctrl(%d)" % (r20, (r38>>14)&1,(r38>>10)&0xf,(r38>>5)&0x1f,(r38>>0)&0x1f))
        print("vga1 rsel(%d),                       i_ctrl(%d), rl_ctrl(%d), oc_dac_pulldn(%d), oc_i_ctrl(%d)" % (r2c, (r50>>7)&0xf,(r50>>3)&0xf, (r50>>2)&1, (r50>>0)&0x3))
        print("vga2 rsel(%d), rs_ctrl(%d),          i_ctrl(%d), rl_ctrl(%d), oc_dac_pulldn(%d), oc_i_ctrl(%d)" % (r28, (r54>>11)&0x1f,(r54>>7)&0xf,(r54>>3)&0xf, (r54>>2)&1, (r54>>0)&0x3))

    def PrintTuneRegs(self,channel=0):
        print ("0x00060020 => 0x%x " % (self.mApb.read(0x00060020,channel)))
        print ("0x00060028 => 0x%x " % (self.mApb.read(0x00060028,channel)))
        print ("0x0006002c => 0x%x " % (self.mApb.read(0x0006002c,channel)))
        print ("0x00060034 => 0x%x " % (self.mApb.read(0x00060034,channel)))
        print ("0x00060120 => 0x%x " % (self.mApb.read(0x00060120,channel)))
        print ("0x00060128 => 0x%x " % (self.mApb.read(0x00060128,channel)))
        print ("0x000601AC => 0x%x " % (self.mApb.read(0x000601AC,channel)))
        print ("0x000601dc => 0x%x " % (self.mApb.read(0x000601dc,channel)))
        print ("0x0006051c => 0x%x " % (self.mApb.read(0x0006051c,channel)))
        print ("0x00061FF8 => 0x%x " % (self.mApb.read(0x00061FF8,channel)))
        print ("0x00062248 => 0x%x " % (self.mApb.read(0x00062248,channel)))
        print ("0x00063450 => 0x%x " % (self.mApb.read(0x00063450,channel)))
        print ("0x0006347c => 0x%x " % (self.mApb.read(0x0006347c,channel)))
#}}}
#----------------------------------------------------------------------------------------------------
# Config - Special
#----------------------------------------------------------------------------------------------------
    def SetTopPorts(self):
        self.mApb.write(0x24000024, 0x00000230 | self.mCfg.lane_en | self.mCfg.ext_clk<<6)
    def Reset(self):
        self.mApb.write(0x24000004, 0x00000003)
        self.mApb.write(0x24000004, 0x00000000)
     
    def SetSLB(self, channel=0):
        self.SetTxBase(channel)
        self.SetRxBase(channel)
        self.mApb.write(0x640a8, 0x2, channel)
        self.mApb.write(0x640b4, 484, channel)
        self.mApb.write(0x4C, 0x3FF3) # tx rcal force, common mode lowest
        self.mApb.write(0x60010, 0x0, channel) # vga3
        self.mApb.write(0x60014, 0x0, channel) # vga2
        self.mApb.write(0x61008, 512-00, channel)
        self.SetRxEqForce(-1,-5,channel)
        #self.SetRxEqForce(1,-50,channel)
        self.mApb.write(0x60090, 0x400, channel) # ioc_cal_en
        if (self.mCfg.data_rate==10.3125) :
            self.SetRxEqForce(1,0,channel)
            self.mApb.write(0x60028, 0x001F, channel)   # vga2 r sel force [4] en [3:0] value high -> gain low
            self.mApb.write(0x60108, 0x7A08, channel)   # adap bw
            self.mApb.write(0x60500, 0x8688, channel)   # skip fine cal
            self.mApb.write(0x62004, 0xc0c0, channel)
            self.mApb.write(0x62008, 0xc0c0, channel)
            self.mApb.write(0x6200C, 0xc0c0, channel)
            self.mApb.write(0x62010, 0xc0c0, channel)
            self.mApb.write(0x63454, 0x5390, channel)   # bbpd en[9] / pd_sel[15:14]
            self.mApb.write(0x6345c, 0xfe20, channel)   # cdr_type
        elif (self.mCfg.data_rate in [53.125,56.25]) :
            self.mApb.write(0x60208, 0x0180, channel) # bist measure time [8:4] 0x19 => 10^9 in 25/10G
            self.mApb.write(0x50084, 0x0010, channel) # [temp]
            self.mApb.write(0x6008C, 2<<3, channel, 3<<3) # pam4:50
        elif (self.mCfg.data_rate in [21.25,22.5]):
            self.mApb.write(0x60040, 0x00ff, channel) # pi settings in rsel[7:6] ictrl[5:4] out rsel[3:2] ictrl[1:0]
            self.mApb.write(0x60064, 0x0603, channel) # pi slew ctrl 7->1 [12:10] pi str [3:0]
            self.mApb.write(0x6008C, 2<<3, channel, 3<<3) # pam2:40 pam4:50
            self.mApb.write(0x60208, 0x0180, channel) # bist measure time [8:4] 0x19 => 10^9 in 25/10G
            self.SetRxEqForce(1,-60,channel)
    def SetELB(self, channel=0):
        self.SetTxBase(channel)
        self.SetRxBase(channel)
        self.SetRxEqForce(-1,-20,channel)
        self.mApb.write(0x61008, 512-20, channel)
        self.mApb.write(0x640a8, 0x2, channel)
        self.mApb.write(0x640b4, 413, channel)
        if (self.mCfg.data_rate==10.3125) :
            self.mApb.write(0x60038, ((1 << 14) | (0 << 10) | (5 << 5) | 5), channel)   # hfef c sel [13:10] i ctrl [9:5], rl ctrl [4:0]
            self.mApb.write(0x60054, ((15 << 11) | (13 << 7) | (14 << 3)), channel)   # vga2 dac lsb ctrl [1:0] 0->3, rs [15:11] i ctrl [6:3], dac pull up [2] 40
            self.mApb.write(0x60108, 0x7A08, channel)   # adap bw
            self.mApb.write(0x60500, 1<<7, channel, mask=  1<<7) # skip fine cal
            self.mApb.write(0x62004, 0xc0c0, channel)
            self.mApb.write(0x62008, 0xc0c0, channel)
            self.mApb.write(0x6200C, 0xc0c0, channel)
            self.mApb.write(0x62010, 0xc0c0, channel)
            self.mApb.write(0x63454, 0x5390, channel)   # bbpd en[9] / pd_sel[15:14]
            self.mApb.write(0x6345c, 0xfe20, channel)   # cdr_type
        elif (self.mCfg.data_rate in [53.125,56.25]) :
            self.mApb.write(0x50084, 2<<3, channel, 3<<3) # [temp]
            self.mApb.write(0x6008C, 2<<3, channel, 3<<3) # pam4:50
            self.mApb.write(0x60208, 0x0180, channel) # bist measure time [8:4] 0x19 => 10^9 in 25/10G
        elif (self.mCfg.data_rate in [21.25,22.5]):
            self.mApb.write(0x60040, 0x00ff, channel) # pi settings in rsel[7:6] ictrl[5:4] out rsel[3:2] ictrl[1:0]
            self.mApb.write(0x60064, 0x0603, channel) # pi slew ctrl 7->1 [12:10] pi str [3:0]
            self.mApb.write(0x6008C, 2<<3, channel, 3<<3) # pam2:40 pam4:50
            self.mApb.write(0x60208, 0x0180, channel) # bist measure time [8:4] 0x19 => 10^9 in 25/10G
            self.SetRxEqForce(1,-60,channel)
            self.SetTxEqDecrease(0,0,0,channel=channel)
    def SetBoostCurrent(self,channel=0):
        self.cboost[channel] = 1
        if self.mCfg.b_dbg_print:
            print("Boost Current")
        self.mApb.write(0x00060054, ((1 << 15) + (15 << 11) + (15 << 7) + (15 << 3) + (0 << 2) + 0), channel)
        self.mApb.write(0x00060050, ((15 << 7) + (15 << 3) + (0 << 2) + 0), channel)
        self.mApb.write(0x00060038, ((0 << 10) + (15 << 5) + 15), channel)
        self.mApb.write(0x00050020, 0x00000001, channel)
        self.mApb.write(0x00060048, 0x00007b9f, channel)
    def UnsetBoostCurrent(self,channel=0):
        self.cboost[channel] = 0
        if self.mCfg.b_dbg_print:
            print("Boost Current Off")
        self.mApb.write(0x60054, 0<<15|31<<11|15<<7|14<<3, channel) # vga2 rs_ctrl, rl_ctrl, i_ctrl
        self.mApb.write(0x60050, 15<<7|15<<3, channel) # vga1 rl/i_ctrl
        self.mApb.write(0x60038, 0<<10|11<<5|11, channel) # afe_hfeq i_ctrl, rl_ctrl
        self.mApb.write(0x00050020, 0x00000002, channel)
        self.mApb.write(0x00060048, 0x0000799f, channel)
    def SetRLB(self,b_boost_current=True,channel=0):
        cm1init = 20
        vga2Gain = 15
        ctleGain = 0
        if self.mCfg.b_dbg_print:
            print("SetRLB")
        self.SetTxBase(channel)
        self.SetRxBase(channel)
        self.mApb.write(0x61008, 512-0, channel) # eom_pi_code
        self.SetRxEqForce(-1,-cm1init, channel)
        self.mApb.write(0x60020, 0x1f-ctleGain, channel)
        self.mApb.write(0x60028, 0x1f-vga2Gain, channel)
        self.mApb.write(0x6002C, 0x3f, channel)
        #self.mApb.write(0x63450, 0x000d, channel)   # debugging by who 190909
        self.mApb.write(0x63454, 0x6530, channel) # CDR
        self.mApb.write(0x60054, 0<<15|31<<11|15<<7|14<<3, channel) # vga2 rs_ctrl, rl_ctrl, i_ctrl
        self.mApb.write(0x60050, 15<<7|15<<3, channel) # vga1 rl/i_ctrl
        self.mApb.write(0x60038, 0<<10|11<<5|11, channel) # afe_hfeq i_ctrl, rl_ctrl
        if b_boost_current:
            self.SetBoostCurrent(channel)
        self.mApb.write(0x60064, 0x120f, channel)
        self.mApb.write(0x60040, 0xaa, channel) # pi in_/mix_rsel/i_ctrl=2
        self.mApb.write(0x60058, 0x128, channel)
        if self.mCfg.data_rate == 10.3125:
            self.mApb.write(0x00060054 , ( (8 << 11) + (15 << 7) + (15 << 3)),channel)     # vga2 dac lsb ctrl [1:0] 0->3, rs [15:11] i ctrl [6:3], dac pull up [2] 40
            self.mApb.write(0x00060050 , ((8 << 7) + (8 << 3)),channel)                    # vga1 dac lsb ctrl [1:0] 0->3, i ctrl [6:3], dac pull up [2] 40
            self.mApb.write(0x00060038 , ((4 << 10) + (8 << 5) + 8),channel)                # hfef c sel [13:10] i ctrl [9:5], rl ctrl [4:0]
            self.mApb.write(0x00060500 , 0x00008688,channel)
            self.mApb.write(0x00050018 , 0x00000001,channel)   # tx 10g mode
            self.mApb.write(0x00050100 , 0x00000042,channel)   # tx 10g en [6]
            self.mApb.write(0x00063454 , 0x00005791,channel)   # bbpd en[9] / pd_sel[15:14]
            self.mApb.write(0x0006345c , 0x0000fe20,channel)   # cdr type [6:5]
            self.mApb.write(0x00062004 , 0x00008080,channel)
            self.mApb.write(0x00062008 , 0x00008080,channel)
            self.mApb.write(0x0006200C , 0x00008080,channel)
            self.mApb.write(0x00062010 , 0x00008080,channel)
            self.mApb.write(0x00060108 , 0x00007A08,channel)   # adap bw
        elif self.mCfg.data_rate in [53.125,56.25]:
            self.mApb.write(0x60208, 0x0180, channel)   # debugging by who 190909
            self.mApb.write(0x50084, 2<<3, channel, 2<<3)
            self.mApb.write(0x6008C, 2<<3, channel, 3<<3)
            #self.mApb.write(0x63450, 0x000b, channel)
            # self.SetTxEqDecrease(0, 0, 0, channel=channel)
        # rx_en is off by default. therefore skip set 0x60088,0x9
        self.SetRxEqForce(-2, 0, channel)

    def TuneRx(self,channel=0):
        self.AfeTuneScale(channel)
    def Init(self):
        self.init_vars()
        self.SetTopPorts()
        self.Reset()
    def Start(self):
        self.Init()
        self.SetCmnBase()
        self.SetPll()
        for i in self.get_active_lane():
            if self.mCfg.media_mode == 'SLB':
                self.SetSLB(i)
            elif self.mCfg.media_mode == 'ELB':
                self.SetELB(i)
            elif self.mCfg.media_mode == 'RLB':
                self.SetRLB(self.mCfg.b_init_boost_current[i],i)
        if self.mCfg.cb_pmad_pre:
            self.mCfg.cb_pmad_pre(self)
        self.SetCmnStart()
        # In order to give same environment when sw uses On/Off, Do On/Off in advance.
        for i in self.get_active_lane():
            if self.mCfg.b_WA0:
                self.SetWA0_Post(i)
            if self.mCfg.media_mode == 'SLB':
                self.mApb.write(0x00060090, 0x00000000, i) # release masking of dig_ioc_en
                self.SetTxBist(channel=i)
                self.SetRxBist(channel=i)
            else:
                self.SetTxOff(channel=i)
                self.SetRxOff(channel=i)
        #self.DumpRegFile(tag='init')
    def SetWA0_Post(self,channel):
        self.mApb.write(0x50000,0x8,channel)
        self.mApb.write(0x50000,0x0,channel)
        self.mApb.write(0x601dc, 0x00000001, channel)
        self.mApb.write(0x6008C,1<<0,channel,1<<0) #rx_en
        if (self.mCfg.data_rate == 10.3125):
            self.mApb.write(0x50100,0x02, channel)
            self.mApb.write(0x50100,0x42, channel)
        if (self.mCfg.data_rate == 10.3125):
            self.mApb.write(0x63450,0x100d,channel)    # skew hold en [12] Debugging by who 190909
        elif (self.mCfg.data_rate == 25.78125):
            self.mApb.write(0x63450,0x000d,channel)    # skew hold en [12] Debugging by who 190909
        else:
            self.mApb.write(0x63450,0x000b,channel)    # skew hold en [12] Debugging by who 190909
#----------------------------------------------------------------------------------------------------
# Measurement
#----------------------------------------------------------------------------------------------------
    def Move_EOM_PI(self,phase=0,channel=0):
        cur_phase = self.mApb.read(0x61008,channel)
        while (cur_phase != phase):
            if(cur_phase < 256 and phase > 256) or (cur_phase > phase):
                cur_phase = cur_phase - 1 if cur_phase != 0 else 512
            else:
                cur_phase = cur_phase + 1 if cur_phase != 511 else 0
            self.mApb.write(0x61008,cur_phase,channel)
    def GetHorizontalCenter(self,channel=0):
        minData = 1 << 30
        minDataPosition = 64
        thres = 5
        self.mApb.write(0x00061020, 0, channel)    # EOM alpha
        self.mApb.write(0x00061018, 0x7017, channel)
        self.mApb.write(0x00060100, 0<<6, channel, 1<<6) # select data_path
        zeroRight = 0
        zeroLeft = 1000
        totalPhase = 128
        phaseStep = 2
        if (self.is_bbpd_rate(self.data_rate)) : # 10G
            totalPhase *= 2
            phaseStep *= 2
        curPhase = self.mApb.read(0x00061008)
        phase_i_init = -40
        for phase_i in range(phase_i_init, totalPhase + 50, phaseStep) :
            if (phase_i < totalPhase / 2) :
                phase = phase_i + 512 - totalPhase / 2
            else :
                phase = phase_i - totalPhase / 2
            # move to initial state
            if (phase_i == phase_i_init) :
                self.Move_EOM_PI(phase,channel)
            self.mApb.write(0x00061008, phase)
            self.mApb.write(0x00060100, 1<<7, channel, 1<<7) # eom_en
            data = self.mApb.read(0x00063428)
            while ((data & 0x2) != 2) :
                data = self.mApb.read(0x00063428)
                Delay(1)
            data1 = self.mApb.read(0x00063418)
            data2 = self.mApb.read(0x0006341C)
            data = data1 + (data2 <<16)
            print ("phase=%d, %d, %d, %d" % (phase, data, data1, data2))
            if (data < minData) :
                minData = data
                minDataPosition = phase_i
            if (zeroLeft == 1000 and data <= thres) :
                zeroLeft = phase_i
            if (zeroLeft != 1000 and data > thres) :
                zeroRight = phase_i
                break
        print("left right : %d, %d" % (zeroLeft, zeroRight))
        if (zeroLeft != 1000 and zeroRight == 0) :
            return zeroLeft + totalPhase / 2
        elif (zeroLeft == 1000 and zeroRight == 0) :
            return minDataPosition
        else :
            return (zeroRight + zeroLeft) / 2

    def GetBathtub(self,channel=0):
        totalPhase = 128 if self.is_bbpd_rate(self.mCfg.data_rate) else 128*2
        phaseStep  = 2 if self.is_bbpd_rate(self.mCfg.data_rate)  else 2*2
        curPhase = self.mApb.read(0x61008,channel)
        centerPosition = self.GetHorizontalCenter(channel)
        print("center : %d" %(centerPosition))
        filename = ("bathtub_%s_ln%s.txt" % (str(self.mCfg.data_rate),str(channel)))
        fs = open(filename,'w')
        self.mApb.write(0x61020,0,channel)
        self.mApb.write(0x61018,0x7017,channel)
        self.mApb.write(0x60100,0<<6,channel,1<<6) #eom_data_path_ch=0(test)
        for phase_i in range(0,totlaPhase-0,phaseStep):
            if (phase_i < totalPhase - centerPosition):
                phase = phase_i + (512-totalPhase) + centerPosition
            else:
                phase = phase_i - (totalPhase - centerPosition)
            if(phase_i==0):
                self.Move_EOM_PI(phase)
            self.mApb.write(0x61008,phase,channel)
            self.mApb.write(0x60100,1<<7,channel,1<<7) # eom_en
            # poll eom_error_accum_done_2_3==1
            data = self.mApb.read(0x00063428)
            while ((data & 0x2) != 2) :
                data = self.mApb.read(0x00063428)
                Delay(1)
            data1 = self.mApb.read(0x00063418)
            data2 = self.mApb.read(0x0006341C)
            data = data1 + (data2 <<16)
            print ("phase=%d, %d, %d, %d" % (phase, data, data1, data2))
            fs.write('%s %s' % (phase_i,str(data)))
        fs.close()
        print ("Bathtub Done")
    def lin_fit_pulse(self, num_point=41, main=10, eq_out=0, plot_en=1, channel=0):
        rcParams.update({'figure.autolayout': True})
        axisFont = {'family': 'serif', 'weight': 'bold', 'size': 12}
        textFont = {'family': 'serif', 'weight': 'bold', 'size': 11}
        labelFont = {'family': 'sans-serif', 'weight': 'bold', 'size': 15}
        titleFont = {'family': 'sans-serif', 'weight': 'bold', 'size': 20}
        plt.rc('font', **axisFont)
        mon_sel = eq_out
        databist = self.mApb.read(0x50104, channel)  # tx bist
        dataencode = self.mApb.read(0x50084, channel)  # encode sel
        self.mApb.write(0x00060190, 0x00000000 | mon_sel, channel)
        self.mApb.write(0x50104, 1 << 2, channel, mask=0x3 << 2)
        self.mApb.write(0x50104, 1 << 5, channel, mask=0x1 << 5)
        self.mApb.write(0x50084, 2 << 3, channel, mask=0x3 << 3)
        self.mApb.write(0x00060190, 0x00000002 | mon_sel, channel)
        self.mApb.write(0x50104, databist, channel)  # tx bist
        self.mApb.write(0x50084, dataencode, channel)  # encode sel
        dumpData=[]
        for i in range(256):
            addr = 0x00065000 + +i * 4
            if (addr == 0x65110):
                addr = 0x65111
            elif (addr == 0x65210):
                addr = 0x65212
            dumpData.append(self.mApb.read(addr ,channel))
        for i in range(256):
            if(dumpData[i]>127):
                dumpData[i] -= 256
        dumpData=np.array(dumpData)
        ### LFP extraction
        prbs13=np.zeros((8191+num_point)*2+13,dtype='int')
        prbs13[0:13] = np.array([1,1,0,1,0,1,0,1,0,0,0,0,0])
        for i in range(13,(8191+num_point)*2+13):
            prbs13[i]=prbs13[i-13]^prbs13[i-12]^prbs13[i-2]^prbs13[i-1]
        prbs13temp = np.reshape(prbs13[13:],[2,-1],'Fort')
        prbs13q=np.zeros(8191+num_point,dtype='float')
        # gray encoding
        for i in range(8191+num_point):
            if (np.array_equal(prbs13temp[:,i], np.array([0,0]))):
                prbs13q[i]=0
            elif (np.array_equal(prbs13temp[:,i], np.array([0,1]))):
                prbs13q[i]=1
            elif (np.array_equal(prbs13temp[:,i], np.array([1,1]))):
                prbs13q[i]=2
            else:
                prbs13q[i]=3
        matY=dumpData/128
        matX1=np.ones((8191+num_point,256))
        for i in range(8191+num_point):
            matX1[i]= np.roll(prbs13q/3*2-1,i)[0:256]
        matCorr1=np.dot(matX1,matY.transpose())
        startIndex1=abs(matCorr1[:8191]).argmax()
        matX2=np.ones((num_point+1,256))
        for i in range(num_point):
            matX2[i]=matX1[i+startIndex1-main]
        matP=np.dot(matY,np.dot(matX2.transpose(), np.linalg.inv(np.dot(matX2,matX2.transpose()))))
        matPulse=matP[0:num_point]
        if(plot_en):
            plt.plot(range(-main,num_point-main),matPulse,'b-o',linewidth=2)
            plt.grid()
            plt.title("Impulse response",**titleFont)
            plt.xlabel("time [UI]",**titleFont)
            plt.xlim([-main,num_point-main])
            if(eq_out==1):
                plt.savefig(self.mCfg.dump_abs_path+'lfp_eq_out.png',dpi=200)
            else:
                plt.savefig(self.mCfg.dump_abs_path+'lfp_adc_out.png',dpi=200)
            plt.close()
        return list(range(-main,num_point-main)),list(matPulse)

    def get_impulse(self, patternwidth=16,channel=0):
        mon_sel=0
        self.mApb.write(0x50118, 0x0001,channel)
        self.mApb.write(0x5011C, 0x0001,channel)
        data1cc = self.mApb.read(0x601cc, channel)   # power rdc en [0]
        databist = self.mApb.read(0x50104, channel)   # tx bist
        dataEncode = self.mApb.read(0x50084, channel)   # tx bist
        self.mApb.write(0x601cc, 0x7ff,channel)   # power rdc en [0]
        filename = self.mCfg.dump_abs_path+"dump_256" + "_ln" + str(channel) + ".txt"
        fs = open(filename, 'w')
        self.mApb.write(0x00060190, 0x00000000|mon_sel, channel)
        self.mApb.write(0x50084, 0<<3, channel, mask=3<<3)
        self.mApb.write(0x50104, 3<<2, channel, mask=0xf<<2)
        self.mApb.write(0x00060190, 0x00000002|mon_sel, channel)
        self.mApb.write(0x50104, databist,channel)   # tx bist
        self.mApb.write(0x50084, dataEncode,channel)
        self.mApb.write(0x601cc, data1cc,channel)   # power rdc en [0]
        for i in range(256):
            addr = 0x00065000 + +i * 4
            if (addr == 0x65110):
                addr = 0x65111
            elif (addr == 0x65210):
                addr = 0x65212
            fs.write("%d\t%d\n"%(i, self.mApb.read(addr ,channel)))
        fs.close()
        return self.impulse_filt(filename,patternwidth)
 
    def impulse_filt(self,filename,patternwidth):
        sinc_en =0
        axisFont = {'family' : 'serif', 'weight' : 'bold','size'   : 12}
        textFont = {'family' : 'serif', 'weight' : 'bold','size'   : 11}
        labelFont = {'family' : 'sans-serif','weight' : 'bold','size'   : 15}
        titleFont = {'family' : 'sans-serif','weight' : 'bold','size'   : 20}
        plt.rc('font', **axisFont)
        inFile=open(filename)
        inData=inFile.readlines()
        data=[int(x.strip().split()[1]) for x in inData[:256]]
        for i in range(256):
            if(data[i]>127):
                data[i] -= 256
        inFile.close()
        maxIndex = data.index(max(data))
        data = np.array(data)
        data = np.roll(data,-(maxIndex%patternwidth-2))
        avgData=np.zeros(patternwidth)
        for i in range(int(256/patternwidth)):
            avgData += data[i*patternwidth:(i+1)*patternwidth]
        avgData /= 256/patternwidth
        avgData -= avgData[0]
        if(sinc_en):
            avgDataSinc = np.zeros(10*len(avgData))
            impTrain=[]
            for i in range(len(avgData)):
                impTrain += ([avgData[i]]+[0]*9)
            sincX = np.arange(-15,15,0.1)
            sincData=np.sinc(sincX)
            avgDataSinc = np.convolve(impTrain,sincData,mode='same')
            maxIndex = list(avgDataSinc).index(max(avgDataSinc))
            avgDataSinc = np.roll(avgDataSinc,-(maxIndex-20))
            plt.plot(np.arange(-2,14,0.1),avgDataSinc[:160],'b',linewidth=2)
            plt.grid()
            plt.title("Impulse response",**titleFont)
            plt.xlabel("time [UI]",**titleFont)
            plt.savefig(filename.replace('.txt','.png'),dpi=200)
            plt.close()
        else:
            plt.plot(range(-2,patternwidth-2),avgData,'b-o',linewidth=2)
            plt.grid()
            plt.title("Impulse response",**titleFont)
            plt.xlabel("time [UI]",**titleFont)
            plt.xlim([-2,patternwidth-2])
            plt.savefig('../dump/impulse.png',dpi=200)
            plt.close()
        return list(range(-2,patternwidth-2)),avgData
    def meas_eye(self, HeightOnly=0,channel=0):
        return self.GetEye(HeightOnly,channel)
    def PMAD_GetHistoEom(self, DataOnly = 0, c0h = 0, mc0h = 0, channel=0) :
        if self.is_bbpd_rate(self.mCfg.data_rate):
            totalPhase = 256
        else :
            totalPhase = 128
        phaseStep = 2
        totalEom = []
        self.mApb.write(0x61000, 0x1B8, channel)   # eom accu time
        centerPosition = self.getHorizontalCenter(channel)
        curPhase = self.mApb.read(0x00061008,channel)
        self.mApb.write(0x00061018, 0x7017,channel)
        self.mApb.write(0x00060100, 0<<6,channel,1<<6)  # RX EOM data path ch / ffe dfe sel[5]
        for phase_i in range(0, totalPhase, phaseStep) :
            print ("start phase_i : %d"%phase_i)
            totalEomTmp = self.PMAD_EomRead(curPhase, phase_i, centerPosition, totalPhase, phaseStep, channel=channel)
            totalEomTmp = self.PMAD_rm3sigma(totalEomTmp,channel=channel)
            if DataOnly == 1 :
                totalEom.append(totalEomTmp)
                if min([int(x[2]) for x in totalEomTmp[int(mc0h):int(c0h)+1]]) != 0 and totalPhase/2 < phase_i:
                    for phase_i2 in range(phase_i, totalPhase, phaseStep) :
                        self.PMAD_EomReadFake(curPhase, phase_i2, centerPosition, totalPhase, phaseStep, channel=channel)
                    break
            else :
                totalEom += totalEomTmp
        if DataOnly == 1 :
            return totalEom
        else :
            self.PMAD_eomPlot(totalEom)
    def PMAD_EomReadFake(self, curPhase, phase_i, centerPosition, totalPhase, phaseStep, end=128, start=0, channel=0) :
        memSize = 128
        memStartAdd = 0x00063010
        totalEom = []
        if self.is_bbpd_rate(self.mCfg.data_rate):
            totalPhase *= 2
            phaseStep *= 2
        if phase_i < totalPhase - centerPosition :
            phase = phase_i + (512 - totalPhase) + centerPosition
        else :
            phase = phase_i - (totalPhase - centerPosition)
        self.mApb.write(0x00061008, phase, channel)
        self.mApb.write(0x00060100, 0<<7, channel, 1<<7)
        self.mApb.write(0x00060100, 1<<7, channel, 1<<7)
    def PMAD_EomRead(self, curPhase, phase_i, centerPosition, totalPhase, phaseStep, end=128, start=0, channel=0) :
        memSize = 128
        memStartAdd = 0x00063010
        totalEom = []
        # 10G
        if self.is_bbpd_rate(self.mCfg.data_rate):
            totalPhase *= 2
            phaseStep *= 2
        if phase_i < totalPhase - centerPosition :
            phase = phase_i + (512 - totalPhase) + centerPosition
        else :
            phase = phase_i - (totalPhase - centerPosition)
        if phase_i == 0 :
            while (curPhase != phase) :
                if (curPhase < 256 and phase > 256) or curPhase > phase :
                    curPhase -= 1
                    if curPhase < 0 :
                        curPhase += 512
                else :
                    curPhase += 1
                    if (curPhase >= 512) :
                        curPhase -= 512
                self.mApb.write(0x00061008, curPhase, channel)
        self.mApb.write(0x00061008, phase, channel)
        self.mApb.write(0x00060100, 0<<7, channel, 1<<7)
        self.mApb.write(0x00060100, 1<<7, channel, 1<<7)
        for mem_i in range(0, memSize) :
            if mem_i < start or mem_i > end :
                totalEom.append([phase_i, mem_i, 0])
            else :
                memAdd = memStartAdd + mem_i * 4
                if mem_i == 0 :
                    data = self.mApb.read(memAdd,channel)
                else :
                    data = self.mApb.read(memAdd,channel)
                totalEom.append([phase_i, mem_i, data])
        self.mApb.write(0x00060100, 0<<7, channel, 1<<7)
        return totalEom
    def getHorizontalCenter(self,ln_i=0):
        minData = 1 << 30
        minDataPosition = 64
        thres = 5
        self.mApb.write(0x00061020, 0, ln_i)
        self.mApb.write(0x00061018, 0x7017, ln_i)
        self.mApb.write(0x00060100, 0<<6, ln_i, 1<<6)
        zeroRight = 0
        zeroLeft = 1000
        totalPhase = 128
        phaseStep = self.mCfg.phaseStep
     
        if self.is_bbpd_rate(self.mCfg.data_rate):
            totalPhase *= 2
            phaseStep *= 2
        curPhase = self.mApb.read(0x00061008 ,ln_i)
        phase_i_init = -40
        for phase_i in range(phase_i_init, totalPhase + 50, phaseStep):
            if (phase_i < totalPhase / 2):
                phase = phase_i + 512 - totalPhase / 2
            else:
                phase = phase_i - totalPhase / 2
            if (phase_i == phase_i_init):
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
            self.mApb.write(0x00060100, 0<<7, ln_i, 1<<7)
            self.mApb.write(0x00060100, 1<<7, ln_i, 1<<7)
         
            data = self.mApb.read(0x00063428 ,ln_i)
            while ((data & 0x2) != 2):
                data = self.mApb.read(0x00063428 ,ln_i)
                Delay(1)
            data1 = self.mApb.read(0x00063418 ,ln_i)
            data2 = self.mApb.read(0x0006341C ,ln_i)
            data = data1 + (data2 << 16)
            #print("%d\t%d\t%d\t%d"%(phase, data, data1, data2))
            if (data < minData):
                minData = data
                minDataPosition = phase_i
            if (zeroLeft == 1000 and data <= thres):
                zeroLeft = phase_i
            if (zeroLeft != 1000 and data > thres):
                zeroRight = phase_i
                break
        print("left right : %d\t%d"%(zeroLeft, zeroRight))
        if (zeroLeft != 1000 and zeroRight == 0):
            return int(zeroLeft + totalPhase / 2)
        elif (zeroLeft == 1000 and zeroRight == 0):
            return int(minDataPosition)
        return int((zeroRight + zeroLeft) / 2)
    def PMAD_rm3sigma(self, EomData, channel) :
        phases=set([int(x[0]) for x in EomData])
        vrefs=set([int(x[1]) for x in EomData])
        phases=sorted(list(phases))
        vrefs=sorted(list(vrefs))
        c0h = float(self.mApb.read(0x6223C,channel)+3)/2.0
        c0l = float(self.mApb.read(0x62240,channel)+1)/2.0
        vrefh = (c0h + c0l)/2.0
        vrefm = 0
        vrefl = -vrefh
        vrefh += 64
        vrefm += 64
        vrefl += 64
        cntNum = np.zeros((len(phases), 4))
        for phase in range(len(phases)) :
            for vref in range(len(vrefs)) :
                if vref >= vrefh :
                    cntNum[phase][3] += EomData[phase*len(vrefs) + vref][2]
                elif vref >= vrefm :
                    cntNum[phase][2] += EomData[phase*len(vrefs) + vref][2]
                elif vref > vrefl :
                    cntNum[phase][1] += EomData[phase*len(vrefs) + vref][2]
                else :
                    cntNum[phase][0] += EomData[phase*len(vrefs) + vref][2]
            #sigma3 = [cntNum[phase][0]*0.05, cntNum[phase][1]*0.05, cntNum[phase][2]*0.05, cntNum[phase][3]*0.05]
            sigma3 = [cntNum[phase][0]*0.0015, cntNum[phase][1]*0.0015, cntNum[phase][2]*0.0015, cntNum[phase][3]*0.0015]
            sigma3s = [sigma3[0], sigma3[1], sigma3[1], sigma3[2], sigma3[2], sigma3[3]]
            data0List  = list(range(int(-c0h+64), int(vrefl)))
            data0List.reverse()
            data1ListL = list(range(int(vrefl), int(-c0l+64)))
            data1ListH = list(range(int(-c0l+64), int(vrefm)))
            data1ListH.reverse()
            data2ListL = list(range(int(vrefm), int(c0l+64)))
            data2ListH = list(range(int(c0l+64), int(vrefh)))
            data2ListH.reverse()
            data3List  = list(range(int(vrefh), int(c0h+64)))
            #for x in range(int(-c0h+64-10), int(c0h+64+10)) :
            #    print (EomData[x][2])
            dataList = [data0List, data1ListL, data1ListH, data2ListL, data2ListH, data3List]
            for ListIdx in range(6) :
                dataCumul = 0
                for vref in dataList[ListIdx] :
                    dataCumul += EomData[phase*len(vrefs) + vref][2]
                    if dataCumul > sigma3s[ListIdx] :
                        break
                    else :
                        EomData[phase*len(vrefs) + vref][2] = 0
        return EomData
    def PMAD_eomPlot(self, EomData):
        axisFont = {'family' : 'serif', 'weight' : 'bold','size'   : 12}
        textFont = {'family' : 'serif', 'weight' : 'bold','size'   : 11}
        labelFont = {'family' : 'sans-serif','weight' : 'bold','size'   : 15}
        titleFont = {'family' : 'sans-serif','weight' : 'bold','size'   : 20}
        plt.rc('font', **axisFont)
        phases=set([int(x[0]) for x in EomData])
        vrefs=set([int(x[1]) for x in EomData])
        phases=sorted(list(phases))
        vrefs=sorted(list(vrefs))
        stepPi=phases[1]-phases[0]
        stepLev=vrefs[1]-vrefs[0]
        if self.is_bbpd_rate(self.mCfg.data_rate):
            totalPi=256
        else :
            totalPi=128
        totalLev=stepLev*(len(vrefs))
        numPi=int(totalPi/stepPi)
        numLev=int(totalLev/stepLev)
        image = np.zeros((numPi,numLev)).astype(np.float)
        for row_i,row in enumerate(image):
            for col_i,col in enumerate(row):
                image[row_i][col_i]=np.nan;
        for i in range(len(EomData)):
            image[int(i/numLev)][numLev-1-i%numLev]=EomData[i][2]
            if(image[int(i/numLev)][numLev-1-i%numLev]==0):
                image[int(i/numLev)][numLev-1-i%numLev]=np.nan;
        plt.imshow(np.array(image.T),extent=[-0.5,0.5,-int(totalLev/2),int(totalLev/2)],aspect='equal',cmap=plt.get_cmap('jet'),interpolation='nearest',alpha=1.0)
        plt.axis('auto')
        plt.grid()
        if not self.is_bbpd_rate(self.mCfg.data_rate):
            plt.ylim([-64,64])
        plt.xlabel("Phase [UI]",**labelFont)
        plt.colorbar()
        plt.show()
    def CheckOverGainAdc(self, limit, ln_i=0):
        maxMin = self.GetAdcMaxMin(0,ln_i)
        maxVal = (maxMin >> 8) - 64
        minVal = 64 - (maxMin & 0x7f)
        for i in range(3):
            maxMin = self.GetAdcMaxMin(i + 1,ln_i)
            maxVal += (maxMin >> 8) - 64
            minVal += 64 - (maxMin & 0x7f)
        maxVal /= 4
        minVal /= 4
        if (maxVal >= limit and minVal >= limit):
            return 1
        else:
            return 0
    def GetAdcMaxMin(self,ch=0, ln_i=0):
        self.mApb.write(0x0006051c, 0x00000000, ln_i)
        self.mApb.write(0x00062248, (ch << 4) | 0, ln_i)
        self.mApb.write(0x00062248, (ch << 4) | 1, ln_i)
        data = self.mApb.read(0x0006224C ,ln_i);
        return data
    def GetBerToTxt(self,ber=0, channel=0):
        filename = ("ber_%s_ln%s.txt" % (str(self.mCfg.data_rate),str(channel)))
        fs = open(filename,'w')
        fs.write('%s\n' % (str(ber)))
        fs.close()
        return 0
#}}} 

