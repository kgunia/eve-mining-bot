import win32gui, win32con, pyautogui, logging, pymsgbox, sys, json
from time import sleep


# CONFIG
LOG_MESSAGE_FORMAT = '[%(asctime)s] %(levelname)s - %(message)s'
LOG_DATE_FORMAT = '%H:%M:%S'
DEFAULT_DELAY = 0.2
MOUSE_MOVEMENT_TIME = 0.25
SHIP_ALIGN_TIME = 4.79

APP_NAME = 'EVE Mining Bot'


# Initialize logging
logging.basicConfig(format=LOG_MESSAGE_FORMAT, datefmt=LOG_DATE_FORMAT, level=logging.INFO)

# Set pause after pyautogui action
pyautogui.PAUSE=DEFAULT_DELAY

with open('resources.json') as file:
    RESOURCES = json.load(file)


def main():
    with open('user.txt', 'r+') as f:
        last_pilot_name = f.read()
        pilot_name = pymsgbox.prompt(text='Podaj nazwę pilota', title=APP_NAME , default=last_pilot_name)
        f.seek(0)  # sets  point at the beginning of the file
        f.truncate()  # Clear previous content
        f.write(pilot_name)

    if pilot_name:
        pilot = Pilot(pilot_name)
        game = Game(pilot)
        ship = Ship(pilot)
    else:
        pymsgbox.alert(text='Nie podałeś nazwy pilota! Zamykam aplikację.', title=APP_NAME, button='OK')
        sys.exit(1)


    while game.is_running():
        game.set_foreground()

        if pilot.locate('quit_game'):
            confirm = pymsgbox.confirm(text='Wszedłeś w ustawienia gry, zawiesiłem bota.', title=APP_NAME, buttons=['Wznów', 'Przerwij'])
            if confirm == 'Przerwij': break

        if ship.is_on_station():
            if ship.is_inventory_full():
                pilot.unload_cargo()
            else:
                pilot.undock()
                # pilot.send_message('opuszczam stacje')
        elif ship.is_warping():
            sleep(10)
        elif ship.is_in_space():
            if not pilot.last_action and ship.is_inventory_full():
                if ship.is_drones_in_space():
                    pilot.return_drones()
                else:
                    pilot.dock_to_station()
                    # pilot.send_message('lece na stacje')
            elif ship.is_on_asteroid_belt():
                if not ship.is_drones_in_space():
                    pilot.launch_drones()
                elif not ship.afterburner:
                    pilot.launch_afterburner(ship)
                elif ship.is_digging():
                        pass
                elif ship.is_inventory_full():
                    if ship.is_drones_in_space():
                        pilot.return_drones()
                    else:
                        pilot.dock_to_station()
                else:
                    #pilot.send_message('biore sie za kopanie')
                    pyautogui.press('f1')
                    pyautogui.press('f2')
                    pyautogui.keyDown('q')
                    pilot.click('asteroid')
                    pyautogui.keyUp('q')
                    pyautogui.move(0,-20)
                    sleep(5)
            else:
                pilot.warp_to_asteroid_belt()
                # pilot.send_message('lece na pas asteroid')
        sleep(1)

    pymsgbox.alert(text='Gra jest wyłączona. Uruchom grę zanim włączysz bota.', title='EVE Mining Bot', button='OK')


class Ship(object):
    on_station = None
    drones_in_space = False
    afterburner = False

    def __init__(self, pilot):
        self.pilot = pilot
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

