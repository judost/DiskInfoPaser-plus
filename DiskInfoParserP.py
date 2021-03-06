"""
by Xioustic (https://github.com/xioustic/)

Uses DiskInfo.exe to create DiskInfo.txt data, then reads
that in and outputs JSON to DiskInfoParser.json.
"""

import subprocess
import enum
import re
import json
import sys

class ReadMode(enum.Enum):
  start = 1
  controllermap = 2
  disklist = 3
  drivedata = 4
  smartdata = 5
  identifydata = 6
  smartreaddata = 7
  smartreadthreshold = 8


import os

def folderM(name):
  try:
    if not os.path.exists(f'./{name}'):  #  ../ 상위 폴더에 만들기
      os.makedirs(f'./{name}') # 이미 있으면 실패함 
  except OSError:
    print('폴더 생성에 실패했습니다.')
    
    
folderM('JSON')
    

import time

i = 0
while(i<1):
      
  title = time.strftime('%Y-%m-%d--%H-%M-%S')

  i += 1

  # generate data
  #print "Running DiskInfo.exe"
  try:
    status = subprocess.call("./Info/DiskInfo.exe /CopyExit")
  except WindowsError as e:
    if "Error 740" in str(e):
      print ("This application must be run as an administrator to get raw access to drives.")
      print ("Exiting.")
      sys.exit(1)
    else:
      raise e

  if status != 0:
    raise Exception("DiskInfo.exe exited with status code "+status)


  # read data
  input_data = None

  with open('./Info/DiskInfo.txt','r', encoding='utf-16') as f: # 구 버전은 16, 신 버전은 8
    input_data = f.read()

  # input_data = input_data.decode('utf-16')  # 인코딩을 이미 필요X


  # parse data
  obj = {"controllers_disks": {}, "disks": []}
  curmode = ReadMode.start
  curdiskname = None
  curdiskidx = None
  curcontroller = None

  for linenum, line in enumerate(input_data.splitlines()):

    # skip blank lines
    if len(line) == 0:
      #print "blank",line
      continue

    # mode pivots
    if re.search("^-- Controller Map",line):
      curmode = ReadMode.controllermap
      continue

    if re.search("^-- Disk List",line):
      curmode = ReadMode.disklist
      continue

    if re.search("^-- S.M.A.R.T. ",line):
      curmode = ReadMode.smartdata
      continue
    
    '''
    if re.search("^-- IDENTIFY_DEVICE ",line):
      curmode = ReadMode.identifydata
      continue

    if re.search("^-- SMART_READ_DATA ",line):
      curmode = ReadMode.smartreaddata
      continue

    if re.search("^-- SMART_READ_THRESHOLD ",line):
      curmode = ReadMode.smartreadthreshold
      continue
    '''

    if curmode == ReadMode.controllermap:
      if line.startswith(" + "):
        curcontroller = line[len(" + "):]
        obj["controllers_disks"][curcontroller] = []
      if line.startswith("   - "):
        obj["controllers_disks"][curcontroller].append(line[len("   - "):])
      continue

    if curmode == ReadMode.disklist:
      result = re.search("^ \((\d+)\) (.*) : (.*) \[.*$",line)
      if result:
        idx, name, size = result.groups()
        obj['disks'].append({"DiskNum": idx, "Model": name, "Disk Size": size})
      elif line.startswith("-----------------"):
        curmode = ReadMode.drivedata
      continue

    result = re.search("^ \((\d+)\) (.*)$",line)
    if result:
      curmode = ReadMode.drivedata
      curdiskidx, curdiskname = result.groups()
      continue

    if curmode == ReadMode.drivedata:
      splitstrip = [x.strip() for x in line.split(" : ")]
      if len(splitstrip) > 1:
        attribute, value = splitstrip
        obj['disks'][int(curdiskidx)-1][attribute] = value
      continue

    if curmode == ReadMode.smartdata:
      result = re.search("^([A-F0-9]{2}) _*(\d*) _*(\d*) _*(\d*) ([A-F0-9]{12}) (.*)$",line)
      if result:
        _id, cur, wor, thr, rawvalues, attributename = result.groups()
        smartobj = {"ID": _id, "Cur": cur, "Wor": wor, "Thr": thr, "RawValues": rawvalues, "Attribute Name": attributename}

        if "S.M.A.R.T." not in obj['disks'][int(curdiskidx)-1]:
          obj['disks'][int(curdiskidx)-1]["S.M.A.R.T."] = []

        obj['disks'][int(curdiskidx)-1]["S.M.A.R.T."].append(smartobj)
      continue

    '''
    if curmode == ReadMode.identifydata:
      # skip header
      if line.startswith("    "):
        continue

      # extract hex, stripping off index at beginning
      hexdata = "".join(line.split(" ")[1:])

      # initialize on disk object if needed
      if "IDENTIFY_DEVICE" not in obj['disks'][int(curdiskidx)-1]:
        obj['disks'][int(curdiskidx)-1]["IDENTIFY_DEVICE"] = ""

      obj['disks'][int(curdiskidx)-1]["IDENTIFY_DEVICE"] += hexdata
      continue

    if curmode == ReadMode.smartreaddata:
      # skip header
      if line.startswith("    "):
        continue

      # extract hex, stripping off index at beginning
      hexdata = "".join(line.split(" ")[1:])

      # initialize on disk object if needed
      if "SMART_READ_DATA" not in obj['disks'][int(curdiskidx)-1]:
        obj['disks'][int(curdiskidx)-1]["SMART_READ_DATA"] = ""

      obj['disks'][int(curdiskidx)-1]["SMART_READ_DATA"] += hexdata
      continue

    if curmode == ReadMode.smartreadthreshold:
      # skip header
      if line.startswith("    "):
        continue

      # extract hex, stripping off index at beginning
      hexdata = "".join(line.split(" ")[1:])

      # initialize on disk object if needed
      if "SMART_READ_THRESHOLD" not in obj['disks'][int(curdiskidx)-1]:
        obj['disks'][int(curdiskidx)-1]["SMART_READ_THRESHOLD"] = ""

      obj['disks'][int(curdiskidx)-1]["SMART_READ_THRESHOLD"] += hexdata
      continue
    '''

  # print(obj.keys()) # dict_keys(['controllers_disks', 'disks'])
  # print(obj['controllers_disks'])
  # print(obj['disks'])
  
  # print(type(obj['disks']))
  # print(len(obj['disks']))
  # print(type(obj['disks'][0]))
  # print(obj['disks'][0]['S.M.A.R.T.'])
  # print(type(obj['disks'][0]['S.M.A.R.T.']))
  # print(len(obj['disks'][0]['S.M.A.R.T.']))
  # print(obj['disks'][0]['S.M.A.R.T.'][0])
  
  # output data
  with open(f"./JSON/{title}Paser.json","w") as f:
    f.write(json.dumps(obj, indent=2, separators=(",", ": "), sort_keys=True))
    

  print(i, '번째 중입니다.')
  # time.sleep(1)
  
# JSON 뽑을 때 변환
# 변환 방법 
# tx = '\uc88b\uc74c'
# aa = bytes(tx, encoding='cp949')
# aa = aa.decode('cp949')

print("It's OK!")
