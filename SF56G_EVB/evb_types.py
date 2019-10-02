from enum import Enum

class PMAD_RxState(Enum):
    IDLE             = 1<<0
    PI_EN            = 1<<1
    CLK_EN           = 1<<2
    BIAS_WAIT        = 1<<3
    ADC_CAL_INIT_RDY = 1<<4
    ADC_CAL_INIT     = 1<<5
    IOC_CAL_RDY      = 1<<6
    IOC_CAL          = 1<<7
    WAIT_AN          = 1<<8
    DC_DET           = 1<<9
    SQUELCH          = 1<<10
    IOC_FL_CAL       = 1<<11
    EQ               = 1<<12
    ADAP             = 1<<13
    MMCDR            = 1<<14
    ADC_CAL_COA_END  = 1<<15
    ADC_CAL_FINE     = 1<<16
    SKEW_CAL         = 1<<17
    NORMAL           = 1<<18
    MOL_CHK          = 1<<19
    TR_INIT          = 1<<20
    CTLE_VGA_SET     = 1<<21
    VGA_GAIN         = 1<<22
    VGA_BG           = 1<<23

class PMAD_TxState(Enum):
    IDLE             = 1<<0
    WAIT             = 1<<1
    CLK_EN           = 1<<2
    SER_CLK_EN       = 1<<3
    SER_CLK_CHK      = 1<<4
    BIAS_WAIT        = 1<<5
    COMP_EN          = 1<<6
    CAL_EN           = 1<<7
    CAL_DONE         = 1<<8
    DRV_EN           = 1<<9
    AN_WAIT          = 1<<10
    SER_DATA_RSTN    = 1<<11
    NORMAL           = 1<<12

class PMAD_IocState(Enum):
      IDLE = 0
      ADC_INIT = 1
      READY = 2
      VGA2 = 3
      VGA3 = 4
      VGA1 = 5
      WAIT = 6
      PRE_FULL = 7
      FULL = 8
      DONE = 9
      
class PMAD_IocSubState(Enum):
      STOP = 0
      CAL_P = 1
      CAL_N = 2
      CAL_OPT = 3
      CAL_OFFSET = 4
      CAL_DATA = 5
      CAL_FULL = 6
      CAL_FULL_RESET = 7
      CAL_FULL_CHECK = 8
      CAL_DONE = 9

class PMAD_InitCalState(Enum):
      IDLE = 0
      WAIT = 1
      CAL_DONE = 2

class PMAD_MainCalState(Enum):
      IDLE = 0
      HOLD = 1
      FINE = 2
      WAIT = 3
      GAIN = 4
      DONE = 5
      BG_CAL = 6
      SLEEP = 7
