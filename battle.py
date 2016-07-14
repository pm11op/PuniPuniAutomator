#!/usr/bin/python
import os, random, time


class Puni:
  debug = 1
  _X = (30, 1037)
  _Y = (1030, 1350)
  swipeLength = 125
  swipeWeight = 4
  macroNum = 1000
  screenShot = './img/ss.png'
  macroPath = './adb/'
  macroName = 'macro.sh'
  _R = 0
  _cmd = []
  _macro = []
    
  def execute(self, cmd):
    if self.debug == 0:
      os.system(cmd)  
    elif self.debug == 1:
      print cmd
      os.system(cmd)  
    elif self.debug == 2:
      print cmd
      
  def touch(self):
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
  def swipe(self, pos=None):
    if self._R < 7 :
      return
    vector = 1
    if self._R%2 == 0:
      vector = -1

    if not pos:
      pos = {}
      pos['x'] = random.randint(self._X[0], self._X[1])
      pos['y'] = random.randint(self._Y[0], self._Y[1])
        
    cmdf = "adb shell input touchscreen swipe %(x1)d %(y1)d %(x2)d %(y2)d"    

    if vector > 0:
      x2 = random.randint(min(self._X[1], max(self._X[0], pos['x'] + vector*self.swipeLength)), min(self._X[1], max(self._X[0], pos['x'] + vector*self.swipeLength*self.swipeWeight)))
      y2 = random.randint(min(self._Y[1], max(self._Y[0], pos['y'] + vector*self.swipeLength)), min(self._Y[1], max(self._Y[0], pos['y'] + vector*self.swipeLength*self.swipeWeight)))
    else:
      x2 = random.randint(min(self._X[1], max(self._X[0], pos['x'] + vector*self.swipeLength*self.swipeWeight)), min(self._X[1], max(self._X[0], pos['x'] + vector*self.swipeLength)))
      y2 = random.randint(min(self._Y[1], max(self._Y[0], pos['y'] + vector*self.swipeLength*self.swipeWeight)), min(self._Y[1], max(self._Y[0], pos['y'] + vector*self.swipeLength)))

    if pos['x'] == x2 and pos['y'] == y2:
      return
    
    cmd = cmdf % {'x1': pos['x'], 'y1': pos['y'], 'x2': x2, 'y2': y2}
    self.intoMacro(cmd)

    if self._R >= 9:
      self.swipe({'x': x2, 'y': y2})
        

  def isFinished(self):
    return False

  def genRNum(self):
    self._R = random.randint(0, 10)

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
#      self.swipe()
      self.touch()
      i += 1
    txt = "\n".join(self._macro)
    f = open(self.macroName, 'w')
    f.write(txt)
    f.close()
    
  def pushMacro(self):
    cmd = 'adb push %(path)s%(macro)s /sdcard/' % {'path': self.macroPath, 'macro': self.macroName}
    self.execute(cmd)

  def doMacro(self):
    cmd = 'adb shell sh /sdcard/%(macro)s' % {'macro': self.macroName}
    self.execute(cmd)
    
import subprocess

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
  
