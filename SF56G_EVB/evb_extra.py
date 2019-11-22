import sys, glob
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
import scipy



def plot_favorite():
    axisFont = {'family': 'serif', 'weight': 'bold', 'size': 11}
    textFont = {'family': 'serif', 'weight': 'bold', 'size': 7}
    labelFont = {'family': 'sans-serif', 'weight': 'bold', 'size': 13}
    titleFont = {'family': 'sans-serif', 'weight': 'bold', 'size': 16}
    rcParams.update({'figure.autolayout': False})
    plt.rc('font', **axisFont)
    return textFont, labelFont, titleFont


def Qfunc(x,cen,sigma,A):
    return 0.5*scipy.special.erfc((x-cen)/(np.sqrt(2)*sigma))*np.exp(A)

def invQfunc(x,cen,sigma,A):
    return 0.5*scipy.special.erfc((cen-x)/(np.sqrt(2)*sigma))*np.exp(A)

def LQfunc(x,cen,sigma,A):
    return np.log(0.5*scipy.special.erfc((x-cen)/(np.sqrt(2)*sigma)).clip(1e-150,np.inf)*np.exp(A))

def LinvQfunc(x,cen,sigma,A):
    return np.log(0.5*scipy.special.erfc((cen-x)/(np.sqrt(2)*sigma)).clip(1e-150,np.inf)*np.exp(A))

def Qfunc_fitting(cdf,adcCode,inv=0):
    BERforfitting=1e-3
    index=np.where((cdf>1e-150) & (cdf<BERforfitting))
    while(len(index[0])<4): # gurantees minimum amount of sample points(=5) for fitting
        BERforfitting=BERforfitting*10
        index=np.where((cdf>1e-150) & (cdf<BERforfitting))
    a=adcCode[index[0]]
    c=cdf[index[0]]
    if(inv==0):
        best_vals, covar = scipy.optimize.curve_fit(LQfunc,a,np.log(c),bounds=([-np.inf,0,-np.inf],[a[0],np.inf,0]),sigma=np.abs(np.log(c)))
    else:
        best_vals, covar = scipy.optimize.curve_fit(LinvQfunc, a, np.log(c),bounds=([a[0], 0, -np.inf], [np.inf, np.inf, 0]),sigma=np.abs(np.log(c)))
    return best_vals



