from evb_types import *
from evb_utils import *
import sys,glob
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams

# plot_256.py
def plot_256(filename):
    axisFont = {'family' : 'serif', 'weight' : 'bold','size'   : 12}
    textFont = {'family' : 'serif', 'weight' : 'bold','size'   : 11}
    labelFont = {'family' : 'sans-serif','weight' : 'bold','size'   : 15}
    titleFont = {'family' : 'sans-serif','weight' : 'bold','size'   : 20}
    plt.rc('font', **axisFont)
    inFile=open(filename)  
    inData=inFile.readlines()
    data=[int(x.strip().split()[1]) for x in inData[:256]]
    inFile.close()
    for i in range(256):
        if(data[i]>127):  
            data[i] -= 256;
    plt.plot(data,'b-o',linewidth=2)
    plt.grid()
    plt.title("256 Data dump",**titleFont)
    #plt.ylabel("Eq out",**labelFont)
    #plt.xlim([0,32])
    plt.ylim([-128,128])
    #plt.legend(loc='upper right',ncol=2,bbox_to_anchor=(1.1,1),prop={'size':8})
    plt.savefig(filename.replace('.txt','.png'),dpi=200)
    plt.close()

# plot_ber_eom.py (Verified)
def plot_ber_eom(filename):
    axisFont = {'family' : 'serif', 'weight' : 'bold','size'   : 10}
    textFont = {'family' : 'serif', 'weight' : 'bold','size'   : 11}
    labelFont = {'family' : 'sans-serif','weight' : 'bold','size'   : 12}
    titleFont = {'family' : 'sans-serif','weight' : 'bold','size'   : 15}
    plt.rc('font', **axisFont)

    totalCntNum=2**22
    inFile=open(filename)  
    inData=inFile.readlines()[:]
    phases=set([int(x.strip().split()[0]) for x in inData])
    vrefs=set([int(x.strip().split()[1]) for x in inData])
    phases=sorted(list(phases))
    vrefs=sorted(list(vrefs))
    stepPi=phases[1]-phases[0]
    stepLev=vrefs[1]-vrefs[0]
    totalPi=128
    totalLev=stepLev*(len(vrefs))
    numPi=int(totalPi/stepPi)
    numLev=int(totalLev/stepLev)
    image = np.zeros((numPi,numLev)).astype(np.float)
    #print (stepPi,stepLev,totalLev,numPi*numLev)
    for i in range(numPi*numLev):
        if(i<len(inData)):
            image[int(i/numLev)][numLev-1-i%numLev]=(float(inData[i].split()[2].strip())/totalCntNum)
        if(image[int(i/numLev)][numLev-1-i%numLev]==0.0):
            image[int(i/numLev)][numLev-1-i%numLev]=np.nan;
        else:
            image[int(i/numLev)][numLev-1-i%numLev]=np.log10(image[int(i/numLev)][numLev-1-i%numLev])
    inFile.close()
    plt.imshow(np.array(image.T),extent=[-0.5,0.5,-int(totalLev/2),int(totalLev/2)],aspect='equal',cmap=plt.get_cmap('jet'),interpolation='nearest',alpha=1.0)
#plt.imshow(np.array(image.T),extent=[1,numPi,1,numLev],aspect='equal',cmap=plt.get_cmap('jet'),interpolation='nearest',alpha=1.0)
    plt.axis('auto')
    plt.grid()
#plt.ylim([-128,128])
    plt.ylim([-50*2,50*2])
    plt.title("EOM result",**titleFont)
#plt.ylabel("Offset code",**labelFont)
    plt.xlabel("Phase [UI]",**labelFont)
    plt.colorbar()
    plt.savefig(filename.replace('ber_data','ber').replace('.txt','.png'),dpi=200)
    plt.close()

