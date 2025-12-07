import time
import sys
import os
import threading
import pyperclip
from pywinauto import Application
import win32gui
import win32event
import win32api
import winerror
import winreg
import ctypes
from PIL import Image
import pystray
from sanitize import sanitize_filename, has_invalid_chars

# Configuration
CHECK_INTERVAL = 0.5
TARGET_WINDOW_TITLES = ["Save As", "另存为", "保存图片", "Save Image", "Save File", "保存文件"]
APP_NAME = "Windows Filename Sanitizer"
AUTHOR = "MuseMorphy"
VERSION = "0.1.1"
ICON_NAME = "sanitize filename icon.png"

RUNNING = True

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def is_save_dialog(title):
    for t in TARGET_WINDOW_TITLES:
        if t in title:
            return True
    return False

def sanitize_active_dialog():
    try:
        hwnd = win32gui.GetForegroundWindow()
        title = win32gui.GetWindowText(hwnd)
        class_name = win32gui.GetClassName(hwnd)
        
        if not is_save_dialog(title):
            return

        # Only process standard Windows dialogs (class #32770)
        # This prevents accidentally modifying content in apps like Word/Excel 
        # if the document title happens to contain "Save As"
        if class_name != "#32770":
            return

        app = Application(backend="win32").connect(handle=hwnd)
        dlg = app.window(handle=hwnd)
        
        edit_ctrl = None
        try:
            if dlg.Edit1.exists():
                edit_ctrl = dlg.Edit1
        except:
            pass
            
        if not edit_ctrl:
            try:
                edits = dlg.descendants(control_type="Edit")
                if edits:
                    edit_ctrl = edits[0]
            except:
                pass

        if edit_ctrl:
            current_text = edit_ctrl.window_text()
            if has_invalid_chars(current_text):
                clean_text = sanitize_filename(current_text)
                if clean_text != current_text:
                    edit_ctrl.set_text(clean_text)
    except Exception:
        pass

def monitor_clipboard():
    last_text = ""
    while RUNNING:
        try:
            text = pyperclip.paste()
            if text != last_text:
                last_text = text
                if text and '\n' not in text and len(text) < 255 and has_invalid_chars(text):
                    # Avoid sanitizing full paths if possible, simple heuristic
                    if ':\\' not in text and ':/' not in text:
                        clean_text = sanitize_filename(text)
                        if clean_text != text:
                            pyperclip.copy(clean_text)
                            last_text = clean_text
        except:
            pass
        time.sleep(1)

def monitor_dialogs():
    while RUNNING:
        sanitize_active_dialog()
        time.sleep(CHECK_INTERVAL)

def set_startup(icon, item):
    state = not item.checked
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_ALL_ACCESS)
        if state:
            exe_path = sys.executable
            if not getattr(sys, 'frozen', False):
                 exe_path = f'"{sys.executable}" "{os.path.abspath(__file__)}"'
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, exe_path)
        else:
            try:
                winreg.DeleteValue(key, APP_NAME)
            except FileNotFoundError:
                pass
        winreg.CloseKey(key)
    except Exception as e:
        print(f"Error setting startup: {e}")

def is_startup_enabled(item):
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ)
        winreg.QueryValueEx(key, APP_NAME)
        winreg.CloseKey(key)
        return True
    except FileNotFoundError:
        return False
    except Exception:
        return False

def show_about(icon, item):
    # Show about dialog in a separate thread to avoid blocking the tray icon
    def _show():
        ctypes.windll.user32.MessageBoxW(0, f"{APP_NAME}\nVersion: {VERSION}\nAuthor: {AUTHOR}", "About", 0)
    threading.Thread(target=_show, daemon=True).start() #作用是避免阻塞托盘图标，使用线程来显示对话框，target=_show表示线程执行的函数，daemon=True表示该线程为守护线程，主程序退出时该线程会自动结束。

def quit_app(icon, item):
    global RUNNING
    RUNNING = False
    icon.stop()

def main():
    # Single Instance Check
    mutex_name = "Global\\WindowsFilenameSanitizer_Mutex"
    mutex = win32event.CreateMutex(None, False, mutex_name)
    if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
        ctypes.windll.user32.MessageBoxW(0, "Windows Filename Sanitizer is already running.", "Error", 0x10)
        return

    # Start monitoring threads
    t1 = threading.Thread(target=monitor_clipboard, daemon=True)
    t2 = threading.Thread(target=monitor_dialogs, daemon=True)
    t1.start()
    t2.start()

    # Setup System Tray
    try:
        image = Image.open(resource_path(ICON_NAME))
        menu = pystray.Menu(
            pystray.MenuItem("Start on Boot", set_startup, checked=is_startup_enabled),
            pystray.MenuItem("About", show_about),
            pystray.MenuItem("Exit", quit_app)
        )
        icon = pystray.Icon(APP_NAME, image, APP_NAME, menu)
        icon.run()
    except Exception as e:
        ctypes.windll.user32.MessageBoxW(0, f"Failed to start tray icon: {e}", "Error", 0x10)

if __name__ == "__main__":
    main()
