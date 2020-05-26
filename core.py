import os
from time import sleep, perf_counter

import PIL
import pyautogui
import pygetwindow as gw
import pytesseract

from parameter import *


class MSG:
    CONNECTION_FAIL = 'Network connection failed. reconnect?'
    MULTI_LOGIN = 'Account has logged in other location'
    ABNORMAL_NETWORK = 'Abnormal network. Please check the network and restart the game.'
    LOGGED_OUT = 'logged out'
    LEVEL_UP = 'level up'


class ResType:
    MONSTER = 0
    CAMP = 1
    FOOD = 2
    WOOD = 3
    IRON = 4
    SILVER = 5


class Button:
    def __init__(self, img, center):
        x, y = center
        self.center = x, y
        self.img = img

    def __getitem__(self, item):
        if item == 0:
            return self.img
        elif item == 1:
            return abs_position(self.center)

    def __repr__(self):
        return str([self.img, abs_position(self.center)])

    def click(self, times=1):
        for _ in range(times):
            pyautogui.click(abs_position(self.center))
            sleep(delay_between_clicks)

    def visible(self):
        filename = img_path(self.img)
        im = PIL.Image.open(filename)
        ndl = resize_by_window(im)
        haystack = self._haystack()
        # ndl.save('ndl.png')
        # haystack.save('hay.png')
        return bool(pyautogui.locate(ndl, haystack, confidence=img_match_confidence))

    def locate_in(self, area):
        filename = img_path(self.img)
        im = PIL.Image.open(filename)
        ndl = resize_by_window(im)
        haystack = pyautogui.screenshot().crop(area)
        return pyautogui.locate(ndl, haystack, confidence=img_match_confidence)

    def _haystack(self):
        filename = img_path(self.img)
        im = PIL.Image.open(filename)
        w, h = round(im.size[0] / 2) + 3, round(im.size[1] / 2) + 3
        im = pyautogui.screenshot()
        abs_center = abs_position(self.center)
        return im.crop((abs_center[0] - w, abs_center[1] - h,
                        abs_center[0] + w, abs_center[1] + h))


# buttons
ally_help = Button('ally_help.png', (465, 900))
kingdom = Button('kingdom.png', (105, 1015))
castle = Button('castle.png', (59, 1023))
desert_camp = Button('camp.png', (547, 881))
back = Button('back.png', (31, 80))
magnifier = Button('magnifier.png', (46, 805))
search = Button('search.png', (297, 1043))
march = Button('march.png', (505, 1045))
avatar = Button('avatar.png', (46, 81))
train = Button('train.png', (408, 548))
msg_confirm = Button('', (390, 655))
screen_center = Button('', (300, 560))
empty_space = Button('', (380, 147))  # 441, 111
half_troop = Button('', (301, 1049))
gather = Button('gather.png', (434, 569))
monster = Button('', (67, 820))
camp = Button('', (161, 820))
farm = Button('', (260, 820))
sawmill = Button('', (355, 820))
iron_mine = Button('', (448, 820))
slv_mine = Button('', (540, 820))
res_coord = [monster, camp, farm, sawmill, iron_mine, slv_mine]

# haystack areas
game_screen = (0, 0, game_window_size[0], game_window_size[1])


def window_pos_ratio():
    wnd = gw.getWindowsWithTitle(win_title[0])[0]
    width, height = wnd.size
    x, y = wnd.topleft
    return x, y, width / GAME_BASE_SIZE[0], (height - BANNER_H) / (GAME_BASE_SIZE[1] - BANNER_H)


def abs_position(pos):
    dx, dy, rx, ry = window_pos_ratio()
    return pos[0] * rx + dx, (pos[1] - BANNER_H) * ry + BANNER_H + dy


def resize_by_window(img):
    wnd = gw.getWindowsWithTitle(win_title[0])[0]
    width, height = wnd.size
    w, h = img.size
    new_im = img.resize((round(w * width / GAME_BASE_SIZE[0]),
                         round(h * height / GAME_BASE_SIZE[1])))
    return new_im


def img_path(filename):
    cwd = os.path.dirname(__file__)
    return os.path.join(cwd, 'image', filename)


def wait(btn: Button, haystack=None, timeout=10):  # timeout counts in seconds
    found = False
    start_time = perf_counter()
    while (perf_counter() - start_time) < timeout:
        if haystack is None:
            found = btn.visible()
        else:
            found = btn.locate_in(haystack)

        if found:
            break
        elif get_error_msg():
            raise TimeoutError('detect error screen in wait()')

    if not found:
        raise TimeoutError('Can not find button: {}'.format(btn))


