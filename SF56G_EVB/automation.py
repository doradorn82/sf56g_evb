import time
import sys
# import os
from sys import path
import pdb
import json
import xlrd
from collections import OrderedDict
import copy
import xlsxwriter
path.append("python")
path.append("python/eti_lib")
path.append("python/external")
path.append("python/tools")
path.append("foundation")
# from portsetup import portsetup
from isi import Isi
from xtalk import Xtalk
from vna import Vna
from thermostream import Thermostream
# import visa
from samsung import Samsung
from viavi import Viavi
# from python.eti_lib.Process_script_command import master_process_script_command
def channel_characterization(isi_min, isi_max, isi_step, xtalk_min, xtalk_max, xtalk_step):
  for isi_level in range(isi_min, isi_max + isi_step, isi_step):
   # Reset to Zero
   loss.set_level(isi_level=0)
   loss.read_level()
   # Set the ISI Level
   loss.set_level(isi_level=isi_level)
   loss.read_level()
   loss.system_error_check()
   for xtalk_level in range(xtalk_min, xtalk_max + xtalk_step, xtalk_step):
    # Reset to Zero
    cross.set_level(xtalk_level_Dplus=0, xtalk_level_Dminus=0)
    cross.read_level()
    # Set the Xtalk Level
    cross.set_level(xtalk_level_Dplus=xtalk_level, xtalk_level_Dminus=xtalk_level)
    cross.read_level()
    cross.system_error_check()
    #time.sleep(10)
    # vnameasure.averaging(avg="ON", avg_no=16)
    # time.sleep(60)
    file_name = r"'G:\Sumanth\new\LC_K5_P83_BP_P64_K10_loss_"+str(isi_level)+"_xtalk_"+ str(
     xtalk_level)+".s6p'"
    vnameasure.measuresp(filename=file_name)
    time.sleep(90)
    # vnameasure.averaging(avg="OFF")
    vnameasure.system_error_check()
    # vnameasure.complete()

def evb_retune(evb):
 # pdb.set_trace()
 evb.reset()
 evb.act_chan_TX(data_patt=data_pattern, datarate=datarate, channel=TXchannel, data_mod=data_mode,
                 serdes_mode=serdes_mode, precoding=precoding, graycoding=graycoding)
 evb.act_chan_RX(data_patt=data_pattern, datarate=datarate, channel=RXchannel, data_mod=data_mode,
                 serdes_mode=serdes_mode, precoding=precoding, graycoding=graycoding)
 evb.set_tx_pre_post(tx_pre=Txpre, tx_post=Txpost, attenuation=Txmain)
 return

