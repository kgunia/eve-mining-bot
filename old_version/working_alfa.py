import pyautogui, time
from datetime import datetime


def current_time():
    now = datetime.now()
    return now.strftime("%H:%M:%S")


# Initialize pyautogui
pyautogui.PAUSE = 0.25
pyautogui.FAILSAFE = True

# Prepare resources
resource_path = './res2/'
resources = [
    'undock.png',
    'undock_alt.png',
    'people_and_places.png',
    'people_and_places_alt.png',
    'asteroid_belt.png',
    'asteroid_belt_alt.png',
    'station.png',
    'station.png_alt',
    'warp_to_zero.png',
    'warp_to_zero_alt.png',
    'station.png',
    'station_alt.png',
    'dock.png',
    'dock_alt.png',
    'overview.png',
    'overview_alt.png',
    'approach_location.png',
    'approach_location_alt.png',
    'menu.png',
    'menu_alt.png',
    'exterior_view.png',
    'exterior_view_alt.png',
    'eve.png',
    'eve_alt.png',
    'drones.png',
    'drones_alt.png',
    'drones_in_bay.png',
    'drones_in_bay_alt.png',
    'launch_drones.png',
    'launch_drones_alt.png',
    'asteroid.png',
    'asteroid_alt.png',
    'approach.png',
    'approach_alt.png',
    'lock_target.png',
    'lock_target_alt.png',
    'mining.png',
    'mining_alt.png',
    'mining_active.png',
    'mining_active_alt.png',
    'search.png',
    'search_alt.png',
    'inventory.png',
    'inventory_alt.png',
    'drones_in_local_space.png',
    'drones_in_local_space_alt.png',
    'return_to_drone_bay.png',
    'return_to_drone_bay_alt.png',
    'ore_hold.png',
    'ore_hold_alt.png',
    'item_hangar.png',
    'item_hangar_alt.png',
]

RESOURCES = {}

for resource in resources:
    name = resource.split(".")[0]
    RESOURCES[name] = resource_path + resource

MOUSE_MOVEMENT_TIME = 0.25
MOUSE_CLICK_DELAY = 0.1


def locate(name, confidence=0.8):
    position = pyautogui.locateOnScreen(RESOURCES[name], confidence)
    if not position:
        position = pyautogui.locateOnScreen(RESOURCES[f'{name}_alt'], confidence)
        # if not position and confidence > 0.2:
        #     position = locate(name, confidence-0.1)

    return position


def click(name, button="left"):
    print(f'[{current_time()}]INFO: lokalizuję obiekt {name}')
    position = locate(name)

    if position:
        print(f'[{current_time()}]INFO: klikam obiekt {name}')
        try:
            position = pyautogui.center(position)
            pyautogui.moveTo(position.x, position.y, MOUSE_MOVEMENT_TIME, pyautogui.easeOutQuad)
            pyautogui.click(button=button)
        except:
            print(f'[{current_time()}]ERROR: nie udało się kliknąć.')
    else:
        print(f'[{current_time()}]ERROR: nie udało się zlokalizować obiektu {name}')


TIME = {
    'undock': 10,
    'warp': 25,
    'docking': 35,
    'launch_drones': 5,
    'return_to_drone_bay': 8,
    'afterburner': 3,
    'approach_to_asteroid': 20,
    'lock_target': 5,
    'mining': 61
}


def main():
    # odlicznie do startu
    print('Starting', end='')

    for i in range(5):
        print('.', end='')
        time.sleep(1)
    print('')

    # kliknij w menu aby aktywować okno gry
    click('menu')

    # # zamknij menu
    # pyautogui.keyDown('ctrl')
    # pyautogui.keyDown('f9')
    # pyautogui.keyUp('f9')
    # pyautogui.keyUp('ctrl')

    # włącz potato mod
    pyautogui.keyDown('ctrl')
    pyautogui.keyDown('shift')
    pyautogui.keyDown('f9')
    pyautogui.keyUp('f9')
    pyautogui.keyUp('shift')
    pyautogui.keyUp('ctrl')

    while True:
        # wydokuj
        click('undock')
        time.sleep(TIME['undock'])

        # leć na pas asteroid
        click('people_and_places')
        # pyautogui.keyDown('s')
        click('asteroid_belt', 'right')
        click('warp_to_zero')
        # pyautogui.keyUp('s')
        time.sleep(TIME['warp'])

        # odpal drony
        click('drones')
        click('drones_in_bay', 'right')
        click('launch_drones')
        time.sleep(TIME['launch_drones'])

        # odpal afterburner
        pyautogui.keyDown('alt')
        pyautogui.keyDown('f1')
        pyautogui.keyUp('f1')
        pyautogui.keyUp('alt')
        time.sleep(TIME['afterburner'])

        # rozpocznij kopanie

        inventory_full = False
        while inventory_full == False:
            # włącz overview
            click('overview')

            # przełącz na zakładkę mining
            click('mining')

            # leć do asteroidy
            pyautogui.keyDown('q')
            click('asteroid')
            pyautogui.keyUp('q')
            time.sleep(TIME['approach_to_asteroid'])

            # namierz cel
            pyautogui.keyDown('ctrl')
            pyautogui.keyUp('ctrl')
            # click('lock_target')
            time.sleep(TIME['lock_target'])

            # rozpocznij kopanie
            pyautogui.press('f1')
            pyautogui.press('f2')

            mining = True
            while mining:
                print(f'[{current_time()}]INFO: czekam aż wykopie')
                time.sleep(TIME['mining'])

                if locate('mining_active'):
                    print(f'[{current_time()}]INFO: ciągle kopie')
                    mining = True
                else:
                    print(f'[{current_time()}]INFO: przestał kopać')
                    mining = False

            # sprawdź ładownię
            click('inventory')
            click('ore_hold')
            if pyautogui.pixelMatchesColor(int(locate('search').left - 80), int(locate('search').top + 28), (6, 74, 95),
                                           tolerance=20):
                inventory_full = True

        # schowaj drony
        click('drones')
        click('drones_in_local_space', 'right')
        click('return_to_drone_bay')
        time.sleep(TIME['return_to_drone_bay'])

        # leć na stację
        click('people_and_places')
        click('station', 'right')
        click('dock')
        time.sleep(TIME['docking'])

        # wyładuj ładownię
        click('inventory')
        click('ore_hold')
        pyautogui.move(110, 0)
        pyautogui.click()
        pyautogui.keyDown('ctrl')
        pyautogui.keyDown('a')
        pyautogui.keyUp('a')
        pyautogui.keyUp('ctrl')
        pos = locate('item_hangar')
        if pos:
            pos = pyautogui.center(pos)
            pyautogui.dragTo(pos.x, pos.y, MOUSE_MOVEMENT_TIME, pyautogui.easeOutQuad)


if __name__ == '__main__':
    main()