def bathtub_extrapolation_vertical(filename, pam4=0, vrefSel=4, berMarginYList=[-12, -15, -17], mode='BOTH',decisionLevelIn=[64]):
    textFont, labelFont, titleFont = plot_favorite()

    eyeOpenBer=1e-4

    marginList = [[0] * len(berMarginYList)] * 3
    berList = [[0.5, 0.5, 0.5]] * 3
    eyeOpenSizeList = [0, 0, 0]

    if(mode=='NONE'):
        return marginList, berList, eyeOpenSizeList

    inFileName = filename

    if (vrefSel == 7):
        adcCode = np.linspace(-230, 230, 128)
    elif (vrefSel == 6):
        adcCode = np.linspace(-220, 220, 128)
    elif (vrefSel == 5):
        adcCode = np.linspace(-210, 210, 128)
    elif (vrefSel == 3):
        adcCode = np.linspace(-190, 190, 128)
    elif (vrefSel == 2):
        adcCode = np.linspace(-180, 180, 128)
    elif (vrefSel == 1):
        adcCode = np.linspace(-170, 170, 128)
    elif (vrefSel == 0):
        adcCode = np.linspace(-160, 160, 128)
    else:
        adcCode = np.linspace(-200, 200, 128)

    inFile = open(inFileName)
    fileRead = inFile.readlines()
    inFile.close()
    hist = np.array(list([float(x.strip().split()[1]) for x in fileRead]))
    dataLen = len(fileRead)

    decisionLevel=decisionLevelIn
    zeroData = np.zeros(dataLen)

    # remove outliar in histogram
    zeroIndex=np.where(hist==0)[0]
    for i in range(len(zeroIndex)-1):
        if((zeroIndex[i+1]-zeroIndex[i])<4): # histogram with width < 3 is deleted
            hist[zeroIndex[i]:zeroIndex[i+1]]=0


    plt.figure(figsize=[7, 5])

    for lev_i, deci in enumerate(decisionLevel):
        if (pam4 == 1):
            eff_lev_i = lev_i
        else:
            eff_lev_i = lev_i + 1
        if (lev_i == 0):
            low = np.hstack((hist[:deci], zeroData[deci:]))
            if (pam4 == 1):
                high = np.hstack((zeroData[:deci], hist[deci:decisionLevel[1]], zeroData[decisionLevel[1]:]))
            else:
                high = np.hstack((zeroData[:deci], hist[deci:]))
        elif (lev_i == 1):
            low = np.hstack((zeroData[:decisionLevel[0]], hist[decisionLevel[0]:deci], zeroData[deci:]))
            high = np.hstack((zeroData[:deci], hist[deci:decisionLevel[2]], zeroData[decisionLevel[2]:]))
        else:
            low = np.hstack((zeroData[:decisionLevel[1]], hist[decisionLevel[1]:deci], zeroData[deci:]))
            high = np.hstack((zeroData[:deci], hist[deci:]))

        pdfLow = low / low.sum()
        pdfHigh = high /high.sum()
        cdfLow = np.zeros(dataLen)
        cdfHigh = np.zeros(dataLen)
        for i in range(dataLen):
            if (pam4 == 1):
                cdfLow[i] = sum(pdfLow[i:]) / 4
                cdfHigh[i] = sum(pdfHigh[:i + 1]) / 4
            else:
                cdfLow[i] = sum(pdfLow[i:]) / 2
                cdfHigh[i] = sum(pdfHigh[:i + 1]) / 2

        # measure vertical Eye open at BER =< eyeOpenBer
        eyeOpenX =np.array([np.interp(np.log10(eyeOpenBer), np.log10(cdfLow[::-1]+1e-150), adcCode[::-1]),np.interp(np.log10(eyeOpenBer), np.log10(cdfHigh+1e-150), adcCode)])
        eyeOpenSizeList[eff_lev_i] = eyeOpenX[1]-eyeOpenX[0]

        fitCdfLow = np.array(cdfLow)
        fitCdfHigh = np.array(cdfHigh)

        if(mode=='BOTH'):
            best_vals = Qfunc_fitting(cdfLow, adcCode, inv=0)
            fitCdfLowQ = Qfunc(adcCode, best_vals[0], best_vals[1], best_vals[2])
            fitCdfLow[np.where(cdfLow < 1e-3)[0]] = fitCdfLowQ[np.where(cdfLow < 1e-3)[0]]

            best_vals = Qfunc_fitting(cdfHigh, adcCode, inv=1)
            fitCdfHighQ = invQfunc(adcCode, best_vals[0], best_vals[1], best_vals[2])
            fitCdfHigh[np.where(cdfHigh < 1e-3)[0]] = fitCdfHighQ[np.where(cdfHigh < 1e-3)[0]]

            fitLowX = np.interp([-1*10**x for x in berMarginYList], -1*fitCdfLow, adcCode)
            fitHighX = np.interp([10**x for x in berMarginYList], fitCdfHigh, adcCode)
            margin = (fitHighX - fitLowX).clip(0,np.inf)

            if (pam4 == 0 or lev_i == 1):
                fitCrossLowY = np.interp(0, adcCode, fitCdfLow)
                fitCrossHighY = np.interp(0, adcCode, fitCdfHigh)
            else:
                fitCrossLowY = np.interp(np.mean(adcCode[deci:deci + 2]), adcCode, fitCdfLow)
                fitCrossHighY = np.interp(np.mean(adcCode[deci:deci + 2]), adcCode, fitCdfHigh)
            fitCrossX = np.interp(0, fitCdfHigh - fitCdfLow, adcCode)
            fitCrossY = np.interp(fitCrossX, adcCode, fitCdfLow)

            marginList[eff_lev_i] = list(margin)
            berList[eff_lev_i] = [fitCrossLowY, fitCrossHighY, fitCrossY]

        else:
           berMarginYList=[]


        ##Plot result
        if (pam4 == 1):
            for data_i in range(dataLen - 2):
                if (data_i < dataLen - 2):
                    if (cdfLow[data_i + 2] > 0.24 and lev_i != 0):
                        cdfLow[data_i] = np.nan
                    if (fitCdfLow[data_i] > 0.24 and lev_i != 0):
                        fitCdfLow[data_i] = np.nan
                    if (cdfHigh[dataLen - data_i - 3] > 0.24 and lev_i != 2):
                        cdfHigh[dataLen - data_i - 1] = np.nan
                    if (fitCdfHigh[dataLen - data_i - 3] > 0.24 and lev_i != 2):
                        fitCdfHigh[dataLen - data_i - 1] = np.nan
        if (eff_lev_i == 0):
            col = 'm'
        elif (eff_lev_i == 1):
            col = 'b'
        else:
            col = 'g'

        if(mode!='BOTH'):
            fitCdfLow = fitCdfLow + fitCdfHigh
            emptyIndex=np.where(fitCdfLow==0)[0]
            if(len(emptyIndex)!=0):
                A=emptyIndex[0]
                B=emptyIndex[-1]
                fitCdfLow[A:B+1]=np.interp(emptyIndex,[A-1,B+1],[fitCdfLow[A-1],fitCdfLow[B+1]]) # interpolation
            fitCdfHigh = fitCdfLow

        plt.semilogy(adcCode, cdfLow, col + 'o', markersize=4)
        plt.semilogy(adcCode, fitCdfLow, col, linewidth=2)
        plt.semilogy(adcCode, cdfHigh, col + 'o', markersize=4)
        plt.semilogy(adcCode, fitCdfHigh, col, linewidth=2)

        plt.semilogy(eyeOpenX, [eyeOpenBer]* 2, col+'--')

        for i in range(len(berMarginYList)):
            if (fitLowX[i] < fitHighX[i]):
                plt.semilogy([fitLowX[i], fitHighX[i]], [10 ** berMarginYList[i]] * 2, 'k--')
            else:
                plt.semilogy([fitLowX[i], fitHighX[i]], [10 ** berMarginYList[i]] * 2, 'r--')
            plt.text(220 + eff_lev_i * 60, 10 ** berMarginYList[i], ' %.1f mV\n(1e%d)' % (margin[i], berMarginYList[i]),**textFont)
        plt.text(220 + eff_lev_i * 60, 1e-4, '<EYE%d%d>' % (eff_lev_i, eff_lev_i + 1), **textFont,color=col)

        if(mode=='BOTH'):
            if (pam4 == 1):
                plt.text(220 + eff_lev_i * 60, 1e-18,
                         'BER@L\n=%.2g\nBER@H\n=%.2g\nBER@X\n=%.2g' % (fitCrossLowY, fitCrossHighY, fitCrossY),
                         **textFont)
            else:
                plt.text(220 + eff_lev_i * 60, 1e-28,
                         'BER@L\n=%.2g\nBER@H\n=%.2g\nBER@X\n=%.2g' % (fitCrossLowY, fitCrossHighY, fitCrossY),
                         **textFont)

    if(mode=='BOTH'):
        berList2=np.array(berList)*np.array([[pam4,pam4,pam4],[1,1,1],[pam4,pam4,pam4]])
        berMaxIndex1=int(berList2.argmax()/3)
        berMaxIndex2=np.mod(berList2.argmax(),3)
        yList=[1e-28,1e-18]
        lhx=['L','H','X']
        plt.text(220 + berMaxIndex1 * 60, yList[pam4],'BER@'+lhx[berMaxIndex2]+'\n=%.2g'% berList2[berMaxIndex1,berMaxIndex2]+('\n'*2*(2-berMaxIndex2)),**textFont,color='red')

    plt.subplots_adjust(top=0.9, left=0.15, bottom=0.15, right=0.7)
    plt.title('Vertical Bathtub BER', **titleFont)
    plt.xlim([-200, 200])
    plt.yticks(10 ** (np.arange(0.0, -31.0, step=-2.0)))
    plt.minorticks_on()
    plt.tick_params(axis='x', which='both', direction='out', length=4, pad=8)
    plt.grid()
    if (pam4 == 1):
        plt.ylim([1e-20, 1])
    else:
        plt.ylim([1e-30, 1])
    plt.xlabel('Voltage [mV]', **labelFont)
    plt.ylabel('BER', **labelFont)
    plt.savefig(filename.replace('histo_data','bathtub_vertical').replace('.txt', '.png'), dpi=200)
    plt.close()

    plt.plot(np.arange(-64,64),hist)
    plt.grid(True)
    plt.savefig(filename.replace('histo_data','histogram').replace('.txt', '.png'), dpi=200)
    plt.close()
    return marginList, berList, eyeOpenSizeList

