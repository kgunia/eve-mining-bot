import pyautogui

class InterfaceObject(object):

    def __init__(self, object):
        self.name = object['name']
        self.path = object['path']
        self.confidence = object['confidence']

    def __str__(self):
        return self.name

    def get_position(self):
        return pyautogui.center(self.get_rect())

    def get_rect(self):
        return pyautogui.locateOnScreen(self.locate(), self.confidence)

    def locate(self):
        return pyautogui.locateOnScreen(self.path, self.confidence)

    def click(self):
        return pyautogui.click(self.get_position())