def ber_test(output_data,evb):
 if lossbox_flag == 1:
  for isi_level in range(isi_min, isi_max + isi_step, isi_step):
   # Reset to Zero
   loss.set_level(isi_level=0)
   loss.read_level()
   # Set the ISI Level
   loss.set_level(isi_level=isi_level)
   loss.read_level()
   loss.system_error_check()
   output_data['ISI Level'] = isi_level
   if Xtalk_flag == 1:
    for xtalk_level in range(xtalk_min, xtalk_max + xtalk_step, xtalk_step):
     # Reset to Zero
     cross.set_level(xtalk_level_Dplus=0, xtalk_level_Dminus=0)
     cross.read_level()
     # Set the Xtalk Level
     cross.set_level(xtalk_level_Dplus=xtalk_level, xtalk_level_Dminus=xtalk_level)
     cross.read_level()
     cross.system_error_check()
     output_data['Xtalk Level'] = xtalk_level
     #time.sleep(10)
     if thermostream_flag == 0:
      for repeat in range(repeatability):
       if repeatability > 1:
        print("Repeatability Number: ", repeat)
        output_data['Repeatability'] = repeat+1
       evb_retune(evb)
       evb.tune_rx()
       if FEC_test:
        FEC.force_resync_fec()
        FEC.force_DSP_resync()
        FEC.start()
       output_data['EVB_Temperature'], output_data['status_values'] = evb.get_status()
       if FEC_test:
        print("#####################################################")
        print(FEC.viavi_ber())
        print(FEC.viavi_fec())
        print(FEC.rx_lane_skew_id())
        print(FEC.rx_lane_skew())
        print(FEC.rx_lane_skew_time())
        print("#####################################################")
        time.sleep(10)
        FEC.stop()
       final_data.append(copy.deepcopy(output_data))
       # if repeatability > 1:
       #  evb_retune()
     elif thermostream_flag == 1:
      evb.tune_rx()
      if FEC_test:
       FEC.force_resync_fec()
       FEC.force_DSP_resync()
       FEC.start()
      output_data['Thermal Temp'] = thermal.read_temp()
      output_data['EVB_Temperature'], output_data['status_values'] = evb.get_status()
      if FEC_test:
       print(FEC.viavi_ber())
       print(FEC.viavi_fec())
       print(FEC.rx_lane_skew_id())
       print(FEC.rx_lane_skew())
       print(FEC.rx_lane_skew_time())
       FEC.stop()
      final_data.append(copy.deepcopy(output_data))
      thermal.cycle(1)
      while True:
       if FEC_test:
        FEC.force_resync_fec()
        FEC.force_DSP_resync()
        FEC.start()
       output_data['Thermal Temp'] = thermal.read_temp()
       output_data['EVB_Temperature'], output_data['status_values'] = evb.get_status()
       if FEC_test:
        print(FEC.viavi_ber())
        print(FEC.viavi_fec())
        print(FEC.rx_lane_skew_id())
        print(FEC.rx_lane_skew())
        print(FEC.rx_lane_skew_time())
        FEC.stop()
       final_data.append(copy.deepcopy(output_data))
       bit_reg = thermal.instrument.query("TESR?")
       binary_value = ('0' * 7 + bin(int(bit_reg))[2:])[-8:]
       print("TESR", bit_reg, binary_value, binary_value[-5])
       print("CYCC?", thermal.instrument.query('CYCC?'))
       if binary_value[-5] == "1":
        break
       time.sleep(60)
   else:
    print(thermostream_flag)
    if thermostream_flag == 0:
     for repeat in range(repeatability):
      if repeatability > 1:
       print("Repeatability Number: ", repeat)
       output_data['Repeatability'] = repeat
      evb.tune_rx()
      if FEC_test:
       FEC.force_resync_fec()
       FEC.force_DSP_resync()
       FEC.start()
      output_data['EVB_Temperature'], output_data['status_values'] = evb.get_status()
      if FEC_test:
       print(FEC.viavi_ber())
       print(FEC.viavi_fec())
       print(FEC.rx_lane_skew_id())
       print(FEC.rx_lane_skew())
       print(FEC.rx_lane_skew_time())
       FEC.stop()
      final_data.append(copy.deepcopy(output_data))
      if repeatability > 1:
       evb_retune(evb)
    elif thermostream_flag == 1:
     evb.tune_rx()
     if FEC_test:
      FEC.force_resync_fec()
      FEC.force_DSP_resync()
      FEC.start()
     output_data['Thermal Temp'] = thermal.read_temp()
     output_data['EVB_Temperature'], output_data['status_values'] = evb.get_status()
     if FEC_test:
      print(FEC.viavi_ber())
      print(FEC.viavi_fec())
      print(FEC.rx_lane_skew_id())
      print(FEC.rx_lane_skew())
      print(FEC.rx_lane_skew_time())
      FEC.stop()
     final_data.append(copy.deepcopy(output_data))
     while True:
      if FEC_test:
       FEC.force_resync_fec()
       FEC.force_DSP_resync()
       FEC.start()
      output_data['EVB_Temperature'], output_data['status_values'] = evb.get_status()
      if FEC_test:
       print(FEC.viavi_ber())
       print(FEC.viavi_fec())
       print(FEC.rx_lane_skew_id())
       print(FEC.rx_lane_skew())
       print(FEC.rx_lane_skew_time())
       FEC.stop()
      final_data.append(copy.deepcopy(output_data))
      bit_reg = thermal.instrument.query("TESR?")
      binary_value = ('0' * 7 + bin(int(bit_reg))[2:])[-8:]
      print("TESR", bit_reg, binary_value, binary_value[-5])
      print("CYCC?", thermal.instrument.query('CYCC?'))
      if binary_value[-5] == "1":
       break
      time.sleep(60)
 else:
  for repeat in range(repeatability):
   if repeatability > 1:
    print("Repeatability Number: ", repeat)
    output_data['Repeatability'] = repeat + 1
   evb.tune_rx()
   if FEC_test:
    FEC.force_resync_fec()
    FEC.force_DSP_resync()
    FEC.start()
   output_data['EVB_Temperature'], output_data['status_values'] = evb.get_status()
   if FEC_test:
    print("#####################################################")
    print(FEC.viavi_ber())
    print(FEC.viavi_fec())
    print(FEC.rx_lane_skew_id())
    print(FEC.rx_lane_skew())
    print(FEC.rx_lane_skew_time())
    print("#####################################################")
    time.sleep(10)
    FEC.stop()
   final_data.append(copy.deepcopy(output_data))
   if repeatability > 1:
    evb_retune(evb)
 # pdb.set_trace()
 return final_data

