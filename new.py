#!/usr/bin/env python3
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk, Gdk, GLib, AppIndicator3
import sys
import os
from collections import deque

class ClipboardManager:
    def __init__(self):
        # Обмежити історію до 15 елементів
        self.clipboard_history = deque(maxlen=10)
        
        # Створити індикатор
        self.indicator = AppIndicator3.Indicator.new(
            "clipboard-manager",
            "edit-paste-symbolic",  # стандартна іконка
            AppIndicator3.IndicatorCategory.APPLICATION_STATUS
        )
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        
        # Створити контекстне меню
        self.menu = Gtk.Menu()
        
        # Додати пункт меню для очищення історії
        clear_item = Gtk.MenuItem(label="Очистити історію")
        clear_item.connect("activate", self.clear_history)
        self.menu.append(clear_item)
        
        # Роздільник
        self.menu.append(Gtk.SeparatorMenuItem())
        
        # Область для історії clipboard
        self.history_items = []
        
        # Додати пункт виходу
        exit_item = Gtk.MenuItem(label="Вийти")
        exit_item.connect("activate", self.quit)
        self.menu.append(exit_item)
        
        self.menu.show_all()
        self.indicator.set_menu(self.menu)
        
        # Отримати доступ до системного clipboard
        self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        
        # Встановити таймер для перевірки змін у clipboard
        GLib.timeout_add(500, self.check_clipboard)
        
        # Зберегти поточний вміст clipboard
        self.last_clipboard_content = None
    
    def check_clipboard(self):
        # Отримати текст з clipboard
        text = self.clipboard.wait_for_text()
        
        if text and text != self.last_clipboard_content:
            self.last_clipboard_content = text
            self.add_to_history(text)
        
        return True  # Продовжувати перевірку
    
    def add_to_history(self, text):
        # Додати текст до історії
        self.clipboard_history.appendleft(text)
        
        # Оновити меню
        self.update_history_menu()
    
    def update_history_menu(self):
        # Видалити старі пункти меню
        for item in self.history_items:
            self.menu.remove(item)
        self.history_items = []
        
        # Додати нові пункти меню
        for i, text in enumerate(self.clipboard_history):
            # Обрізати довгий текст
            display_text = text if len(text) < 50 else text[:47] + "..."
            item = Gtk.MenuItem(label=f"{i+1}. {display_text}")
            item.connect("activate", self.on_history_item_selected, text)
            self.history_items.append(item)
            self.menu.insert(item, i)  # Вставити після статичних елементів
        
        self.menu.show_all()
    
    def on_history_item_selected(self, widget, text):
        # Встановити обраний текст у clipboard
        self.clipboard.set_text(text, -1)
        self.last_clipboard_content = text
    
    def clear_history(self, widget):
        self.clipboard_history.clear()
        self.update_history_menu()
    
    def quit(self, widget):
        Gtk.main_quit()
    
    def show_menu_near_cursor(self):
        # Отримати позицію курсора
        display = Gdk.Display.get_default()
        seat = display.get_default_seat()
        _, x, y, _ = seat.get_pointer().get_position()
        
        # Показати меню біля курсора
        self.menu.popup(
            None, None, 
            lambda menu, data: (x, y, True),
            None, 0, Gtk.get_current_event_time()
        )

if __name__ == "__main__":
    manager = ClipboardManager()
    
    # Для демонстрації можна викликати show_menu_near_cursor() при запуску
    # У реальному додатку це робитиметься при кліку на іконку
    GLib.timeout_add(1000, manager.show_menu_near_cursor)
    
    Gtk.main()