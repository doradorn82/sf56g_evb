import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from scipy import optimize
import time

import os
import sys
evb_path = r'C:/Users/SAMSUNG/Desktop/CISCO visit/3. Programs/Python_env/GitHub/sf56g_evb/SF56G_EVB'
os.environ['SF56G_EVB_PATH'] = evb_path
sys.path.insert(0,evb_path)
from LibSF56G import SF56G

def gaussian(x, amp, cen, wid):
    return amp * np.exp(-(x-cen)**2 / wid)

def poly_1(x, a, b):
    return a* x + b

class Develop(object):
    def __init__(self,chip=None):
        if chip:
            self.mApb = chip.mApb
            self.GetEye_HeightData = chip.mPmad.GetEye_HeightData
            self.GetEye_HnC = chip.mPmad.GetEye_HnC
            self.SetEomPosition = chip.mPmad.SetEomPosition
            self.dump_path = chip.mCfg.dump_path
        else:
            self.dump_path = '../dump'
        self.phase_max = 64
        self.phase_min =-64
        self.phase_step = 1
        self.fonts  = self.plot_favorite() # fonts:=textFont,labelFont,titleFont
        self.b_plot_en = True

    def GetHorizonBathtub(self, channel=0):
        # 0. vars
        err01_l = []
        err12_l = []
        err23_l = []

        # 1. find vertical center (using histo_eom)
        # get reference
        c0h = min(63, int((self.mApb.read(0x6223C, channel) + 3) / 2.0))  # 25
        c0l = min(63, int((self.mApb.read(0x62240, channel) + 1) / 2.0))  # 9
        pam4 = (c0l != 0)
        # get histo data
        height_data = self.GetEye_HeightData(target=range(128), channel=channel)
        print (height_data[:32])
        print (height_data[32:64])
        print (height_data[64:96])
        print (height_data[96:])
        # find Height and Center
        if pam4:
            h01, c01 = self.GetEye_HnC(height_data, 64 - c0h, 64 - c0l)
            h12, c12 = self.GetEye_HnC(height_data, 64 - c0l, 64 + c0l)
            h23, c23 = self.GetEye_HnC(height_data, 64 + c0l, 64 + c0h)
        else:
            h01, c01 = 0, 0
            h12, c12 = self.GetEye_HnC(height_data, 64 - c0h, 64 + c0h)
            h23, c23 = 0, 0
        # 2. sweep phase and get err_eom.cnt with get err_eom.alpha=vertical_center
        print("c01=0x%x" % c01)
        self.mApb.write(0x6101C, c01, channel)
        self.mApb.write(0x61020, c12, channel)
        self.mApb.write(0x61024, c23, channel)

        self.SetEomPosition(self.phase_min, channel)
        self.mApb.write(0x61018, 0x7017, channel)  # TODO: accumulate time
        for phase_sign in range(self.phase_min, self.phase_max, self.phase_step):
            print("phase=%d" % phase_sign)
            phase = phase_sign if phase_sign >= 0 else (phase_sign+512)
            # move to target phase
            self.mApb.write(0x61008, phase, channel)
            # eom en
            self.mApb.write(0x60100, 0 << 7, channel, 1 << 7)
            self.mApb.write(0x60100, 1 << 7, channel, 1 << 7)
            # wait err_eom done
            self.mApb.poll(0x63428, 1 << 1, channel, 1 << 1)
            # get the results
            err01_l.append(self.mApb.read(0x63410, channel) | (self.mApb.read(0x63414, channel) << 16))
            err12_l.append(self.mApb.read(0x63418, channel) | (self.mApb.read(0x6341C, channel) << 16))
            err23_l.append(self.mApb.read(0x63420, channel) | (self.mApb.read(0x63424, channel) << 16))

        print("err01 list=>", err01_l)
        print("err12 list=>", err12_l)
        print("err23 list=>", err23_l)
        if True:
            f01 = open(self.dump_path+'/err01_list.txt','w')
            f12 = open(self.dump_path+'/err12_list.txt','w')
            f23 = open(self.dump_path+'/err23_list.txt','w')
            for e in err01_l:
                f01.write(str(e)+'\n')
            for e in err12_l:
                f12.write(str(e)+'\n')
            for e in err23_l:
                f23.write(str(e)+'\n')
            f01.close()
            f12.close()
            f23.close()
        # 3. draw extra_polation and get 3 points (width at 1e-12, [fitCrossLowY,fitCrossHighY,fitCrossY])
        extra12 = self.GetExtrapolation(err12_l,22)

        return extra12

    def GetExtrapolation(self,err_list, countNum=22):
        pi_code   = np.array(range(self.phase_min,self.phase_max,self.phase_step)) # x-axis
        half_len  = int(len(err_list)/2)
        half_zero = np.zeros(half_len)
        #left_param = [-10,30] ;
        #rght_param = [ 10,-30] ;
        left_param = [1,-50,40]
        rght_param = [1,50,40]

        # distribute left and right ber
        ber_list  = np.array(err_list) / 2**countNum
        left_ber  = np.hstack((ber_list[:half_len],half_zero))
        rght_ber  = np.hstack((half_zero,ber_list[half_len:]))

        # TODO: curve fit
        left_curve_x1 = 0
        left_curve_x2 = 0
        state = 'FIND_X1'
        for i,ber in enumerate(left_ber):
            if state == 'FIND_X1':
                if ber < 1e-5:
                    left_curve_x1 = pi_code[i]
                    state = 'FIND_X2'
            elif state == 'FIND_X2':
                if ber < 1e-15:
                    left_curve_x2 = pi_code[i]
                    state = 'DONE'

        print(left_ber)
        print(left_curve_x1,left_curve_x2)
        curve_func = gaussian
        best_vals, covar = optimize.curve_fit(curve_func, pi_code, left_ber, left_param)
        left_fit  = curve_func(pi_code, best_vals[0],best_vals[1],best_vals[2])
        left_fit  /= sum(left_fit)

        best_vals, covar = optimize.curve_fit(curve_func, pi_code, rght_ber, rght_param)
        rhgt_fit = curve_func(pi_code, best_vals[0],best_vals[1],best_vals[2])
        rhgt_fit /= sum(rhgt_fit)

        # TODO: find margin
        margin_list = [-12,-15,-17]

        # TODO: find cross points
        left_y  = np.interp(0,pi_code,left_fit)
        rght_y  = np.interp(0,pi_code,rhgt_fit)
        crss_x  = np.interp(0,(rhgt_fit-left_fit),pi_code)
        crss_y  = np.interp(crss_x, pi_code, left_fit)

        #----------------------------------------------------------------------------------------------------
        # Plot
        #----------------------------------------------------------------------------------------------------
        if self.b_plot_en:
            plt.figure(figsize=[7,6])
            # raw,fit
            plt.semilogy(pi_code,left_ber,'bo')
            plt.semilogy(pi_code,rght_ber,'bo')
            plt.semilogy(pi_code,left_fit)
            plt.semilogy(pi_code,rhgt_fit)
            # crss
            plt.text(crss_x,1e-28,'BER@L = %.2g\nBER@H = %.2g\nBER@X = %.2g'%(left_y,rght_y,crss_y),color='k',fontsize=12)
            # config
            plt.grid()
            plt.xlim([self.phase_min,self.phase_max])
            plt.ylim([1e-30,1])
            plt.yticks(10**(np.arange(0.0,-31.0,step=-2.0)))
            plt.minorticks_on()
            plt.tick_params(axis='x',which='both',direction='out',length=4,pad=8)
            plt.xlabel('Phase',**self.fonts[1])
            plt.ylabel('BER',**self.fonts[1],fontsize=18)
            plt.savefig(self.dump_path+'/h_bath.png',dpi=200)
            plt.close()

        return [left_y,rght_y,crss_y]

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
        inFileName=r'C:\Users\SAMSUNG\Desktop\CISCO visit\3. Programs\Python_env\GitHub\sf56g_evb\dump\histo_example3.txt'
        inFile      = open(inFileName)
        fileRead    = inFile.readlines()
        inFile.close()
        err_list = np.array(list([int(x.strip().split()[0]) for x in fileRead]))
        t = Develop()
        o = t.GetExtrapolation(err_list)

    if test_num == 1:
        chip = SF56G()
        chip.SetConfig('lane_en',1)
        chip.SetConfig('b_dbg_print',True)
        chip.build()
        print(chip.mCfg)
        if(chip.init_evb() < 0):
            print("exit by apb error")
            exit (-1)
        chip.set_datarate(53.125)
        chip.act_chan_TX('PRBS13',channel=0)
        chip.act_chan_RX('PRBS13',channel=0)
        chip.set_tx_pre_post(0,-0.15,0)
        chip.tune_init()
        chip.tune_rx()
        chip.mPmad.PrintLaneState()
        chip.mPmad.PrintAllRxCoef()
        chip.GetHistogram()

        ber = chip.meas_ber()
        print("ber=%4.2e" % (ber))
        if ber < 1e-4:
            # dut
            t = Develop(chip)
            t_beg = time.time()
            o = t.GetHorizonBathtub()
            t_end = time.time()
            print("processing time = %ds" % (t_end-t_beg))

