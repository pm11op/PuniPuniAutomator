#!/usr/bin/python
import os, random, time


class Puni:
  debug = 1
  _X = (30, 1037)
  _Y = (1030, 1350)


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


  def swipe(self):
    r = random.randint(0, 10)
    if r <= 7 :
      return
        
    cmdf = "adb shell input touchscreen swipe %(x1)d %(x2)d %(y1)d %(y2)d"    
    x1 = random.randint(self._X[0], self._Y[0])
    y1 = random.randint(self._X[1], self._Y[1])
    x2 = random.randint(self._X[0], self._Y[0])
    y2 = random.randint(self._X[1], self._Y[1])

    cmd = cmdf % {'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2}
    self.execute(cmd)

    
Puni = Puni()
while (1):
  Puni.swipe()
  Puni.touch()
  time.sleep(0.1)

    