def log(*args):
    from datetime import datetime
    now = datetime.now()
    current_time = now.strftime("[%H:%M:%S]")
    message = list(args)
    message.insert(0, current_time)
    print(' '.join(str(e) for e in message))


def countdown_timer(secs):
    print("Start", end="")
    for s in range(secs - 1, 0, -1):
        sleep(1.00)
        print("..{}".format(s), end="")
    sleep(1)
    print("..GO!")


# def game_init():
#     log('Initialize game window')
#     bs = gw.getWindowsWithTitle(win_title[0])[0]
#     bs.restore()
#     bs.moveTo(0, 0)
#     bs.resizeTo(game_window_size[0], game_window_size[1])


def ally_need_help():
    return ally_help.visible()


def help_ally():
    ally_help.click()


# def update_troop_status():
#     troop_info_area = [(10, 200, 37, 227),
#                        (10, 244, 37, 271),
#                        (10, 288, 37, 315)]
#     ts_images = {'back': 'ts_back.png',
#                  'enemy_atk': 'ts_enemy_atk.png',
#                  'gathering': 'ts_gathering.png',
#                  'monster_atk': 'ts_monster_atk.png',
#                  'scouting': 'ts_scouting.png',
#                  'transfer': 'ts_transfer.png',
#                  'reinforce': 'ts_reinforce.png',
#                  'rally': 'ts_rally.png'
#                  }
#     result = []
#     # confirm in kingdom screen
#     if (castle.visible() and not desert_camp.visible()) \
#             or search.visible():
#         im = pyautogui.screenshot()
#         for area in troop_info_area:
#             for status, img in ts_images.items():
#                 try:
#                     if pyautogui.locate(img_path(img), im.crop(area), confidence=0.9):
#                         result.append(status)
#                         break
#                 except IOError:
#                     log('File is missing:', img_path(img))
#         return result
#     else:
#         pass
def update_troop_status():
    troop_info_area = [(10, 200, 37, 227),
                       (10, 244, 37, 271),
                       (10, 288, 37, 315)]
    ts_images = {'back': 'ts_back.png',
                 'enemy_atk': 'ts_enemy_atk.png',
                 'gathering': 'ts_gathering.png',
                 'monster_atk': 'ts_monster_atk.png',
                 'scouting': 'ts_scouting.png',
                 'transfer': 'ts_transfer.png',
                 'reinforce': 'ts_reinforce.png',
                 'rally': 'ts_rally.png'
                 }
    result = []
    # confirm in kingdom screen
    if (castle.visible() and not desert_camp.visible()) \
            or search.visible():

        for area in troop_info_area:
            x1, y1, x2, y2 = area
            dx, dy, rx, ry = window_pos_ratio()

            x1 = x1 * rx + dx
            y1 = (y1 - BANNER_H) * ry + BANNER_H + dy
            x2 = x2 * rx + dx
            y2 = (y2 - BANNER_H) * ry + BANNER_H + dy

            haystack = pyautogui.screenshot().crop((x1, y1, x2, y2))
            for status, img in ts_images.items():
                try:
                    im = PIL.Image.open(img_path(img))
                    ndl = resize_by_window(im)
                    if pyautogui.locate(ndl, haystack, confidence=img_match_confidence):
                        result.append(status)
                        break
                except IOError:
                    log('File is missing:', img_path(img))
        return result
    else:
        return None


def img2str(im):
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    return pytesseract.image_to_string(im)


def get_error_msg():
    err_images = {
        MSG.LOGGED_OUT: 'coe_icon.png',
        MSG.LEVEL_UP: 'msg_confirm.png',
    }
    result = None
    for msg, img in err_images.items():
        haystack = pyautogui.screenshot().crop(game_screen)
        if pyautogui.locate(img_path(img), haystack, confidence=0.9):
            result = msg
            break
    else:
        msg_box = (60, 500, 540, 600)
        err_messages = [MSG.CONNECTION_FAIL,
                        MSG.MULTI_LOGIN,
                        MSG.ABNORMAL_NETWORK]
        img = pyautogui.screenshot().crop(msg_box)
        img = PIL.ImageOps.invert(img)
        message = ' '.join(img2str(img).split())
        if message in err_messages:
            result = message
    return result


def go_kingdom():
    for _ in range(5):  # try 5 times then abort
        if back.visible():
            back.click()
            sleep(1)
        else:
            break
    try:
        wait(castle)
    except TimeoutError:
        kingdom.click()
        wait(castle, timeout=60)
        log('go_kingdom complete')


