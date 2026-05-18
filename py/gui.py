from tkinter import *
from tkinter import ttk # modern gui
import pywinstyles, sys # for black title bar WINDOWS ONLY
import sv_ttk # tkinter sun valley theme
import darkdetect # for detecting what theme OS is set to

root = Tk() # create window
root.title("docuScan") # set title

main = ttk.Frame(root, padding=10) # create frame
main.grid()

ttk.Label(main, text="Hello World!").grid(column=0, row=0)
ttk.Button(main, text="Quit", command=root.destroy).grid(column=1, row=0)

sv_ttk.set_theme(darkdetect.theme()) # set theme depending on current OS theme

def apply_theme_to_titlebar(root): # windows only
    import platform
    if platform.system() != "Windows":
        return  # do nothing on macOS/Linux
    
    version = sys.getwindowsversion()

    if version.major == 10 and version.build >= 22000:
        # Set the title bar color to the background color on Windows 11 for better appearance
        pywinstyles.change_header_color(root, "#1c1c1c" if sv_ttk.get_theme() == "dark" else "#fafafa")
    elif version.major == 10:
        pywinstyles.apply_style(root, "dark" if sv_ttk.get_theme() == "dark" else "normal")

        # A hacky way to update the title bar's color on Windows 10 (it doesn't update instantly like on Windows 11)
        root.wm_attributes("-alpha", 0.99)
        root.wm_attributes("-alpha", 1)

apply_theme_to_titlebar(root)

root.mainloop()
