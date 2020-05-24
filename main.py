import random
import threading
import time

from core import *

fatal_stop = False
game_windows = []
resource_collect_time = []
tribute_collect_time = []
wall_repair_time = []


def ally_help_monitor():
    global fatal_stop
    log('[Thread start] ally help monitor')
    while True:
        if fatal_stop:
            log('Stop ally_help_monitor')
            break
        elif ally_need_help():
            help_ally()
            log('Help ally complete')
        sleep(random.randint(0, 10))
        sleep(random.randint(0, 10))


# def troop_status_monitor():
#     global troop_status
#     log('[Thread start] troop status monitor')
#     while True:
#         if fatal_stop:
#             log('Stop troop_status_monitor')
#             break
#         temp = update_troop_status()
#         if temp is None:
#             pass
#         else:
#             troop_status = temp


def initialize():
    # grab game windows
    global game_windows
    game_windows = gw.getWindowsWithTitle('BS')

    # setup game windows
    for hwnd in game_windows:
        hwnd.moveTo(0, 0)
        hwnd.resizeTo(game_window_size[0], game_window_size[1])
        hwnd.minimize()
    game_windows[0].restore()

    # initialize parameters
    global resource_collect_time
    global tribute_collect_time
    for _ in game_windows:
        resource_collect_time.append(0)
        tribute_collect_time.append(0)
        wall_repair_time.append(0)


def switch_window():
    global game_windows
    global resource_collect_time
    global tribute_collect_time

    game_windows.append(game_windows.pop(0))
    game_windows[-1].minimize()
    game_windows[0].restore()

    resource_collect_time.append(resource_collect_time.pop(0))
    tribute_collect_time.append(tribute_collect_time.pop(0))
    wall_repair_time.append(wall_repair_time.pop(0))
    log('Window switched')


def main():
    global fatal_stop

    # initialize threads
    fatal_stop = False
    threads = {
        ally_help_monitor,
    }
    for thread in threads:
        t = threading.Thread(target=thread)
        t.start()

    # main loop starts from here
    try:
        # go kingdom screen so we can update troops status
        go_kingdom()

        # wait for background threads to update status
        sleep(5)

        global resource_collect_time
        global tribute_collect_time
        global wall_repair_time
        window_switch_time = 0  # switch immediately in first loop
        while True:

            # dispatch troops to gather
            res = [ResType.FOOD, ResType.WOOD, ResType.IRON]
            troop_status = update_troop_status()
            if troop_status is None:
                empty_slot = 0
            else:
                empty_slot = troop_slot - len(troop_status)
            # log('[Main Loop] troop_status = {}'.format(troop_status))
            while empty_slot > 0:
                if empty_slot == 1:
                    if not gather_super_mine():
                        go_gathering(random.choice(res))
                elif empty_slot >= 2:
                    if not gather_super_mine(half=True):
                        go_gathering(random.choice(res), half=True)
                empty_slot -= 1

            # collect resources
            if time.time() - resource_collect_time[0] > 1200:  # every 20 minutes
                log('Go collecting resources')
                collect_resource()
                resource_collect_time[0] = time.time()
                log('Resources collect complete')

            # collect tribute
            if time.time() - tribute_collect_time[0] > 1800:  # every 30 minutes:
                log('Go collecting tribute')
                collect_tribute()
                tribute_collect_time[0] = time.time()
                log('Tribute collect complete')

            # repair wall
            if repair_wall and time.time() - wall_repair_time[0] > 1800:  # every 30 minutes:
                log('Start repair wall')
                repair_wall()
                wall_repair_time[0] = time.time()
                log('Repair wall complete')

            # switch window
            if len(game_windows) > 1 and time.time() - window_switch_time > 600:  # every 10 minutes
                switch_window()
                window_switch_time = time.time()

            sleep(10)

            # # wait or next loop and
            # n = 0
            # while n < 60:  # about 106 seconds
            #     if get_error_msg():  # check err_msg while waiting next loop
            #         log('Detected error screen when waiting next main loop start')
            #         raise TimeoutError('main.py')
            #     n += 1

            # trying to keep connection alive
            # empty_space.click()

    except IndexError:  # should be happened from getWindowsWithTitle when no wnd title can be found:
        pass

    except (TimeoutError, TypeError, pyautogui.FailSafeException) as e:
        fatal_stop = True
        while threading.activeCount() > 1:  # wait for thread stopping
            continue
        recovery(e)

    except (KeyboardInterrupt, SystemExit):  # interrupt by user
        fatal_stop = True
        while threading.activeCount() > 1:  # wait for thread stopping
            continue
        log('Interrupt by user')


def internet_on():
    import urllib.request
    import urllib.error
    try:
        urllib.request.urlopen('http://216.58.192.142', timeout=10)
        return True
    except urllib.error.URLError as err:
        return False


def recovery(err):
    log('[Start recover flow]')
    em = get_error_msg()
    log('Error message:', em)
    if em == MSG.MULTI_LOGIN:
        log('Waiting for {} seconds to reconnect'.format(multi_login_restart_delay))
        sleep(multi_login_restart_delay)
        msg_confirm.click()
        sleep(60)
        empty_space.click()
        main()

    elif em == MSG.CONNECTION_FAIL:
        msg_confirm.click()
        sleep(60)
        empty_space.click()
        main()

    elif em == MSG.ABNORMAL_NETWORK:
        log('Checking internet status ...')
        while not internet_on():
            sleep(1)
        log('Internet status: OK')
        msg_confirm.click()
        sleep(60)

    elif em == MSG.LOGGED_OUT:
        log('Checking internet status ...')
        while not internet_on():
            sleep(1)
        log('Internet status: OK')
        pos = pyautogui.locateCenterOnScreen(img_path('coe_icon.png'), confidence=0.99)
        pyautogui.click(pos)
        sleep(60)
        main()

    else:
        log('Can not recognise the error')
        pyautogui.screenshot().save('err_' + time.strftime('%m%d%H%M%S', time.localtime()) + '.png')
        raise Exception(err)


if __name__ == '__main__':
    countdown_timer(3)
    initialize()
    main()
