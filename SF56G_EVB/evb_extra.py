import sys,glob
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import copy
#from scipy.optimize import curve_fit
from matplotlib import rcParams
from scipy import optimize
def plot_favorite():
    axisFont = {'family' : 'serif', 'weight' : 'bold','size'   : 11}
    textFont = {'family' : 'serif', 'weight' : 'bold','size'   : 7}
    labelFont = {'family' : 'sans-serif','weight' : 'bold','size'   : 13}
    titleFont = {'family' : 'sans-serif','weight' : 'bold','size'   : 16}
    rcParams.update({'figure.autolayout': False})
    plt.rc('font', **axisFont)
    return textFont,labelFont,titleFont
def normFunc(x, xMean, sigma):
    return 1/(sigma*np.sqrt(2*np.pi)) * np.e**(-0.5*((x-xMean)/sigma)**2)

def gaussian(x, amp, cen, wid):
    out=np.ones(len(x))
    if(wid<=0):
        return out
    else:
        for i in range(len(x)):
            if(((x[i]-cen)**2/wid)<40):
                out[i] = amp * np.exp(-(x[i]-cen)**2 / wid)
            else:
                out[i] = 0
    return out

def bathtub_extrapolation_vertical(filename,filename2,countNum=29,countNum2=19,pam4=0,vrefSel=4,berMarginYList=[-12,-15,-17]):
    textFont,labelFont,titleFont = plot_favorite()

    inFileName=filename
    inFileName2=filename2

    if(vrefSel==7):
        adcCode=np.linspace(-230,230,128)
    elif(vrefSel==6):
        adcCode=np.linspace(-220,220,128)
    elif(vrefSel==5):
        adcCode=np.linspace(-210,210,128)
    elif(vrefSel==3):
        adcCode=np.linspace(-190,190,128)
    elif(vrefSel==2):
        adcCode=np.linspace(-180,180,128)
    elif(vrefSel==1):
        adcCode=np.linspace(-170,170,128)
    elif(vrefSel==0):
        adcCode=np.linspace(-170,170,128)
    else:
        adcCode=np.linspace(-200,200,128)

    inFile      = open(inFileName)
    fileRead    = inFile.readlines()
    inFile.close()
    hist     = np.array(list([float(x.strip().split()[1]) for x in fileRead]))
    inFile      = open(inFileName2)
    fileRead    = inFile.readlines()
    inFile.close()
    hist2     = np.array(list([float(x.strip().split()[1]) for x in fileRead]))
    dataLen=len(fileRead)

    decisionLevel = []
    left=1000
    right=0
    for i in range(dataLen-1):
        if(left==1000 and right==0 and hist[i]>1000 and hist[i+1]<=1000):
            left = i
        elif(left!=1000 and right==0 and hist[i]<1000 and hist[i+1]>=1000):
            right = i
            decisionLevel.append(int((left+right)/2))
            left=1000
            right=0
            if((pam4==1 and len(decisionLevel)==3) or (pam4==0)):
                break
    zeroData=np.zeros(dataLen)
    marginList=[[0]*len(berMarginYList)]*3
    berList=[[0.5,0.5,0.5]]*3
    plt.figure(figsize=[7,5])

    for lev_i,deci in enumerate(decisionLevel):
        if(pam4==1):
            eff_lev_i = lev_i
        else:
            eff_lev_i = lev_i + 1
        if(lev_i==0):
            low  = np.hstack((hist[:deci],zeroData[deci:]))
            if(pam4==1):
                high = np.hstack((zeroData[:deci],hist[deci:decisionLevel[1]],zeroData[decisionLevel[1]:]))
            else:
                high = np.hstack((zeroData[:deci],hist[deci:]))
        elif(lev_i==1):
            low  = np.hstack((zeroData[:decisionLevel[0]],hist[decisionLevel[0]:deci],zeroData[deci:]))
            high  = np.hstack((zeroData[:deci],hist[deci:decisionLevel[2]],zeroData[decisionLevel[2]:]))
        else:
            low  = np.hstack((zeroData[:decisionLevel[1]],hist[decisionLevel[1]:deci],zeroData[deci:]))
            high = np.hstack((zeroData[:deci],hist[deci:]))
        maxIdxLow  = np.argmax(low)
        maxIdxHigh = np.argmax(high)
       
        cntMax = (2**16)-1
        accMax = 2**countNum
       
        clipIdxLow  = []
        clipIdxHigh = []
        for i in range(dataLen):
            if(low[i] == cntMax):
                low[i] = hist2[i]*(2**(countNum-countNum2))
            if(high[i] == cntMax):
                high[i] = hist2[i]*(2**(countNum-countNum2))
        pdfLow  = low/np.sum(low)
        pdfHigh = high/np.sum(high)
        cdfLow = np.zeros(dataLen)
        cdfHigh= np.zeros(dataLen)
        for i in range(dataLen):
            if(pam4==1):
                cdfLow[i]  = sum(pdfLow[i:])/4
                cdfHigh[i] = sum(pdfHigh[:i+1])/4
            else:
                cdfLow[i]  = sum(pdfLow[i:])/2
                cdfHigh[i] = sum(pdfHigh[:i+1])/2
        
        for i in range(dataLen):
            if(cdfLow[i] > 1e-5):
                low1e5Index=i
            if(cdfLow[i] < 1e-15):
                lowStopIndex=i
                cdfLow[i:]=[0]*(dataLen-i)
                break
        for i in range(dataLen):
            if(cdfHigh[i] > 1e-5):
                high1e5Index=i
                break
        for i in range(dataLen):
            if(cdfHigh[i] > 1e-15):
                highStartIndex=i
                cdfHigh[:i]=[0]*i
                break
        
        fitCdfLow  = np.zeros(dataLen)
        fitCdfHigh = np.zeros(dataLen)
       
        best_vals, covar = optimize.curve_fit(gaussian, adcCode, pdfLow,[1,adcCode[low1e5Index],40]) 
        for i in range(30):
            fitPdfLow = gaussian(adcCode,best_vals[0],best_vals[1],best_vals[2]*(1+i*0.02))
            fitPdfLow /= sum(fitPdfLow)
            for j in range(dataLen):
                fitCdfLow[j]  = sum(fitPdfLow[j:])/2
            if(fitCdfLow[lowStopIndex-2] >= cdfLow[lowStopIndex-2]):
                fitPdfLow = gaussian(adcCode,best_vals[0],best_vals[1],best_vals[2]*(1+(i-1)*0.02))
                fitPdfLow /= sum(fitPdfLow)
                for j in range(dataLen):
                    if(pam4==1):
                        fitCdfLow[j]  = sum(fitPdfLow[j:])/4
                    else:
                        fitCdfLow[j]  = sum(fitPdfLow[j:])/2
                break
        best_vals, covar = optimize.curve_fit(gaussian, adcCode, pdfHigh,[1,adcCode[high1e5Index],40]) 
        for i in range(30):
            fitPdfHigh = gaussian(adcCode,best_vals[0],best_vals[1],best_vals[2]*(1+i*0.02))
            fitPdfHigh /= sum(fitPdfHigh)
            for j in range(dataLen):
                fitCdfHigh[j] = sum(fitPdfHigh[:j+1])/2
            if(fitCdfHigh[highStartIndex+2] >= cdfHigh[highStartIndex+2]):
                fitPdfHigh = gaussian(adcCode,best_vals[0],best_vals[1],best_vals[2]*(1+i*0.02))
                fitPdfHigh /= sum(fitPdfHigh)
                for j in range(dataLen):
                    if(pam4==1):
                        fitCdfHigh[j] = sum(fitPdfHigh[:j+1])/4
                    else:
                        fitCdfHigh[j] = sum(fitPdfHigh[:j+1])/2
                break
    
        for i in range(dataLen):
            if(i==dataLen-1):
                needExtraIndex = i
                break
            if(fitCdfLow[i] < 1e-15):
                needExtraIndex = i
                break
        if(needExtraIndex>1):
            for i in range(needExtraIndex,dataLen):
                fitCdfLow[i] = fitCdfLow[needExtraIndex-1]/(fitCdfLow[needExtraIndex-2]/fitCdfLow[needExtraIndex-1])**(i-needExtraIndex+1)
        
        for i in range(dataLen):
            if(fitCdfHigh[i] > 1e-15):
                needExtraIndex = i
                break
        if(needExtraIndex<dataLen-2):
            for i in range(0,needExtraIndex):
                fitCdfHigh[i] = fitCdfHigh[needExtraIndex]/(fitCdfHigh[needExtraIndex+1]/fitCdfHigh[needExtraIndex])**(needExtraIndex-i)
        fitLowX = np.interp(berMarginYList,np.log10(fitCdfLow[:low1e5Index:-1]),adcCode[:low1e5Index:-1])
        fitHighX = np.interp(berMarginYList,np.log10(fitCdfHigh[:high1e5Index]),adcCode[:high1e5Index])
        margin = (fitHighX-fitLowX)
        for i in range(len(margin)):
            if(margin[i]<=0):
                margin[i]=0
        if(pam4==0 or lev_i==1):
            fitCrossLowY = np.interp(0,adcCode,fitCdfLow)
            fitCrossHighY = np.interp(0,adcCode,fitCdfHigh)
        else:
            fitCrossLowY = np.interp(np.mean(adcCode[deci:deci+2]),adcCode,fitCdfLow)
            fitCrossHighY = np.interp(np.mean(adcCode[deci:deci+2]),adcCode,fitCdfHigh)
        fitCrossX = np.interp(0,fitCdfHigh-fitCdfLow,adcCode)
        fitCrossY = np.interp(fitCrossX,adcCode,fitCdfLow)
        marginList[eff_lev_i] = list(margin)
        berList[eff_lev_i] = [fitCrossLowY,fitCrossHighY,fitCrossY]
       
        ##Plot result
        if(pam4==1):
            for data_i in range(dataLen-2):
                if(data_i<dataLen-2):
                    if(cdfLow[data_i+2]>0.24 and lev_i!=0):
                        cdfLow[data_i]=np.nan
                    if(fitCdfLow[data_i]>0.24 and lev_i!=0):
                        fitCdfLow[data_i]=np.nan
                    if(cdfHigh[dataLen-data_i-3]>0.24 and lev_i!=2):
                        cdfHigh[dataLen-data_i-1]=np.nan
                    if(fitCdfHigh[dataLen-data_i-3]>0.24 and lev_i!=2):
                        fitCdfHigh[dataLen-data_i-1]=np.nan
        if(lev_i==0):
            col='b'
        elif(lev_i==1):
            col='m'
        else:
            col='g'
        plt.semilogy(adcCode,cdfLow,col+'o')
        plt.semilogy(adcCode,fitCdfLow,col,linewidth=2)
        plt.semilogy(adcCode,cdfHigh,col+'o')
        plt.semilogy(adcCode,fitCdfHigh,col,linewidth=2)
        for i in range(len(berMarginYList)):
            if(fitLowX[i]<fitHighX[i]):
                plt.semilogy([fitLowX[i], fitHighX[i]], [10 ** berMarginYList[i]] * 2, 'k--')
            else:
                plt.semilogy([fitLowX[i], fitHighX[i]], [10 ** berMarginYList[i]] * 2, 'r--')
            #plt.text(fitHighX[i],10**berMarginYList[i],' %.1f mV\n(1e%d)'%(margin[i],berMarginYList[i]),**textFont)
            plt.text(220+eff_lev_i*60, 10 ** berMarginYList[i], ' %.1f mV\n(1e%d)' % (margin[i], berMarginYList[i]), **textFont)
            plt.text(220+eff_lev_i*60, 10 ** berMarginYList[i], ' %.1f mV\n(1e%d)' % (margin[i], berMarginYList[i]), **textFont)
        #plt.text(fitCrossX,1e-28,'BER@L\n=%.2g\nBER@H\n=%.2g\nBER@X\n=%.2g'%(fitCrossLowY,fitCrossHighY,fitCrossY),**textFont)
        plt.text(220 + eff_lev_i * 60, 1e-4, '<EYE%d%d>'%(eff_lev_i,eff_lev_i+1), **textFont)
        plt.text(220 + eff_lev_i * 60, 1e-28, 'BER@L\n=%.2g\nBER@H\n=%.2g\nBER@X\n=%.2g' % (fitCrossLowY, fitCrossHighY, fitCrossY),
                          **textFont)
    plt.subplots_adjust(top=0.9,left=0.15,bottom=0.15,right=0.7)
    plt.title('Vertical Bathtub BER',**titleFont)
    plt.xlim([-200,200])
    plt.yticks(10**(np.arange(0.0,-31.0,step=-2.0)))
    plt.minorticks_on()
    plt.tick_params(axis='x',which='both',direction='out',length=4,pad=8)
    plt.grid()
    plt.ylim([1e-30,1])
    plt.xlabel('Voltage [mV]',**labelFont)
    plt.ylabel('BER',**labelFont)
    plt.savefig(filename.replace('.txt','_bathtub.png'),dpi=200)
    plt.close()
    return marginList,berList

