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
  _col_fin = (250, 213, 113) #BGR
  _cols_special = [(62, 251, 226), (185, 254, 230)] #BGR  
  _col_margin = 15
  _flag_fin = False
  _my_yokais = [(175, 614), (373, 558), (590, 540), (801, 560), (1019, 616)]
  img = []
    
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
    

  def isFinished(self):
    if not self._flag_fin or len(self.img) is 0:
      return False
    
    for yx in self._px_fin:
      pixelBGR = self.img[yx[1], yx[0]]
      if not self.compareColor(self._col_fin, pixelBGR):
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
    
  def compareColor(self, col1, col2):
    b = col1[0] - col2[0]
    if abs(b) > self._col_margin:
      return False
    g = col1[1] - col2[1]
    if abs(g) > self._col_margin:
      return False
    r = col1[2] - col2[2]
    if abs(r) > self._col_margin:
      return False
    return True
    

    
  def genRNum(self):
    self._R = random.randint(0, 10)
    

  def takeScreenShot(self):
#    if self._R >= 2:
#      return
    
    self._flag_fin = True
        
    cmd1 = 'adb shell screencap -p /sdcard/screen.png'
    cmd2 = 'adb pull /sdcard/screen.png %(imgpath)s' % {'imgpath': self.screenShot}
    self.execute(cmd1)
    self.execute(cmd2)


  def battleStart(self):
    self.touch(650, 1300)
    self._flag_fin = False
    time.sleep(8)

  def doSpecial(self, num):
    self.touch(self._my_yokais[num][0], self._my_yokais[num][1])
    print 'do special #%d' % num

  def checkSpecialGage(self):
    if len(self.img) is 0:
      return
    
    for i, yokai in enumerate(self._my_yokais):
      pixelBGR = self.img[yokai[1], yokai[0]]
      for color in self._cols_special:
        if self.compareColor(color, pixelBGR):
          self.killMacro()        
          self.doSpecial(i)
          self.doMacro()
          return
        
    
  def doMacro(self):
    self._P = subprocess.Popen(['adb', 'shell', 'sh /sdcard/%(macro)s' % {'macro': self.macroName}])
    
  def killMacro(self):
    self._P.kill()
      
  def onLoop(self):
    if self._flag_fin:
      self.img = cv2.imread(self.screenShot)
  
    if self._P.poll() is 0:
      print 'loop!!'
      self.doMacro()

    return
  
Puni = Puni()
Puni.battleStart()
Puni.doMacro()



while (1):
  Puni.onLoop()
  Puni.genRNum()
  Puni.takeScreenShot()
  Puni.checkSpecialGage()
  if Puni.isFinished():
    Puni.finish()
  
  time.sleep(2)