def go_castle():
    for _ in range(5):  # try 5 times then abort
        if back.visible():
            back.click()
            sleep(1)
        else:
            break
    try:
        wait(kingdom)
    except TimeoutError:
        castle.click()
        wait(kingdom, timeout=60)
        log('go_castle complete')


def go_gathering(res, half=False):
    go_kingdom()
    magnifier.click()
    wait(search)
    res_coord[res].click()
    search.click()
    sleep(5)
    screen_center.click()
    gather.click()
    wait(march)
    if train.visible():
        back.click()
        log('No troops for gathering')
    else:
        if half:
            half_troop.click()
        march.click()
        wait(avatar)
        log('Troops go gathering {}'.format(res))


def click(x, y, delay=delay_between_clicks):
    pyautogui.click(x, y)
    sleep(delay)


def swipe(*args, interval=delay_between_clicks, duration=2):
    up, down, left, right = (300, 500), (300, 700), (200, 600), (400, 600)
    for move in args[0]:
        if move == 'up':
            pyautogui.moveTo(down[0], down[1])
            pyautogui.dragTo(up[0], up[1], duration=duration)
        elif move == 'down':
            pyautogui.moveTo(up[0], up[1])
            pyautogui.dragTo(down[0], down[1], duration=duration)
        elif move == 'left':
            pyautogui.moveTo(right[0], right[1])
            pyautogui.dragTo(left[0], left[1], duration=duration)
        elif move == 'right':
            pyautogui.moveTo(left[0], left[1])
            pyautogui.dragTo(right[0], right[1], duration=duration)
        sleep(interval)


def find_click(images):
    haystack = pyautogui.screenshot().crop(game_screen)
    for img in images:
        pos = pyautogui.locate(img_path(img), haystack, confidence=0.8)
        if pos:
            pos = pyautogui.center(pos)
            click(pos[0], pos[1])
            images.remove(img)


def collect_resource():
    res_ready_img = ['ready_food.png', 'ready_wood.png', 'ready_iron.png', 'ready_silver.png', 'ready_gold.png']
    go_kingdom()
    go_castle()
    swipe(['up'] * 3 + ['right'] * 2, interval=delay_between_clicks)
    find_click(res_ready_img)
    swipe(['up'], interval=delay_between_clicks)
    find_click(res_ready_img)
    swipe(['right'] * 4, interval=delay_between_clicks)
    find_click(res_ready_img)
    swipe(['down'] * 2, interval=delay_between_clicks)
    find_click(res_ready_img)
    go_kingdom()


def collect_tribute():
    go_kingdom()
    go_castle()
    swipe(['left'] * 4, interval=delay_between_clicks)
    haystack = pyautogui.screenshot().crop(game_screen)
    pos = pyautogui.locate(img_path('tribute.png'), haystack, confidence=0.8)
    if pos is None:
        log('Tribute is not ready')
        go_kingdom()
        return
    pos = pyautogui.center(pos)
    click(pos[0], pos[1])
    click(300, 620)
    sleep(3)
    empty_space.click()
    go_kingdom()


def repair_wall():
    go_kingdom()
    go_castle()
    swipe(['left'] * 4 + ['up'] * 3 + ['left'], interval=delay_between_clicks)
    haystack = pyautogui.screenshot().crop(game_screen)
    pos = pyautogui.locate(img_path('wall.png'), haystack, confidence=0.8)
    if pos is None:
        log('Can not find wall image')
        go_kingdom()
        return
    pos = pyautogui.center(pos)
    click(pos[0], pos[1])
    click(338, 532)
    click(162, 1044)
    back.click()
    go_kingdom()


def gather_super_mine(half=False):
    click(532, 1051)  # alliance
    click(91, 595)  # territory
    click(363, 175)  # alliance super mine

    haystack = pyautogui.screenshot().crop(game_screen)
    img = img_path('super_mine_link.png')
    pos = pyautogui.locate(img, haystack, confidence=0.9)
    if pos:
        pos = pyautogui.center(pos)
        click(pos[0], pos[1])
    else:
        go_kingdom()
        log('No super mine available')
        return False

    screen_center.click()
    sleep(3)
    if gather.visible():
        gather.click()
    else:
        log('Troop in super mine already')
        return False
    wait(march)
    if train.visible():
        back.click()
        log('No troops for gathering')
    else:
        if half:
            half_troop.click()
        march.click()
        wait(avatar)
        log('Go gathering super mine')
    return True
