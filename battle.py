#!/usr/bin/python
import os, random, time, subprocess, cv2


class Puni:
  debug = 1
  _X = (30, 1037)
  _Y = (1030, 1550)
  swipeLength = 50
  swipeWeight = 2
  macroNum = 300
  screenShot = './img/ss.png'
  macroPath = './adb/'
  macroName = 'macro.sh'
  _R = 0
  _SR = 0
  _P = None
  _cmd = []
  _macro = []
  _swipeTrack = []
  _px_fin = [(18, 40), (533, 40), (1053, 40)]
  _col_fin = [250, 213, 113] #BGR
  _col_margin = 15
  _flag_fin = False
    
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

#    x = random.randint(self._X[0], self._Y[0])
#    y = random.randint(self._X[1], self._Y[1])
    x = 412
    y = 1600
    cmd = cmdf % {'x': x, 'y': y}
    self.intoMacro(cmd)


  ##
  #
  ##
  def swipeEvent(self, pos=None):
    if self._R < 7 :
      return
    self.swipeSimple()
#    self.swipeRandom(pos)

  def swipeSimple(self):
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
sendevent /dev/input/event5 1 330 0
sendevent /dev/input/event5 0 2 0
sendevent /dev/input/event5 0 0 0
"""[1:-1]
    pattern = [((508, 1544), (497, 1656)),
               ((470, 1548), (535, 1616)),
               ((537, 1544), (497, 1609)),
               ((462, 1632), (353, 1600)),
               ((527, 1655), (708, 1629))]
    p  = random.randint(0, len(pattern)-1)
    cmd = cmdf % {'x1': pattern[p][0][0], 'y1': pattern[p][0][1], 'x2': pattern[p][1][0], 'y2': pattern[p][1][1]}
    self.intoMacro(cmd)

    
    
  def swipeRandom(self, pos=None):
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
      self.swipeRandom({'x': x2, 'y': y2})
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
    if not self._flag_fin:
      return False
    
    img = cv2.imread(self.screenShot)
    for yx in self._px_fin:
      pixelBGR = img[yx[1], yx[0]]
      if not self.compareColor(pixelBGR):
        return False
    return True      
#      print pixelBGR
#      img[yx[1], yx[0]] = [0, 0, 0]

#    cv2.imshow("Show Image", img)
#    cv2.waitKey(0)
#    cv2.destroyAllWindows()

  def finish(self):
    print 'battle finished!'
    self._P.kill()
    exit()
    
  def compareColor(self, col):
    b = self._col_fin[0] - col[0]
    if abs(b) > self._col_margin:
      return False
    g = self._col_fin[1] - col[1]
    if abs(g) > self._col_margin:
      return False
    r = self._col_fin[2] - col[2]
    if abs(r) > self._col_margin:
      return False
    return True
    

    
  def genRNum(self):
    self.genSRNum()
    self._R = random.randint(0, 10)
    
  def genSRNum(self):
    self._SR = random.randint(7, 10)

  def takeScreenShot(self):
    if self._R >= 2:
      return
    
    self._flag_fin = True
        
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
    self._flag_fin = False
    time.sleep(5)

  def doMacro(self):
    self.battleStart()
    self._P = subprocess.Popen(['adb', 'shell', 'sh /sdcard/%(macro)s' % {'macro': self.macroName}])

  def onLoop(self):
    if self._P.poll() is 0:
      print 'loop!!'
      self._P = subprocess.Popen(['adb', 'shell', 'sh /sdcard/%(macro)s' % {'macro': self.macroName}])

Puni = Puni()
Puni.makeMacro()
Puni.pushMacro()
Puni.doMacro()



while (1):
  Puni.onLoop()
  Puni.genRNum()
  Puni.takeScreenShot()
  if Puni.isFinished():
    Puni.finish()
  
  time.sleep(1)
  