class Pilot(object):
    last_message =  ''

    def __init__(self,name):
        self.name = name
        self.last_action = True

    def send_message(self, message):
        if message != self.last_message:
            self.click('corp_chat')
            pyautogui.press('space')
            pyautogui.typewrite(f'Szefuniu, {message}')
            pyautogui.press('enter')
            self.click('overview')

    def check_inventory(self):
        self.last_action = 'check-inventory'
        logging.info("pilot.check_inventory")

        if self.locate('inventory'):
            if self.match('search'):
                return True
        return False

    def launch_drones(self):
        self.last_action = 'launch-drones'
        logging.info('pilot.launch_drones')

        if self.click('drones_in_bay', 'right'):
            if self.click('launch_drones'):
                return True
        return False

    def return_drones(self):
        self.last_action = 'return-drones'
        logging.info('pilot.return_drones')

        if self.click('drones_in_local_space', 'right'):
            if self.click('return_to_drone_bay'):
                return True
        return False

    def launch_afterburner(self,ship):
        self.launch_afterburner = 'launch_afterburner'
        logging.info('pilot.launch_afterburner')

        pyautogui.keyDown('alt')
        pyautogui.keyDown('f1')
        pyautogui.keyUp('f1')
        pyautogui.keyUp('alt')
        ship.afterburner = True


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
        self.last_action = 'warp-to-asteroid-belt'
        logging.info("pilot.warp_to_asteroid_belt")

        if self.locate('people_and_places'):
            if self.click('asteroid_belt', 'right'):
                if self.click('warp_to_zero'):
                    sleep(SHIP_ALIGN_TIME)
                    return True
        return False


    def dock_to_station(self):
        self.last_action = 'dock_to_station'
        logging.info("pilot.dock_to_station")
        if self.locate('people_and_places'):
            if self.click('station', 'right'):
                if self.click('dock'):
                    sleep(SHIP_ALIGN_TIME)
                    return True
        return False



    def undock(self):
        self.last_action = 'undock'
        logging.info("pilot.undock")
        if self.click('undock'):
            return True
        return False

    def locate(self, obj):
        localization = pyautogui.locateOnScreen(RESOURCES[obj]['path'], confidence=RESOURCES[obj]['confidence'])
        if not localization and RESOURCES[obj]['path_alt']:
            localization = pyautogui.locateOnScreen(RESOURCES[obj]['path_alt'], confidence=RESOURCES[obj]['confidence'])
        return localization


    def click(self, obj, button="left"):
        logging.debug(f'pilot.click({obj}, {button})')
        rect = self.locate(obj)
        logging.debug(f'pilot.click.rect={rect}')
        if rect:
            position = pyautogui.center(rect)
            logging.debug(f'pilot.click.position={position}')
            pyautogui.moveTo(position.x, position.y, MOUSE_MOVEMENT_TIME, pyautogui.easeOutQuad)
            pyautogui.click(button=button)
            ret = True
        else: ret =False
        logging.debug(f'pilot.click.return={ret}')
        return ret

    def match(self,obj):
        if obj == 'search':
            search = self.locate('search')
            if search:
                x = search.left - 80
                y = search.top + 28
                color = (6, 74, 95)
                tolerance = 20
                return pyautogui.pixelMatchesColor(int(x), int(y), color, tolerance=tolerance)





class Game(object):

    def __init__(self, pilot):
        self.name = f'EVE - {pilot.name}'
        self.last_known_rect = None

    def find(self):
        return win32gui.FindWindow(None, self.name)

    def is_running(self):
        if self.find() != 0: return True

    def get_rect(self):
        return win32gui.GetWindowRect(self.find())

    def bring_to_front(self):
        win32gui.ShowWindow(self.find(), win32con.SW_SHOWMAXIMIZED)
        win32gui.SetForegroundWindow(self.find())
        return True

    def is_the_right_position(self):
        return self.last_known_rect == self.get_rect()

    def move_to_the_right_side(self,delay):
        if self.bring_to_front():
            sleep(DEFAULT_DELAY)
            pyautogui.hotkey('win', 'right')
            self.last_known_rect = self.get_rect()

    def set_foreground(self):
        try:
            win32gui.SetForegroundWindow(self.find())
        except:
            sleep(DEFAULT_DELAY)
            win32gui.SetForegroundWindow(self.find())


if __name__ == '__main__':
    main()


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
                if loop > 3 : break
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
                pyautogui.press(f'f{loop+1}')
                loop += 1

            pyautogui.move(-50,0)




    def clean_inventory():
        progress_bar = pyautogui.locateOnScreen('progress_bar.png')
        position = pyautogui.center(progress_bar)
        pyautogui.moveTo(position.x+50, position.y+50, MOUSE_MOVEMENT_TIME, pyautogui.easeOutQuad)
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






