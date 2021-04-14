import win32gui, win32com.client, pyautogui, logging, pymsgbox, sys, json, pyperclip, time, keyboard

from time import sleep


# CONFIG
LOG_MESSAGE_FORMAT = '[%(asctime)s] %(levelname)s - %(message)s'
LOG_DATE_FORMAT = '%H:%M:%S'
DEFAULT_DELAY = 0.1
MOUSE_MOVEMENT_TIME = 0.2
MOUSE_MOVEMENT_TYPE = pyautogui.easeOutQuad
SHIP_ALIGN_TIME = 4.79
APP_NAME = 'EVE Mining Bot'
WINDOW_MAXIMIZED = False
ASTEROID_BELT_NAME = False

# Set pause after pyautogui action
pyautogui.PAUSE=0.1
pyautogui.FAILSAFE = False

# Initialize logging
logging.basicConfig(format=LOG_MESSAGE_FORMAT, datefmt=LOG_DATE_FORMAT, level=logging.WARNING)

# Load resources
with open('resources.json') as file:
    RESOURCES = json.load(file)

for key in RESOURCES:
    resource = RESOURCES[key]
    resource['visible'] = None

def wait(event, waiting_time=30):
    start_time = time.time()
    while not event:
        current_time = time.time()
        working_time = current_time - start_time / 60
        print('wait..')
        # if working_time > waiting_time:
        #     text = f'Coś jest nie tak, czekam już ponad {waiting_time} sekund!'
        #     pymsgbox.alert(text=text, title=APP_NAME)
    return True

def main():


    asteroid_belts = []

    # MAIN LOOP
    while game.is_running():


        if keyboard.is_pressed('esc') or pilot.locate('quit_game'):
            text = 'Wszedłeś w ustawienia gry, zawiesiłem bota.'
            confirm = pymsgbox.confirm(text=text, title=APP_NAME)
            if confirm == 'Cancel': break

        if not game.is_active(): game.bring_to_front()

        if not game.init:
            instance = pilot.locate_all('asteroid_belt')
            for object in instance:
                asteroid_belts.append(AsteroidBelt(object))

            if ASTEROID_BELT_NAME:
                for asteroid_belt in asteroid_belts:
                    asteroid_belt.name = pilot.get_asteroid_belt_name(asteroid_belt)


            if len(asteroid_belts) > 0:
                game.init = True
                asteroid_belts[0].empty = True

        if not ship.inventory_full: ship.is_inventory_full()

        if ship.is_warping():
            ship.afterburner = False
            
        elif ship.is_on_station():
            print('on station')
            print(ship.inventory_full)
            if ship.inventory_full:
                print(pilot.last_action)
                if pilot.last_action != 'unload_cargo':
                    print('unload_cargo')
                    if wait(pilot.unload_cargo()):
                        print('unload_cargo True')
                        ship.inventory_full = False
                    else:
                        print('unload_cargo True')

            else:
                if pilot.last_action != 'undock': wait(pilot.undock())
            
        elif ship.is_in_space():
            print('in space')
            if ship.inventory_full:
                if ship.is_drones_in_space():
                    if pilot.last_action != 'return_drones': wait(pilot.return_drones())
                elif pilot.last_action != 'dock_to_station':
                    if not pilot.locate('asteroid_save'):
                        wait(pilot.save_location())
                    else:
                        wait(pilot.dock_to_station())
            
            elif ship.is_on_asteroid_belt():
                print('on asteroid belt')
                if not ship.is_drones_in_space():

                    if pilot.last_action != 'launch_drones':  wait(pilot.launch_drones())
                elif not ship.afterburner:
                    print(ship.afterburner)
                    if pilot.last_action != 'launch_afterburner':
                        ship.afterburner = pilot.launch_afterburner()
                        print(ship.afterburner)
                elif ship.is_digging():

                    miners = pilot.locate_all('miner')
                    counter = 0
                    for miner in miners: counter += 1
                    if counter == 1:
                        pyautogui.press('f1')

                    if pilot.locate('asteroid_save'):
                        wait(pilot.remove_location())
                else:
                    if pilot.last_action == 'start_digging':
                        time.sleep(2)
                    pilot.start_digging()
            elif pilot.last_action != 'dock_to_station':
                print('in unknown position')
                if pilot.locate('asteroid_save'):
                    wait(pilot.warp_to('asteroid_save'))
                elif pilot.last_action != 'warp_to_asteroid_belt':
                    wait(pilot.warp_to_asteroid_belt(asteroid_belts))


        center = pyautogui.center(game.rect)
        pilot.move_to(center)


    text = 'Gra jest wyłączona. Uruchom grę zanim włączysz bota'
    pymsgbox.alert(text=text, title=APP_NAME,button='OK')


    #ship = Ship(pilot)