def save_data():
 with open(filename.split(".")[0] + "_results_" + outputfile + '.json', 'w') as f:
  json.dump(final_data, f)
 return
 # worksheet = workbook.add_worksheet(outputfile)
 # col = 0
 # for key1 in final_data[0]:
 #  if key1 != "status_values":
 #   worksheet.write(0, col, key1)
 #   col += 1
 #  else:
 #   key2 = final_data[0][key1].keys()[0]
 #   for key3 in final_data[0][key1][key2]:
 #    if not isinstance(final_data[0][key1][key2][key3], list):
 #     worksheet.write(0, col, key3)
 #     col += 1
 #    else:
 #     for loop in range(len(final_data[0][key1][key2][key3])):
 #      worksheet.write(0, col, key3 + str(loop))
 #      col += 1
 #
 # for row in range(len(final_data)):
 #  numberofchannels = len(final_data[row]['RX channel'])
 #  for rx in range(numberofchannels):
 #   col = 0
 #   rowvalue = (numberofchannels * row) + 1 + rx
 #   # print(rowvalue)
 #   for key1 in final_data[row]:
 #    if key1 == "RX channel" or key1 == "TX channel":
 #     worksheet.write(rowvalue, col, final_data[row][key1][rx])
 #     # worksheet.write(len(final_data["RX channel"]) * row + 1 + rx, col, final_data[row][key1][rx])
 #     col += 1
 #    elif key1 != "status_values":
 #     # print(key1)
 #     worksheet.write(rowvalue, col, final_data[row][key1])
 #     # worksheet.write(len(final_data["RX channel"])*row + 1 + rx, col, final_data[row][key1])
 #     col += 1
 #    else:
 #     # print(row, key1, rx, len(final_data[row][key1][final_data[row]["RX channel"][rx]]))
 #     for key3 in final_data[row][key1][final_data[row]["RX channel"][rx]]:
 #      if not isinstance(final_data[row][key1][final_data[row]["RX channel"][rx]][key3], list):
 #       worksheet.write(rowvalue, col,
 #                       final_data[row][key1][final_data[row]["RX channel"][rx]][key3])
 #       col += 1
 #      else:
 #       for loop in range(len(final_data[row][key1][final_data[row]["RX channel"][rx]][key3])):
 #        worksheet.write(rowvalue, col,
 #                        final_data[row][key1][final_data[row]["RX channel"][rx]][key3][
 #                         loop])
 #        col += 1
 #
 # return

