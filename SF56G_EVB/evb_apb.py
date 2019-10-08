from evb_utils import *
add_evb_dll()
from LibEVB import EVBMain


class EVB_APB(object):
    def __init__(self):
        self.mCfg = None

    def connect(self,mCfg):
        self.mCfg = mCfg

    def GetEVBStatus(self):
        Delay(self.mCfg.apb_delay)
        return EVBMain.EVB_GetStatus()

    def GetApbResult(self):
        raddr0 = EVBMain.apb_raddr0
        raddr1 = EVBMain.apb_raddr1
        raddr2 = EVBMain.apb_raddr2
        raddr3 = EVBMain.apb_raddr3
        print ("raddr = 0x%x" % (raddr3<<24|raddr2<<16|raddr1<<8|raddr0))
        return EVBMain.apb_result
   
    def read(self,addr,channel=0):
        Delay(self.mCfg.apb_delay)
        raddr = addr+0x40000*channel
        rdata = EVBMain.EVB_ApbRead(raddr)
        if self.mCfg.b_dbg_apb_read:
            print ("[ApbRead] 0x%x => 0x%x" % (raddr,rdata))
        return rdata
    def poll(self,addr,data,channel=0,mask=0xffff,timeout=1000):
        cnt = 0
        find = False
        while cnt < timeout and not find:
            rdata = self.read(addr,channel)
            cnt += 1
            Delay(self.mCfg.apb_poll_delay)
            if rdata & mask == data:
                find = True
        if (cnt >= timeout):
            print("[apb] poll (0x%x-ln%d) timeout" % (addr,channel))


    def write(self,addr,data,channel=0,mask=None,track=False):
        waddr = addr+0x40000*channel
        if mask is not None:
            rdata = EVBMain.EVB_ApbRead(waddr)
            wdata = (rdata & (0xffff-mask)) | (data & mask)
        else:
            wdata = data
        if track:
            rdata = EVBMain.EVB_ApbRead(waddr)
            print ("[ApbWrite] 0x%x = 0x%x -> 0x%x" % (waddr,rdata,wdata))

        EVBMain.EVB_ApbWrite(waddr,wdata)

        if self.mCfg.b_dbg_apb_write:
            print ("[ApbWrite] 0x%x <= 0x%x" % (waddr,wdata))
        Delay(self.mCfg.apb_delay)
   
    def multi_write(self,addr,data,lane_strb=0x1,mask=None):
        for i in range(4):
            if (lane_strb >> i) & 1 == 1:
                self.write(addr,data,i,mask)

    def init_evb(self):
        EVBMain.EVB_Init()