def plot_ber_eom_10g(filename):
    axisFont = {'family' : 'serif', 'weight' : 'bold','size'   : 10}
    textFont = {'family' : 'serif', 'weight' : 'bold','size'   : 11}
    labelFont = {'family' : 'sans-serif','weight' : 'bold','size'   : 12}
    titleFont = {'family' : 'sans-serif','weight' : 'bold','size'   : 15}
    plt.rc('font', **axisFont)
    totalCntNum=2**22
    inFile=open(filename)  
    inData=inFile.readlines()[:]
    phases=set([int(x.strip().split()[0]) for x in inData])
    vrefs=set([int(x.strip().split()[1]) for x in inData])
    phases=sorted(list(phases))
    vrefs=sorted(list(vrefs))
    stepPi=phases[1]-phases[0]
    stepLev=vrefs[1]-vrefs[0]
    totalPi=256
    totalLev=stepLev*(len(vrefs))
    numPi=int(totalPi/stepPi)
    numLev=int(totalLev/stepLev)
    image = np.zeros((numPi,numLev)).astype(np.float)
    for i in range(numPi*numLev):
        if(i<len(inData)):
            image[int(i/numLev)][numLev-1-i%numLev]=(float(inData[i].split()[2].strip())/totalCntNum)
        if(image[int(i/numLev)][numLev-1-i%numLev]==0.0):
            image[int(i/numLev)][numLev-1-i%numLev]=np.nan;
        else:
            image[int(i/numLev)][numLev-1-i%numLev]=np.log10(image[int(i/numLev)][numLev-1-i%numLev])
    inFile.close()
    plt.imshow(np.array(image.T),extent=[-0.5,0.5,-int(totalLev/2),int(totalLev/2)],aspect='equal',cmap=plt.get_cmap('jet'),interpolation='nearest',alpha=1.0)
#plt.imshow(np.array(image.T),extent=[1,numPi,1,numLev],aspect='equal',cmap=plt.get_cmap('jet'),interpolation='nearest',alpha=1.0)
    plt.axis('auto')
    plt.grid()
#plt.ylim([-100,100])
    plt.title("EOM result",**titleFont)
#plt.ylabel("Offset code",**labelFont)
    plt.xlabel("Phase [UI]",**labelFont)
    plt.colorbar()
    plt.savefig(filename.replace('ber_data','ber').replace('.txt','.png'),dpi=200)
    plt.close()

