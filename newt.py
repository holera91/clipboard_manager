#!/usr/bin/env python3
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
gi.require_version('Keybinder', '3.0')
from gi.repository import Gtk, Gdk, GLib, AppIndicator3, Keybinder
import sys
from collections import deque

class ClipboardManager:
    def __init__(self):
        self.clipboard_history = deque(maxlen=10)
        
        # Ініціалізація індикатора
        self.indicator = AppIndicator3.Indicator.new(
            "clipboard-manager",
            "edit-paste-symbolic",
            AppIndicator3.IndicatorCategory.APPLICATION_STATUS
        )
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        
        # Створення меню
        self.menu = Gtk.Menu()
        
        # Елементи меню
        clear_item = Gtk.MenuItem(label="Очистити історію")
        clear_item.connect("activate", self.clear_history)
        self.menu.append(clear_item)
        
        self.menu.append(Gtk.SeparatorMenuItem())
        
        self.history_items = []
        
        exit_item = Gtk.MenuItem(label="Вийти")
        exit_item.connect("activate", self.quit)
        self.menu.append(exit_item)
        
        self.menu.show_all()
        self.indicator.set_menu(self.menu)
        
        # Clipboard
        self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        self.last_clipboard_content = None
        
        # Ініціалізація keybinder
        Keybinder.init()
        Keybinder.bind("<Super>v", self.show_menu_shortcut)
        
        # Таймер для перевірки буферу обміну
        GLib.timeout_add(500, self.check_clipboard)
    
    def show_menu_shortcut(self, keystring, user_data):
        # Отримуємо позицію курсора
        display = Gdk.Display.get_default()
        seat = display.get_default_seat()
        _, x, y, _ = seat.get_pointer().get_position()
        
        # Показуємо меню
        self.menu.popup(
            None, None, 
            lambda menu, data: (x, y, True),
            None, 0, Gtk.get_current_event_time()
        )
        return True  # Заборонити подальшу обробку клавіш
    
    def check_clipboard(self):
        text = self.clipboard.wait_for_text()
        if text and text != self.last_clipboard_content:
            self.last_clipboard_content = text
            self.add_to_history(text)
        return True
    
    def add_to_history(self, text):
        self.clipboard_history.appendleft(text)
        self.update_history_menu()
    
    def update_history_menu(self):
        for item in self.history_items:
            self.menu.remove(item)
        self.history_items = []
        
        for i, text in enumerate(self.clipboard_history):
            display_text = text if len(text) < 50 else text[:47] + "..."
            item = Gtk.MenuItem(label=f"{i+1}. {display_text}")
            item.connect("activate", self.on_history_item_selected, text)
            self.history_items.append(item)
            self.menu.insert(item, i)
        
        self.menu.show_all()
    
    def on_history_item_selected(self, widget, text):
        self.clipboard.set_text(text, -1)
        self.last_clipboard_content = text
    
    def clear_history(self, widget):
        self.clipboard_history.clear()
        self.update_history_menu()
    
    def quit(self, widget):
        Keybinder.unbind("<Super>v")
        Gtk.main_quit()

if __name__ == "__main__":
    manager = ClipboardManager()
    Gtk.main()