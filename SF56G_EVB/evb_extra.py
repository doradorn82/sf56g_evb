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
    textFont = {'family' : 'serif', 'weight' : 'bold','size'   : 9}
    labelFont = {'family' : 'sans-serif','weight' : 'bold','size'   : 13}
    titleFont = {'family' : 'sans-serif','weight' : 'bold','size'   : 16}
    rcParams.update({'figure.autolayout': True})
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
    marginList=[]
    berList=[]
    plt.figure(figsize=[6,5])
    for lev_i,deci in enumerate(decisionLevel):
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
        marginList.append(margin)
        berList.append([fitCrossLowY,fitCrossHighY,fitCrossY])
       
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
            col='r'
        else:
            col='g'
        plt.semilogy(adcCode,cdfLow,col+'o')
        plt.semilogy(adcCode,fitCdfLow,col,linewidth=2)
        plt.semilogy(adcCode,cdfHigh,col+'o')
        plt.semilogy(adcCode,fitCdfHigh,col,linewidth=2)
        for i in range(len(berMarginYList)):
            plt.semilogy([fitLowX[i],fitHighX[i]],[10**berMarginYList[i]]*2,'k--')
            plt.text(fitHighX[i],10**berMarginYList[i],' %.1f mV\n(1e%d)'%(margin[i],berMarginYList[i]),**textFont)
        plt.text(fitCrossX,1e-28,'BER@L\n=%.2g\nBER@H\n=%.2g\nBER@X\n=%.2g'%(fitCrossLowY,fitCrossHighY,fitCrossY),**textFont)
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

