#!/usr/bin/python
__doc__ = """{f}

Usage:
    {f} [-l | --left] [-r | --right] [-x <x_coordinate>] [-y <y_coordinate>]
    {f} -h | --help

Options:
    -l, --left          search an enemy from left to right
    -r, --right         search an enemy from right to left
    -x <X_COORDINATE>   x coordinate for an enemy
    -y <Y_COORDINATE>   y coordinate for an enemy
    -h --help           Show this screen and exit.
""".format(f=__file__)

from docopt import docopt

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
  _img_playButton = '%s/img/play_button.png' % DIR
  _img_noSoul = '%s/img/soul_0_gray.png' % DIR
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
  _max_soul = 30
  _cols_map = [(246, 202, 93), (246, 202, 93)] #BGR  
  _col_margin = 15
  _flag_fin = False
  _my_yokais = [(175, 614), (373, 558), (590, 540), (801, 560), (1019, 616)]
  img = []
  _search_direction = 2  # 2->random, 1->LtoR, 0->RtoL
  _search_xy = None # search by xy coordinate 
  _FSM_BATTLE = 1  
  _FSM_RESULT = 2
  _FSM_LOOSE = 3

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

  def onBattleFinish(self):
    logger.info('battle finished!')
    self._P.kill()
#    self.goToMap()
#    self.sendSoul()

  def _back(self):
    cmd = 'adb shell input keyevent 4'
    self.execute(cmd)

  def _ok(self):
    self.touch(540, 1000)
    self.touch(540, 1100)
    self.touch(540, 1200)
    self.touch(540, 1300)
    self.touch(540, 1400)
    self.touch(540, 1500)
    
  def goToMap(self, src=None):
    if self.isInMap():
      logger.info('already in map')
      return
    
    if not src:
      method = self._back
    else:
      method = self._ok
    
    for i in range(0, 6):
      time.sleep(4)      
      if self.isInMap():
        logger.info('return to map')
        return
      method()
    
    
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
    time.sleep(0.5)
    self.touch(self._my_yokais[num][0], self._my_yokais[num][1])
    logger.info( 'do special #%d' % num )
    time.sleep(0.5)

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
    if self._search_xy:
      self.touch(self._search_xy['x'], self._search_xy['y'])
      time.sleep(4)
      return
    
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
    playButton = cv2.imread(self._img_playButton)
    res = cv2.matchTemplate(img, playButton, cv2.TM_SQDIFF)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    if min_val < 540000000:
      return True
    logger.debug('waiting template match', min_val)
    return False

  def isNoSoul(self):
    Puni.takeScreenShot()
    img = cv2.imread(self.screenShot, cv2.IMREAD_GRAYSCALE)   
    
    method = cv2.TM_CCOEFF
    needle  = cv2.imread(self._img_noSoul, cv2.IMREAD_GRAYSCALE)
    w, h = needle.shape[::-1]
    res = cv2.matchTemplate(img, needle, method)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
#    print (min_val, max_val, min_loc, max_loc)

    if max_val > 26210000 and max_val < 26220000:
      logger.warning('no soul template match', (min_val, max_val, min_loc, max_loc))
      return True
    
  def sendSoul(self):
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

  def isAlive(self):
    ret = subprocess.check_output(['adb', 'shell', 'ps', 'com.Level5.YWP'])
    if ret.find('com.Level5.YWP') > -1:
      return True
    return False

    
  def startApp(self):
    logger.info('starting app')
    i=0
    subprocess.call(['adb', 'shell', 'am', 'start', '-n', 'com.Level5.YWP/com.example.sgf.MainActivity'])
    while (i<10):
      if self.isAlive():
        break
      time.sleep(1)
      i+=1
    time.sleep(10)
    self.touch(540, 960)
    time.sleep(4)
    self.touch(540, 960)
    time.sleep(4)
    self.touch(780, 1650)
    time.sleep(10)



