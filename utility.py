import os
from time import sleep, perf_counter

import PIL
import pyautogui
from parameter import DELAY_BETWEEN_CLICKS


class Button:
    def __init__(self, img, center):
        self.center = center
        self.img = img

    def __getitem__(self, item):
        if item == 0:
            return self.img
        elif item == 1:
            return self.center

    def __repr__(self):
        return str([self.img, self.center])

    def click(self, times=1):
        for _ in range(times):
            pyautogui.click(self.center)
            sleep(DELAY_BETWEEN_CLICKS)

    def is_visible(self):
        filename = img_path(self.img)
        im = PIL.Image.open(filename)
        w, h = im.size
        haystack = self._haystack(w + 5, h + 5)
        return bool(pyautogui.locate(filename, haystack, confidence=0.9))

    def is_visible_in(self, area):
        filename = img_path(self.img)
        haystack = pyautogui.screenshot().crop(area)
        return bool(pyautogui.locate(filename, haystack, confidence=0.9))

    def _haystack(self, width=25, height=25):
        w, h = round(width / 2), round(height / 2)
        im = pyautogui.screenshot()
        return im.crop((self.center[0] - w, self.center[1] - h,
                        self.center[0] + w, self.center[1] + h))


def log(*args):
    from datetime import datetime
    now = datetime.now()
    current_time = now.strftime("[%H:%M:%S]")
    message = list(args)
    message.insert(0, current_time)
    print(' '.join(str(e) for e in message))


def img_path(filename):
    cwd = os.path.dirname(__file__)
    return os.path.join(cwd, 'image', filename)


def wait(btn: Button, haystack=None, timeout=10):  # timeout counts in seconds
    found = False
    start_time = perf_counter()
    while (perf_counter() - start_time) < timeout:
        if haystack is None:
            found = btn.is_visible()
        else:
            found = btn.is_visible_in(haystack)

        if found:
            break

    if not found:
        raise TimeoutError('Can not find button: {}'.format(btn))
