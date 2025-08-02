import tkinter as tk
from screeninfo import get_monitors
import keyboard
import pyautogui
import sys
import json
from ctypes import windll
import time

from ui.grid import Grid
from utils.mdebug import mprint, debug_section
from ui.v01 import MainTk
# from userconfig.easy import config
# TODO: Replace 'easy' with a variable name like:
# config_type = 'easy'  # At top of file
# from userconfig.{config_type} import config

import importlib

from keys import keybindings

# from ctypes import windll


# Set DPI awareness to handle high DPI displays properly
try:
    # Windows 8.1 and later
    windll.shcore.SetProcessDpiAwareness(2)  # PROCESS_PER_MONITOR_DPI_AWARE_V2
except AttributeError:
    try:
        # Windows 8.0
        windll.shcore.SetProcessDpiAwareness(1)  # PROCESS_PER_MONITOR_DPI_AWARE
    except AttributeError:
        # Windows 7 and earlier
        windll.user32.SetProcessDPIAware()

main_container = None

grids_visible = False

grid_keys = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
arrow_keys = ['up', 'down', 'left', 'right']


overlay_toggle_key = ['caps lock', '$']
clear_and_click_key= ['enter']
clear_and_ctrl_click_key= ['space']
quit_key = 'ctrl+shift+q'
reload_config_key = 'ctrl+shift+r'


def load_config(config_name):
    global main_container
    try:
        my_module = importlib.import_module(f"userconfig.{config_name}")
    except ModuleNotFoundError:
        print(f"Error: Module '{config_name}' not found.")
        raise ValueError(f"Config '{config_name}' not found.")

    return my_module.config

    # main_container.create_grid_components(config)


def inject_hires_config():
    global main_container
    config = load_config('hires')
    main_container.create_grid_components(config)

def inject_num_config():
    global main_container
    config = load_config('num')
    main_container.create_grid_components(config)

def inject_easy_config():
    global main_container
    config = load_config('easy')
    main_container.create_grid_components(config)


def mouse_click_event(ctrl=False):
    global grids_visible
    # main_container.after(0, main_container.hide_grids)
    main_container.hide_grids()
    x, y = pyautogui.position()
    print(f"clicking at {x}, {y}")
    if ctrl:
        keyboard.press('ctrl')
        time.sleep(0.1)
    pyautogui.click()
    time.sleep(0.1)
    if ctrl:
        keyboard.release('ctrl')
    grids_visible = False



@debug_section(True)
def toggle_grids():
    global grids_visible
    if grids_visible:
        main_container.after(1, main_container.hide_grids)
        grids_visible = False
        # keyboard.unhook(process_keystroke)
    else:
        main_container.after(1, main_container.show_grids)
        grids_visible = True
        # keyboard.hook(process_keystroke, suppress=True)

@debug_section(True)
def quit_all():
    global main_container
    if main_container:
        main_container.after(1, main_container.quit)


@debug_section(False)
def process_keystroke(event):
    def to_string(event, send_key):
        f_arr = []

        if event.name in ['ctrl', 'alt', 'shift']:
            return True
        if event.event_type in ['down']:
            return True

        ctrl = 'ctrl' if keyboard.is_pressed('ctrl') else None
        alt = 'alt' if keyboard.is_pressed('alt') else None
        shift = 'shift' if keyboard.is_pressed('shift') else None
        f_arr.append(ctrl)
        f_arr.append(alt)
        f_arr.append(shift)
        f_arr.append(event.name)
        mprint('keystroke', '+'.join(filter(None, f_arr)), f"send_key: {send_key}")

    global grids_visible, grid_keys, main_container, overlay_toggle_key, clear_and_click_key, quit_key


    send_key = True
    f_display_a = []
    f_display_a.append(event.name)
    f_display_a.append(event.event_type)
    f_display_a.append('ctrl')


    # Handle both KEY_DOWN and KEY_UP events
    if event.event_type == keyboard.KEY_DOWN:
        # Key down logic
        if event.name in [quit_key, *overlay_toggle_key]:
            send_key = False
        if event.name == 'backspace' and grids_visible:
            send_key = False

        if grids_visible:
            send_key = False

        # quit all
        if event.name.lower() == 'z' and keyboard.is_pressed('shift') and keyboard.is_pressed('ctrl'):
            main_container.after(100, quit_all)
            return False

        # toggle grids
        if event.name in overlay_toggle_key and main_container:
            main_container.after(100, toggle_grids)

        # process single key and backspace
        if grids_visible and (
                    event.name in grid_keys 
                    or event.name in 'backspace'
                ):
            main_container.process_single_key(event.name)
            send_key = False

        # clear and click
        if grids_visible and event.name in clear_and_click_key:
            x, y = pyautogui.position()
            main_container.after(0, mouse_click_event)
            send_key = False

        # clear and ctrl click
        if grids_visible and event.name in clear_and_ctrl_click_key:
            x, y = pyautogui.position()
            main_container.after(0, mouse_click_event, True)
            send_key = False

        # keyboard launching stuff
        if not grids_visible and keyboard.is_pressed('ctrl') and keyboard.is_pressed('alt') and keyboard.is_pressed('shift'):
            if event.name in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz':
                print("ctrl+alt+shift")
                main_container.process_menu_key(event.name.lower())

    elif event.event_type == keyboard.KEY_UP:
        # Key up logic - ensure we don't suppress key up events for modifier keys
        # that we might have suppressed on key down
        if event.name in ['shift', 'ctrl', 'alt']:
            # Always allow modifier key up events to pass through
            send_key = True
        elif event.name in [quit_key, *overlay_toggle_key]:
            send_key = False
        elif event.name == 'backspace' and grids_visible:
            send_key = False
        elif grids_visible:
            send_key = False

    to_string(event, send_key)


    return send_key



def mouse_location():
    x, y = pyautogui.position()
    print(x, y)

def toggle_keyboard_status():
    global main_container
    if main_container:
        main_container.toggle_keyboard_status()
        keybindings.toggle_keys('mainkeys')
        print("-"*40)

if __name__ == "__main__":

    if len(sys.argv) > 1:
        config_name = sys.argv[1]
    else:
        config_name = 'easy'
    print(f'Loading: {config_name}')
    
    config_path = f"userconfig/{config_name}.json"
    config = json.load(open(config_path))

    main_container = MainTk(config)
    # inject_hires_config()
    # inject_num_config()
    # keyboard.add_hotkey('f2', toggle_keyboard_status, suppress=True)
    keyboard.hook(process_keystroke, suppress=True)

    main_container.mainloop()
