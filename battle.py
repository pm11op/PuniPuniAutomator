#!/usr/bin/python
import os, random, time, subprocess, cv2

DIR = os.path.dirname(os.path.realpath(__file__))

class Puni:
  debug = 1
  _X = (30, 1037)
  _Y = (1030, 1550)
  swipeLength = 50
  macroNum = 300
  screenShot = '%s/img/ss.png' % DIR
  playButton = '%s/img/play_button.png' % DIR
  macroPath = '%s/adb/' % DIR
  macroName = 'macro.sh'
  _R = 0
  _SR = 0
  _P = None
  _cmd = []
  _macro = []
  _px_fin = [(18, 40), (533, 40), (1053, 40)]
  _col_fin = (250, 213, 113) #BGR
  _cols_special = [(62, 251, 226), (185, 254, 230), (78, 247, 218), (47, 255, 196), (151, 255, 237), (211, 255, 245), (57, 255, 214)] #BGR
  _col_margin_special = 25  
  _px_map = [(60, 1719), (218, 1719), (990, 1719)]
  _px_soul = (450, 1619)
  _max_soul = 30
  _cols_map = [(87, 225, 255), (87, 225, 255), (247, 203, 95)] #BGR  
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

  # debugging purpose
  def getPixColor(self, xys=[(0, 0)], takeSS=True):
    if takeSS:
      Puni.takeScreenShot()
    img = cv2.imread(self.screenShot)   
    for xy in xys:
      print img[xy[1], xy[0]]
      img[xy[1], xy[0]] = [0, 0, 0]
      
    cv2.imwrite('%s/img/tmp.png' % DIR, img)
      

  def isInMap(self):
    Puni.takeScreenShot()
    img = cv2.imread(self.screenShot)    
    for i, yx in enumerate(self._px_map):
      pixelBGR = img[yx[1], yx[0]]
      if not self.compareColor(self._cols_map[i], pixelBGR):
        return False
    return True      

  
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
    self.goToMap()

  def goToMap(self):
    for i in range(0, 6):
      if self.isInMap():
        exit()
      
      self.touch(540, 1000)
      self.touch(540, 1100)
      self.touch(540, 1200)
      self.touch(540, 1300)
      self.touch(540, 1400)
      self.touch(540, 1500)
      time.sleep(4)
    
    
  def compareColor(self, col1, col2, margin=None):
    if not margin:
      margin = self._col_margin
    b = col1[0] - col2[0]
    if abs(b) > margin:
      return False
    g = col1[1] - col2[1]
    if abs(g) > margin:
      return False
    r = col1[2] - col2[2]
    if abs(r) > margin:
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
        if self.compareColor(color, pixelBGR, self._col_margin_special):
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
  
  def searchEnemy(self, num):
    for i in range(1, 9):
      self.touch(i*100, 900 + num * 100)

  def isInBattleWaiting(self):
    Puni.takeScreenShot()
    img = cv2.imread(self.screenShot)   
    playButton = cv2.imread(self.playButton)
    res = cv2.matchTemplate(img, playButton, cv2.TM_SQDIFF)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    if min_val < 540000000:
      return True
    return False


  def sendSoul(self):
    Puni.touch(self._px_soul[0], self._px_soul[1])
    time.sleep(1)
    Puni.touch(self._px_soul[0], self._px_soul[1])
    Puni.touch(830, 640)
    time.sleep(1)
    Puni.touch(540, 1200)
    
#    for i in range(0, self._max_soul):
      
    exit()
      
if __name__ == "__main__":
                        
  Puni = Puni()

#  Puni.getPixColor([(175, 614), (373, 558), (590, 540), (801, 560), (1019, 616)], False)
#  exit()
#  Puni.goToMap()
#  exit()
  Puni.sendSoul()
  
  if Puni.isInMap():
    print 'in map'
    i = 0
    while (i < 3):
      Puni.searchEnemy(i)
      i += 1
  
  if not Puni.isInBattleWaiting():
    print 'not in battle waiting'
    exit()
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
