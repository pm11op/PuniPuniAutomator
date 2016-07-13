#!/usr/bin/python
import os, random, time


class Puni:
  debug = 1
  _X = (30, 1037)
  _Y = (1030, 1350)
  swipeLength = 125
  swipeWeight = 4

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
    r = random.randint(0, 10)
    if r < 7 :
      return
    vector = 1
    if r%2 == 0:
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

    cmd = cmdf % {'x1': pos['x'], 'y1': pos['y'], 'x2': x2, 'y2': y2}
    self.execute(cmd)

    if r >= 9:
      self.swipe({'x': x2, 'y': y2})
        

  def isFinished(self):
    return False
  
    
Puni = Puni()
while (1):
  if Puni.isFinished():
    exit()
  Puni.swipe()
  Puni.touch()
  time.sleep(0.08)
#  time.sleep(1)
    
