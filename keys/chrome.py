import pyautogui
import keyboard
import time
from utils.mdebug import mprint, debug_section

# CLICK FUNCTIONS
@debug_section(enabled=True)
def mouseclick():
    mprint("v1", "Mouse clicked")
    pyautogui.click()

@debug_section(enabled=True)
def shift_click():
    mprint("v1", "Shift clicked")
    keyboard.press('shift')
    time.sleep(0.1)
    pyautogui.click()
    time.sleep(0.1)
    keyboard.release('shift')

@debug_section(enabled=True)
def ctrl_click():
    mprint("v1", "Ctrl clicked")
    keyboard.press('ctrl')
    time.sleep(0.1)
    pyautogui.click()
    time.sleep(0.1)
    keyboard.release('ctrl')

@debug_section(enabled=True)
def next_tab():
    mprint("v1", "Next tab")
    keyboard.send('ctrl+tab')

# BROWSER FUNCTIONS
@debug_section(enabled=True)
def browser_back():
    mprint("v1", "Browser back")
    keyboard.send('alt+left')

@debug_section(enabled=True)
def browser_forward():
    mprint("v1", "Browser forward")
    keyboard.send('alt+right')

@debug_section(enabled=True)
def delete_tab():
    keyboard.send('ctrl+w')

@debug_section(enabled=True)
def move_mouse(xoffset, yoffset):
    x, y = pyautogui.position()
    pyautogui.moveTo(x + xoffset, y + yoffset, duration=.2, tween=pyautogui.easeOutQuad)

@debug_section(enabled=True)
def scroll_up(by=300):
    pyautogui.scroll(-by)

@debug_section(enabled=True)
def scroll_down(by=300):
    pyautogui.scroll(by)





class ChromeKeysBindings():
    def __init__(self):
        self.keys = [

            # Browser keys
            ('q', browser_back, [], True, "Browser back"),
            ('e', browser_forward, [], True, "Browser forward"),
            ('a', mouseclick, [], True, "Mouse click"),
            ('d', shift_click, [], True, "Shift click"),
            ('s', ctrl_click, [], True, "Ctrl click"),
            ('tab', next_tab, [], True, "Next tab"),
            ('w', delete_tab, [], True, "Delete tab"),

            # Mouse movement keys
            ('k', move_mouse, [0, -200], True, "Move mouse up"),
            ('j', move_mouse, [0, 200], True, "Move mouse down"),
            ('h', move_mouse, [-200, 0], True, "Move mouse left"),
            ('l', move_mouse, [200, 0], True, "Move mouse right"),
            ('shift+k', move_mouse, [0, -100], True, "Move mouse up"),
            ('shift+j', move_mouse, [0, 100], True, "Move mouse down"),
            ('shift+h', move_mouse, [-100, 0], True, "Move mouse left"),
            ('shift+l', move_mouse, [100, 0], True, "Move mouse right"),
            ('ctrl+k', move_mouse, [0, -10], True, "Move mouse up"),
            ('ctrl+j', move_mouse, [0, 10], True, "Move mouse down"),
            ('ctrl+h', move_mouse, [-10, 0], True, "Move mouse left"),
            ('ctrl+l', move_mouse, [10, 0], True, "Move mouse right"),
            ('alt+k', move_mouse, [0, -5], True, "Move mouse up"),
            ('alt+j', move_mouse, [0, 5], True, "Move mouse down"),
            ('alt+h', move_mouse, [-5, 0], True, "Move mouse left"),
            ('alt+l', move_mouse, [5, 0], True, "Move mouse right"),
            ('u', scroll_up, [], True, "Scroll up"),
            ('i', scroll_down, [], True, "Scroll down"),
            ('shift+i', lambda: scroll_up(600), [], True, "Scroll up"),
            ('shift+o', lambda: scroll_down(600), [], True, "Scroll down"),

        ]

    def activate(self):
        for key, function, args, suppress, description in self.keys:
            keyboard.add_hotkey(key, function, args, suppress)
            mprint("v1", f"Loaded key: {key} - {description}")
    def deactivate(self):
        for key, function, args, suppress, description in self.keys:
            keyboard.remove_hotkey(key)
            mprint("v1", f"Unloaded key: {key} - {description}")



