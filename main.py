import random
# import threading
import time

import yaml

from core import *

# fatal_stop = False
games = []


# def ally_help_monitor():
#     global fatal_stop
#     log('[Thread start] ally help monitor')
#     while True:
#         if fatal_stop:
#             log('Stop ally_help_monitor')
#             break
#         elif ally_need_help():
#             help_ally()
#             log('Help ally complete')
#         sleep(random.randint(0, 10))
#         sleep(random.randint(0, 10))


def load_config():
    with open('config.yaml', 'r') as stream:
        config = yaml.safe_load(stream)
    return config


def initialize():
    # grab game windows
    global games
    all_hwnd = gw.getAllWindows()

    # load config file
    configs = load_config()

    valid_hwnd = [h for h in all_hwnd if h.title in configs.keys()]
    for hwnd in valid_hwnd:
        config = configs[hwnd.title]
        config['hwnd'] = hwnd
        config['title'] = hwnd.title
        config['resource_collect_time'] = 0
        config['tribute_collect_time'] = 0
        config['wall_repair_time'] = 0
        config['tribute_collect_interval'] = default_tribute_collect_interval
        games.append(config)

        # setup game windows
        hwnd.moveTo(0, 0)
        hwnd.resizeTo(game_window_size[0], game_window_size[1])
        hwnd.minimize()

    games[0]['hwnd'].restore()
    log('Initialization finished. There are {} game window(s) found.'.format(len(games)))
    log('Configurations for each game:')
    for config in games:
        log(config)
    log('Now in {}'.format(games[0]['title']))


def switch_window():
    global games
    games[0]['hwnd'].minimize()
    games.append(games.pop(0))
    games[0]['hwnd'].restore()
    log('Window switched to', games[0]['title'])
    t = time.time()
    log('resource_collect_time: {}, tribute_collect_time: {}, tribute_collect_interval: {}'
        .format(round(t - games[0]['resource_collect_time']),
                round(t - games[0]['tribute_collect_time']),
                games[0]['tribute_collect_interval']))
    # log(games[0])


def main():
    # global fatal_stop

    # initialize threads
    # fatal_stop = False
    # threads = {
    #     # ally_help_monitor,
    # }
    # for thread in threads:
    #     t = threading.Thread(target=thread)
    #     t.start()

    global games
    # main loop starts from here
    try:
        # go kingdom screen so we can update troops status
        go_kingdom()

        # wait for background threads to update status
        sleep(5)

        window_switch_timestamp = 0  # switch immediately in first loop
        while True:

            # ally help
            if ally_need_help():
                help_ally()
                log('Help ally complete')

            # dispatch troops to gather
            troop_status = update_troop_status()
            if troop_status is None:
                empty_slot = 0
            else:
                empty_slot = games[0]['troop_slot'] - len(troop_status)
            # log('[Main Loop] troop_status = {}'.format(troop_status))

            if games[0]['super_mine_gathering'] \
                    and empty_slot > 0 \
                    and gather_super_mine(half=False if empty_slot == 1 else True):
                empty_slot -= 1

            while empty_slot > 0:
                go_gathering(random.choice(games[0]['resource_type']), half=False if empty_slot == 1 else True)
                empty_slot -= 1

            # collect resources
            if time.time() - games[0]['resource_collect_time'] > 1200:  # every 20 minutes
                log('Go collecting resources')
                collect_resource()
                games[0]['resource_collect_time'] = time.time()
                log('Resources collect complete')

            # collect tribute
            if time.time() - games[0]['tribute_collect_time'] > games[0]['tribute_collect_interval']:
                log('Go collecting tribute')
                games[0]['tribute_collect_interval'] = collect_tribute()
                games[0]['tribute_collect_time'] = time.time()
                log('Tribute collect complete. Will be back in', secs2hms(games[0]['tribute_collect_interval'], 's'))

            # repair wall
            if games[0]['wall_repair'] and time.time() - games[0]['wall_repair_time'] > 1800:  # every 30 minutes
                log('Start repair wall')
                repair_wall()
                games[0]['wall_repair_time'] = time.time()
                log('Repair wall complete')

            # switch window
            if len(games) > 1 and time.time() - window_switch_timestamp > 60:  # every minute
                switch_window()
                window_switch_timestamp = time.time()

            # abnormal detection
            if get_error_msg():
                raise TimeoutError('Error screen caught in main loop')

    # except IndexError:  # should be happened from getWindowsWithTitle when no wnd title can be found:
    #     pass

    except (TimeoutError, TypeError, pyautogui.FailSafeException) as e:
        # fatal_stop = True
        # while threading.activeCount() > 1:  # wait for thread stopping
        #     log(threading.activeCount())
        #     continue
        recovery(e)

    except (KeyboardInterrupt, SystemExit):  # interrupt by user
        # fatal_stop = True
        # while threading.activeCount() > 1:  # wait for thread stopping
        #     continue
        log('Interrupt by user')


def internet_on():
    import urllib.request
    import urllib.error
    try:
        urllib.request.urlopen('http://216.58.192.142', timeout=10)
        return True
    except urllib.error.URLError:
        return False


def recovery(err):
    log('[Start recover flow]:', err)

    err = get_error_msg()
    log('[Error message]:', err)

    if err == MSG.MULTI_LOGIN:
        log('Wait for {} seconds to reconnect'.format(multi_login_restart_delay))
        sleep(multi_login_restart_delay)
        msg_confirm.click()
        sleep(60)
        empty_space.click()
        main()

    elif err == MSG.CONNECTION_FAIL:
        msg_confirm.click()
        sleep(60)
        empty_space.click()
        main()

    elif err == MSG.ABNORMAL_NETWORK:
        log('Checking internet status ...')
        while not internet_on():
            sleep(5)
        log('Internet status: OK')
        msg_confirm.click()
        sleep(60)
        main()

    elif err == MSG.LOGGED_OUT:
        log('Checking internet status ...')
        while not internet_on():
            sleep(5)
        log('Internet status: OK')
        pos = pyautogui.locateCenterOnScreen(img_path('coe_icon.png'), confidence=0.9)
        pyautogui.click(pos)
        sleep(60)
        main()

    elif err == MSG.LEVEL_UP:
        click(298, 864, delay=5)
        go_kingdom()
        main()

    else:
        log('Can not recognise the error')
        pyautogui.screenshot().save('err_' + time.strftime('%m%d%H%M%S', time.localtime()) + '.png')
        raise Exception(err)


if __name__ == '__main__':
    countdown_timer(3)
    initialize()
    main()