class PuniFSM:
  def __init__(self, Puni):
    self.Puni = Puni
    
  def on_init(self, e):
    logging.info('fsm:init')
    if not self.Puni.isAlive():
      logging.info('Puni is not running')
      self.Puni.startApp()
      
      if not self.Puni.isAlive():
        self.panic('Puni is never2 running')
  
      
    self.Puni.goToMap()
    if not self.Puni.isInMap():
      self.Puni.goToMap(src=self.Puni._FSM_LOOSE)
    
  def on_map(self, e):
    logging.info('fsm:map')

  def on_search(self, e):
    logging.info('fsm:search')
    i=0
    if self.Puni.isNoSoul():
      self.panic('no soul')
      return
    
    while (i < 3):
      self.Puni.searchEnemy(i)
      i += 1
  
    
  def on_waiting(self, e):
    logging.info('fsm:waiting')
    if not self.Puni.isInBattleWaiting():
      self.panic('not in battle waiting')
    
  def on_fight(self, e):
    logging.info('fsm:fight')
    self.Puni.doMacro()

    i = 0  
    while (i<150):
      self.Puni.onLoop()
      self.Puni.genRNum()
      self.Puni.takeScreenShot()
#      self.Puni.checkSpecialGage()
      if Puni.isFinished():
        return
      time.sleep(0.8)
      i+=1
      
    self.panic('battle timeout')
    

  def on_battle(self, e):
    logging.info('fsm:battle')
    self.Puni.battleStart()
    
  def on_result(self, e):
    logging.info('fsm:result')
    self.Puni.onBattleFinish()
    self.Puni.goToMap(src=self.Puni._FSM_RESULT)

  def on_finish(self, e):
    logging.info('fsm:finish')
    exit()
    
  def on_ranking(self, e):
    logging.info('fsm:ranking')
    self.Puni.sendSoul()
    
  def panic(self, msg):
    logging.error(msg)
    exit()

def parse(Puni):
  args = docopt(__doc__)
  if args['--left']:
    Puni._search_direction = 1
  elif args['--right']:
    Puni._search_direction = 0
  elif args['-x'] and args['-y']:
    Puni._search_xy = {'x': int(args['-x']), 'y': int(args['-y'])}

    
if __name__ == "__main__":
  Puni = Puni()
  args = parse(Puni)

#  if Puni.isNoSoul():
#    print 'no soul'
#  exit()

  PFSM = PuniFSM(Puni)
  fsm = Fysom({ 'initial': 'init',
                'events': [
                  {'name': 'goToMap', 'src': 'init', 'dst': 'map'},
                  {'name': 'goToMap', 'src': 'battle_waiting', 'dst': 'map'},
                  {'name': 'goToMap', 'src': 'result', 'dst': 'map'},
                  {'name': 'goToMap', 'src': 'ranking', 'dst': 'map'},
                  {'name': 'searchEnemy', 'src': 'map', 'dst': 'search'},
                  {'name': 'waiting', 'src': 'search', 'dst': 'battle_waiting'},
                  {'name': 'fight', 'src': 'battle_waiting', 'dst': 'battle'},
                  {'name': 'showResult', 'src': 'battle', 'dst': 'result'},
                  {'name': 'sendSoul', 'src': 'map', 'dst': 'ranking'},
                  {'name': 'panic', 'src': '*', 'dst': 'error'},
                  {'name': 'exit', 'src': 'map', 'dst': 'finish'}
                  ],
                'callbacks': {
                  'oninit': PFSM.on_init,
                  'onmap': PFSM.on_map,
                  'onsearchEnemy': PFSM.on_search,
                  'onbattle_waiting': PFSM.on_waiting,
                  'onfight': PFSM.on_fight,
                  'onbattle': PFSM.on_battle,                  
                  'onranking': PFSM.on_ranking,                  
                  'onresult': PFSM.on_result,                  
                  'onfinish': PFSM.on_finish,
              }})
  fsm.goToMap()
  if random.randint(0, 20) is 0:
    fsm.sendSoul()
    fsm.goToMap()    
    fsm.exit()
  fsm.searchEnemy()
  fsm.waiting()
  fsm.fight()
  fsm.showResult()
  fsm.goToMap()
#  fsm.sendSoul()
#  fsm.goToMap()
  fsm.exit()
  exit()
  

#  Puni.getPixColor([(175, 614), (373, 558), (590, 540), (801, 560), (1019, 616)], False)
#  exit()
#  Puni.goToMap()
#  exit()
#  Puni.sendSoul()
