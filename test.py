#!/usr/bin/env python3
import tkinter as tk
from tkinter import Menu
from pynput import keyboard
import subprocess
from collections import deque
import sys

class ClipboardManager:
    def __init__(self):
        self.history = deque(maxlen=10)
        self.root = tk.Tk()
        self.root.withdraw()
        self.current_menu = None
        self.last_clip = ""
        
        # Комбінація клавіш (змініть на потрібну)
        self.hotkey = keyboard.GlobalHotKeys({
            '<ctrl>+<alt>+v': self.show_menu  # Використовуємо Ctrl+Alt+V як альтернативу
        })
        self.hotkey.start()
        
        self.check_clipboard()

    def check_clipboard(self):
        try:
            current = subprocess.check_output(
                ['xclip', '-o', '-selection', 'clipboard'],
                stderr=subprocess.DEVNULL
            ).decode('utf-8').strip()
            
            if current and current != self.last_clip:
                self.history.appendleft(current)
                self.last_clip = current
        except:
            pass
            
        self.root.after(500, self.check_clipboard)

    def show_menu(self):
        if not self.history or self.current_menu:
            return
            
        self.current_menu = Menu(self.root, tearoff=0)
        
        for idx, item in enumerate(self.history):
            label = f"{idx+1}. {item[:50]}..." if len(item) > 50 else item
            self.current_menu.add_command(
                label=label,
                command=lambda t=item: self.paste_text(t)
            )
        
        # Позиція курсора (спрощений спосіб)
        x = self.root.winfo_pointerx()
        y = self.root.winfo_pointery()
        self.current_menu.tk_popup(x, y)
        
        # Закриття меню при кліку поза ним
        self.current_menu.bind("<Unmap>", lambda e: self.close_menu())

    def close_menu(self):
        if self.current_menu:
            self.current_menu.destroy()
            self.current_menu = None

    def paste_text(self, text):
        try:
            subprocess.run(
                ['xclip', '-selection', 'clipboard'],
                input=text.encode('utf-8'),
                check=True
            )
            # Імітація Ctrl+V
            controller = keyboard.Controller()
            with controller.pressed(keyboard.Key.ctrl):
                controller.press('v')
                controller.release('v')
        finally:
            self.close_menu()

    def run(self):
        try:
            self.root.mainloop()
        finally:
            self.hotkey.stop()

if __name__ == "__main__":
    # Перевірка залежностей
    try:
        import pynput
        # Перевірка доступності xclip
        subprocess.check_output(['which', 'xclip'], stderr=subprocess.DEVNULL)
    except (ImportError, subprocess.CalledProcessError):
        print("Потрібні бібліотеки:")
        print("1. Встановіть pynput: pip install pynput")
        print("2. Встановіть xclip: sudo apt install xclip")
        sys.exit(1)
    
    ClipboardManager().run()