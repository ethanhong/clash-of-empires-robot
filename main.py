import threading
import random
import time

from core import *
from parameter import TROOP_SLOT
from recovery import recovery

fatal_stop = False
resource_ready = False
troop_status = []
screen = None


def screen_monitor():
    global screen
    log('[Thread start] screen monitor')
    while True:
        if fatal_stop:
            log('Stop screen_monitor')
            break
        screen = get_screen()


def ally_help_monitor():
    log('[Thread start] ally help monitor')
    while True:
        if fatal_stop:
            log('Stop ally_help_monitor')
            break
        elif ally_need_help():
            help_ally()
            log('Help ally complete')
        sleep(1)


def troop_status_monitor():
    global troop_status
    log('[Thread start] troop status monitor')
    while True:
        if fatal_stop:
            log('Stop troop_status_monitor')
            break
        temp = update_troop_status()
        if temp is None:
            pass
        else:
            troop_status = temp


def resource_ready_timer():
    global resource_ready
    log('[Thread start] resource ready timer')
    n = 0
    while True:
        if fatal_stop:
            log('Stop resource_ready_timer')
            break
        sleep(1)
        n += 1
        if n >= 3600:  # 1 hour
            resource_ready = True
            n = 0


def main():
    # countdown to start
    countdown_timer(3)

    # setup environment
    pyautogui_init()
    game_init()
    sleep(1)  # need some time for window stable

    # initialize threads
    threads = {
        ally_help_monitor,
        troop_status_monitor,
        # resource_ready_timer,
        # screen_monitor,
    }
    for thread in threads:
        t = threading.Thread(target=thread)
        t.start()

    go_kingdom()  # go kingdom screen to update troops status
    sleep(5)  # wait for back ground threads to update status

    # main loop start here
    try:
        while True:
            log('[Main Loop] troop_status = {}, screen = {}'.format(troop_status, screen))
            if resource_ready:
                collect_resource()

            res = [ResType.FOOD, ResType.WOOD, ResType.IRON]
            empty_slot = TROOP_SLOT - len(troop_status)
            while empty_slot > 0:
                if empty_slot == 1:
                    go_gathering(random.choice(res))
                elif empty_slot >= 2:
                    go_gathering(random.choice(res), half=True)
                empty_slot -= 1

    except (TimeoutError, TypeError, pyautogui.FailSafeException) as e:
        global fatal_stop
        fatal_stop = True
        pyautogui.screenshot().save('err_' + time.strftime('%m%d%H%M%S', time.localtime()) + '.png')
        recovery()
        raise Exception(e)


if __name__ == '__main__':
    main()
