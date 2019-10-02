import sys,glob
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import copy
#from scipy.optimize import curve_fit
from matplotlib import rcParams
def plot_favorite():
    axisFont = {'family' : 'serif', 'weight' : 'bold','size'   : 12}
    textFont = {'family' : 'serif', 'weight' : 'bold','size'   : 11}
    labelFont = {'family' : 'sans-serif','weight' : 'bold','size'   : 15}
    titleFont = {'family' : 'sans-serif','weight' : 'bold','size'   : 20}
    plt.rc('font', **axisFont)
    return textFont,labelFont,titleFont
def normFunc(x, xMean, sigma):
    return 1/(sigma*np.sqrt(2*np.pi)) * np.e**(-0.5*((x-xMean)/sigma)**2)

def bathtub_extrapolation_nrz(filename,countNum=19):
    textFont,labelFont,titleFont = plot_favorite()

    inFileName=filename
    numExtrap=2
    ignLast=1
   
    #sysPath='D:\\Work\\AutomationPjt\\DisplayPort_Automation_GBE\\WindowsFormsApp1\\bin\\Debug\\'
    inFile      = open(inFileName)
    fileRead    = inFile.readlines()
    adcCode     = np.array(list([float(x.strip().split()[0]) for x in fileRead]))
    nrzHist     = np.array(list([float(x.strip().split()[1]) for x in fileRead]))
   
    ##Split histogram at center point
    nrzZero = np.zeros(int(len(nrzHist)/2))
    nrzLow  = np.hstack((nrzHist[:int(len(nrzHist)/2)],nrzZero))
    nrzHigh = np.hstack((nrzZero,nrzHist[int(len(nrzHist)/2):]))
    maxIdxLow  = np.argmax(nrzLow)
    maxIdxHigh = np.argmax(nrzHigh)
   
    cntMax = (2**16)-1
    accMax = 2**countNum
   
    numClipLow  = 0.5*accMax-np.sum(nrzLow)
    numClipHigh = 0.5*accMax-np.sum(nrzHigh)
   
    clipIdxLow  = []
    clipIdxHigh = []
    for i in range(len(adcCode)):
        if(nrzLow[i] == cntMax):
            clipIdxLow.append(i)
        if(nrzHigh[i] == cntMax):
            clipIdxHigh.append(i)
   
    if not (len(clipIdxLow)==0):
        fillCntLow = numClipLow//len(clipIdxLow)
        resCntLow  = numClipLow - fillCntLow*len(clipIdxLow)
        for i,idx in enumerate(clipIdxLow):
            if(i == len(clipIdxLow)//2):
                nrzLow[idx] += fillCntLow + resCntLow
            else:
                nrzLow[idx] += fillCntLow
        pdfLow  = nrzLow/(0.5*accMax)
    else:
        pdfLow  = nrzLow/np.sum(nrzLow)
   
    if not (len(clipIdxHigh)==0):
        fillCntHigh = numClipHigh//len(clipIdxHigh)
        resCntHigh  = numClipHigh - fillCntHigh*len(clipIdxHigh)
        for i,idx in enumerate(clipIdxHigh):
            if(i == len(clipIdxHigh)//2):
                nrzHigh[idx] += fillCntHigh + resCntHigh
            else:
                nrzHigh[idx] += fillCntHigh
        pdfHigh = nrzHigh/(0.5*accMax)
    else:
        pdfHigh = nrzHigh/np.sum(nrzHigh)


    ##CDF
    cdfLow  = np.zeros(len(nrzHist))
    cdfHigh = np.zeros(len(nrzHist))
    for i in range(len(nrzHist)):
        for j in range(i):
            cdfLow[i]  += pdfLow[j]
            cdfHigh[i] += pdfHigh[len(nrzHist)-1-j]
    cdfHigh = cdfHigh[::-1]
   
    ##Error function
    errpdfLow  = (1-cdfLow)/2
    errpdfHigh = (1-cdfHigh)/2
   
    validBerLow  = []
    validBerHigh = []
    validCodeLow  = []
    validCodeHigh = []
    for i in range(len(adcCode)):
        if(errpdfLow[i] > 10**-15):
            validBerLow.append(errpdfLow[i])
            validCodeLow.append(i)
        else:
            errpdfLow[i]=0
        if(errpdfHigh[i] > 10**-15):
            validBerHigh.append(errpdfHigh[i])
            validCodeHigh.append(i)
        else:
            errpdfHigh[i]=0
    berEdge = validBerLow[-1] if validBerLow[-1] > validBerHigh[0] else validBerHigh[0]
   
    ##Extrapolate bathtub
    cOffset = len(adcCode)/2
    extraCodeLow  = np.delete(adcCode,validCodeLow)
    extraCodeHigh = np.delete(adcCode,validCodeHigh)
    if(ignLast==1):
        zLow = np.polyfit(validCodeLow[-numExtrap-1:-1],np.log10(validBerLow[-numExtrap-1:-1]),1)
        extraLow = zLow[0]*np.hstack((validCodeLow[-numExtrap-1:],extraCodeLow))+zLow[1]
        zHigh = np.polyfit(validCodeHigh[1:numExtrap+1],np.log10(validBerHigh[1:numExtrap+1]),1)
        extraHigh = zHigh[0]*np.hstack((extraCodeHigh,validCodeHigh[:numExtrap+1]))+zHigh[1]
    else:
        zLow = np.polyfit(validCodeLow[-numExtrap:],np.log10(validBerLow[-numExtrap:]),1)
        extraLow = zLow[0]*np.hstack((validCodeLow[-numExtrap:],extraCodeLow))+zLow[1]
        zHigh = np.polyfit(validCodeHigh[:numExtrap],np.log10(validBerHigh[:numExtrap]),1)
        extraHigh = zHigh[0]*np.hstack((extraCodeHigh,validCodeHigh[:numExtrap]))+zHigh[1]
   
    crossVal = (zHigh[1]-zLow[1])/(zLow[0]-zHigh[0])
    berAtCross = 10**(zHigh[0]*crossVal+zHigh[1])
   
    ber12codeLow  = np.ceil((-12-zLow[1])/zLow[0])
    ber12codeHigh = np.trunc((-12-zHigh[1])/zHigh[0])
    ber12margin   = ber12codeHigh - ber12codeLow
   
    ##Plot result
    plt.figure(figsize=[7,6])
    plt.title('Estimated BER from Histogram',**titleFont)
    plt.semilogy(adcCode-cOffset,errpdfLow,'bo')
    plt.semilogy(adcCode-cOffset,errpdfHigh,'ro')
    if(ignLast==1):
        plt.semilogy(np.hstack((validCodeLow[-numExtrap-1:],extraCodeLow))-cOffset,10**extraLow,'b')
        plt.semilogy(np.hstack((extraCodeHigh,validCodeHigh[:numExtrap+1]))-cOffset,10**extraHigh,'r')
    else:
        plt.semilogy(np.hstack((validCodeLow[-numExtrap:],extraCodeLow))-cOffset,10**extraLow,'b')
        plt.semilogy(np.hstack((extraCodeHigh,validCodeHigh[:numExtrap]))-cOffset,10**extraHigh,'r')
    plt.semilogy([ber12codeLow-cOffset,ber12codeHigh-cOffset],[10**-12,10**-12],'k--')
    plt.text(ber12codeHigh-cOffset+2,10**-11.5,'margin=%dcode'%ber12margin,color='k',fontsize=12)
    plt.text(crossVal-cOffset+2,berAtCross,'BER at X-point=%.3g'%berAtCross,color='k',fontsize=12)
    plt.text(-64,10**-3.8,'numExtrap=%d\nignoreLast=%d'%(numExtrap,ignLast),color='gray',fontsize=10)
    #plt.xlim([maxIdxLow-10-cOffset, maxIdxHigh+10-cOffset])
    plt.ylim([10**-30,10])
    plt.yticks(10**(np.arange(0.0,-31.0,step=-2.0)))
    plt.minorticks_on()
    plt.tick_params(axis='x',which='both',direction='out',length=4,pad=8)
    #plt.grid(color='gray',dashes=(4,2))
    plt.grid()
    plt.xlabel('ADC code [7-bit]',**labelFont)
    plt.ylabel('BER',**labelFont,fontsize=18)
    plt.savefig(filename.replace('.txt','_bathtub.png'),dpi=200)
    plt.close()

    return berAtCross

def bathtub_extrapolation_pam4(filename,countNum=19):

    rcParams.update({'figure.autolayout': True})
    textFont,labelFont,titleFont = plot_favorite()


    inFileName=filename
    outFileName=filename.replace('.txt','.png')

    #inFileName='D:\\Work\\AutomationPjt\\DisplayPort_Automation_GBE\\WindowsFormsApp1\\bin\\Debug\\histo_data_acc.txt'
    #outFileName='D:\\Work\\AutomationPjt\\DisplayPort_Automation_GBE\\WindowsFormsApp1\\bin\\Debug\\histo_data_rlb36db_53g_reg_reg_NN_33_ln0.txt'

    mu       = 2   # modulation index : pam4 = 2
    ignLast  = 1
    numExtrap= 2

    inFile      = open(inFileName)
    fileRead    = inFile.readlines()
    adcCode     = np.array(list([int(x.strip().split()[0]) for x in fileRead]))
    pamHist     = np.array(list([float(x.strip().split()[1]) for x in fileRead]))

    peakCnt=[]
    peakIdx=[]
    notchCnt=[]
    notchIdx=[]
    notchDiff=[]
    notchLCR=[]
    slope=1
    histCntPre = 0
    for i in range(1,len(adcCode)):
        if(slope==1): #Increase
            if(pamHist[i] >= histCntPre):
                histCntPre=pamHist[i]
            else:
                histCntPre=pamHist[i]
                peakCnt.append(pamHist[i-1])
                peakIdx.append(i-1)
                slope=0
        else: #Decrease
            if(pamHist[i] <= histCntPre):
                histCntPre=pamHist[i]
            else:
                histCntPre=pamHist[i]
                notchCnt.append(pamHist[i-1])
                notchIdx.append(i-1)
                slope=1
    #if(len(notchIdx)==3):
    #    notchIdx[1]=64
    print('notchIdx :',notchIdx)
    if(len(notchIdx) > 2**mu-1):
        print('%d notch point exist..'%len(notchIdx))
        for i in range(len(notchIdx)-1):
            notchDiff.append(notchIdx[i+1]-notchIdx[i])
        for i in range(len(notchIdx)):
            if(notchIdx[i]>60 and notchIdx[i]<68):
                print('notch idx for upper eye  : %d'%notchIdx[i+1])
                print('notch idx for center eye : %d'%notchIdx[i])
                print('notch idx for lower eye  : %d'%notchIdx[i-1])
                notchLCR.append(notchIdx[i-1])
                notchLCR.append(notchIdx[i])
                notchLCR.append(notchIdx[i+1])

    pamHistSub = np.zeros((2**mu,len(adcCode)))
    if(len(notchIdx)==2**mu-1):
        pam4Bound = np.hstack((0,notchIdx,len(adcCode)-1))
    else:
        pam4Bound = np.hstack((0,notchLCR,len(adcCode)-1))

    pdfPam     = np.zeros((2**mu,len(adcCode)))
    cdfPam     = np.zeros((2**mu,len(adcCode)))
    cdfPamReve = np.zeros((2**mu,len(adcCode)))
    errPam     = np.zeros((2**mu,len(adcCode)))
    errPamReve = np.zeros((2**mu,len(adcCode)))
    pdfPamFit  = np.zeros((2**mu,len(adcCode)))
    cdfPamFit  = np.zeros((2**mu,len(adcCode)))
    cdfPamFitReve = np.zeros((2**mu,len(adcCode)))
    errPamFit     = np.zeros((2**mu,len(adcCode)))
    errPamFitReve = np.zeros((2**mu,len(adcCode)))
   
    for i in range(2**mu):
        #print('level %d'%i)
        for j in range(int(pam4Bound[i]),int(pam4Bound[i+1]+1)):
            if(j==0 or j==len(adcCode)-1):
                pamHistSub[i][j]=pamHist[j]
            elif(j==pam4Bound[i]):
                pamHistSub[i][j]=np.ceil(pamHist[j]/2)
            elif(j==pam4Bound[i+1]):
                pamHistSub[i][j]=np.trunc(pamHist[j]/2)
            else:
                pamHistSub[i][j]=pamHist[j]

    cntMax = (2**16)-1
    #cntMax = 2**99
    accMax = 2**(countNum)
    numClipPam = np.zeros(2**mu)
    fillCntPam = np.zeros(2**mu)
    resCntPam  = np.zeros(2**mu)
    crossVal   = np.zeros(2**mu-1)
    berCross   = np.zeros(2**mu-1)
    ber12codeL = np.zeros(2**mu-1)
    ber12codeR = np.zeros(2**mu-1)
    ber12margin= np.zeros(2**mu-1)
    blankList  = []
    clipIdxPam = [copy.deepcopy(blankList) for i in range(2**mu)]

    validBerPam      = [copy.deepcopy(blankList) for i in range(2**mu)]
    validCodePam     = [copy.deepcopy(blankList) for i in range(2**mu)]
    validBerPamReve  = [copy.deepcopy(blankList) for i in range(2**mu)]
    validCodePamReve = [copy.deepcopy(blankList) for i in range(2**mu)]
    extraCodePam     = []
    extraCodePamReve = []
    fitCoeff         = []
    extraPam         = []
    fitCoeffReve     = []
    extraPamReve     = []
    invIdx           = []
    crossCoeff       = []
    crossCoeffReve   = []
    crossValFit      = np.zeros(2**mu-1)
    berCrossFit      = np.zeros(2**mu-1)
    for i in range(2**mu):
        numClipPam[i]  = 0.25*accMax-np.sum(pamHistSub[i])

        for j in range(len(adcCode)):
            if(pamHistSub[i][j] == cntMax):
                clipIdxPam[i].append(j)

        if not (len(clipIdxPam[i])==0):
            fillCntPam[i] = numClipPam[i]/len(clipIdxPam[i])
            resCntPam[i]  = numClipPam[i] - fillCntPam[i]*len(clipIdxPam[i])
            for j,idx in enumerate(clipIdxPam[i]):
                if(j == len(clipIdxPam[i])/2):
                    pamHistSub[i][idx] += fillCntPam[i] + resCntPam[i]
                else:
                    pamHistSub[i][idx] += fillCntPam[i]
            pdfPam[i]  = pamHistSub[i]/(accMax)*2
        else:
            pdfPam[i]  = pamHistSub[i]/np.sum(pamHistSub[i])/2

        #popt, pcov = curve_fit(normFunc, adcCode, pdfPam[i], bounds=(0., [110., 10.]))
        #pdfPamFit[i] = normFunc(adcCode,popt[0],popt[1])

        for j in range(len(adcCode)):
            for k in range(j):
                cdfPam[i][j]     += pdfPam[i][k]
                #cdfPamFit[i][j]  += pdfPamFit[i][k]
                cdfPamReve[i][len(adcCode)-1-j]    += pdfPam[i][len(adcCode)-1-k]
                #cdfPamFitReve[i][len(adcCode)-1-j] += pdfPamFit[i][len(adcCode)-1-k]
        errPam[i]     = 0.5-cdfPam[i]
        errPamReve[i] = 0.5-cdfPamReve[i]
        #errPamFit[i]     = 1.0-cdfPamFit[i]
        #errPamFitReve[i] = 1.0-cdfPamFitReve[i]

        for j in range(len(adcCode)):
            if(errPam[i][j] > 10**-15):
                validBerPam[i].append(errPam[i][j]/2)
                validCodePam[i].append(adcCode[j])
            else:
                #errPam[i][j]=np.nan
                errPam[i][j]=0
            if(errPamReve[i][j] > 10**-15):
                validBerPamReve[i].append(errPamReve[i][j]/2)
                validCodePamReve[i].append(adcCode[j])
            else:
                errPamReve[i][j]=0
                #errPamReve[i][j]=np.nan

        #berEdge = validBerLow[-1] if validBerLow[-1] > validBerHigh[0] else validBerHigh[0]
        extraCodePam.append(np.delete(adcCode,validCodePam[i]))
        extraCodePamReve.append(np.delete(adcCode,validCodePamReve[i]))

        ##Extrapolate bathtub
        if(ignLast==1):
            fitCoeff.append( np.polyfit(validCodePam[i][-numExtrap-1:-1],np.log10(validBerPam[i][-numExtrap-1:-1]),1) )
            extraPam.append( fitCoeff[i][0]*np.hstack((validCodePam[i][-numExtrap-1:],extraCodePam[i]))+fitCoeff[i][1] )
            fitCoeffReve.append( np.polyfit(validCodePamReve[i][1:numExtrap+1],np.log10(validBerPamReve[i][1:numExtrap+1]),1) )
            extraPamReve.append( fitCoeffReve[i][0]*np.hstack((extraCodePamReve[i],validCodePamReve[i][:numExtrap+1]))+fitCoeffReve[i][1] )
        else:
            fitCoeff.append( np.polyfit(validCodePam[i][-numExtrap:],np.log10(validBerPam[i][-numExtrap:]),1) )
            extraPam.append( fitCoeff[i][0]*np.hstack((validCodePam[i][-numExtrap:],extraCodePam[i]))+fitCoeff[i][1] )
            fitCoeffReve.append( np.polyfit(validCodePamReve[i][:numExtrap],np.log10(validBerPamReve[i][:numExtrap]),1) )
            extraPamReve.append( fitCoeffReve[i][0]*np.hstack((extraCodePamReve[i],validCodePamReve[i][:numExtrap]))+fitCoeffReve[i][1] )

    for i in range(2**mu-1):
        crossVal[i] = (fitCoeffReve[i+1][1]-fitCoeff[i][1])/(fitCoeff[i][0]-fitCoeffReve[i+1][0])
        berCross[i] = 10**(fitCoeff[i][0]*crossVal[i]+fitCoeff[i][1])
        ber12codeL[i]  = np.ceil((-12-fitCoeff[i][1])/fitCoeff[i][0])
        ber12codeR[i]  = np.trunc((-12-fitCoeffReve[i+1][1])/fitCoeffReve[i+1][0])
        if(ber12codeR[i]-ber12codeL[i] <= 0):
            ber12margin[i] = 0
        else:
            ber12margin[i] = ber12codeR[i] - ber12codeL[i]

    cOffset = len(adcCode)/2
    blankList          = []
    limitBerPam      = [copy.deepcopy(blankList) for i in range(2**mu)]
    limitCodePam     = [copy.deepcopy(blankList) for i in range(2**mu)]
    limitBerPamReve  = [copy.deepcopy(blankList) for i in range(2**mu)]
    limitCodePamReve = [copy.deepcopy(blankList) for i in range(2**mu)]
    for i in range(2**mu):
        for j in range(len(validBerPam[i])):
            if(validBerPam[i][j]<0.25):
            #if not (validBerPam[i][j] == 1):
                limitBerPam[i].append(validBerPam[i][j])
                limitCodePam[i].append(validCodePam[i][j])
        for j in range(len(validBerPamReve[i])):
            if(validBerPamReve[i][j]<0.25):
            #if not (validBerPamReve[i][j] == 1):
                limitBerPamReve[i].append(validBerPamReve[i][j])
                limitCodePamReve[i].append(validCodePamReve[i][j])
    for i in range(2**mu-1):
        for j in range(len(adcCode)):
            #if(errPamFit[i][j]-errPamFitReve[i+1][j]<0):
            if(errPam[i][j]-errPamReve[i+1][j]<0):
                invIdx.append(j)
                break
    #    print(errPam[i])
    #    crossCoeff.append(np.polyfit(adcCode[invIdx[i]-1:invIdx[i]+1],np.log10(errPam[i][invIdx[i]-1:invIdx[i]+1]),1))
    #    crossCoeffReve.append(np.polyfit(adcCode[invIdx[i]-1:invIdx[i]+1],np.log10(errPamReve[i+1][invIdx[i]-1:invIdx[i]+1]),1) )
        #crossCoeff.append(np.polyfit(adcCode[invIdx[i]-1:invIdx[i]+1],np.log10(errPamFit[i][invIdx[i]-1:invIdx[i]+1]),1))
        #crossCoeffReve.append(np.polyfit(adcCode[invIdx[i]-1:invIdx[i]+1],np.log10(errPamFitReve[i+1][invIdx[i]-1:invIdx[i]+1]),1) )
    #for i in range(2**mu-1):
    #    crossValFit[i] = (crossCoeffReve[i][1]-crossCoeff[i][1])/(crossCoeff[i][0]-crossCoeffReve[i][0])
    #    berCrossFit[i] = 10**(crossCoeff[i][0]*crossValFit[i]+crossCoeff[i][1])

    ##Plot accumulated pam4 histogram
    #plt.figure(figsize=[6,5])
    #plt.title('<Historam>',**titleFont)
    #plt.plot(adcCode-len(adcCode)/2,pamHist,'b-')
    #plt.xlabel('ADC code [7-bit]',**labelFont)
    #plt.ylabel('Count',**labelFont)
    ##plt.yticks(10**(np.arange(0.0,-31.0,step=-2.0)))
    ##plt.ylim([10**-14,10])
    #plt.minorticks_on()
    ##plt.tick_params(axis='x',which='both',direction='out',length=4,pad=8)
    #plt.tick_params(axis='both', which='major', labelsize=14)
    #f = mticker.ScalarFormatter(useOffset=True, useMathText=True)
    #g = lambda x,pos : "${}$".format(f._formatSciNotation('%1.10e' % x))
    #plt.gca().yaxis.set_major_formatter(mticker.FuncFormatter(g))
    ##plt.grid(color='gray',dashes=(4,2))
    #plt.grid()
    #plt.savefig('pam4_histogram_14p4.png',dpi=200)

    #%% linear extrapolation
    plt.figure(figsize=[7,6])
    xAxisExtrap      = []
    xAxisExtrapReve  = []
    for i in range(2**mu-1):
        if(ignLast==1):
            xAxisExtrap.append(np.hstack((validCodePam[i][-numExtrap-1:],crossVal[i]))-cOffset)
            xAxisExtrapReve.append(np.hstack((crossVal[i],validCodePamReve[i+1][:numExtrap+1]))-cOffset)
        else:
            xAxisExtrap.append(np.hstack((validCodePam[i][-numExtrap:],crossVal[i]))-cOffset)
            xAxisExtrapReve.append(np.hstack((crossVal[i],validCodePamReve[i+1][:numExtrap]))-cOffset)
    #plt.subplot(2,1,2)

    plt.title('Estimated BER from Histogram',**titleFont)
    plt.semilogy(np.array(limitCodePam[0])-cOffset,limitBerPam[0],'ro-')
    plt.semilogy(np.array(limitCodePamReve[1])-cOffset,limitBerPamReve[1],'ro-')
    plt.semilogy(np.array(limitCodePam[1])-cOffset,limitBerPam[1],'go-')
    plt.semilogy(np.array(limitCodePamReve[2])-cOffset,limitBerPamReve[2],'go-')
    plt.semilogy(np.array(limitCodePam[2])-cOffset,limitBerPam[2],'bo-')
    plt.semilogy(np.array(limitCodePamReve[3])-cOffset,limitBerPamReve[3],'bo-')
    #print(xAxisExtrap[0])
    #print(np.hstack((10**extraPam[0][:(numExtrap+ignLast+1)],berCross[0])))
    if(ignLast==1):
        plt.semilogy(xAxisExtrap[0],    np.hstack((10**extraPam[0][:(numExtrap+ignLast)],berCross[0])),'r--')
        plt.semilogy(xAxisExtrapReve[0],np.hstack((berCross[0],10**extraPamReve[1][-(numExtrap+ignLast):])),'r--')
        plt.semilogy(xAxisExtrap[1],    np.hstack((10**extraPam[1][:(numExtrap+ignLast)],berCross[1])),'g--')
        plt.semilogy(xAxisExtrapReve[1],np.hstack((berCross[1],10**extraPamReve[2][-(numExtrap+ignLast):])),'g--')
        plt.semilogy(xAxisExtrap[2],    np.hstack((10**extraPam[2][:(numExtrap+ignLast)],berCross[2])),'b--')
        plt.semilogy(xAxisExtrapReve[2],np.hstack((berCross[2],10**extraPamReve[3][-(numExtrap+ignLast):])),'b--')
    else:
        plt.semilogy(xAxisExtrap[0],    np.hstack((10**extraPam[0][:(numExtrap+ignLast)],berCross[0])),'r--')
        plt.semilogy(xAxisExtrapReve[0],np.hstack((berCross[0],10**extraPamReve[1][-(numExtrap+ignLast):])),'r--')
        plt.semilogy(xAxisExtrap[1],    np.hstack((10**extraPam[1][:(numExtrap+ignLast)],berCross[1])),'g--')
        plt.semilogy(xAxisExtrapReve[1],np.hstack((berCross[1],10**extraPamReve[2][-(numExtrap+ignLast):])),'g--')
        plt.semilogy(xAxisExtrap[2],    np.hstack((10**extraPam[2][:(numExtrap+ignLast)],berCross[2])),'b--')
        plt.semilogy(xAxisExtrapReve[2],np.hstack((berCross[2],10**extraPamReve[3][-(numExtrap+ignLast):])),'b--')
    #plt.semilogy(xAxisExtrapReve[0][0],berCross[0],'ko')
    #plt.semilogy(xAxisExtrapReve[1][0],berCross[1],'ko')
    #plt.semilogy(xAxisExtrapReve[2][0],berCross[2],'ko')
    plt.text(xAxisExtrapReve[0][0]+1,berCross[0],'%.2g'%berCross[0],**textFont,color='r',fontsize=14,)
    plt.text(xAxisExtrapReve[1][0]+1,berCross[1],'%.2g'%berCross[1],**textFont,color='g',fontsize=14,)
    plt.text(xAxisExtrapReve[2][0]+1,berCross[2],'%.2g'%berCross[2],**textFont,color='b',fontsize=14,)
    plt.yticks(10**(np.arange(0.0,-31.0,step=-2.0)))
    plt.ylim([10**-15,1.5])
    plt.xlim([-40,40])
    plt.minorticks_on()
    plt.tick_params(axis='both', which='major', labelsize=14)
    plt.tick_params(axis='x',which='both',direction='out',length=4,pad=8)
    #plt.grid(color='gray',dashes=(4,2))
    plt.grid()
    plt.xlabel('ADC code [7-bit]',**labelFont)
    plt.ylabel('BER',**labelFont)
    plt.savefig(filename.replace('.txt','_bathtub_pam4.png'),dpi=200)
    plt.close()

    avgBer = np.mean(berCross)
    return avgBer

#    plt.figure(figsize=[8,6])
#    plt.title('<Estimated BER>',**titleFont)
#    plt.semilogy(adcCode-cOffset,np.zeros(len(adcCode))) # plot full range
#    plt.semilogy(np.array(limitCodePam[0])-cOffset,limitBerPam[0],'ro-')
#    plt.semilogy(np.array(limitCodePamReve[1])-cOffset,limitBerPamReve[1],'ro-')
#    plt.semilogy(np.array(limitCodePam[1])-cOffset,limitBerPam[1],'go-')
#    plt.semilogy(np.array(limitCodePamReve[2])-cOffset,limitBerPamReve[2],'go-')
#    plt.semilogy(np.array(limitCodePam[2])-cOffset,limitBerPam[2],'bo-')
#    plt.semilogy(np.array(limitCodePamReve[3])-cOffset,limitBerPamReve[3],'bo-')
#    plt.semilogy(adcCode-cOffset,errPamFit[0],'r*--')
#    plt.semilogy(adcCode-cOffset,errPamFit[1],'g*--')
#    plt.semilogy(adcCode-cOffset,errPamFit[2],'b*--')
#    plt.semilogy(adcCode-cOffset,errPamFitReve[1],'r*--')
#    plt.semilogy(adcCode-cOffset,errPamFitReve[2],'g*--')
#    plt.semilogy(adcCode-cOffset,errPamFitReve[3],'b*--')
#
#    plt.plot(crossValFit[0]-cOffset,berCrossFit[0],'ko')
#    plt.plot(crossValFit[1]-cOffset,berCrossFit[1],'ko')
#    plt.plot(crossValFit[2]-cOffset,berCrossFit[2],'ko')
#    plt.text(crossValFit[0]-cOffset+1,berCrossFit[0],'%.2g'%berCrossFit[0],**textFont,color='r',fontsize=14)
#    plt.text(crossValFit[1]-cOffset+1,berCrossFit[1],'%.2g'%berCrossFit[1],**textFont,color='g',fontsize=14)
#    plt.text(crossValFit[2]-cOffset+1,berCrossFit[2],'%.2g'%berCrossFit[2],**textFont,color='b',fontsize=14)
#    plt.yticks(10**(np.arange(0.0,-31.0,step=-2.0)))
#    plt.ylim([10**-15,1.5])
#    plt.xlim([-40,40])
#    plt.minorticks_on()
#    plt.tick_params(axis='both', which='major', labelsize=14)
#    plt.tick_params(axis='x',which='both',direction='out',length=4,pad=8)
#    #plt.grid(color='gray',dashes=(4,2))
#    plt.grid()
#    plt.xlabel('ADC code [7-bit]',**labelFont)
#    plt.ylabel('BER',**labelFont)
#    plt.savefig(filename.replace('.txt','_bathtub.png'),dpi=200)
#    plt.close()



def accHisto_clip(arg):
    fileName=arg[1].split('.txt')[0]+'.txt'
    numIter=arg[1].split('_')[-1]

    if(numIter=='0'):
        inFile      = open(fileName)
        lines    = inFile.readlines()    
        adcCode     = np.array(list([float(x.strip().split()[0]) for x in lines]))
        nrzHist     = np.array(list([float(x.strip().split()[1]) for x in lines]))
       
        ##Check and Compensate clipping
        cntMax = (2**16)-1
        accMax = 2**19
       
        numClip  = accMax-np.sum(nrzHist)
       
        clipIdx  = []
        for i in range(len(adcCode)):
            if(nrzHist[i] == cntMax):
                clipIdx.append(i)

        if not (len(clipIdx)==0):
            fillCnt = numClip//len(clipIdx)
            resCnt  = numClip - fillCnt*len(clipIdx)
            for i,idx in enumerate(clipIdx):
                if(i == len(clipIdx)//2):
                    nrzHist[idx] += fillCnt + resCnt
                else:
                    nrzHist[idx] += fillCnt
        outFile = open('histo_data_acc.txt', 'w')
        for i in range(len(adcCode)):
            outFile.write('%d %d\n'%(adcCode[i],nrzHist[i]))
        outFile.close()

    else:
        accFile     = open('histo_data_acc.txt')
        accLines    = accFile.readlines()
        adcCode     = np.array(list([float(x.strip().split()[0]) for x in accLines]))
        accHist     = np.array(list([float(x.strip().split()[1]) for x in accLines]))
       
        inFile  = open(fileName)
        lines   = inFile.readlines()
        nrzHist = np.array(list([float(x.strip().split()[1]) for x in lines]))
       
        ##Check and Compensate clipping
        cntMax = (2**16)-1
        accMax = 2**19
        numClip  = accMax-np.sum(nrzHist)
        clipIdx  = []
        for i in range(len(adcCode)):
            if(nrzHist[i] == cntMax):
                clipIdx.append(i)
        if not (len(clipIdx)==0):
            fillCnt = numClip//len(clipIdx)
            resCnt  = numClip - fillCnt*len(clipIdx)
            for i,idx in enumerate(clipIdx):
                if(i == len(clipIdx)//2):
                    nrzHist[idx] += fillCnt + resCnt
                else:
                    nrzHist[idx] += fillCnt
     
        accHist += nrzHist
        outFile = open('histo_data_acc.txt', 'w')
        for i in range(len(adcCode)):
            outFile.write('%d %d\n'%(adcCode[i],accHist[i]))
        outFile.close()