class InterfaceObject(object):
    inside = False
    outside = False

class Interface(InterfaceObject):
    inventory = InterfaceObject()
    people_and_places = InterfaceObject()

    def check(self, location_type):
        if location_type == 'inside':
            self.inside = True if self.inventory.inside else False
        elif location_type == 'outside':
            self.outside = True if self.inventory.outside else False

class Pilot(object):
    previous_action = None
    current_action = None
    location = None
    location_type = None
    asteroid_belt = None
    asteroid_save = None

    def __init__(self, name):
        self.name = name
        self.game = Game(self.name)
        self.ship = Ship()
        print(f'Witaj {self.name}!')

    def status(self, time):
        print(f'{round(time,2)}, location: {self.location_type}/{self.location}, '
              f'interface[inside:{self.game.interface.inside}, outside:{self.game.interface.outside}]'
              f'cargo_full:{self.ship.cargo_full}, drones_in_space:{self.ship.drones_in_space}, '
              f'asteroid_save:{self.asteroid_save}'
              )

    def run(self):
        start = time.time()
        if self.game.is_running(): # jeżeli gra jest uruchomiona
            if self.game.is_active(): # jeżeli okno gry jest aktywne
                if pilot.locate('menu'):
                    self.location_type, self.location = self.where_i_am() # sprawdź gdzie jest statek
                    if self.location_type and self.location:
                        if self.location_type == 'inside':
                            if self.game.interface.inside:
                                if self.location == 'station':
                                    if self.ship.cargo_full:
                                        self.ship.cargo_full = not self.unload_cargo()
                                    else: self.find_and_click('undock')
                            else:
                                if self.game.interface.inventory.inside:
                                    self.game.interface.check(self.location_type)
                                else: self.game.interface.inventory.inside = self.check_inventory(self.location_type)

                        elif self.location_type == 'outside':
                            if self.game.interface.outside:
                                if self.location != 'warp':
                                    if self.ship.cargo_full:
                                        if self.ship.drones_in_space:
                                            self.hotkey('shift','r')
                                            self.ship.drones_in_space = False

                                        if self.locate('asteroid'):
                                            self.hotkey('alt', 'e')
                                            self.save_location()
                                            self.asteroid_save = True
                                            self.hotkey('alt', 'e')

                                        if self.dock_to_station():
                                            time.sleep(10)

                                        else:
                                            self.move(500,0)
                                            self.click()
                                    elif self.location == 'asteroid_belt':
                                        if self.asteroid_save:
                                            self.remove_location()



                                        if self.locate('miner'):
                                            instance = self.locate_all('miner')
                                            counter = 0
                                            for object in instance:
                                                counter += 1

                                            if counter < 2:
                                                self.press('f1')

                                            self.ship.cargo_full = self.check_cargo()

                                        else:
                                            asteroid = self.locate('asteroid')
                                            if asteroid:

                                                if not self.ship.drones_in_space:
                                                    self.move(500, 0)
                                                    self.click()
                                                    self.hotkey('shift', 'f')
                                                    self.ship.drones_in_space = True

                                                if not self.ship.afterburner:
                                                    self.hotkey('alt','f1')
                                                    self.ship.afterburner = True

                                                pyautogui.press('f1')
                                                time.sleep(0.5)
                                                pyautogui.press('f2')
                                                pyautogui.keyDown('q')
                                                self.find_and_click('asteroid')
                                                pyautogui.keyUp('q')
                                                time.sleep(2)
                                                self.move(0,-50)
                                            else:
                                                if self.asteroid_belt:
                                                    self.asteroid_belt.empty = True
                                                self.warp_to_asteroid_belt()
                                        pass # TODO asteroid belt logic:
                                    elif self.location == 'space':
                                        if self.asteroid_save:
                                            self.find_and_click('asteroid_save','right')
                                            self.find_and_click('warp_to_zero')
                                        else:
                                            self.warp_to_asteroid_belt()

                                else:
                                    self.ship.afterburner = False  # TODO warp logic:
                            else:
                                if self.game.interface.inventory.outside:
                                    self.game.interface.check(self.location_type)
                                else:
                                    if self.check_inventory(self.location_type)\
                                            and self.check_people_and_places()\
                                            and self.check_drones():
                                        self.game.interface.inventory.outside = True
                                    else:
                                        self.game.interface.inventory.outside = False
                        else: pass
                    else: pass
                else: pass
            else: self.game.bring_to_front()
        else: print(f'Gra {self.game.name} jest wyłączona')
        stop = time.time()
        working_time = stop - start
        self.status(working_time)

    def where_i_am(self):
        if self.locate('undock'): return 'inside', 'station'
        elif self.locate('warping'): return 'outside', 'warp'
        elif self.locate('asteroid_belt_1'): return 'outside', 'asteroid_belt'
        elif self.locate('overview'): return 'outside', 'space'
        elif self.locate('overview'): return 'outside', 'space'
        else: return None, None

    def check_inventory(self, location_type):
        inventory = pilot.locate('inventory')
        if inventory:
            ship = pilot.locate('ship')
            if ship:
                ore_hold = pilot.locate('ore_hold')
                if ore_hold:
                    if location_type == 'inside':
                        if pilot.locate('item_hangar'):
                            if pilot.locate('search'):
                                position = self.center(ore_hold)
                                self.move_to(position)
                                self.click()
                                sleep(2)
                                self.ship.cargo_full=self.check_cargo()
                                return True
                            else:
                                return False
                        else:
                            ship_hangar = self.locate('ship_hangar')
                            position = self.center(ship_hangar)
                            self.move_to(position)
                            self.move(-58, 0)
                            self.click()
                    elif location_type == 'outside':
                        if pilot.locate('search'):
                            position = self.center(ore_hold)
                            self.move_to(position)
                            self.click()
                            sleep(2)
                            self.ship.cargo_full=self.check_cargo()
                            return True
                        else:
                            return False
                    else: return False
                else:
                    position = self.center(ship)
                    self.move_to(position)
                    self.move(-18, 0)
                    self.click()
            else:
                position = self.center(inventory)
                self.move_to(position)
                self.move(50, 50)
                self.scroll(500)
        else:
            self.hotkey('alt', 'c')

    def check_people_and_places(self):
        people_and_places = pilot.locate('people_and_places')
        if people_and_places:
            shared_locations = pilot.locate('shared_locations')
            if shared_locations:
                mining_folder = pilot.locate('mining_folder')
                if mining_folder:
                    asteroid_belt = pilot.locate('asteroid_belt')
                    if asteroid_belt:
                        self.asteroid_belts = []
                        instance = pilot.locate_all('asteroid_belt')
                        for object in instance:
                            self.asteroid_belts.append(AsteroidBelt(object))

                        if ASTEROID_BELT_NAME:
                            for asteroid_belt in self.asteroid_belts:
                                asteroid_belt.name = self.get_asteroid_belt_name(asteroid_belt)


                        if self.locate('asteroid_save'):
                            self.remove_location()
                            self.asteroid_save

                        return True
                    else:
                        position = self.center(mining_folder)
                        self.move_to(position)
                        self.click()
                else:
                    position = self.center(shared_locations)
                    self.move_to(position)
                    self.click()
            else:
                position = self.center(people_and_places)
                self.move_to(position)
                self.move(-35, 110)
                self.click()
        else:
            self.hotkey('alt', 'e')

    def check_drones(self):
        drones_in_local_space = pilot.locate('drones_in_local_space')
        if drones_in_local_space:
            drones_in_space_open = pilot.locate('drones_in_space_open')
            if drones_in_space_open:
                idle = self.locate('idle')
                fighting = self.locate('fighting')
                self.ship.drones_in_space = True if idle or fighting else False
                return True
            else:
                position = self.center(drones_in_local_space)
                self.move_to(position)
                self.click()
        else:
            return False

    def get_asteroid_belt_name(self, object):

        self.move_to(object.position)
        self.click('right')
        self.find_and_click('edit_location')

        event = pyautogui.locateOnScreen('./res/dialog_edit_location.png', confidence=0.9)
        wait(event, 0.1)

        self.hotkey('ctrl', 'c')
        self.hotkey('ctrl', 'w')

        clipboard = pyperclip.paste()
        name = clipboard.replace(' ( Asteroid Belt )', '')
        return name

    def remove_location(self):
        if self.find_and_click('asteroid_save', 'right'):
            if self.find_and_click('remove_location'):
                self.find_and_click('yes')
                return True
        return False

    def save_location(self):

        if self.find_and_click('asteroid', 'right'):
            if self.find_and_click('save_location'):
                pyautogui.typewrite('Z_ASTEROID_SAVE')
                folder = self.locate('folder')
                if folder:
                    position = pyautogui.center(folder)
                    self.move_to(position)
                    pyautogui.move(100, 0)

                    pyautogui.leftClick()
                    if self.find_and_click('mining_folder'):
                        if self.find_and_click('in_3_hours'):
                            if self.find_and_click('submit'):

                                return True

        return False

    def send_message(self, message):
        if message != self.last_message:
            self.click('corp_chat')
            pyautogui.press('space')
            pyautogui.typewrite(f'Szefuniu, {message}')
            pyautogui.press('enter')
            self.click('overview')

    def start_digging(self):
        self.last_action = 'start_digging'
        logging.info("pilot.start_digging")

        pyautogui.press('f1')
        pyautogui.press('f2')
        pyautogui.keyDown('q')
        self.click('asteroid')
        pyautogui.keyUp('q')

    def check_cargo(self):
        # self.last_action = 'check_inventory'
        # logging.info("pilot.check_inventory")

        if self.locate('inventory'):
            if self.match('search'):
                return True

        return False

    def launch_drones(self):
        self.last_action = 'launch_drones'
        logging.info('pilot.launch_drones')

        if self.click('drones_in_bay', 'right'):
            if self.click('launch_drones'):
                return True
        return False

    def return_drones(self):
        self.last_action = 'return_drones'
        logging.info('pilot.return_drones')

        if self.click('drones_in_local_space', 'right'):
            if self.click('return_to_drone_bay'):
                return True
        return False

    def launch_afterburner(self):
        self.last_action = 'launch_afterburner'
        logging.info('pilot.launch_afterburner')

        pyautogui.keyDown('alt')
        pyautogui.keyDown('f1')
        pyautogui.keyUp('f1')
        pyautogui.keyUp('alt')

        return True

    def unload_cargo(self):
        self.last_action = 'unload_cargo'
        logging.info('pilot.unload_cargo')

        progress_bar = self.locate('progress_bar')
        if progress_bar:
            position = pyautogui.center(progress_bar)
            if position:
                pyautogui.moveTo(position.x + 50, position.y + 50, MOUSE_MOVEMENT_TIME, pyautogui.easeOutQuad)
                pyautogui.click()
                pyautogui.keyDown('ctrl')
                pyautogui.keyDown('a')
                pyautogui.keyUp('a')
                pyautogui.keyUp('ctrl')
                item_hangar = self.locate('item_hangar')
                if item_hangar:
                    position = pyautogui.center(item_hangar)
                    if position:
                        pyautogui.mouseDown()
                        pyautogui.moveTo(position.x, position.y, MOUSE_MOVEMENT_TIME, pyautogui.easeOutQuad)
                        pyautogui.mouseUp()
                        return True
        return False

    def warp_to_asteroid_belt(self):
        self.last_action = 'warp_to_asteroid_belt'
        logging.info("pilot.warp_to_asteroid_belt")

        for asteroid_belt in self.asteroid_belts:
            if not asteroid_belt.empty:
                self.move_to(asteroid_belt.position)
                self.click('right')
                if self.find_and_click('warp_to_zero'):
                    self.asteroid_belt = asteroid_belt
                    time.sleep(10)
                    return True
                    break

        return False

    def warp_to(self, obj):
        if self.locate('people_and_places'):
            if self.click(obj, 'right'):
                if self.click('warp_to_zero'):
                    return True
        return False

    def dock_to_station(self):
        self.last_action = 'dock_to_station'
        logging.info("pilot.dock_to_station")
        if self.locate('people_and_places'):
            if self.find_and_click('refinery', 'right'):
                if self.find_and_click('dock'):
                    return True
        return False

    def undock(self):
        self.last_action = 'undock'
        logging.info("pilot.undock")

        if self.click('undock'):
            return True
        return False

    def locate(self, obj):
        object = pyautogui.locateOnScreen(RESOURCES[obj]['path'], confidence=RESOURCES[obj]['confidence'],
                                          grayscale=RESOURCES[obj]['grayscale'])
        if not object and RESOURCES[obj]['path_alt']:
            object = pyautogui.locateOnScreen(RESOURCES[obj]['path_alt'], confidence=RESOURCES[obj]['confidence'],
                                          grayscale=RESOURCES[obj]['grayscale'])
        return object

    def locate_all(self, obj):
        instance = pyautogui.locateAllOnScreen(RESOURCES[obj]['path'], confidence=RESOURCES[obj]['confidence'])
        if not instance and RESOURCES[obj]['path_alt']:
            instance = pyautogui.locateAllOnScreen(RESOURCES[obj]['path_alt'], confidence=RESOURCES[obj]['confidence'])
        return instance

    def center(self, rect):
        return pyautogui.center(rect)

    def click(self, button="left"):
        return pyautogui.click(button=button)
    
    def press(self, key):
        return pyautogui.press(key)
        
    def scroll(self,i):
        return pyautogui.scroll(i)

    def find_and_click(self, obj, button="left"):
        logging.debug(f'pilot.click({obj}, {button})')
        rect = self.locate(obj)
        logging.debug(f'pilot.click.rect={rect}')
        if rect:
            position = self.center(rect)
            logging.debug(f'pilot.click.position={position}')
            self.move_to(position)
            self.click(button=button)
            ret = True
        else:
            ret = False
        logging.debug(f'pilot.click.return={ret}')
        return ret

    def move_to(self, position):
        return pyautogui.moveTo(position.x, position.y, MOUSE_MOVEMENT_TIME, MOUSE_MOVEMENT_TYPE)

    def move(self, x, y):
        return pyautogui.move(x, y, MOUSE_MOVEMENT_TIME, MOUSE_MOVEMENT_TYPE)

    def match(self, obj):
        if obj == 'search':
            search = self.locate('search')
            if search:
                x = search.left - 80
                y = search.top + 28
                color = (6, 74, 95)
                tolerance = 20
                return pyautogui.pixelMatchesColor(int(x), int(y), color, tolerance=tolerance)

    def hotkey(self, a, b, c=None):
        pyautogui.keyDown(a)
        pyautogui.keyDown(b)
        if c:
            pyautogui.keyDown(c)
            pyautogui.keyUp(c)
        pyautogui.keyUp(b)
        pyautogui.keyUp(a)

