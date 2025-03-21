#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import shutil
import time
import numpy.random
import subprocess
import PIL.Image
import infi.systray

BACKGROUNDS_DIRECTORY = os.path.join(os.environ.get("UserProfile"), r"Pictures\Backgrounds")
THEMES_DIRECTORY = os.path.join(os.environ.get("AppData"), r"Microsoft\Windows\Themes")
DEST_FILE_NAME = r"TranscodedWallpaper"

DELAY_BETWEEN_UPDATES = 180  # update every 3 mn
IMAGE_EXTENSIONS = [".png", ".jpg", ".jpeg"]


class MySysTrayIcon(infi.systray.SysTrayIcon):  # update the SysTrayIcon class to be able to change
    # the menu options buttons after the start.
    def __init__(self,
                 icon,
                 hover_text,
                 menu_options=None,
                 on_quit=None,
                 default_menu_index=None,
                 window_class_name=None,
                 quit_icon=None):
        super().__init__(icon, hover_text, menu_options, on_quit, default_menu_index, window_class_name, quit_icon)
        self._quit_icon = quit_icon

    def update_menu_options(self, menu_options=None):
        menu_options = menu_options or ()
        menu_options = menu_options + (("Quit", self._quit_icon, infi.systray.SysTrayIcon.QUIT),)
        self._next_action_id = infi.systray.SysTrayIcon.FIRST_ID
        self._menu_actions_by_id = set()
        self._menu_options = self._add_ids_to_menu_options(list(menu_options))
        self._menu_actions_by_id = dict(self._menu_actions_by_id)

        self._menu = None  # delete the previous menu so that it is recreated with the new menu_options
        self._show_menu()


def test_correct_ratio():
    test_ratio = 16. / 9
    list_files = os.listdir(BACKGROUNDS_DIRECTORY)
    for image_file in list_files:
        img = PIL.Image.open(os.path.join(BACKGROUNDS_DIRECTORY, image_file))
        width = img.width
        height = img.height
        ratio = float(width) / height
        if abs(ratio - test_ratio) < .0008:
            continue
        else:
            print(image_file, round(abs(ratio - test_ratio), 6))
    sys.exit(0)


def test_correct_images():
    list_files = os.listdir(BACKGROUNDS_DIRECTORY)
    for image_file in list_files:
        if os.path.splitext(image_file)[1] not in IMAGE_EXTENSIONS:
            print(image_file)
    sys.exit(0)


TOOL_RUNNING = True
NEXT_WALLPAPER = False
PREVIOUS_WALLPAPER = False
PREVIOUS_WALLPAPERS = []


def change_background(systray: MySysTrayIcon, previous: bool = False):
    global PREVIOUS_WALLPAPERS

    if not previous:  # if next wallpaper
        list_files = os.listdir(BACKGROUNDS_DIRECTORY)
        list_images = [file for file in list_files
                       if os.path.splitext(file)[1] in IMAGE_EXTENSIONS
                       and file not in PREVIOUS_WALLPAPERS]
        image_file = numpy.random.choice(list_images)
        PREVIOUS_WALLPAPERS.append(image_file)
        if len(PREVIOUS_WALLPAPERS) > 10:  # keep in memory only the last 10 wallpapers
            PREVIOUS_WALLPAPERS.pop(0)

        elif len(PREVIOUS_WALLPAPERS) == 2:  # we're adding the second wallpaper, we can now use the previous option
            next_option, previous_option = get_menu_options()
            systray.update_menu_options(next_option + previous_option)

    else:  # previous wallpaper
        image_file = PREVIOUS_WALLPAPERS[-2]  # get previous wallpaper, -1 is the current one
        PREVIOUS_WALLPAPERS.pop()  # delete the -1

        if len(PREVIOUS_WALLPAPERS) == 1:  # we only have in memory the current wallpaper, we cannot use previous option
            next_option, _ = get_menu_options()
            systray.update_menu_options(next_option)

    shutil.copyfile(os.path.join(BACKGROUNDS_DIRECTORY, image_file), os.path.join(THEMES_DIRECTORY, DEST_FILE_NAME))
    with open(os.path.join(THEMES_DIRECTORY, DEST_FILE_NAME + "_img.txt"), "w") as f:
        f.write(image_file)  # we store the name of the image in a text file


def update_screen():
    # Powershell command to force update the wallpaper
    ps_file = os.path.join(os.path.dirname(__file__), "update_screen.ps1")
    subprocess.call(f"powershell -file \"{ps_file}\"", shell=True)


def get_menu_options():
    def go_to_next_wallpaper(_):
        global NEXT_WALLPAPER
        NEXT_WALLPAPER = True

    def go_to_previous_wallpaper(_):
        global PREVIOUS_WALLPAPER
        PREVIOUS_WALLPAPER = True

    play_icon = os.path.join(os.path.dirname(__file__), "play_icon.ico")
    previous_icon = os.path.join(os.path.dirname(__file__), "previous_icon.ico")
    next_option = (("Next Wallpaper", play_icon, go_to_next_wallpaper),)
    previous_option = (("Previous Wallpaper", previous_icon, go_to_previous_wallpaper),)

    return next_option, previous_option


def tray_icon() -> MySysTrayIcon:
    def stop(_):
        global TOOL_RUNNING
        TOOL_RUNNING = False

    icon = os.path.join(os.path.dirname(__file__), "py.ico")
    stop_icon = os.path.join(os.path.dirname(__file__), "stop_icon.ico")

    next_option, _ = get_menu_options()
    systray = MySysTrayIcon(icon, "Wallpaper Slideshow", next_option, on_quit=stop, quit_icon=stop_icon)
    systray.start()
    return systray


def main():
    global TOOL_RUNNING, NEXT_WALLPAPER, PREVIOUS_WALLPAPER
    # test_correct_ratio()
    # test_correct_images()

    systray = tray_icon()  # activate the tray icon
    # it enables to be able to quit the program, and also it allows to skip immediately to another wallpaper

    next_exec_time = 0
    while TOOL_RUNNING:
        current_time = time.perf_counter()

        if PREVIOUS_WALLPAPER:
            print("previous wallpaper")
            PREVIOUS_WALLPAPER = False
            next_exec_time = current_time + DELAY_BETWEEN_UPDATES
            change_background(systray, previous=True)
            update_screen()

        elif NEXT_WALLPAPER or current_time >= next_exec_time:
            print("next wallpaper")
            NEXT_WALLPAPER = False
            next_exec_time = current_time + DELAY_BETWEEN_UPDATES
            change_background(systray)
            update_screen()

        time.sleep(.1)  # check every tenth of second, so that it is reactive when the tray icon is deleted
        # or when a next wallpaper is asked

    print("quit")


if __name__ == "__main__":
    main()
