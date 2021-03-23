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
logging.basicConfig(format=LOG_MESSAGE_FORMAT, datefmt=LOG_DATE_FORMAT, level=logging.DEBUG)

# Set pause after pyautogui action
pyautogui.PAUSE=DEFAULT_DELAY

with open('resources.json') as file:
    RESOURCES = json.load(file)


def main():
    pilot_name = pymsgbox.prompt(text='Podaj nazwę pilota', title=APP_NAME , default='Astrid Dirtsa')
    if pilot_name:

        pilot = Pilot(pilot_name)
        game = Game(pilot)
        ship = Ship(pilot)

    else:
        pymsgbox.alert(text='Nie podałeś nazwy pilota! Zamykam aplikację.', title=APP_NAME, button='OK')
        sys.exit(1)

    while True:
        # sleep(DEFAULT_DELAY)
        if game.is_running():
            game.set_foreground()
            if game.is_the_right_position():
                # freeze when game settings is open
                if pilot.locate('quit_game'):
                    confirm = pymsgbox.confirm(text='Wszedłeś w ustawienia gry, zawiesiłem bota.', title=APP_NAME, buttons=['Wznów', 'Przerwij'])


                if ship.is_on_station():
                    if ship.is_inventory_full():
                        logging.info("# TODO opróżnij inventory")
                    else:
                        pilot.undock()
                elif ship.is_warping():
                    print('WARPING!!!!!!!!!!!!!!!')
                    sleep(10)
                elif ship.is_in_space():
                    if not pilot.last_action and ship.is_inventory_full():
                        logging.info("# TODO leć na stację")
                    elif ship.is_on_asteroid_belt():
                         logging.info("# TODO zacznij kopać")
                    else:
                        pilot.warp_to_asteroid_belt()

                    # else:
                    #     print('leć na pas asteroid')

            else: game.move_to_the_right_side(DEFAULT_DELAY)
        else:
            pymsgbox.alert(text='Gra jest wyłączona. Uruchom grę zanim włączysz bota.', title='EVE Mining Bot', button='OK')
            break

class Ship(object):
    on_station = None

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

class Pilot(object):

    def __init__(self,name):
        self.name = name
        self.last_action = True

    def check_inventory(self):
        self.last_action = 'check-inventory'
        logging.debug("pilot.check_inventory")
        if self.click('inventory') and self.click('ore_hold'):
            return self.match('search')
        else:
            pymsgbox.alert(text="Nie mogę sprawdzić ivnentory. Sprawdź interface", title=APP_NAME, button="OK")

    def warp_to_asteroid_belt(self):
        self.last_action = 'warp-to-asteroid-belt'
        logging.debug("pilot.warp_to_asteroid_belt")
        self.click('people_and_places')
        self.click('asteroid_belt', 'right')
        self.click('warp_to_zero')
        sleep(SHIP_ALIGN_TIME)

    def undock(self):
        self.last_action = 'undock'
        self.click('undock')




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