def bathtub_extrapolation_horizontal(filename, filename2, countNum=29, countNum2=18, pam4=0, berMarginYList=[-12, -15, -17], mode='BOTH'):
    textFont, labelFont, titleFont = plot_favorite()
    eyeOpenBer = 1e-4

    marginList = [[0] * len(berMarginYList)] * 3
    berList = [[0.5, 0.5, 0.5]] * 3
    eyeOpenSizeList=[0,0,0]

    if(mode=='NONE'):
        return marginList, berList, eyeOpenSizeList

    inFileName = filename
    inFileName2 = filename2

    inFile = open(inFileName)
    fileRead = inFile.readlines()
    inFile.close()
    hist = np.array(list([float(x.strip().split()[1]) for x in fileRead]))
    inFile = open(inFileName2)
    fileRead = inFile.readlines()
    inFile.close()
    hist2 = np.array(list([float(x.strip().split()[1]) for x in fileRead]))
    if (pam4 == 1):
        levelNum = 3
    else:
        levelNum = 1
    cntMax = (2 ** 16) - 1

    for i in range(len(hist)):
        if (hist[i] == cntMax):
            hist[i] = hist2[i] * (2 ** (countNum - countNum2))

    # remove outliar in histogram
    zeroIndex=np.where(hist==0)[0]
    for i in range(len(zeroIndex)-1):
        if((zeroIndex[i+1]-zeroIndex[i])<4): # histogram with width < 3 is deleted
            hist[zeroIndex[i]:zeroIndex[i+1]]=0


    phaseCode = np.array([int(x.strip().split()[0]) for x in fileRead])
    if(pam4==0):
        phaseStep = int(phaseCode[1] - phaseCode[0])
    else:
        phaseStep = int(phaseCode[3] - phaseCode[0])
    totalPhase = int(phaseCode[-1] - phaseCode[0] +phaseStep)

    dataLen = int(totalPhase/phaseStep)
    halfPhase = int(dataLen/2)
    zeroData = np.zeros(dataLen)
    plt.figure(figsize=[7, 5])
    for lev_i in range(levelNum):
        if (pam4 == 1):
            eff_lev_i = lev_i
        else:
            eff_lev_i = lev_i + 1
        low = np.hstack((hist[lev_i:halfPhase * levelNum:levelNum], zeroData[halfPhase:]))
        high = np.hstack((zeroData[:halfPhase], hist[halfPhase * levelNum + lev_i::levelNum]))
        for i in range(dataLen-1):
            if(low[i+1] != 0 and low[i] == 0):
                low[i] = low[i+1]
            if (high[i + 1] == 0 and high[i] != 0):
                high[i+1] = high[i]
        pdfLow = low / 2 ** (countNum)
        pdfHigh = high / 2 ** (countNum)
        cdfLow = np.zeros(dataLen)
        cdfHigh = np.zeros(dataLen)
        for i in range(dataLen):
            if (pam4 == 1):
                cdfLow[i] = sum(pdfLow[i:]) / 4 *phaseStep
                cdfHigh[i] = sum(pdfHigh[:i + 1]) / 4 *phaseStep
            else:
                cdfLow[i] = sum(pdfLow[i:]) / 2 *phaseStep
                cdfHigh[i] = sum(pdfHigh[:i + 1]) / 2 *phaseStep

        # measure horizontal Eye open at BER =< eyeOpenBer
        phase = (np.array(range(0,totalPhase,phaseStep))-int(totalPhase/2)) / 2**int(np.log2(max(phaseCode))+1)
        eyeOpenX = np.array([np.interp(np.log10(eyeOpenBer), np.log10(cdfLow[::-1]+1e-150), phase[::-1]), np.interp(np.log10(eyeOpenBer), np.log10(cdfHigh+1e-150), phase)])
        eyeOpenSize = min(np.abs(eyeOpenX))
        eyeOpenX = np.array([-1 * eyeOpenSize, eyeOpenSize])
        eyeOpenSizeList[eff_lev_i] = eyeOpenSize * 2

        fitCdfLow = np.array(cdfLow)
        fitCdfHigh = np.array(cdfHigh)

        if (mode=='BOTH'):
            best_vals = Qfunc_fitting(cdfLow, phase, inv=0)
            fitCdfLowQ = Qfunc(phase, best_vals[0], best_vals[1], best_vals[2])
            fitCdfLow[np.where(cdfLow < 1e-3)[0]] = fitCdfLowQ[np.where(cdfLow < 1e-3)[0]]

            best_vals = Qfunc_fitting(cdfHigh, phase, inv=1)
            fitCdfHighQ = invQfunc(phase, best_vals[0], best_vals[1], best_vals[2])
            fitCdfHigh[np.where(cdfHigh < 1e-3)[0]] = fitCdfHighQ[np.where(cdfHigh < 1e-3)[0]]

            fitLowX = np.interp([-1*10**x for x in berMarginYList], -1*fitCdfLow, phase)
            fitHighX = np.interp([10**x for x in berMarginYList], fitCdfHigh, phase)
            margin = np.zeros(len(berMarginYList))
            for mar_i in range(len(berMarginYList)):
                margin[mar_i] = min(fitHighX[mar_i],-fitLowX[mar_i])*2
                if(margin[mar_i]<0):
                    margin[mar_i]=0
            marginList[eff_lev_i] = list(margin)
            fitCrossLowY = np.interp(0, phase, fitCdfLow)
            fitCrossHighY = np.interp(0, phase, fitCdfHigh)
            fitCrossX = np.interp(0, fitCdfHigh - fitCdfLow, phase)
            fitCrossY = np.interp(fitCrossX, phase, fitCdfLow)
            marginList[eff_lev_i] = list(margin)
            berList[eff_lev_i] = [fitCrossLowY, fitCrossHighY, fitCrossY]
        else:
            berMarginYList=[]


        ##Plot result
        if (eff_lev_i == 0):
            col = 'm'
        elif (eff_lev_i == 1):
            col = 'b'
        else:
            col = 'g'

        if (mode != 'BOTH'):
            fitCdfLow = fitCdfLow + fitCdfHigh
            emptyIndex=np.where(fitCdfLow==0)[0]
            if(len(emptyIndex)!=0):
                A=emptyIndex[0]
                B=emptyIndex[-1]
                fitCdfLow[A:B+1]=np.interp(emptyIndex,[A-1,B+1],[fitCdfLow[A-1],fitCdfLow[B+1]]) # interpolation
            fitCdfHigh = fitCdfLow



        plt.semilogy(phase, cdfLow, col + 'o', markersize=4)
        plt.semilogy(phase, fitCdfLow, col, linewidth=2)
        plt.semilogy(phase, cdfHigh, col + 'o', markersize=4)
        plt.semilogy(phase, fitCdfHigh, col, linewidth=2)

        plt.semilogy(eyeOpenX, [eyeOpenBer]* 2, col+'--')

        for i in range(len(berMarginYList)):
            if (margin[i] > 0):
                plt.semilogy([-margin[i]/2, margin[i]/2], [10 ** berMarginYList[i]] * 2, 'k--')
            else:
                plt.semilogy([-margin[i]/2, margin[i]/2], [10 ** berMarginYList[i]] * 2, 'r--')
            plt.text(220 * 0.6 / 200 + eff_lev_i * 60 * 0.5 / 200, 10 ** berMarginYList[i], ' %.2f UI\n(1e%d)' % (margin[i], berMarginYList[i]),
                     **textFont)

        plt.text(220 * 0.6 / 200 + eff_lev_i * 60 * 0.5 / 200, 1e-4, '<EYE%d%d>' % (eff_lev_i, eff_lev_i + 1), **textFont,color=col)


        if(mode=='BOTH'):
            if (pam4 == 1):
                plt.text(220 * 0.6 / 200 + eff_lev_i * 60 * 0.5 / 200, 1e-18,
                         'BER@L\n=%.2g\nBER@R\n=%.2g\nBER@X\n=%.2g' % (fitCrossLowY, fitCrossHighY, fitCrossY),
                         **textFont)
            else:
                plt.text(220 * 0.6 / 200 + eff_lev_i * 60 * 0.5 / 200, 1e-28,
                         'BER@L\n=%.2g\nBER@R\n=%.2g\nBER@X\n=%.2g' % (fitCrossLowY, fitCrossHighY, fitCrossY),
                         **textFont)

    if(mode=='BOTH'):
        berList2=np.array(berList)*np.array([[pam4,pam4,pam4],[1,1,1],[pam4,pam4,pam4]])
        berMaxIndex1=int(berList2.argmax()/3)
        berMaxIndex2=np.mod(berList2.argmax(),3)
        yList=[1e-28,1e-18]
        lhx=['L','R','X']
        plt.text(220 * 0.6 / 200 + berMaxIndex1 * 60 * 0.5 / 200, yList[pam4],'BER@'+lhx[berMaxIndex2]+'\n=%.2g'% berList2[berMaxIndex1,berMaxIndex2]+('\n'*2*(2-berMaxIndex2)),**textFont,color='red')



    plt.subplots_adjust(top=0.9, left=0.15, bottom=0.15, right=0.7)
    plt.title('Horizontal Bathtub BER', **titleFont)
    plt.xlim([-0.6, 0.6])
    plt.yticks(10 ** (np.arange(0.0, -31.0, step=-2.0)))
    plt.minorticks_on()
    plt.tick_params(axis='x', which='both', direction='out', length=4, pad=8)
    plt.grid()
    if (pam4 == 1):
        plt.ylim([1e-20, 1])
    else:
        plt.ylim([1e-30, 1])
    plt.xlabel('Phase [UI]', **labelFont)
    plt.ylabel('BER', **labelFont)
    plt.savefig(filename.replace('hori_data','bathtub_horizontal').replace('.txt', '.png'), dpi=200)
    plt.close()
    return marginList, berList, eyeOpenSizeList