def plot_ber_eom_pam4(filename):
    axisFont = {'family' : 'serif', 'weight' : 'bold','size'   : 10}
    textFont = {'family' : 'serif', 'weight' : 'bold','size'   : 11}
    labelFont = {'family' : 'sans-serif','weight' : 'bold','size'   : 12}
    titleFont = {'family' : 'sans-serif','weight' : 'bold','size'   : 15}
    plt.rc('font', **axisFont)
    fileList=[filename.replace('_12.txt','_01.txt'),filename,filename.replace('_12.txt','_23.txt')]
    vrefFile=filename.replace('_12.txt','_vref.txt')

    totalCntNum=2**22
    vref=int(open(vrefFile).readline().strip())
    inFile=open(fileList[1])
    inData=inFile.readlines()
    phases=set([int(x.strip().split()[0]) for x in inData])
    vrefs=set([int(x.strip().split()[1]) for x in inData])
    inFile.close()
    phases=sorted(list(phases))
    vrefs=sorted(list(vrefs))
    stepPi=phases[1]-phases[0]
    stepLev=vrefs[1]-vrefs[0]
    totalPi=128
    totalLev=stepLev*(len(vrefs))
    numPi=int(totalPi/stepPi)
    numLev=int(totalLev/stepLev)
    image= np.zeros((3,numPi,numLev)).astype(np.float)
    fullImage= np.ones((numPi,int(256/stepLev))).astype(np.float)*0.5
    for file_i,filename in enumerate(fileList):
        inFile=open(filename)  
        inData=inFile.readlines()
        for i in range(len(inData)):
            image[file_i][int(i/numLev)][numLev-1-i%numLev]=(float(inData[i].split()[2].strip())/totalCntNum)
        inFile.close()
    for raw_i,raw in enumerate(image[1]):
        for col_i,col in enumerate(raw):
            if(fullImage[raw_i][int((128-totalLev/2)/stepLev)+col_i]>image[1][raw_i][col_i]):
                fullImage[raw_i][int((128-totalLev/2)/stepLev)+col_i] = image[1][raw_i][col_i]
    for raw_i,raw in enumerate(image[0]):
        for col_i,col in enumerate(raw):
            if(fullImage[raw_i][int((128+vref-totalLev/2)/stepLev)+col_i]>image[0][raw_i][col_i]):
                fullImage[raw_i][int((128+vref-totalLev/2)/stepLev)+col_i] = image[0][raw_i][col_i]

    for raw_i,raw in enumerate(image[2]):
        for col_i,col in enumerate(raw):
            if(fullImage[raw_i][int((128-vref-totalLev/2)/stepLev)+col_i]>image[2][raw_i][col_i]):
                fullImage[raw_i][int((128-vref-totalLev/2)/stepLev)+col_i] = image[2][raw_i][col_i]

    for raw_i,raw in enumerate(fullImage):
        for col_i,col in enumerate(raw):
            if(fullImage[raw_i][col_i]==0):
                fullImage[raw_i][col_i]=np.nan;
            else:
                fullImage[raw_i][col_i]=np.log10(fullImage[raw_i][col_i])
    plt.imshow(np.array(fullImage.T),extent=[-0.5,0.5,-128,128],aspect='equal',cmap=plt.get_cmap('jet'),interpolation='nearest',alpha=1.0)
    plt.axis('auto')
    plt.grid()
    plt.title("EOM result",**titleFont)
    plt.ylim([-64,64])
    plt.ylabel("Offset code",**labelFont)
    plt.xlabel("Phase [UI]",**labelFont)
    plt.colorbar()
    plt.savefig(fileList[1].replace('ber_data_','ber_').replace('_12.txt','.png'),dpi=200)
    plt.close()

def plot_ch_histo(filename):
    axisFont = {'family' : 'serif', 'weight' : 'bold','size'   : 12}
    textFont = {'family' : 'serif', 'weight' : 'bold','size'   : 11}
    labelFont = {'family' : 'sans-serif','weight' : 'bold','size'   : 15}
    titleFont = {'family' : 'sans-serif','weight' : 'bold','size'   : 20}
    plt.rc('font', **axisFont)
    inFile=open(filename)  
    inData=inFile.readlines()
    phases=set([int(x.strip().split()[0]) for x in inData])
    vrefs=set([int(x.strip().split()[1]) for x in inData])
    phases=sorted(list(phases))
    vrefs=sorted(list(vrefs))
    stepPi=phases[1]-phases[0]
    stepLev=vrefs[1]-vrefs[0]
    totalPi=32
    totalLev=stepLev*(len(vrefs))
    numPi=int(totalPi/stepPi)
    numLev=int(totalLev/stepLev)
    image = np.zeros((numPi,numLev)).astype(np.float)
    for row_i,row in enumerate(image):
        for col_i,col in enumerate(row):
            image[row_i][col_i]=np.nan;
    for i in range(len(inData)):
        image[int(i/numLev)][numLev-1-i%numLev]=inData[i].split()[2].strip()
        if(image[int(i/numLev)][numLev-1-i%numLev]==0):
            image[int(i/numLev)][numLev-1-i%numLev]=np.nan;
    inFile.close()
    plt.imshow(np.array(image.T),extent=[0,32,-int(totalLev/2),int(totalLev/2)],aspect='equal',cmap=plt.get_cmap('jet'),interpolation='nearest',alpha=1.0)
