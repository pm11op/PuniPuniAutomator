#!/usr/bin/python
import os, random, time, subprocess, cv2
from PIL import Image
from datetime import datetime
from fysom import Fysom

DIR = os.path.dirname(os.path.realpath(__file__))

from logging import getLogger,StreamHandler,DEBUG
import logging.config
logging.config.fileConfig('%s/logging.conf' % DIR)

logger = getLogger(__name__)



class Puni:
  _X = (30, 1037)
  _Y = (1030, 1550)
  swipeLength = 50
  macroNum = 300
  screenShot = '%s/img/ss.png' % DIR
  screenShotLogDir = '%s/img/ss/' % DIR
  screenShotLogName = '%s.png'
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
  _px_map = [(321, 1722), (555, 1722)]
  _px_soul = (450, 1619)
  _max_soul = 10
  _cols_map = [(246, 202, 93), (246, 202, 93)] #BGR  
  _col_margin = 15
  _flag_fin = False
  _my_yokais = [(175, 614), (373, 558), (590, 540), (801, 560), (1019, 616)]
  img = []
  _search_direction = 2  # 2->random, 1->LtoR, 0->RtoL
  _FSM_BATTLE = 1  
    
  def execute(self, cmd):
    logger.debug(cmd) 
    os.system(cmd)  


  def touch(self, x, y):
    cmdf = "adb shell input touchscreen tap %(x)d %(y)d"
    cmd = cmdf % {'x': x, 'y': y}
    self.execute(cmd)

  def swipe(self, pos=None):
    cmdf = """
adb shell sendevent /dev/input/event5 1 330 1
adb shell sendevent /dev/input/event5 3 58 1
adb shell sendevent /dev/input/event5 3 53 %(x1)d
adb shell sendevent /dev/input/event5 3 54 %(y1)d
adb shell sendevent /dev/input/event5 0 2 0
adb shell sendevent /dev/input/event5 0 0 0
adb shell sendevent /dev/input/event5 3 53 %(x2)d
adb shell sendevent /dev/input/event5 3 54 %(y2)d
adb shell sendevent /dev/input/event5 0 2 0
adb shell sendevent /dev/input/event5 0 0 0
adb shell sendevent /dev/input/event5 3 53 %(x2)d
adb shell sendevent /dev/input/event5 3 54 %(y2)d
adb shell sendevent /dev/input/event5 0 2 0
adb shell sendevent /dev/input/event5 0 0 0
adb shell sendevent /dev/input/event5 3 53 %(x3)d
adb shell sendevent /dev/input/event5 3 54 %(y3)d
adb shell sendevent /dev/input/event5 0 2 0
adb shell sendevent /dev/input/event5 0 0 0
adb shell sendevent /dev/input/event5 3 53 %(x3)d
adb shell sendevent /dev/input/event5 3 54 %(y3)d
adb shell sendevent /dev/input/event5 0 2 0
adb shell sendevent /dev/input/event5 0 0 0
adb shell sendevent /dev/input/event5 3 53 %(x4)d
adb shell sendevent /dev/input/event5 3 54 %(y4)d
adb shell sendevent /dev/input/event5 0 2 0
adb shell sendevent /dev/input/event5 0 0 0
adb shell sendevent /dev/input/event5 3 53 %(x4)d
adb shell sendevent /dev/input/event5 3 54 %(y4)d
adb shell sendevent /dev/input/event5 0 2 0
adb shell sendevent /dev/input/event5 0 0 0
adb shell sendevent /dev/input/event5 3 53 %(x5)d
adb shell sendevent /dev/input/event5 3 54 %(y5)d
adb shell sendevent /dev/input/event5 0 2 0
adb shell sendevent /dev/input/event5 0 0 0
adb shell sendevent /dev/input/event5 1 330 0
adb shell sendevent /dev/input/event5 0 2 0
adb shell sendevent /dev/input/event5 0 0 0
"""[1:-1]
    args = {'x1': pos['x1'], 'y1': pos['y1'], 'x5': pos['x2'], 'y5': pos['y2']}
    for i in range(2, 5):
      args['x'+str(i)] = args['x'+str(i-1)] + (pos['x2']-pos['x1'])/4
      args['y'+str(i)] = args['y'+str(i-1)] + (pos['y2']-pos['y1'])/4
    cmd = cmdf % args      
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
    logger.info('battle finished!')
    self._P.kill()
    self.goToMap()
    self.sendSoul()

  def goToMap(self):
    for i in range(0, 6):
      time.sleep(4)      
      if self.isInMap():
        logger.info('return to map')
        return
      self.touch(540, 1000)
      self.touch(540, 1100)
      self.touch(540, 1200)
      self.touch(540, 1300)
      self.touch(540, 1400)
      self.touch(540, 1500)
 
    
    
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

    file = self.screenShotLogDir + self.screenShotLogName % datetime.now().strftime('%Y%m%d%H%M%S')
    Image.open(self.screenShot).resize((270, 480)).save(file)


  def battleStart(self):
    self.touch(650, 1300)
    self._flag_fin = False
    time.sleep(8)

  def doSpecial(self, num):
    self.touch(self._my_yokais[num][0], self._my_yokais[num][1])
    logger.info( 'do special #%d' % num )

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
      logger.info('loop!!')
      self.doMacro()

    return
  
  def searchEnemy(self, num):
    direction = self._search_direction
    if self._search_direction is 2:
      direction = random.randint(0,1)
      
    if direction is 1:
      for i in range(1, 9):
        self.touch(i*100, 900 + num * 100)
    else:
      for i in range(1, 10):
        self.touch(1080 - i*100, 900 + num * 100)

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
    if self._R >= 1:
      return
    Puni.touch(self._px_soul[0], self._px_soul[1])
    time.sleep(2)
    
    logger.info('start sending soul')
    
    for i in range(0, self._max_soul):    
      # send soul
      Puni.touch(830, 640)
      Puni.touch(830, 740)
      Puni.touch(830, 840)
      Puni.touch(830, 940)
      Puni.touch(830, 1040)
      Puni.touch(830, 1140)
      Puni.touch(830, 1240)
      time.sleep(2)

      #OK
      Puni.touch(540, 1000)
      Puni.touch(540, 1050)
      Puni.touch(540, 1100)      
      time.sleep(2)    
      Puni.swipe({'x1': 540, 'y1': 800, 'x2': 540, 'y2': 722})
    
      
    time.sleep(2)
    Puni.touch(100, 1700)
    logger.info('end sending soul')

