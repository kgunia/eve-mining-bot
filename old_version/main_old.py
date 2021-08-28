import pyautogui, random, time
undock = './res/undock.png'

found = False
CORR = 10

class Bobber():
    img = './res/bobber.png'
    founded = False
    targeted = False


    def find(self):
        self.position = pyautogui.locateOnScreen(self.img, confidence=0.7)
        if self.position:
            self.founded = True
        else:
            self.position = False

    def target(self):
        corr = 10
        pos = pyautogui.center(self.position)
        x = random.uniform(pos.x - corr, pos.x + corr)
        y = random.uniform(pos.y - corr, pos.y + corr)
        t = random.uniform(0.1, 0.2)
        pyautogui.moveTo(x, y, t)
        self.targeted = True

    def wait(self):
        return pyautogui.locateOnScreen(self.img, confidence=0.7)

    def catch(self):
        pyautogui.keyDown('shift')
        pyautogui.click(button='left')
        pyautogui.keyUp('shift')
        time.sleep(random.uniform(1, 2))
        pyautogui.press('=')
        time.sleep(random.uniform(1, 2))
        self.founded = False
        self.targeted = False

bobber = Bobber()



def undock():
    undock = './res/undock.png'
    position = pyautogui.locateOnScreen(undock, confidence=0.7)
    center = pyautogui.center(position)
    pyautogui.moveTo(center.x, center.y, 1)
    pyautogui.click(button='left')
    time.sleep(12)


rens = './res/rens_moon8.png'
rafinery = './res/rafinery.png'
def dock(station):
    dock = './res/dock.png'
    position = pyautogui.locateOnScreen(station, confidence=0.7)
    center = pyautogui.center(position)
    pyautogui.moveTo(center.x, center.y, 1)
    pyautogui.click(button='right')
    position = pyautogui.locateOnScreen(dock, confidence=0.7)
    center = pyautogui.center(position)
    pyautogui.moveTo(center.x, center.y, 1)
    pyautogui.click(button='left')
    time.sleep(60)

def afterburner():
    pyautogui.keyDown('alt')
    pyautogui.keyDown('f1')
    pyautogui.keyUp('alt')
    pyautogui.keyUp('f1')

def jump_to_asteroids():
    asteroid_belt = './res/asteroid_belt.png'
    position = pyautogui.locateOnScreen(asteroid_belt, confidence=0.7)
    center = pyautogui.center(position)
    pyautogui.moveTo(center.x, center.y, 1)
    pyautogui.click(button='right')
    warp_to_0 = './res/warp_to_0.png'
    position = pyautogui.locateOnScreen(warp_to_0, confidence=0.7)
    center = pyautogui.center(position)
    pyautogui.moveTo(center.x, center.y, 1)
    pyautogui.click(button='left')
    time.sleep(45)

def approach_to_asteroid():
    overview = './res/overview.png'
    position = pyautogui.locateOnScreen(overview, confidence=0.6)
    center = pyautogui.center(position)
    pyautogui.moveTo(center.x, center.y+70, 1)

    pyautogui.click(button='right')

    aproach = './res/aproach.png'
    position = pyautogui.locateOnScreen(aproach, confidence=0.7)
    center = pyautogui.center(position)
    pyautogui.moveTo(center.x, center.y, 1)
    pyautogui.click(button='left')
    time.sleep(30)

def lock():
    lock = './res/lock.png'
    position = pyautogui.locateOnScreen(lock, confidence=0.7)
    center = pyautogui.center(position)
    pyautogui.moveTo(center.x, center.y, 1)
    pyautogui.click(button='left')
    time.sleep(5)

def mine():
    pyautogui.keyDown('f1')
    pyautogui.keyUp('f1')
    pyautogui.keyDown('f2')
    pyautogui.keyUp('f2')

def still_mining():
    still_mining = './res/still_mining.png'
    return pyautogui.locateOnScreen(still_mining, confidence=0.7)

def lauch_drones():
    time.sleep(5)
    pyautogui.keyDown('shift')
    pyautogui.keyDown('f')
    pyautogui.keyUp('shift')
    pyautogui.keyUp('f')
    time.sleep(5)