class Resource(object):
    last_position = None
    def __init__(self, object):
        self.name = object['name']
        self.path = object['path']
        self.path_alt = object['path_alt']
        self.confidence = object['confidence']

    def __str__(self):
        return self.name

class AsteroidBelt(object):
    empty = False
    name = 'Unknown Asteroid belt'

    def __init__(self, object):
        self.position = pyautogui.center(object)

class Ship(object):
    on_station = None
    drones_in_space = False
    afterburner = False
    cargo_full = False
    warping = False

    def __init__(self):

        self.state = None

    def is_on_station(self):
        self.on_station = True if self.pilot.locate('undock') else False
        return self.on_station

    def is_in_space(self):
        self.in_space = True if self.pilot.locate('overview') else False
        return self.in_space

    def is_on_asteroid_belt(self):
        self.on_asteroid_belt = self.pilot.locate('asteroid_belt_1')
        return self.on_asteroid_belt

    def is_inventory_full(self):
        self.inventory_full = self.pilot.check_inventory()
        return self.inventory_full

    def is_warping(self):
        self.warping = self.pilot.locate('warping')
        return self.warping

    def is_drones_in_space(self):
        self.drones_in_space = True if self.pilot.locate('idle') or self.pilot.locate('fighting') else False
        return self.drones_in_space

    def is_digging(self):
        self.digging = True if self.pilot.locate('miner') else False
        return self.digging