class PuniFSM:
  def init(self, e):
    logging.info('init')

  def finish(self, e):
    logging.info('finish')
    exit()
    
if __name__ == "__main__":
  Puni = Puni()
  PFSM = PuniFSM()
  fsm = Fysom({ 'initial': 'init',
                'events': [
                  {'name': 'goToMap', 'src': 'init', 'dst': 'map'},
                  {'name': 'goToMap', 'src': 'battle_waiting', 'dst': 'map'},
                  {'name': 'goToMap', 'src': 'result', 'dst': 'map'},
                  {'name': 'goToMap', 'src': 'ranking', 'dst': 'map'},
                  {'name': 'searchEnemy', 'src': 'map', 'dst': 'battle_waiting'},
                  {'name': 'fight', 'src': 'battle_waiting', 'dst': 'battle'},
                  {'name': 'showResult', 'src': 'battle', 'dst': 'result'},
                  {'name': 'sendSoul', 'src': 'map', 'dst': 'ranking'},
                  {'name': 'panic', 'src': '*', 'dst': 'error'},
                  {'name': 'exit', 'src': 'map', 'dst': 'finish'}
                  ],
                'callbacks': {
                  'oninit': PFSM.init,
                  'onfinish': PFSM.finish,
              }})
  fsm.goToMap()
  fsm.searchEnemy()
  fsm.fight()
  fsm.showResult()
  fsm.goToMap(Puni._FSM_BATTLE)
  fsm.sendSoul()
  fsm.goToMap()
  fsm.exit()
  exit()
  

#  Puni.getPixColor([(175, 614), (373, 558), (590, 540), (801, 560), (1019, 616)], False)
#  exit()
#  Puni.goToMap()
#  exit()
#  Puni.sendSoul()


  
  if Puni.isInMap():
    logger.info('in map')
    i = 0
    while (i < 3):
      Puni.searchEnemy(i)
      i += 1
  
  if not Puni.isInBattleWaiting():
    logger.info('not in battle waiting')
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
      exit()
    time.sleep(2)