if __name__ == '__main__':
 start_time = time.time()
 global filename
 filename = sys.argv[1]
 wb = xlrd.open_workbook(filename)
 sheet = wb.sheet_by_index(0)
 global workbook, outputfile
 workbook = xlsxwriter.Workbook(filename.split(".")[0] + "_results.xlsx")
 global lossbox_flag, isi_max, isi_min, isi_step, isi_port, loss_mode
 global Xtalk_flag, xtalk_port_Dplus, xtalk_port_Dminus, xtalk_min, xtalk_max, xtalk_step
 global thermostream_flag, thermostream_gpibid , ramp_up_rate, ramp_down_rate, ramp_up_temp, ramp_down_temp, stime
 global num_cycles, ramping, cycling, repeatability, sweeping, ber_measure_interval
 global evb_flag, data_pattern, datarate, TXchannel, RXchannel, data_mode, precoding, graycoding, serdes_mode
 global final_data, Txpre, Txpost, Txmain
 global loss, cross, thermal, viavi_IP_address, FEC, viavi_PORT, FEC_test
 for test in range(1, sheet.nrows):
  input_data = {}
  for parameters in range(sheet.ncols):
   if sheet.cell_value(test, parameters) == "-":
    input_data[sheet.cell_value(0, parameters)] = None
   else:
    input_data[sheet.cell_value(0, parameters)] = sheet.cell_value(test, parameters)
 # all the parameters initialised below will be initialised through gui later
  if input_data['ISI COM Port']:
   lossbox_flag = 1
   isi_port = input_data['ISI COM Port']#.encode()
   loss_mode = "P"
   isi_min = int(input_data['ISI Min'])
   isi_max = int(input_data['ISI Max'])
   isi_step = int(input_data['ISI Step'])
  else:
   lossbox_flag = 0
  if input_data['Xtalk Dplus COM Port'] and input_data['Xtalk Dminus COM Port']:
   Xtalk_flag = 1
   xtalk_port_Dplus = input_data['Xtalk Dplus COM Port']#.encode()
   xtalk_port_Dminus = input_data['Xtalk Dminus COM Port']#.encode()
   xtalk_min = int(input_data['Xtalk Min'])
   xtalk_max = int(input_data['Xtalk Max'])
   xtalk_step = int(input_data['Xtak Step'])
  else:
   Xtalk_flag = 0
  # VNA_flag = int(input_data['VNA'])
  VNA_flag = 0
  if input_data['Thermo GPIB_ID']:
   thermostream_flag = 1
   thermostream_gpibid = input_data['Thermo GPIB_ID']
   ramp_up_rate = int(input_data['Ramp Up Rate'])
   ramp_down_rate = int(input_data['Ramp Down Rate'])
   ramp_up_temp = int(input_data['Max Temp'])
   ramp_down_temp = int(input_data['Min Temp'])
   stime = int(input_data['Soak Time'])
   ber_measure_interval = 20
   num_cycles = int(input_data['Number of Cycles'])
   if num_cycles == 0:
    num_cycles = 1
    ramping = 1
   else:
    cycling = 1
    ramping = 0
  else:
   thermostream_flag = 0
  print(type(input_data['Repeatability']), input_data['Repeatability'])
  input_data['Repeatability'] = int(input_data['Repeatability'])
  if input_data['Repeatability'] == 0:
   repeatability = 1
   sweeping = 1
  else:
   repeatability = input_data['Repeatability']
   sweeping = 0
  vna_gpibid = 'GPIB0::16::INSTR'
  evb_flag = 1  # input_data["Evb"]
  data_pattern = input_data['Data Pattern']#.encode()
  datarate = float(input_data['Data Rate'].split()[1][:-1])
  TXchannel = [int(c) for c in input_data["TX Pairs"].split(",")]
  RXchannel = [int(c) for c in input_data["RX Pairs"].split(",")]
  data_mode = input_data['Data Rate'].split()[0]
  precoding = int(input_data['Pre Coding'])
  graycoding = int(input_data['Gray Coding'])
  serdes_mode = None
  outputfile = input_data['Output Filename']#.encode()
  if input_data["TX Pre Min"]:
   Tx_pre_min = [int(c) for c in input_data["TX Pre Min"].split(",")]
  else:
   Tx_pre_min = None
  if input_data["TX Main Min"]:
   Tx_main_min = [int(c) for c in input_data["TX Main Min"].split(",")]
  else:
   Tx_main_min = None
  if input_data["TX Post Min"]:
   Tx_post_min = [int(c) for c in input_data["TX Post Min"].split(",")]
  else:
   Tx_post_min = None

  if input_data["TX Pre Max"]:
   Tx_pre_max = [int(c) for c in input_data["TX Pre Max"].split(",")]
  if input_data["TX Main Max"]:
   Tx_main_max = [int(c) for c in input_data["TX Main Max"].split(",")]
  if input_data["TX Post Max"]:
   Tx_post_max = [int(c) for c in input_data["TX Post Max"].split(",")]
  if input_data["TX Pre step"]:
   Tx_pre_step = [int(c) for c in input_data["TX Pre step"].split(",")]
  if input_data["TX Main step"]:
   Tx_main_step = [int(c) for c in input_data["TX Main step"].split(",")]
  if input_data["TX Post step"]:
   Tx_post_step = [int(c) for c in input_data["TX Post step"].split(",")]
  Txpre = Tx_pre_min
  Txpost = Tx_post_min
  Txmain = Tx_main_min
  # pdb.set_trace()
  if lossbox_flag == 1:
   loss = Isi(port=isi_port)
   loss.setup()
   identity = loss.device_identity()
   loss.reset()
   loss.set_remote()
   if "CLE1200" in identity:
    loss.set_mode(mode = loss_mode)
    loss.read_mode()
  if Xtalk_flag == 1:
   cross = Xtalk(port_Dplus = xtalk_port_Dplus, port_Dminus = xtalk_port_Dminus)
   cross.setup()
   cross.device_identity()
   cross.reset()
   cross.set_remote()
  # else:
  #  cross = None
  if VNA_flag == 1:
   vnameasure = Vna(gpibid=vna_gpibid)
   vnameasure.setup()
   vnameasure.device_identity()
   vnameasure.system_error_check()
   # vnameasure.configure()
   # vnameasure.instrument.query("CALC:PAR:DEF:EXT 'MyMeas2',S12;*OPC?")
   print(vnameasure.instrument.query("SYST:CHAN:CAT?"))
   # vnameasure.instrument.write("DISP:WINDow1:TRACe1:FEED 'MyMeas2'")
   name = vnameasure.instrument.query("SYST:MEAS:NAME?")
   vnameasure.system_error_check()
   print("name", name)
   # print(vnameasure.instrument.query("CALC:PAR:SEL " + name))
   vnameasure.system_error_check()
  if thermostream_flag == 1:
   thermal = Thermostream(gpibid=thermostream_gpibid)
   thermal.setup()
   thermal.device_identity()
   thermal.dut_configure()
   thermal.instrument.write('RSTP')
   thermal.instrument.write("WNDW 1")
   thermal.ramping_up(ramp_up=ramp_up_rate)
   thermal.ramping_down(ramp_low=ramp_down_rate)
   thermal.set_cycleno(num_cycles)
   thermal.setpoint(temperature=ramp_down_temp, stepn=0)
   thermal.soak_time(stime)
   thermal.instrument.write("STAD 1")
   time.sleep(2)
   thermal.setpoint(temperature=ramp_up_temp, stepn=1)
   if ramping == 1:
    thermal.soak_time(60*4)
   else:
    thermal.soak_time(stime)
   thermal.instrument.write("STAD 1")
   for i in range(2, 10):
    thermal.instrument.write('SETN ' + str(i))
    thermal.instrument.write("STAD 0")
    time.sleep(2)
   # thermal.instrument.write('SETN ' + str(0))
   # thermal.instrument.write("STAD 1")
  # else:
  #  thermal = None
  if input_data["Test Name"] == "FEC BER test":
   FEC_test = True
   viavi_IP_address = '169.254.136.60'
   viavi_PORT = '11066'
   FEC = Viavi(viavi_IP_address, viavi_PORT)
   FEC.setup()
   FEC.device_identity()
  else:
   FEC_test = False
  if evb_flag == 1:
   # pdb.set_trace()
   output_data = OrderedDict()
   output_data['TX channel'] = TXchannel
   output_data['RX channel'] = RXchannel
   output_data['Data Mode'] = data_mode
   output_data['Datarate'] = datarate
   output_data['Data Pattern'] = data_pattern
   output_data['Precoding'] = precoding
   output_data['Greycoding'] = graycoding

   # evb = None
   if test == 1:
    evb = Samsung()
    evb.init_evb()
   else:
    # del evb
    evb = Samsung()
   evb.act_chan_TX(data_patt=data_pattern, datarate=datarate, channel=TXchannel, data_mod=data_mode,
       precoding=precoding, graycoding=graycoding)
   evb.act_chan_RX(data_patt=data_pattern, datarate=datarate, channel=RXchannel, data_mod=data_mode,
       precoding=precoding, graycoding=graycoding)
   evb.set_tx_pre_post(tx_pre=Txpre, tx_post=Txpost, attenuation=Txmain)
   # Txpre, Txpost, Txmain = evb.set_tx_pre_post(tx_pre=Txpre, tx_post=Txpost, attenuation=Txmain)
   # # output_data['TX FIR Coeff'] = evb.TxFirCoef
   # for pre in range(len(Txpre)):
   #  # output_data['TX_FIR_Pre_'+str(pre+1)] = Txpre[pre]
   # for main in range(len(Txmain)):
   #  # output_data['TX_FIR_Main_'+str(main+1)] = Txmain[main]
   # for post in range(len(Txpost)):
   #  # output_data['TX_FIR_Post_'+str(post+1)] = Txpost[post]
  final_data = []
  # with open('results.json','w') as f:
  #  json.dump(final_data, f)
  # exit(0)
  # pdb.set_trace()
  ber_test(output_data,evb)
  save_data()
 workbook.close()
 if thermostream_flag == 1:
  thermal.thermo_off()
 # del evb
 print(time.time()-start_time)

'''
# vnameasure.instrument.query("CALC:DATA:SNP:PORTs:Save '1,2,3,4,5,6', 'G:\\Sumanth\\new\\testing.s6p';*OPC?")
# vnameasure.system_error_check()
# channel_characterization(isi_min, isi_max, isi_step, xtalk_min, xtalk_max, xtalk_step)
# vnameasure.instrument.write("TRIG:CHAN:AUX:ENAB ON")
# vnameasure.instrument.write("TRIG:SOUR IMM")
# vnameasure.instrument.write("TRIG:CHAN:AUX:INT SWE")
# vnameasure.averaging(avg="ON", avg_no=16)
# file_name = r"'G:\Sumanth\new\testing.s6p'"
# vnameasure.measuresp(filename=file_name)
# vnameasure.system_error_check()
# vnameasure.averaging(avg="OFF")
# vnameasure.instrument.write("TRIG:CHAN:AUX:ENAB OFF")
'''