class Game(object):

    def __init__(self, pilot_name):
        self.name = f'EVE - {pilot_name}'
        self.interface = Interface()

    def is_running(self):
        self.hwnd = win32gui.FindWindow(None, self.name)
        return True if self.hwnd != 0 else False

    def is_active(self):
        active_window = win32gui.GetForegroundWindow()
        return True if self.hwnd == active_window else False

    def bring_to_front(self):
        win_size = 3 if WINDOW_MAXIMIZED else 1
        win32gui.ShowWindow(self.hwnd, win_size)
        pyautogui.keyDown('alt')
        try: win32gui.SetForegroundWindow(self.hwnd)
        except Exception as e: print(e)
        pyautogui.keyUp('alt')
        self.rect = win32gui.GetWindowRect(self.hwnd)

def testasdq():
    asteroid_belts = []
    instance = pyautogui.locateAllOnScreen('./res/asteroid_belt.png', confidence=0.99)
    for object in instance:
        a = AsteroidBelt(object)
        print(a.name)
        # asteroid_belts.append(AsteroidBelt(object))

# salvaging()
# clean_inventory()

def salvaging():
    sleep(3)

    while pyautogui.locateOnScreen('wreck.png'):
        while pyautogui.locateOnScreen('salvager.png'):
            print('ciągle zbiera')
            sleep(1)

        wrecks = pyautogui.locateAllOnScreen('wreck.png')
        wreck_list = []
        loop = 0
        for wreck in wrecks:
            if loop > 3: break
            wreck_list.append(wreck)
            loop += 1

        for wreck in wreck_list:
            position = pyautogui.center(wreck)
            pyautogui.moveTo(position.x, position.y, MOUSE_MOVEMENT_TIME, pyautogui.easeOutQuad)
            pyautogui.keyDown('ctrl')
            pyautogui.click()
            pyautogui.keyUp('ctrl')
        sleep(3)

        loop = 0
        for wreck in wreck_list:
            position = pyautogui.center(wreck)
            pyautogui.moveTo(position.x, position.y, MOUSE_MOVEMENT_TIME, pyautogui.easeOutQuad)
            pyautogui.click()
            pyautogui.press(f'f{loop + 1}')
            loop += 1

        pyautogui.move(-50, 0)

