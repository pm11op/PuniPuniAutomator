#!/usr/bin/python
import os, random, time, subprocess


class Puni:
  debug = 1
  _X = (30, 1037)
  _Y = (1030, 1550)
  swipeLength = 50
  swipeWeight = 2
  macroNum = 1000
  screenShot = './img/ss.png'
  macroPath = './adb/'
  macroName = 'macro.sh'
  _R = 0
  _SR = 0
  _P = None
  _cmd = []
  _macro = []
  _swipeTrack = []
    
  def execute(self, cmd):
    if self.debug == 0:
      os.system(cmd)  
    elif self.debug == 1:
      print cmd
      os.system(cmd)  
    elif self.debug == 2:
      print cmd

  def touch(self, x, y):
    cmdf = "adb shell input touchscreen tap %(x)d %(y)d"
    cmd = cmdf % {'x': x, 'y': y}
    self.execute(cmd)
    
  def touchEvent(self):
    cmdf = """
sendevent /dev/input/event5 1 330 1
sendevent /dev/input/event5 3 58 1
sendevent /dev/input/event5 3 53 %(x)d
sendevent /dev/input/event5 3 54 %(y)d
sendevent /dev/input/event5 0 2 0
sendevent /dev/input/event5 0 0 0
sendevent /dev/input/event5 1 330 0
sendevent /dev/input/event5 0 2 0
sendevent /dev/input/event5 0 0 0
"""[1:-1]

    x = random.randint(self._X[0], self._Y[0])
    y = random.randint(self._X[1], self._Y[1])

    cmd = cmdf % {'x': x, 'y': y}
    self.intoMacro(cmd)


  ##
  #
  ##
  def swipeEvent(self, pos=None):
    if self._R < 7 :
      return

    if self._SR == 7:
      (vectorX, vectorY) = (-1, -1)
    elif self._SR == 8:
      (vectorX, vectorY) = (-1, 1)
    elif self._SR == 9:
      (vectorX, vectorY) = (1, 1)
    elif self._SR == 10:
      (vectorX, vectorY) = (1, -1)
      
    if not pos:
      self._swipeTrack = []
      pos = {}
      pos['x'] = random.randint(self._X[0], self._X[1])
      pos['y'] = random.randint(self._Y[0], self._Y[1])

      cmdf = """
sendevent /dev/input/event5 1 330 1
sendevent /dev/input/event5 3 58 1
sendevent /dev/input/event5 1 330 1
sendevent /dev/input/event5 3 58 1
sendevent /dev/input/event5 3 53 %(x1)d
sendevent /dev/input/event5 3 54 %(y1)d
sendevent /dev/input/event5 0 2 0
sendevent /dev/input/event5 0 0 0
sendevent /dev/input/event5 3 53 %(x2)d
sendevent /dev/input/event5 3 54 %(y2)d
sendevent /dev/input/event5 0 2 0
sendevent /dev/input/event5 0 0 0
"""[1:-1]
      
    else:
      cmdf = """
sendevent /dev/input/event5 3 53 %(x2)d
sendevent /dev/input/event5 3 54 %(y2)d
sendevent /dev/input/event5 0 2 0
sendevent /dev/input/event5 0 0 0
"""[1:-1]

    x2 = random.randint(min(self._X[1], max(self._X[0], min(pos['x'] + vectorX*self.swipeLength, pos['x'] + vectorX*self.swipeLength*self.swipeWeight))), min(self._X[1], max(self._X[0], max(pos['x'] + vectorX*self.swipeLength, pos['x'] + vectorX*self.swipeLength*self.swipeWeight))))
    y2 = random.randint(min(self._Y[1], max(self._Y[0], min(pos['y'] + vectorY*self.swipeLength, pos['y'] + vectorY*self.swipeLength*self.swipeWeight))), min(self._Y[1], max(self._Y[0], max(pos['y'] + vectorY*self.swipeLength, pos['y'] + vectorY*self.swipeLength*self.swipeWeight))))

#    print ('x', pos['x'], vectorX*self.swipeLength, x2)
#    print ('y', pos['y'], vectorY*self.swipeLength, y2)    
    
    if pos['x'] == x2 and pos['y'] == y2 or pos['x'] in self._X or pos['y'] in self._Y :
      self.swipeEnd()
      return
    
    cmd = cmdf % {'x1': pos['x'], 'y1': pos['y'], 'x2': x2, 'y2': y2}
    self._swipeTrack.append(cmd)

    if self._SR >= 9:
      self.genSRNum()
      self.swipeEvent({'x': x2, 'y': y2})
    else:
      self.swipeEnd()

  def swipeEnd(self):
    cmd = """
sendevent /dev/input/event5 1 330 0
sendevent /dev/input/event5 0 2 0
sendevent /dev/input/event5 0 0 0
"""[1:-1]
    self._swipeTrack.append(cmd)
    cmd = "\n".join(self._swipeTrack)
    self.intoMacro(cmd)

  def isFinished(self):
    return False

  def genRNum(self):
    self.genSRNum()
    self._R = random.randint(0, 10)
    
  def genSRNum(self):
    self._SR = random.randint(7, 10)

  def takeScreenShot(self):
#    if self._R >= 3:
#      return
        
    cmd1 = 'adb shell screencap -p /sdcard/screen.png'
    cmd2 = 'adb pull /sdcard/screen.png %(imgpath)s' % {'imgpath': self.screenShot}
    self.execute(cmd1)
    self.execute(cmd2)

  def intoMacro(self, cmd):
    self._macro.append(cmd)
    
  def makeMacro(self):
    self._macro = []
    i = 0
    while i < self.macroNum:
      self.genRNum()
      self.swipeEvent()
      self.touchEvent()
      i += 1
    txt = "\n".join(self._macro)
    f = open(self.macroPath + self.macroName, 'w')
    f.write(txt)
    f.close()
    
  def pushMacro(self):
    cmd = 'adb push %(path)s%(macro)s /sdcard/' % {'path': self.macroPath, 'macro': self.macroName}
    self.execute(cmd)

  def battleStart(self):
    self.touch(650, 1300)
    time.sleep(2)

  def doMacro(self):
    self.battleStart()
    self._P = subprocess.Popen(['adb', 'shell', 'sh /sdcard/%(macro)s' % {'macro': self.macroName}])  

Puni = Puni()
Puni.makeMacro()
Puni.pushMacro()
Puni.doMacro()

#while (1):
#  Puni.takeScreenShot()
#  Puni.genRNum()
#  Puni.takeScreenShot()
#  if Puni.isFinished():
#    exit()
#  time.sleep(0.08)
#  time.sleep(1)
    
# p = subprocess.Popen(['adb', 'shell', 'sh /sdcard/touch.sh'])
#  if p.poll() is 0 :
#    p = subprocess.Popen(['adb', 'shell', 'sh /sdcard/touch.sh'])
#  continue
  
