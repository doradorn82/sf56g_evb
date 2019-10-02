import os
import sys
from time import time
evb_path = os.path.abspath('../SF56G_EVB')
os.environ['SF56G_EVB_PATH'] = evb_path
sys.path.insert(0,evb_path)
from LibSF56G import SF56G

chip = SF56G()
chip.SetConfig('lane_en',0x1)
chip.build()
#alias
r = chip.mApb.read
w = chip.mApb.write

# sequence
chip.test_apb()
