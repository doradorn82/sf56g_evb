from evb_utils import *
from evb_types import *
import ctypes
import marshal

class FT260_PyWrap(object):
    def __init__(self, dll_path='dll/LibFT260.dll'):
        self._mydll = ctypes.WinDLL(dll_path)
        self.FT260_CreateDeviceList = self._mydll['FT260_CreateDeviceList']
        self.FT260_GetDevicePath = self._mydll['FT260_GetDevicePath']
        self.FT260_Open = self._mydll['FT260_Open']
        self.FT260_Close = self._mydll['FT260_Close']
        self.FT260_I2CMaster_Init = self._mydll['FT260_I2CMaster_Init']
        self.FT260_I2CMaster_Read = self._mydll['FT260_I2CMaster_Read']
        self.FT260_I2CMaster_Write = self._mydll['FT260_I2CMaster_Write']
        self.FT260_I2CMaster_Reset = self._mydll['FT260_I2CMaster_Reset']
        self.FT260_SetClock = self._mydll['FT260_SetClock']
        # shared vars
        self.FT260_ID = "hid#vid_0403&pid_6030&mi_00"  # FT260의 VID = 0x0403 ,PID = 0x6030, MI = 0x00(I2C)  정보
        self.I2C_rx = marshal.dumps("aa")
        self.devNum = ctypes.c_uint32(0)
        self.mhandle = ctypes.c_uint32(0)
        # public vars
        self.i2c_result = ""
        self.apb_result = ""
        self.debug_print = 0
        self.apb_raddr0 = 0
        self.apb_raddr1 = 0
        self.apb_raddr2 = 0
        self.apb_raddr3 = 0
        self.verbosity = Verbosity.MED

    def FT260_Device_Search(self):
        pValue = self.get_bytes_array([0]*256)

        if self.FT260_CreateDeviceList(ctypes.byref(self.devNum)) != int(FT260_STATUS.FT260_OK):
            return -1

        for i in range(int(self.devNum.value)):
            self.FT260_GetDevicePath(ctypes.byref(pValue), 256, i)

            sbuf = ''
            for j,s in enumerate(pValue):
                sbuf += chr(s)
            sbuf = sbuf.replace('\x00', '')
            if self.FT260_ID in sbuf:
                return i
        return -2

    def FT260_initial(self, device_index=-1):
        i2c_speed = ctypes.c_int(1000)

        if device_index == -1:
            return -1
        if self.FT260_Open(device_index, ctypes.byref(self.mhandle)) != int(FT260_STATUS.FT260_OK):
            return -2
        if self.FT260_I2CMaster_Init(self.mhandle, i2c_speed) != int(FT260_STATUS.FT260_OK):
            return -3
        if self.FT260_I2CMaster_Reset(self.mhandle) != int(FT260_STATUS.FT260_OK):
            return -4
        self.FT260_SetClock(self.mhandle, 1)
        return 0

    # ----------------------------------------------------------------------------------------------------
    # Private function
    # ----------------------------------------------------------------------------------------------------
    def print_list(self, data_list,tag=''):
        l = '%s'%tag
        for data in data_list:
            l += (str(hex(data))+' ')
        print(l)

    def myprint(self, *args, verbosity=Verbosity.MED):
        if int(self.verbosity) >= int(verbosity):
            print(*args)

    def get_bytes_array(self, init_list):
        # return ((ctypes.c_byte * len(init_list))(*init_list))
        return ((ctypes.c_uint8 * len(init_list))(*init_list))

    def FT260_I2CWrite(self, device_id, addr, value):

        wlength = ctypes.c_int32(0)
        aa_l = [addr & 0xff, value & 0xff]
        aa = (ctypes.c_byte * len(aa_l))(*aa_l)
        di = ctypes.c_int32(device_id >> 1)

        ret = self.FT260_I2CMaster_Write(self.mhandle, di, 6, aa, 2, ctypes.byref(wlength))
        if ret != 0:
            self.myprint("[I2C Write] I2C Master Write Error (Error code=%d)" % (ret),verbosity=Verbosity.DEBUG)
            self.i2c_result = ("[I2C Write] I2C Master Write Error (Error code=%d)" % (ret))
            return -1
        else:
            self.myprint("[I2C Write] Success 0x%x <= 0x%x" % (addr, value),verbosity=Verbosity.DEBUG)
            self.i2c_result = ("[I2C Write] Success 0x%x <= 0x%x" % (addr, value))
            return ret

    def FT260_I2CReadS(self, device_id, addr):
        # type convert
        rlength = ctypes.c_int32(0)
        wlength = ctypes.c_int32(0)
        aa = self.get_bytes_array([0] * 8)
        bb = self.get_bytes_array([addr & 0xff] + [0] * 7)
        di = ctypes.c_int32(device_id >> 1)

        ret = self.FT260_I2CMaster_Write(self.mhandle, di, 2, bb, 1, ctypes.byref(wlength))
        if ret == 0:
            ret = self.FT260_I2CMaster_Read(self.mhandle, di, 6, aa, 1, ctypes.byref(rlength))
            if ret != 0:
                self.myprint("[I2C Read] I2C Master Read Error (Error code=%d)" % ret,verbosity=Verbosity.DEBUG)
                self.i2c_result = ("[I2C Read] I2C Master Read Error (Error code=%d)" % ret)
        else:
            self.myprint("[I2C Read] I2C Master Write Error (Error code=%d)" % ret,verbosity=Verbosity.DEBUG)
            self.i2c_result = ("[I2C Read] I2C Master Write Error (Error code=%d)" % ret)
        return aa[0]

    def FT260_I2CRead(self, device_id, addr, length):
        # type convert
        rlength = ctypes.c_int32(0)
        wlength = ctypes.c_int32(0)
        aa = self.get_bytes_array([0] * 8)
        bb = self.get_bytes_array([addr & 0xff] + [0] * 7)

        ret = self.FT260_I2CMaster_Write(self.mhandle, device_id>>1, 2, bb, 1, ctypes.byref(wlength))
        if ret == 0:
            ret = self.FT260_I2CMaster_Read(self.mhandle, device_id>>1, 6, aa, length, ctypes.byref(rlength))
            if ret != 0:
                self.myprint("[I2C Read] I2C Master Read Error (Error code=%d)" % ret,verbosity=Verbosity.DEBUG)
                self.i2c_result = ("[I2C Read] I2C Master Read Error (Error code=%d)" % ret)
        else:
            self.myprint("[I2C Read] I2C Master Write Error (Error code=%d)" % ret,verbosity=Verbosity.DEBUG)
            self.i2c_result = ("[I2C Read] I2C Master Write Error (Error code=%d)" % ret)
        return aa

    def DTBD_Init(self):
        if self.FT260_I2CWrite(0xE, 0x00, 0x80) != 0:
            return -1
        if self.FT260_I2CWrite(0xE, 0x01, 0x04) != 0:
            return -1
        if self.FT260_I2CWrite(0xE, 0x02, 0x00) != 0:
            return -1
        if self.FT260_I2CWrite(0xE, 0x03, 0x00) != 0:
            return -1
        if self.FT260_I2CWrite(0xE, 0x04, 0x00) != 0:
            return -1
        if self.FT260_I2CWrite(0xE, 0x05, 0x00) != 0:
            return -1
        if self.FT260_I2CWrite(0xE, 0x06, 0x00) != 0:
            return -1
        if self.FT260_I2CWrite(0xE, 0x07, 0x00) != 0:
            return -1
        if self.FT260_I2CWrite(0xE, 0x08, 0x00) != 0:
            return -1
        if self.FT260_I2CWrite(0xE, 0x09, 0x00) != 0:
            return -1
        if self.FT260_I2CWrite(0xE, 0x0A, 0x10) != 0:
            return -1
        if self.FT260_I2CWrite(0xE, 0x0B, 0x00) != 0:
            return -1
        if self.FT260_I2CWrite(0xE, 0x0C, 0xFF) != 0:
            return -1
        if self.FT260_I2CWrite(0xE, 0x0D, 0xEF) != 0:
            return -1
        if self.FT260_I2CWrite(0xE, 0x0E, 0x7F) != 0:
            return -1
        if self.FT260_I2CWrite(0xE, 0x0F, 0xFF) != 0:
            return -1
        if self.FT260_I2CWrite(0xE, 0x10, 0xF7) != 0:
            return -1
        if self.FT260_I2CWrite(0xE, 0x11, 0x7F) != 0:
            return -1
        if self.FT260_I2CWrite(0xE, 0x12, 0x22) != 0:
            return -1
        if self.FT260_I2CWrite(0xE, 0x13, 0x00) != 0:
            return -1
        if self.FT260_I2CWrite(0xE, 0x14, 0x00) != 0:
            return -1
        if self.FT260_I2CWrite(0xE, 0x15, 0x00) != 0:
            return -1
        if self.FT260_I2CWrite(0xE, 0x16, 0x04) != 0:
            return -1
        if self.FT260_I2CWrite(0xE, 0x17, 0x00) != 0:
            return -1
        if self.FT260_I2CWrite(0xE, 0x18, 0x00) != 0:
            return -1
        if self.FT260_I2CWrite(0xE, 0x19, 0x00) != 0:
            return -1
        if self.FT260_I2CWrite(0xE, 0x1A, 0x00) != 0:
            return -1
        if self.FT260_I2CWrite(0xE, 0x1B, 0x00) != 0:
            return -1
        if self.FT260_I2CWrite(0xE, 0x1C, 0x00) != 0:
            return -1
        if self.FT260_I2CWrite(0xE, 0x1D, 0x00) != 0:
            return -1
        if self.FT260_I2CWrite(0xE, 0x1E, 0xFF) != 0:
            return -1
        if self.FT260_I2CWrite(0xE, 0x1F, 0xCF) != 0:
            return -1
        if self.FT260_I2CWrite(0xE, 0x20, 0xFE) != 0:
            return -1
        if self.FT260_I2CWrite(0xE, 0x21, 0x01) != 0:
            return -1
        if self.FT260_I2CWrite(0xE, 0x22, 0x00) != 0:
            return -1
        if self.FT260_I2CWrite(0xE, 0x23, 0x00) != 0:
            return -1
        if self.FT260_I2CWrite(0xE, 0x30, 0x00) != 0:
            return -1
        if self.FT260_I2CWrite(0xE, 0x31, 0x00) != 0:
            return -1
        if self.FT260_I2CWrite(0xE, 0x32, 0x00) != 0:
            return -1
        if self.FT260_I2CWrite(0xE, 0x33, 0x00) != 0:
            return -1
        if self.FT260_I2CWrite(0xE, 0x34, 0x00) != 0:
            return -1
        if self.FT260_I2CWrite(0xE, 0x35, 0x00) != 0:
            return -1
        if self.FT260_I2CWrite(0xE, 0x36, 0x00) != 0:
            return -1
        if self.FT260_I2CWrite(0xE, 0x37, 0x00) != 0:
            return -1
        if self.FT260_I2CWrite(0xE, 0x38, 0x00) != 0:
            return -1
        if self.FT260_I2CWrite(0xE, 0x39, 0x00) != 0:
            return -1
        if self.FT260_I2CWrite(0xE, 0x3A, 0x00) != 0:
            return -1
        if self.FT260_I2CWrite(0xE, 0x3B, 0x00) != 0:
            return -1
        if self.FT260_I2CWrite(0xE, 0x3C, 0x00) != 0:
            return -1
        if self.FT260_I2CWrite(0xE, 0x3D, 0x00) != 0:
            return -1
        if self.FT260_I2CWrite(0xE, 0x3E, 0x00) != 0:
            return -1
        if self.FT260_I2CWrite(0xE, 0x3F, 0x00) != 0:
            return -1
        if self.FT260_I2CWrite(0xE, 0x40, 0x00) != 0:
            return -1
        if self.FT260_I2CWrite(0xE, 0x41, 0x00) != 0:
            return -1
        if self.FT260_I2CWrite(0xE, 0x42, 0x00) != 0:
            return -1
        if self.FT260_I2CWrite(0xE, 0x43, 0x00) != 0:
            return -1
        if self.FT260_I2CWrite(0xE, 0x44, 0x00) != 0:
            return -1
        if self.FT260_I2CWrite(0xE, 0x45, 0x00) != 0:
            return -1
        if self.FT260_I2CWrite(0xE, 0x46, 0x00) != 0:
            return -1
        if self.FT260_I2CWrite(0xE, 0x47, 0x00) != 0:
            return -1
        if self.FT260_I2CWrite(0xE, 0x48, 0x00) != 0:
            return -1
        if self.FT260_I2CWrite(0xE, 0x49, 0x00) != 0:
            return -1
        if self.FT260_I2CWrite(0xE, 0x4A, 0x00) != 0:
            return -1
        if self.FT260_I2CWrite(0xE, 0x4B, 0x00) != 0:
            return -1
        if self.FT260_I2CWrite(0xE, 0x4C, 0x00) != 0:
            return -1
        if self.FT260_I2CWrite(0xE, 0x4D, 0x00) != 0:
            return -1
        if self.FT260_I2CWrite(0xE, 0x4E, 0x00) != 0:
            return -1
        if self.FT260_I2CWrite(0xE, 0x4F, 0x00) != 0:
            return -1
        if self.FT260_I2CWrite(0xE, 0x50, 0x00) != 0:
            return -1
        if self.FT260_I2CWrite(0xE, 0x51, 0x00) != 0:
            return -1
        if self.FT260_I2CWrite(0xE, 0x52, 0x00) != 0:
            return -1
        if self.FT260_I2CWrite(0xE, 0x53, 0x00) != 0:
            return -1
        if self.FT260_I2CWrite(0xE, 0x30, 0x80) != 0:
            return -1
        if self.FT260_I2CWrite(0xE, 0x42, 0x02) != 0:
            return -1
        if self.FT260_I2CWrite(0xE, 0x46, 0x04) != 0:
            return -1
        return 0

    # ----------------------------------------------------------------------------------------------------
    # API
    # ----------------------------------------------------------------------------------------------------
    def EVB_Init(self):
        dev_index = self.FT260_Device_Search()

        if self.FT260_initial(dev_index) != 0:
            return -1
        return self.DTBD_Init()

    def EVB_ApbRead(self, addr):
        def byte2dec(data):
            if(data<0):
                out = data+ 256
            else:
                out = data
            return out
        # debug
        self.apb_result = addr
        # convert type
        wlength = ctypes.c_int32(0)
        addr_l = [(addr>> 8 * i) & 0xff for i in range(3,-1,-1)]
        aa_l = [0x80]+addr_l+[0x0]*4
        aa = self.get_bytes_array(aa_l)
        # operation
        self.FT260_I2CMaster_Write(self.mhandle, (0xE >> 1), 6, aa, 5, ctypes.byref(wlength))
        data_l = self.FT260_I2CRead(0xE, 0x84, 4)
        data = (data_l[0] << 24) | (data_l[1] << 16) | (data_l[2] << 8) | data_l[3]
        return data

    def EVB_ApbWrite(self, addr, data):
        # convert type
        wlength = ctypes.c_int32(0)
        addr_l = [(addr >> 8 * i) & 0xff for i in range(3,-1,-1)]
        data_l = [(data >> 8 * i) & 0xff for i in range(3,-1,-1)]
        aa_l   = [0x80] + addr_l + data_l
        aa     = self.get_bytes_array(aa_l)
        # operation
        return self.FT260_I2CMaster_Write(self.mhandle, (0xE >> 1), 6, aa, 9, ctypes.byref(wlength))

    def EVB_GetStatus(self):
        return i2c_result;


