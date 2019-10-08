import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from scipy import optimize
import time

import os
import sys
evb_path = r'C:/Users/SAMSUNG/Desktop/CISCO visit/3. Programs/Python_env/github/sf56g_evb/SF56G_EVB'
os.environ['SF56G_EVB_PATH'] = evb_path
sys.path.insert(0,evb_path)
from LibSF56G import SF56G

def gaussian(x, amp, cen, wid):
    return amp * np.exp(-(x-cen)**2 / wid)

def curve_func_log10(x, a, b, c):
    return a * (10**(b*x + c))

def curve_func_order1(x, a, b):
    return a * x + b


class Develop(object):
    def __init__(self,chip=None):
        if chip:
            self.mApb = chip.mApb
            self.GetEye_HeightData = chip.mPmad.GetEye_HeightData
            self.GetEye_HnC = chip.mPmad.GetEye_HnC
            self.SetEomPosition = chip.mPmad.SetEomPosition
        else:
            self.dump_abs_path = '../dump'
        self.phase_max = 90
        self.phase_min =-90
        self.phase_step = 1
        self.pi_half_period = 64
        self.num_curve_x = 3

        self.fonts  = self.plot_favorite() # fonts:=textFont,labelFont,titleFont

    def GetBathHorizon(self, accum_set = 12, plot_en=False, dump_en=False, channel=0):
        def get_count_num(accum_set=7):
            count_set = [8,10,12,14, 16,18,20,22, 24,26,27,28, 29,30,31,32]
            return count_set[accum_set] if accum_set < len(count_set) else 32

        # 1. find vertical center (can be skipped if GetEye is done in advance)
        c0h = min(63, int((self.mApb.read(0x6223C, channel) + 3) / 2.0))
        c0l = min(63, int((self.mApb.read(0x62240, channel) + 1) / 2.0))
        pam4 = (c0l != 0)
        height_data = self.GetEye_HeightData(target=range(128), channel=channel)
        h12, c12 = self.GetEye_HnC(height_data, 64 - c0h, 64 + c0h)

        # 2. sweep phase and get err_eom.cnt
        err_list = {'01':[],'12':[],'23':[]} if pam4 else {'12':[]}
        uc12 = (c12-64)*2 if (c12-64)*2 >= 0 else (c12-64)*2+256
        # set alpha (internnaly, vref is also used, so only offset shall be set)
        self.mApb.write(0x6101C, uc12, channel)
        self.mApb.write(0x61020, uc12, channel)
        self.mApb.write(0x61024, uc12, channel)
        self.SetEomPosition(self.phase_min, channel)
        self.mApb.write(0x61018, 0x017|accum_set<<12, channel)
        for phase_sign in range(self.phase_min, self.phase_max, self.phase_step):
            phase = phase_sign if phase_sign >= 0 else (phase_sign+512)
            if phase%10 == 0:
                print("phase=(s:%d,u:%d)" % (phase_sign,phase))
            # move to target phase
            self.mApb.write(0x61008, phase, channel)
            # eom en, eom_path
            self.mApb.write(0x60100, 0<<6| 0<<7, channel, 1<<6|1<<7)
            self.mApb.write(0x60100, 1<<7, channel, 1<<7)
            # wait err_eom done
            self.mApb.poll(0x63428, 1 << 1, channel, 1 << 1)
            # get the results
            if pam4:
                err_list['01'].append(self.mApb.read(0x63410, channel) | (self.mApb.read(0x63414, channel) << 16))
                err_list['23'].append(self.mApb.read(0x63420, channel) | (self.mApb.read(0x63424, channel) << 16))
            err_list['12'].append(self.mApb.read(0x63418, channel) | (self.mApb.read(0x6341C, channel) << 16))

        if dump_en:
            for key,data_l in err_list.items():
                fh = open(self.dump_abs_path+'err'+key+'_list.txt','w')
                for data in data_l:
                    fh.write(str(data)+'\n')
                fh.close()
        # 3. Extrapolation
        extra_result = {}
        count_num = get_count_num(accum_set)
        for key,data_l in err_list.items():
            extra_result[key] = self.GetExtrapolation(data_l,count_num)

        # 4. plot
        if plot_en:
            self.PlotBathHorizon(extra_result)

        # 5. 3 points
        result = []
        result.append([0,0,0] if not pam4 else [extra_result['01']['left_y'],extra_result['01']['rght_y'],extra_result['01']['crss_y']])
        result.append([extra_result['12']['left_y'],extra_result['12']['rght_y'],extra_result['12']['crss_y']])
        result.append([0,0,0] if not pam4 else [extra_result['23']['left_y'],extra_result['23']['rght_y'],extra_result['23']['crss_y']])
        return result

    def GetExtrapolation(self, err_list, countNum=22):
        def get_fit_err_list(err_list,pi_half_period=64):
            center_left  = np.array(err_list).argmin()
            center_rght  = len(err_list) - np.array(err_list[-1::-1]).argmin()
            center       = max(pi_half_period, int((center_left + center_rght) / 2))
            fit_err_list = err_list[center - pi_half_period:center + pi_half_period]
            return fit_err_list
        def replace_zero(list,replace=1e-50):
            for idx,data in enumerate(list):
                if data == 0:
                    list[idx] = replace
            return list
        # common
        pi_code    = np.array(range(-self.pi_half_period, self.pi_half_period, 1))
        left_param = [-1, -10]
        rght_param = [1, -10]
        curve_func = curve_func_order1

        # align center
        fit_err_list = get_fit_err_list(err_list,self.pi_half_period)

        # distribute left and right ber
        ber_list  = np.array(fit_err_list) / 2**countNum
        half_zero = np.zeros(self.pi_half_period)
        left_ber  = np.hstack((ber_list[:self.pi_half_period],half_zero))
        rght_ber  = np.hstack((half_zero,ber_list[self.pi_half_period:]))

        # curve fit
        left_curve_x_end = max(self.num_curve_x,left_ber.argmin())
        left_curve_x_beg = left_curve_x_end-self.num_curve_x
        left_curve_x     = pi_code[left_curve_x_beg:left_curve_x_end]
        left_curve_y     = np.log10(replace_zero(left_ber[left_curve_x_beg:left_curve_x_end]))
        rght_curve_x_beg = len(rght_ber)-max(self.num_curve_x,np.array(rght_ber[-1::-1]).argmin())
        rght_curve_x_end = rght_curve_x_beg+self.num_curve_x
        rght_curve_x     = pi_code[rght_curve_x_beg:rght_curve_x_end]
        rght_curve_y     = np.log10(replace_zero(rght_ber[rght_curve_x_beg:rght_curve_x_end]))

        left_fit_param, covar = optimize.curve_fit(curve_func, left_curve_x, left_curve_y, left_param)
        rght_fit_param, covar = optimize.curve_fit(curve_func, rght_curve_x, rght_curve_y, rght_param)
        left_fit = np.hstack((left_ber[:left_curve_x_beg], (10**curve_func(pi_code[left_curve_x_beg:], left_fit_param[0],left_fit_param[1]))))
        rght_fit = np.hstack( (10**curve_func(pi_code[:rght_curve_x_end], rght_fit_param[0],rght_fit_param[1]), rght_ber[rght_curve_x_end:]) )

        #print('left_ber=>',left_ber)
        #print('left curve =>', left_curve_x, left_curve_y)
        #print('left_fit=>',left_fit)
        #print('left_fit_param=>',left_fit_param)
        #print('rght_ber=>',rght_ber)
        #print('rght curve =>', rght_curve_x, rght_curve_y)
        #print('rght_fit=>',rght_fit)
        #print('rght_fit_param=>',rght_fit_param)

        # TODO: find margin
        margin_list = [-12,-15,-17]

        # find cross points
        left_y = np.interp(0,pi_code,left_fit)
        rght_y = np.interp(0,pi_code,rght_fit)
        crss_x = np.interp(0,(rght_fit-left_fit),pi_code)
        crss_y = np.interp(crss_x, pi_code, left_fit)
        # gather results
        result = {}
        result['left_ber'] = left_ber
        result['left_fit'] = left_fit
        result['left_y']   = left_y
        result['rght_ber'] = rght_ber
        result['rght_fit'] = rght_fit
        result['rght_y']   = rght_y
        result['crss_x']   = crss_x
        result['crss_y']   = crss_y
        return result

    def PlotBathHorizon(self,data_pack):
        pi_code = np.array(range(-self.pi_half_period, self.pi_half_period, 1))
        plt.figure(figsize=[7,6])
        idx = 0
        for key,data in data_pack.items():
            # raw,fit
            #plt.semilogy(pi_code,data['left_ber'],'bo')
            #plt.semilogy(pi_code,data['rght_ber'],'bo')
            plt.semilogy(pi_code,data['left_fit'])
            plt.semilogy(pi_code,data['rght_fit'])
            # crss
            plt.text(0,10**-(20+4*idx),'<EYE%s>\nBER@L = %.2e\nBER@H = %.2e\nBER@X = %.2e'%(key,data['left_y'],data['rght_y'],data['crss_y']),color='k',fontsize=10)
            idx+=1
        # config
        plt.grid()
        plt.xlim([-64,64])
        plt.ylim([1e-30,1])
        plt.yticks(10**(np.arange(0.0,-31.0,step=-2.0)))
        plt.minorticks_on()
        plt.tick_params(axis='x',which='both',direction='out',length=4,pad=8)
        plt.xlabel('Phase',**self.fonts[1])
        plt.ylabel('BER',**self.fonts[1],fontsize=18)
        plt_name = (self.mCfg.dump_abs_path+'hbat'+self.mCfg.GetCondition()+'.png') if hasattr(self,'mCfg') else '../dump/hbath.png'
        plt.savefig(plt_name,dpi=200)
        plt.close()


    def plot_favorite(self):
        axisFont = {'family' : 'serif', 'weight' : 'bold','size'   : 12}
        textFont = {'family' : 'serif', 'weight' : 'bold','size'   : 11}
        labelFont = {'family' : 'sans-serif','weight' : 'bold','size'   : 15}
        titleFont = {'family' : 'sans-serif','weight' : 'bold','size'   : 20}
        rcParams.update({'figure.autolayout': True})
        plt.rc('font', **axisFont)
        return textFont,labelFont,titleFont