def return_drones():
    pyautogui.keyDown('shift')
    pyautogui.keyDown('r')
    pyautogui.keyUp('shift')
    pyautogui.keyUp('r')
    time.sleep(10)

def is_full():
    inventory_search = './res/inventory_search.png'
    position = pyautogui.locateOnScreen(inventory_search, confidence=0.7)
    center = pyautogui.center(position)
    pyautogui.moveTo(center.x, center.y, 1)
    im = pyautogui.screenshot()

    print(im.getpixel((int(position.left-5), int(position.top+10))))
    print (pyautogui.pixelMatchesColor(int(position.left - 5), int(position.top + 10), (6, 74, 95), tolerance=20))
    return pyautogui.pixelMatchesColor(int(position.left-5), int(position.top+10), (6, 74, 95), tolerance=20)


def move_ore_to_item_hangar():
    ore_hold = './res/ore_hold.png'
    position = pyautogui.locateOnScreen(ore_hold, confidence=0.7)
    center = pyautogui.center(position)
    pyautogui.moveTo(center.x, center.y, 1)
    pyautogui.click(button='left')
    pyautogui.moveTo(center.x+120, center.y, 1)
    pyautogui.click(button='left')
    pyautogui.keyDown('ctrl')
    pyautogui.keyDown('a')
    pyautogui.keyUp('ctrl')
    pyautogui.keyUp('a')


    item_hangar = './res/item_hangar.png'
    position = pyautogui.locateOnScreen(item_hangar, confidence=0.7)
    center = pyautogui.center(position)
    pyautogui.mouseDown(button='left')
    pyautogui.moveTo(center.x, center.y, 1)
    pyautogui.mouseUp(button='left')

def is_docked():
    undock = './res/undock.png'
    return pyautogui.locateOnScreen(undock, confidence=0.7)

statuses = {
    0: 'station',
    1: 'space',
    2: 'asteroid belt',
    3: 'mining'

}

status = 0
cargo = 0

time.sleep(3)
while True:
    if is_docked():
        print('przenoszę rudę do hangaru')
        # move_ore_to_item_hangar()
        print('opuszczam stację')
        undock()
    else:
        print('skaczę do pasa asteroid')
        jump_to_asteroids()
        print('wypuszczam drony')
        lauch_drones()
        print('włączam afterburner')
        afterburner()
        while not is_full():
            print('sprawdzam czy ładownia jest pełna')
            if not still_mining():
                print('podlatuję do asteroidy')
                approach_to_asteroid()
                print('celuję')
                lock()
                print('zaczynam kopać')
                mine()

        print('cofam drony')
        return_drones()
        print('wracam na stację')
        dock(rafinery)


# jump_to_asteroids()
# time.sleep(5)
# afterburner()
# approach_to_asteroid()
#
# lock()
# mine()
#
# while still_mining():
#     print('kopie')
#     time.sleep(10)

# lauch_drones()
#
# if is_full():
#     return_drones()
#     dock(rafinery)



# while True:

    # print("Szukam spławika")
    # bobber.find()
    # if bobber.founded:
    #     print("Spławik znaleziony")
    #     bobber.target()
    #     if bobber.targeted:
    #         print("Spławik namierzony")
    #         while bobber.wait():
    #             print("Czekam na branie")
    #         print("łapię!")
    #         bobber.catch()



    # if pos:
    #     pos = pyautogui.center(pos)
    #     x = random.uniform(pos.x - corr, pos.x + corr)
    #     y = random.uniform(pos.y - corr, pos.y + corr)
    #     t = random.uniform(0.1, 0.2)
    #     time.sleep(random.uniform(1, 2))
    #     pyautogui.moveTo(x, y, t)
    #
    # else:
    #     pyautogui.keyDown('shift')
    #     pyautogui.click(button='left')
    #     pyautogui.keyUp('shift')
    #     time.sleep(random.uniform(1, 2))
    #     pyautogui.press('=')