def curve_func_order1(x, a, b):
    return a * x + b
def bathtub_extrapolation_horizontal(err_list, countNum=22, margin_list=[-12,-15,-17],tag=''):
    extra_h_curve_num = 4
    pi_period = 128
    pi_half_period = int(pi_period/2)
    def get_fit_err_list(err_list,pi_half_period=64):
        center_left  = np.array(err_list).argmin()
        center_rght  = len(err_list) - np.array(err_list[-1::-1]).argmin()
        center       = max(pi_half_period, int((center_left + center_rght) / 2))
        fit_center   = min((len(err_list)-pi_half_period),max(pi_half_period,center))
        fit_err_list = err_list[fit_center - pi_half_period:fit_center + pi_half_period]
        #if (fit_center != center):
        #    print("[extra_ber_h] center left(%d) rght(%d) mid(%d) fit(%d) list len(%d)" %(center_left,center_rght,center,fit_center,len(fit_err_list)))
        return fit_err_list
    def replace_zero(list,replace=1e-50):
        for idx,data in enumerate(list):
            if data == 0:
                list[idx] = replace
        return list
    # common
    pi_code    = np.array(range(-pi_half_period, pi_half_period, 1))
    left_param = [-1, -10]
    rght_param = [1, -10]
    curve_func = curve_func_order1

    # align center
    fit_err_list = get_fit_err_list(err_list,pi_half_period)

    # distribute left and right ber
    ber_list  = np.array(fit_err_list) / 2**countNum
    half_zero = np.zeros(pi_half_period)
    left_ber  = np.hstack((ber_list[:pi_half_period],half_zero))
    rght_ber  = np.hstack((half_zero,ber_list[pi_half_period:]))

    # curve fit
    curve_num        = extra_h_curve_num
    left_curve_x_end = max(curve_num,left_ber.argmin())-2
    left_curve_x_beg = left_curve_x_end-curve_num-2
    left_curve_x     = pi_code[left_curve_x_beg:left_curve_x_end-2]
    left_curve_y     = np.log10(replace_zero(left_ber[left_curve_x_beg:left_curve_x_end-2]))

    rght_curve_x_beg = len(rght_ber)-max(curve_num,np.array(rght_ber[-1::-1]).argmin())+2
    rght_curve_x_end = rght_curve_x_beg+curve_num+2
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
    #print(("[%s] rght_fit_param=>" %(tag)),rght_fit_param)
    #print(('[%s] rght_ber=>' %(tag)),rght_ber)
    #print(('[%s] rght_fit=>' %(tag)),rght_fit)
    #print('rght_fit_param=>',rght_fit_param)

    # find margin
    left_margin = np.interp(margin_list,np.log10(left_fit)[::-1],pi_code[::-1])
    rght_margin = np.interp(margin_list,np.log10(rght_fit),pi_code)
    margin   = (rght_margin-left_margin)/128
    margin   = [m if m > 0 else 0 for m in margin]

    # find cross points
    left_y = np.interp(0,pi_code,left_fit)
    rght_y = np.interp(0,pi_code,rght_fit)
    crss_x = np.interp(0,(rght_fit-left_fit),pi_code)
    crss_y = np.interp(crss_x, pi_code, left_fit)
    # gather results
    result = {}
    result['left_ber'] = left_ber
    result['left_fit'] = left_fit
    result['rght_ber'] = rght_ber
    result['rght_fit'] = rght_fit
    result['crss_x']   = crss_x
    result['ber_center'] = [left_y,rght_y,crss_y]
    result['margin']   = margin
    result['left_margin'] = left_margin/128
    result['rght_margin'] = rght_margin/128
    return result