if __name__ == '__main__':
    test_num = 1
    if test_num == 2:
        dut = Develop()
        #inFileName=r'C:\Users\SAMSUNG\Desktop\CISCO visit\3. Programs\Python_env\GitHub\ber_eom(53g_prbs7)\err12_list.txt'
        dir_name = r'C:\Users\SAMSUNG\Desktop\CISCO visit\3. Programs\Python_env\GitHub\ber_eom(53g_prbs7)/'
        #dir_name = r'C:\Users\SAMSUNG\Desktop\CISCO visit\3. Programs\Python_env\GitHub\ber_eom(25g_prbs31)/'
        file_names = ['err01_list.txt','err12_list.txt','err23_list.txt']
        keys = ['01','12','23'] if ('53g' in dir_name) else ['12']
        extra_result = {}
        for key in keys:
            fh      = open(dir_name+'err'+key+'_list.txt')
            data_list = np.array(list([int(x.strip().split()[0]) for x in fh.readlines()]))
            extra_result[key] = dut.GetExtrapolation(data_list)
            fh.close()
        dut.PlotBathHorizon(extra_result)

    if test_num == 1:
        chip = SF56G()
        chip.SetConfig('lane_en',1)
        chip.SetConfig('extra_h_dump',True)
        chip.SetConfig('extra_h_plot',True)
        chip.SetConfig('extra_h_plot_raw',True)
        chip.SetConfig('b_dbg_print',True)
        chip.build()
        #print(chip.mCfg)
        if(chip.init_evb(channels=[0]) < 0):
            print("exit by apb error")
            exit (-1)
        #chip.set_datarate(53.125)
        chip.set_datarate(25.78125)
        chip.act_chan_TX('PRBS31',channel=0)
        chip.act_chan_RX('PRBS31',channel=0)
        chip.set_tx_pre_post(tx_pre1=-0.15,attenuation=1)
        chip.tune_init()
        #chip.tune_rx()
        chip.mPmad.PrintLaneState()
        chip.mPmad.PrintAllRxCoef()
        #chip.GetHistogram()

        ber = chip.meas_ber()
        print("ber=%4.2e" % (ber))
        if ber < 1e-4:
            # dut
            t_beg = time.time()
            #status = chip.mPmad.GetStatus(HeightOnly=1,lin_fit_en=0,tag='test run',channel=0)
            status = chip.mPmad.get_extra_ber_horizontal(10,0)
            t_end = time.time()
            print("processing time = %ds" % (t_end-t_beg))
            print(status)