#plt.imshow(np.array(image.T),extent=[1,numPi,1,numLev],aspect='equal',cmap=plt.get_cmap('jet'),interpolation='nearest',alpha=1.0)
    plt.axis('auto')
    plt.grid()
#plt.title("Error count",**titleFont)
#plt.ylabel("ADC code",**labelFont)
    plt.xlabel("Ch. #",**labelFont)
    plt.colorbar()
    plt.savefig(filename.replace('ch_histo_data_','ch_histo_').replace('.txt','.png'),dpi=100)
    plt.close()

def plot_coeff(filename):
    axisFont = {'family' : 'serif', 'weight' : 'bold','size'   : 12}
    textFont = {'family' : 'serif', 'weight' : 'bold','size'   : 11}
    labelFont = {'family' : 'sans-serif','weight' : 'bold','size'   : 15}
    titleFont = {'family' : 'sans-serif','weight' : 'bold','size'   : 20}
    plt.rc('font', **axisFont)
    inFile=open(filename)
    inData=inFile.readlines()
    ber=[float(x.strip().split()[12]) for x in inData]
    rmList=[]
    for i in range(len(ber)):
        if(ber[i]>0.1):
            rmList.append(i)
    for i in range(len(rmList)):
        del(inData[rmList[-i-1]])
    cdr=[int(x.strip().split()[0]) for x in inData]
    cm2=[int(x.strip().split()[1]) for x in inData]
    cm1=[int(x.strip().split()[2]) for x in inData]
    c0=[int(x.strip().split()[3])*4 for x in inData]
    c1=[int(x.strip().split()[4]) for x in inData]
    c2=[int(x.strip().split()[5]) for x in inData]
    c3=[int(x.strip().split()[6]) for x in inData]
    c4=[int(x.strip().split()[7]) for x in inData]
    c5=[int(x.strip().split()[8]) for x in inData]
    c6=[int(x.strip().split()[9]) for x in inData]
    c7=[int(x.strip().split()[10]) for x in inData]
    c8=[int(x.strip().split()[11]) for x in inData]
    for i,d in enumerate(cdr):
        if(i!=0):
            if(d<cdr[i-1]-2):
                cdr[i]=d+128
    for i,d in enumerate(ber):
        if(d==0):
            ber[i]=1e-11;
    inFile.close()
#cdr=c1
    plt.plot(cdr,cm2,linewidth=2,label='C[-2]')
    plt.plot(cdr,cm1,linewidth=2,label='C[-1]')
    plt.plot(cdr,c0,linewidth=3,label='C[ 0]')
    plt.plot(cdr,c1,linewidth=2,label='C[ 1]')
    plt.plot(cdr,c2,linewidth=2,label='C[ 2]')

    plt.grid()
    plt.title("Coefficient",**titleFont)
    plt.ylabel("Coeff. Code",**labelFont)
    plt.xlabel("CDR Code",**labelFont)
#plt.xlim([0,32])
#plt.ylim([-128,128])
    plt.legend(loc='upper right',prop={'size':8})
#plt.legend(loc='upper right',ncol=2,bbox_to_anchor=(1.1,1),prop={'size':8})
    plt.savefig(filename.replace('.txt','.png'),dpi=200)
    plt.close()

