import threading
import random
import time

from core import *
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
        sleep(10)


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

    go_kingdom()  # go kingdom screen so we can update troops status
    sleep(5)  # wait for background threads to update status

    # main loop starts from here
    try:
        global resource_ready
        resource_ready = True  # collect resource in the beginning
        while True:
            log('[Main Loop] troop_status = {}, screen = {}'.format(troop_status, screen))

            # dispatch troops to gather
            res = [ResType.FOOD, ResType.WOOD, ResType.IRON]
            empty_slot = troop_slot - len(troop_status)
            while empty_slot > 0:
                if empty_slot == 1:
                    go_gathering(random.choice(res))
                elif empty_slot >= 2:
                    go_gathering(random.choice(res), half=True)
                empty_slot -= 1

            # collect resources
            if resource_ready:
                collect_resource()
                resource_ready = False
                log('Resources collect complete')

            # wait or next loop
            sleep(60)  # main loop every 60 seconds

    except IndexError:  # should be happened from getWindowsWithTitle when no wnd title can be found:
        pass

    except (TimeoutError, TypeError, pyautogui.FailSafeException) as e:
        global fatal_stop
        fatal_stop = True
        pyautogui.screenshot().save('err_' + time.strftime('%m%d%H%M%S', time.localtime()) + '.png')
        recovery()
        raise Exception(e)


if __name__ == '__main__':
    main()
