#!/usr/bin/env python3
import signal
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, AppIndicator3, GObject
import time
from threading import Thread

from nvidiafancontrol import FanControl

class Indicator():
    def __init__(self):
        # start fan control process
        self.fc = FanControl()
        self.fct = Thread(target=self.fc.run)
        self.fct.setDaemon(True)   
        self.fct.start()

        self.display_val = "NVIDIAX"
        self.app = 'test123'
        iconpath = "/home/yuval/bin/icon.png"
        self.indicator = AppIndicator3.Indicator.new(
            self.app, iconpath,
            AppIndicator3.IndicatorCategory.OTHER)
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)       
        self.indicator.set_menu(self.create_menu())
        self.indicator.set_label(self.display_val, self.app)
        # the thread:
        self.update = Thread(target=self.set_display)
        # daemonize the thread to make the indicator stopable
        self.update.setDaemon(True)
        self.update.start()

    def create_menu(self):
        menu = Gtk.Menu()
        # menu item 1

        # img = Gtk.Image()
        # img.set_from_file(filename)
        for stat in self.fc.status:
            item_1 = Gtk.MenuItem(stat)
            menu.append(item_1)
        # separator
        menu_sep = Gtk.SeparatorMenuItem()
        menu.append(menu_sep)
        # quit
        item_quit = Gtk.MenuItem('Quit')
        item_quit.connect('activate', self.stop)
        menu.append(item_quit)

        menu.show_all()
        return menu


    def set_display(self):
        while True:
            time.sleep(1)
            GObject.idle_add(
                self.indicator.set_label,
                self.fc.short_status, self.app,
                priority=GObject.PRIORITY_DEFAULT
                )
            menu = self.create_menu()
            GObject.idle_add(
                self.indicator.set_menu,
                menu
                )
    def stop(self, source):
        self.fc.disable_fan_control("[gpu:0]")
        self.fc.disable_fan_control("[gpu:1]")
        Gtk.main_quit()


Indicator()
# this is where we call GObject.threads_init()
GObject.threads_init()
signal.signal(signal.SIGINT, signal.SIG_DFL)
Gtk.main()
