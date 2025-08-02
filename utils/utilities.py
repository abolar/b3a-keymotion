from screeninfo import get_monitors
import pyautogui
import win32api
import win32con
import win32gui

monitors = list(enumerate(get_monitors()))
print(monitors)

monitor_scale_factor = {
    0: 1.0,
    1: 1.0 #2/3.,
}

def get_monitor_from_location(x, y):
    global monitors
    for i, monitor in monitors:
        if monitor.x <= x <= monitor.x + monitor.width and monitor.y <= y <= monitor.y + monitor.height:
            return i
    return None

def get_monitor_scale_factor(monitor_index):
    global monitor_scale_factor
    return monitor_scale_factor[monitor_index] / monitor_scale_factor[0]


def scale_coordinates(x, y, width, height,):
    monitor_index = get_monitor_from_location(x, y)
    scale_factor = get_monitor_scale_factor(monitor_index)
    return int(round(x * scale_factor)), int(round(y * scale_factor)), int(round(width * scale_factor)), int(round(height * scale_factor))

if __name__ == "__main__":

    # x: 0, y: 0, width: 128, height: 144

    print(scale_coordinates(4000, 0, 128, 144))