class EVB_APB(object):
    def __init__(self):
        self.mCfg = None
        dll_path = get_dll_path() + '/LibFT260.dll'
        self.com_bd = FT260_PyWrap(dll_path)

    def connect(self,mCfg):
        self.mCfg = mCfg

    def GetEVBStatus(self):
        Delay(self.mCfg.apb_delay)
        return self.com_bd.EVB_GetStatus()

    def GetApbResult(self):
        raddr0 = self.com_bd.apb_raddr0
        raddr1 = self.com_bd.apb_raddr1
        raddr2 = self.com_bd.apb_raddr2
        raddr3 = self.com_bd.apb_raddr3
        print ("raddr = 0x%x" % (raddr3<<24|raddr2<<16|raddr1<<8|raddr0))
        return self.com_bd.apb_result
   
    def read(self,addr,channel=0):
        Delay(self.mCfg.apb_delay)
        raddr = addr+0x40000*channel
        rdata = self.com_bd.EVB_ApbRead(raddr)
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
            rdata = self.com_bd.EVB_ApbRead(waddr)
            wdata = (rdata & (0xffff-mask)) | (data & mask)
        else:
            wdata = data
        if track:
            rdata = self.com_bd.EVB_ApbRead(waddr)
            print ("[ApbWrite] 0x%x = 0x%x -> 0x%x" % (waddr,rdata,wdata))
        if self.mCfg.track_apb_write_en and (waddr in self.mCfg.track_apb_write_addr):
            print ("[ApbWrite] 0x%x = 0x%x" % (waddr,wdata))
        self.com_bd.EVB_ApbWrite(waddr,wdata)

        if self.mCfg.b_dbg_apb_write:
            print ("[ApbWrite] 0x%x <= 0x%x" % (waddr,wdata))
        Delay(self.mCfg.apb_delay)
   
    def multi_write(self,addr,data,lane_strb=0x1,mask=None):
        for i in range(4):
            if (lane_strb >> i) & 1 == 1:
                self.write(addr,data,i,mask)

    def init_evb(self):
        self.com_bd.EVB_Init()

if __name__ == '__main__':
    class ApbConfig(object):
        def __init__(self):
            self.apb_delay = 0
            self.b_dbg_apb_write = False
            self.b_dbg_apb_read = False
            self.apb_poll_delay = 0
            self.track_apb_write_en = False
            self.track_apb_write_addr = []

    def gbe_test(lib):
        lib.init_evb()
        lib.com_bd.verbosity = Verbosity.DEBUG
        lib.write(0x24000024, 0x231)
        lib.write(0x24000004, 0x3)
        lib.write(0x24000004, 0x0)
        r0 = lib.read(0x0)
        r1 = lib.read(0x4)
        r2 = lib.read(0xffc)
        print("apb test result : %s" % 'pass' if (r0!=r1) else 'fail')
        print('rdata =', hex(r0),hex(r1),hex(r2))

    import os
    import sys
    from time import time

    evb_path = os.path.abspath('../SF56G_EVB')
    os.environ['SF56G_EVB_PATH'] = evb_path
    sys.path.insert(0, evb_path)

    lib = EVB_APB()
    cfg = ApbConfig()
    lib.connect(cfg)
    gbe_test(lib)
