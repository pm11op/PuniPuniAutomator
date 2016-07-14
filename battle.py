#!/usr/bin/python
import os, random, time


class Puni:
  debug = 1
  _X = (30, 1037)
  _Y = (1030, 1350)
  swipeLength = 125
  swipeWeight = 4
  screenShot = './img/ss.png'
  _R = 0
  _cmd = []

  def execute(self, cmd):
    if self.debug == 0:
      os.system(cmd)  
    elif self.debug == 1:
      print cmd
      os.system(cmd)  
    elif self.debug == 2:
      print cmd
      
  def touch(self):
    cmdf = "adb shell input touchscreen tap %(x)d %(y)d"    
    x = random.randint(self._X[0], self._Y[0])
    y = random.randint(self._X[1], self._Y[1])

    cmd = cmdf % {'x': x, 'y': y}
    self.execute(cmd)


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
    self.execute(cmd)

    if self._R >= 9:
      self.swipe({'x': x2, 'y': y2})
        

  def isFinished(self):
    return False

  def onLoopInit(self):
    self._R = random.randint(0, 10)

  def takeScreenShot(self):
#    if self._R >= 3:
#      return
        
    cmd1 = 'adb shell screencap -p /sdcard/screen.png'
    cmd2 = 'adb pull /sdcard/screen.png %(imgpath)s' % {'imgpath': self.screenShot}
    self.execute(cmd1)
    self.execute(cmd2)

    
import subprocess

Puni = Puni()
p = subprocess.Popen(['adb', 'shell', 'sh /sdcard/touch.sh'])
while (1):
#  Puni.takeScreenShot()
  if p.poll() is 0 :
    p = subprocess.Popen(['adb', 'shell', 'sh /sdcard/touch.sh'])
  continue
  Puni.onLoopInit()
  Puni.takeScreenShot()
  if Puni.isFinished():
    exit()
  Puni.swipe()
  Puni.touch()
  time.sleep(0.08)
#  time.sleep(1)
    
