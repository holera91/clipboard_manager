#!/usr/bin/env python3
import tkinter as tk
from tkinter import Menu
from pynput import keyboard, mouse
import time
import sys
from collections import deque
import subprocess

class ClipboardManager:
    def __init__(self):
        self.history = deque(maxlen=10)
        self.root = tk.Tk()
        self.root.withdraw()
        self.current_menu = None  # Для відстеження поточного меню
        self.setup_global_hotkey()
        self.setup_clipboard_monitor()
        self.last_clip = ""

        # Відстежуємо кліки мишкою
        self.mouse_listener = mouse.Listener(on_click=self.on_mouse_click)
        self.mouse_listener.start()

    def setup_global_hotkey(self):
        self.hotkey = keyboard.GlobalHotKeys({
            '<cmd>+v': self.show_menu
        })
        self.hotkey.start()

    def setup_clipboard_monitor(self):
        self.root.after(500, self.check_clipboard)

    def check_clipboard(self):
        try:
            current = subprocess.check_output(
                ['xclip', '-o', '-selection', 'clipboard'],
                stderr=subprocess.DEVNULL
            ).decode('utf-8').strip()
            
            if current and current != self.last_clip:
                self.history.appendleft(current)
                self.last_clip = current
                
        except subprocess.CalledProcessError:
            pass
        except Exception:
            pass
            
        self.root.after(500, self.check_clipboard)

    def show_menu(self):
        if not self.history:
            return
            
        self.current_menu = Menu(self.root, tearoff=0)
        for idx, item in enumerate(self.history):
            label = f"{idx+1}. {item[:50]}..." if len(item) > 50 else item
            self.current_menu.add_command(
                label=label,
                command=lambda text=item: self.paste_text(text)
            )
        
        # Додаємо обробник закриття меню
        self.current_menu.bind("<Unmap>", lambda e: self.on_menu_close())
        
        x, y = self.get_mouse_pos()
        self.current_menu.tk_popup(x, y)

    def on_mouse_click(self, x, y, button, pressed):
        # Якщо меню відкрите і клік поза ним
        if pressed and self.current_menu and button == mouse.Button.left:
            menu_x = self.current_menu.winfo_rootx()
            menu_y = self.current_menu.winfo_rooty()
            menu_width = self.current_menu.winfo_width()
            menu_height = self.current_menu.winfo_height()
            
            if not (menu_x <= x <= menu_x + menu_width and 
                    menu_y <= y <= menu_y + menu_height):
                self.current_menu.destroy()
                self.current_menu = None

    def on_menu_close(self):
        self.current_menu = None

    def get_mouse_pos(self):
        controller = mouse.Controller()
        return controller.position

    def paste_text(self, text):
        try:
            subprocess.run(
                ['xclip', '-selection', 'clipboard'],
                input=text.encode('utf-8'),
                check=True
            )
            kb = keyboard.Controller()
            with kb.pressed(keyboard.Key.ctrl):
                kb.press('v')
                kb.release('v')
        except Exception:
            pass
        finally:
            if self.current_menu:
                self.current_menu.destroy()
                self.current_menu = None

    def run(self):
        self.root.mainloop()

    def __del__(self):
        if self.mouse_listener:
            self.mouse_listener.stop()

if __name__ == "__main__":
    try:
        import pynput
    except ImportError:
        print("Встановіть pynput: pip install pynput")
        sys.exit(1)
    
    ClipboardManager().run()