def clean_inventory():
    progress_bar = pyautogui.locateOnScreen('progress_bar.png')
    position = pyautogui.center(progress_bar)
    pyautogui.moveTo(position.x + 50, position.y + 50, MOUSE_MOVEMENT_TIME, pyautogui.easeOutQuad)
    pyautogui.click()
    pyautogui.keyDown('ctrl')
    pyautogui.keyDown('a')
    pyautogui.keyUp('a')
    pyautogui.keyUp('ctrl')
    item_hangar = pyautogui.locateOnScreen('item_hangar.png')
    position = pyautogui.center(item_hangar)
    pyautogui.mouseDown()
    pyautogui.moveTo(position.x, position.y, MOUSE_MOVEMENT_TIME, pyautogui.easeOutQuad)
    pyautogui.mouseUp()


if __name__ == '__main__':
    def get_pilot_name():
        with open('user.txt', 'r+') as file:
            last_pilot_name = file.read()  # get pilot name from file
            text = 'Podaj nazwę pilota'
            pilot_name = pymsgbox.prompt(text=text, title=APP_NAME, default=last_pilot_name)
            if pilot_name:
                file.seek(0)  # sets  point at the beginning of the file
                file.truncate()  # clear previous content
                file.write(pilot_name)  # save pilot name to file
            else: sys.exit(1)
        return pilot_name if pilot_name != '' else None

    pilot_name = get_pilot_name()

    pilot = Pilot(pilot_name)



    while True:
        pilot.run()