def plot_eom(filename):
    axisFont = {'family' : 'serif', 'weight' : 'bold','size'   : 12}
    textFont = {'family' : 'serif', 'weight' : 'bold','size'   : 11}
    labelFont = {'family' : 'sans-serif','weight' : 'bold','size'   : 15}
    titleFont = {'family' : 'sans-serif','weight' : 'bold','size'   : 20}
    plt.rc('font', **axisFont)
    inFile=open(filename)  
    inData=inFile.readlines()
    phases=set([int(x.strip().split()[0]) for x in inData])
    vrefs=set([int(x.strip().split()[1]) for x in inData])
    phases=sorted(list(phases))
    vrefs=sorted(list(vrefs))
    stepPi=phases[1]-phases[0]
    stepLev=vrefs[1]-vrefs[0]
    totalPi=128
    totalLev=stepLev*(len(vrefs))
    numPi=int(totalPi/stepPi)
    numLev=int(totalLev/stepLev)
    image = np.zeros((numPi,numLev)).astype(np.float)
    for row_i,row in enumerate(image):
        for col_i,col in enumerate(row):
            image[row_i][col_i]=np.nan;
    for i in range(len(inData)):
        image[int(i/numLev)][numLev-1-i%numLev]=inData[i].split()[2].strip()
        if(image[int(i/numLev)][numLev-1-i%numLev]==0):
            image[int(i/numLev)][numLev-1-i%numLev]=np.nan;
    inFile.close()
    plt.imshow(np.array(image.T),extent=[-0.5,0.5,-int(totalLev/2),int(totalLev/2)],aspect='equal',cmap=plt.get_cmap('jet'),interpolation='nearest',alpha=1.0)
#plt.imshow(np.array(image.T),extent=[1,numPi,1,numLev],aspect='equal',cmap=plt.get_cmap('jet'),interpolation='nearest',alpha=1.0)
    plt.axis('auto')
    plt.grid()
    plt.ylim([-64,64])
#plt.ylim([-32,32])
#plt.title("Error count",**titleFont)
#plt.ylabel("ADC code",**labelFont)
    plt.xlabel("Phase [UI]",**labelFont)
    plt.colorbar()
    plt.savefig(filename.replace('eom_data_','eom_').replace('.txt','.png'),dpi=100)
    plt.close()

def plot_eom_10g(filename):
    axisFont = {'family' : 'serif', 'weight' : 'bold','size'   : 12}
    textFont = {'family' : 'serif', 'weight' : 'bold','size'   : 11}
    labelFont = {'family' : 'sans-serif','weight' : 'bold','size'   : 15}
    titleFont = {'family' : 'sans-serif','weight' : 'bold','size'   : 20}
    plt.rc('font', **axisFont)
    inFile=open(filename)  
    inData=inFile.readlines()
    phases=set([int(x.strip().split()[0]) for x in inData])
    vrefs=set([int(x.strip().split()[1]) for x in inData])
    phases=sorted(list(phases))
    vrefs=sorted(list(vrefs))
    stepPi=phases[1]-phases[0]
    stepLev=vrefs[1]-vrefs[0]
    totalPi=256
    totalLev=stepLev*(len(vrefs))
    numPi=int(totalPi/stepPi)
    numLev=int(totalLev/stepLev)
    image = np.zeros((numPi,numLev)).astype(np.float)
    for row_i,row in enumerate(image):
        for col_i,col in enumerate(row):
            image[row_i][col_i]=np.nan;
    for i in range(len(inData)):
        image[int(i/numLev)][numLev-1-i%numLev]=inData[i].split()[2].strip()
        if(image[int(i/numLev)][numLev-1-i%numLev]==0):
            image[int(i/numLev)][numLev-1-i%numLev]=np.nan;
    inFile.close()
    plt.imshow(np.array(image.T),extent=[-0.5,0.5,-int(totalLev/2),int(totalLev/2)],aspect='equal',cmap=plt.get_cmap('jet'),interpolation='nearest',alpha=1.0)
#plt.imshow(np.array(image.T),extent=[1,numPi,1,numLev],aspect='equal',cmap=plt.get_cmap('jet'),interpolation='nearest',alpha=1.0)
    plt.axis('auto')
    plt.grid()
#plt.title("Error count",**titleFont)
#plt.ylabel("ADC code",**labelFont)
    plt.xlabel("Phase [UI]",**labelFont)
    plt.colorbar()
    plt.savefig(filename.replace('eom_data_','eom_').replace('.txt','.png'),dpi=100)
    plt.close()

