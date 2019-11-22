from enum import Enum, IntEnum

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

class Verbosity(IntEnum):
    NONE  = 0
    LOW   = 1
    MED   = 2
    HIGH  = 3
    FULL  = 4
    DEBUG = 5

class FT260_STATUS(IntEnum):
    FT260_OK = 0
    FT260_INVALID_HANDLE = 1
    FT260_DEVICE_NOT_FOUND = 2
    FT260_DEVICE_NOT_OPENED = 3
    FT260_DEVICE_OPEN_FAIL = 4
    FT260_DEVICE_CLOSE_FAIL = 5
    FT260_INCORRECT_INTERFACE = 6
    FT260_INCORRECT_CHIP_MODE = 7
    FT260_DEVICE_MANAGER_ERROR = 8
    FT260_IO_ERROR = 9
    FT260_INVALID_PARAMETER = 10
    FT260_NULL_BUFFER_POINTER = 11
    FT260_BUFFER_SIZE_ERROR = 12
    FT260_UART_SET_FAIL = 13
    FT260_RX_NO_DATA = 14
    FT260_GPIO_WRONG_DIRECTION = 15
    FT260_INVALID_DEVICE = 16
    FT260_I2C_READ_FAIL = 17
    FT260_OTHER_ERROR = 18


class FT260_I2C_CONDITION(IntEnum):
    FT260_I2C_NONE = 0
    FT260_I2C_START = 2
    FT260_I2C_REPEATED_START = 3
    FT260_I2C_STOP = 4
    FT260_I2C_START_AND_STOP = 6


class FT260_Clock_Rate(IntEnum):
    FT260_SYS_CLK_12M = 0
    FT260_SYS_CLK_24M = 1
    FT260_SYS_CLK_48M = 2
