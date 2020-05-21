from recovery import recovery
from utility import *

GAME_WINDOW_SIZE = (600, 1105)


class Screen:
    CASTLE = 'castle'
    KINGDOM = 'kingdom'
    DESERT = 'desert'
    NO_AVATAR = 'no avatar'
    ERROR = 'error'
    UNKNOWN = 'unknown'


class ResType:
    MONSTER = 0
    CAMP = 1
    FOOD = 2
    WOOD = 3
    IRON = 4
    SILVER = 5


# buttons
ally_help = Button('ally_help.png', (471, 907))
kingdom = Button('kingdom.png', (105, 1015))
castle = Button('castle.png', (49, 1023))
desert_camp = Button('camp.png', (547, 881))
back = Button('back.png', (31, 80))
magnifier = Button('magnifier.png', (46, 814))
search = Button('search.png', (297, 1043))
march = Button('march.png', (505, 1045))
avatar = Button('avatar.png', (46, 81))
msg_confirm = Button('', (300, 655))
screen_center = Button('', (300, 560))
empty_space = Button('', (441, 111))
half_troop = Button('', (301, 1049))
gather = Button('', (434, 569))
monster = Button('', (67, 820))
camp = Button('', (161, 820))
farm = Button('', (260, 820))
sawmill = Button('', (355, 820))
iron_mine = Button('', (448, 820))
slv_mine = Button('', (540, 820))
res_coord = [monster, camp, farm, sawmill, iron_mine, slv_mine]

# haystack areas
game_screen = (0, 0, GAME_WINDOW_SIZE[0], GAME_WINDOW_SIZE[1])
prompt_msg = (85, 450, 517, 690)


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
            found = btn.visible_in(haystack)

        if found:
            break

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


def pyautogui_init():
    log('Initialize PyAutoGui')
    pyautogui.FAILSAFE = True


def game_init():
    log('Initialize game window')
    import win32gui
    import win32con
    hwnd = win32gui.FindWindow(None, 'BlueStacks')
    win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
    win32gui.SetForegroundWindow(hwnd)
    win32gui.MoveWindow(hwnd, 0, 0, GAME_WINDOW_SIZE[0], GAME_WINDOW_SIZE[1], True)


def ally_need_help():
    return ally_help.is_visible()


def help_ally():
    ally_help.click()


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
    if (castle.is_visible() and not desert_camp.is_visible()) \
            or search.is_visible():
        im = pyautogui.screenshot()
        for area in troop_info_area:
            for status, img in ts_images.items():
                try:
                    if pyautogui.locate(img_path(img), im.crop(area), confidence=0.9):
                        result.append(status)
                        break
                except IOError:
                    log('File is missing:', img_path(img))
        return result
    else:
        pass


def get_screen():
    buttons = {
        desert_camp: Screen.DESERT,  # desert should be check first or it will mis-judge to kingdom
        back: Screen.NO_AVATAR,
        castle: Screen.KINGDOM,
        kingdom: Screen.CASTLE,
    }
    result = Screen.UNKNOWN
    for btn, srn in buttons.items():
        if btn.is_visible():
            result = srn
            break
    return result


def go_kingdom():
    while back.is_visible():
        back.click()
        sleep(1)
    try:
        wait(castle)
    except TimeoutError:
        kingdom.click()
        wait(castle, timeout=60)
        log('go_kingdom complete')


def go_gathering(res, half=False):
    try:
        go_kingdom()
        magnifier.click()
        wait(search)
        res_coord[res].click()
        search.click()
        sleep(5)
        screen_center.click()
        gather.click()
    except (TimeoutError, TypeError):
        recovery()
        return

    try:
        wait(march)
    except TimeoutError:
        back.click()
        log('No troops for gathering')
    else:
        if half:
            half_troop.click()
        march.click()
        try:
            wait(avatar)
            log('Troops go gathering {}'.format(res))
        except TimeoutError:
            log('No march slot available')
            back.click(2)
            wait(avatar)


def collect_resource():  # todo: collect resources
    pass