def PlotHisto(filename):
    #print (sys.argv[1])
    axisFont = {'family' : 'serif', 'weight' : 'bold','size'   : 12}
    textFont = {'family' : 'serif', 'weight' : 'bold','size'   : 11}
    labelFont = {'family' : 'sans-serif','weight' : 'bold','size'   : 15}
    titleFont = {'family' : 'sans-serif','weight' : 'bold','size'   : 20}
    plt.rc('font', **axisFont)
    inFile=open(filename)  
    inData=inFile.readlines()
    histData=[x.split()[1].strip() for x in inData[:-1]]
    inFile.close()
    histData=np.array(histData).astype(np.int)
    plt.plot(np.array(range(len(histData)))-int(len(histData)/2),histData,'b',label='raw')
    plt.grid()
##plt.xlim([0,96*2])
    plt.title('Vertical histogram',**titleFont)
    plt.xlabel('ADC value',**labelFont)
#plt.ylabel('',**labelFont)
#plt.legend(loc='upper right',fontsize=11)
    plt.savefig(filename.replace('.txt','.png'),dpi=200)
    plt.close()

def plot_histo_ber(filename):
    rcParams.update({'figure.autolayout': True})
    axisFont = {'family' : 'serif', 'weight' : 'bold','size'   : 12}
    textFont = {'family' : 'serif', 'weight' : 'bold','size'   : 10}
    labelFont = {'family' : 'sans-serif','weight' : 'bold','size'   : 15}
    titleFont = {'family' : 'sans-serif','weight' : 'bold','size'   : 20}
    plt.rc('font', **axisFont)
    inFile=open(filename)  
    inData=inFile.readlines()
    histData=[x.strip() for x in inData[:-1]]
    inFile.close()
    histData=np.log10(np.array(histData).astype(np.float64))
    med=np.power(10,np.median(histData))
    min=np.power(10,np.min(histData))
    max=np.power(10,np.max(histData))
    n,b=np.histogram(histData, bins=100,range=(-10,-1))
    plt.plot(b[:-1],n,'b')
    plt.grid()
    plt.text(-9.5,35,"BER min. = %.3g\nBER med. = %.3g\nBER max. = %.3g"%(min,med,max),**textFont)
    plt.xlim([-10,-1])
    plt.ylim([0,40])
    plt.title('BER distribution',**titleFont)
    plt.xlabel('log(BER)',**labelFont)
#plt.ylabel('',**labelFont)
#plt.legend(loc='upper right',fontsize=11)
    plt.savefig(filename.replace('.txt','.png'),dpi=200)
    plt.close()

def plot_temp(fileList=None):
    rcParams.update({'figure.autolayout': True})
    axisFont = {'family' : 'serif', 'weight' : 'bold','size'   : 12}
    textFont = {'family' : 'serif', 'weight' : 'bold','size'   : 10}
    labelFont = {'family' : 'sans-serif','weight' : 'bold','size'   : 15}
    titleFont = {'family' : 'sans-serif','weight' : 'bold','size'   : 20}
    plt.rc('font', **axisFont)
    if fileList is None:
        fileList = glob.glob(os.environ['SF56G_EVB_PATH']+'/../*.txt')
        print(fileList)

    for filename in fileList:
        inFile=open(filename)  
        inData=inFile.readlines()
        histData=[x.strip() for x in inData[:-1]]
        inFile.close()
        histData=np.log10(np.array(histData).astype(np.float64))
        med=np.power(10,np.median(histData))
        n,b=np.histogram(histData, bins=100,range=(-10,-3))
        plt.plot(b[:-1],n,'b')
        plt.grid()
        plt.text(-9.5,35,"BER median = %.3g"%(med),**textFont)
        plt.xlim([-10,-2])
        plt.ylim([0,40])
        plt.title('BER distribution',**titleFont)
        plt.xlabel('log(BER)',**labelFont)
        #plt.ylabel('',**labelFont)
        #plt.legend(loc='upper right',fontsize=11)
        plt.savefig(filename.replace('.txt','.png'),dpi=200)
        plt.close()

def plot_vco(filename):
    axisFont = {'family' : 'serif', 'weight' : 'bold','size'   : 12}
    textFont = {'family' : 'serif', 'weight' : 'bold','size'   : 11}
    labelFont = {'family' : 'sans-serif','weight' : 'bold','size'   : 15}
    titleFont = {'family' : 'sans-serif','weight' : 'bold','size'   : 20}
    plt.rc('font', **axisFont)
    inFile=open(filename)  
    inData=inFile.readlines()
    afcs=[int(x.strip().split()[0]) for x in inData]
    vcis=[int(x.strip().split()[1]) for x in inData]
    cnt=[float(x.strip().split()[2]) for x in inData]
    inFile.close()
    vciNum=0
    for afc in afcs:
        if(afc==afcs[0]):
            vciNum += 1
    freq = np.zeros((int(len(cnt)/vciNum),vciNum))

    afcSet=afcs[::vciNum]
    for afc_i in range(int(len(afcs)/vciNum)):
        for vci_i in range(vciNum):
            freq[afc_i][vci_i] = cnt[afc_i*vciNum + vci_i]
        plt.plot(vcis[:vciNum],freq[afc_i],linewidth=2,label='@ %d'%afcSet[afc_i])

    plt.grid()
#plt.title("Error count",**titleFont)
    plt.ylabel("Frequency [GHz]",**labelFont)
    plt.xlabel("Vci sel",**labelFont)
    plt.xlim([0,9])
    plt.ylim([6,16])
    plt.legend(loc='upper right',ncol=2,bbox_to_anchor=(1.1,1),prop={'size':8})
    plt.savefig(filename.replace('.txt','.png'),dpi=200)
    plt.close()



def plot_favorite():
    axisFont = {'family' : 'serif', 'weight' : 'bold','size'   : 11}
    textFont = {'family' : 'serif', 'weight' : 'bold','size'   : 9}
    labelFont = {'family' : 'sans-serif','weight' : 'bold','size'   : 13}
    titleFont = {'family' : 'sans-serif','weight' : 'bold','size'   : 16}
    rcParams.update({'figure.autolayout': True})
    plt.rc('font', **axisFont)
    return textFont,labelFont,titleFont

def PlotBerHorizontal_Bathtub(data_pack,plot_raw_en=False,pi_period=128,plt_name='hbath.png'):
    fonts = plot_favorite()
    half_period = int(pi_period/2)
    pi_code = np.array(range(-half_period, half_period, 1))
    plt.figure(figsize=[6,5])
    idx = 0
    for key,data in data_pack.items():
        # raw,fit
        if plot_raw_en:
            plt.semilogy(pi_code/128,data['left_ber'],'bo')
            plt.semilogy(pi_code/128,data['rght_ber'],'bo')
        plt.semilogy(pi_code/128,data['left_fit'],'b',linewidth=2)
        plt.semilogy(pi_code/128,data['rght_fit'],'b',linewidth=2)
        # crss
        plt.text(0,10**-(20+4*idx),'<EYE%s>\nBER@L = %.2e\nBER@H = %.2e\nBER@X = %.2e'%(key,data['left_y'],data['rght_y'],data['crss_y']),color='k',fontsize=10)
        idx+=1
    # config
    plt.grid()
    plt.xlim([-0.5,0.5])
    plt.ylim([1e-30,1])
    plt.yticks(10**(np.arange(0.0,-31.0,step=-2.0)))
    plt.minorticks_on()
    plt.tick_params(axis='x',which='both',direction='out',length=4,pad=8)
    plt.title('Horizontal Bathtub BER',**fonts[2])
    plt.xlabel('Phase [UI]',**fonts[1])
    plt.ylabel('BER',**fonts[1])
    plt.savefig(plt_name,dpi=200)
    plt.close()
