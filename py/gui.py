from tkinter import *
from tkinter import ttk # provides access to the Tk themed widget set
from tkinter import filedialog
from tkinter import messagebox # for update dialog
import pywinstyles, sys # for black title bar WINDOWS ONLY
import sv_ttk # tkinter sun valley theme
import darkdetect # for detecting what theme OS is set to
from PIL import ImageTk,Image # image processing
import webbrowser # for opening links
import os # for extracting just the file name of the image
import requests # for checking updates through GitHub API

def updateCheck():
    url = "https://api.github.com/repos/dwaaad/docuScan/releases/latest"
    data = requests.get(url).json()
    if data["tag_name"] != APP_VERSION:
        update_response = messagebox.askokcancel("New version available!", "A newer version is available, would you like to update?")
        if update_response == 1:
            webbrowser.open("https://api.github.com/repos/dwaaad/docuScan/releases/latest")

#auto update on start
startup_update = True
if startup_update:
    updateCheck()

global theme
theme = darkdetect.theme()#replace darkdetect.theme() with accessing a save.txt in which the default value is set to darkdetect.theme()

white_point = 0.5 * 255 # 0 (black) to 255 (white)
black_point = 0.99 * 255 # 99%

def scanImage():
    global new_image # for the saveFile() function
    # Open image and convert it to greyscale
    og_img = Image.open(filepath).convert('LA') # L = luminance | A = alpha
    mode=og_img.mode # get the mode again because we've now switched to Luminance
    
    og_pixel_map = og_img.load()# Load all pixels from the image.

    new_image = Image.new(mode, (width, height))# Create a new image matching the original image's color mode, and size.
    new_pixel_map = new_image.load() # Load all the pixels from this new image as well.

    for x in range(width):
        for y in range(height):
            # Copy the original pixel to the new pixel map.
            og_pixel = og_pixel_map[x, y]
            og_l = og_pixel[0] # luminance
            og_a = og_pixel[1] # alpha
            
            if og_pixel[0] < white_point:
                new_pixel = (0, og_a)
                new_pixel_map[x, y] = new_pixel
            if og_pixel[0] > white_point and og_pixel[0] < black_point:
                new_pixel = (255, og_a)
                new_pixel_map[x, y] = new_pixel

    # both of these should be in the preview frame
    new_image.show()#do this when the user double clicks the previewed image in the pireview panel
    save.config(state="normal")

def openFile():
    global filepath, width, height, filename
    
    all_exts = Image.registered_extensions()# Get all registered Pillow extensions
    supported_exts = [ext.lower() for ext, fmt in all_exts.items() if fmt in Image.SAVE]

    #join these into one string for the open file dialog
    img_filter = " ".join(f"*{ext}" for ext in supported_exts)
    
    filepath = filedialog.askopenfilename(
        initialdir="/original_images",
        title="Select Image to be Scanned",
        filetypes=(("Image files", img_filter), ("All files", "*.*"))
    )

    try:# Open image and display info
        og_img = Image.open(filepath)

        # Grab and store img info
        filename = os.path.basename(og_img.filename)
        size_bytes = os.path.getsize(filepath)
        width,height=og_img.size
        mode=og_img.mode

        # Show information about the original image.
        clearFrame(details)#instead of disclaimer.grid_forget()
        display_filepath = ttk.Label(details,text=f"Original image: {filepath}").grid(column=0, row=0)
        display_size = ttk.Label(details,text=f"Size: {width} x {height} pixels").grid(column=0, row=1)
        display_mode = ttk.Label(details,text=f"Colour Mode: {mode}").grid(column=0, row=2)
        display_bytes = ttk.Label(details,text=f"File Size: {size_bytes} bytes").grid(column=0, row=3)

        # activate buttons so that they are clickable
        white_point_slider.config(state="normal")
        black_point_slider.config(state="normal")
        scan.config(state="normal")

    except Image.UnidentifiedImageError:
        disclaimer.grid_forget()
        wrong_image = ttk.Label(details,text=f"Error: {filepath} is either corrupted or not supported.").grid(column=0, row=0)

def openRepo():
    webbrowser.open("https://github.com/dwaaad/docuScan")

def openWebsite():
    webbrowser.open("https://dwaaad.github.io/docuScan/")

def themeDark():
    theme = "dark"#save this preference to a .txt
    sv_ttk.set_theme(theme)
    apply_theme_to_titlebar(root)

def themeLight():
    theme = "light"#save this preference to a .txt
    sv_ttk.set_theme(theme)
    apply_theme_to_titlebar(root)

def themeAuto():
    theme = darkdetect.theme()#save this preference to a .txt
    sv_ttk.set_theme(theme)
    apply_theme_to_titlebar(root)

def clearFrame(frame):
    for widget in frame.winfo_children():
        widget.destroy()

def saveFile():
    new_filename = f"scanned_{filename}"
    new_filepath = f"modified_images/{new_filename}"
    new_image.save(new_filepath)
    exe_dir = os.path.dirname(os.path.abspath(__file__))
    exe_dir = exe_dir.replace("\\", "/") # replace backslashes with forward slashes for consistency
    display_save = ttk.Label(details,text=f"\nSucessfully saved new image to: {exe_dir}/{new_filepath}").grid(column=0, row=4)
    # give some kind of option to open the image either by double clicking as a link or using button or what

root = Tk() # create window

# METADATA SETUP
root.resizable(False, False)
root.title("docuScan") # set title
small_icon = PhotoImage(file="../images/docuScan_favicon_x16.png")
large_icon = PhotoImage(file="../images/docuScan_favicon_x32.png")
root.iconphoto(False, large_icon, small_icon)
global APP_VERSION
APP_VERSION = "v0.2.0-alpha"

#navbar menu
menu = Menu(root)
if darkdetect.theme() == "dark":
    menu.configure(
        bg="#1c1c1c",
        fg="white",
        activebackground="#2a2a2a",
        activeforeground="white"
    )


file = Menu(menu, tearoff=0)
file.add_command(label="Open", command=openFile)
file.add_command(label="Recent Files")
file.add_separator()
file.add_command(label="Exit", command=root.destroy)

menu.add_cascade(label="File", menu=file) # add file sub-menu to menu bar


view = Menu(menu, tearoff=0)
menu.add_cascade(label="View", menu=view)

theme = Menu(view, tearoff=0)
theme.add_command(label="Auto")
theme.add_command(label="Dark Mode", command=themeDark)
theme.add_command(label="Light Mode", command=themeLight)

view.add_cascade(label="Appearence", menu=theme)


helpMenu = Menu(menu, tearoff=0)
helpMenu.add_command(label="Web Version", command=openWebsite)
helpMenu.add_command(label="GitHub Repository", command=openRepo)
helpMenu.add_separator()

updates = Menu(menu,tearoff=0)
updates.add_command(label="Check Now", command=updateCheck)
updates.add_checkbutton(label="Check on Start", variable=startup_update)
helpMenu.add_cascade(label="Check for Updates...", menu=updates)

helpMenu.add_separator()
helpMenu.add_command(label="About")
menu.add_cascade(label="Help", menu=helpMenu)

#options
main = ttk.LabelFrame(root, text="Options (NOT FUNCTIONAL YET)", padding=20) # create frame
main.grid(column=0, row=0, padx=(30,0), pady=(30,15))

#image details
details = ttk.LabelFrame(root, text="Details", padding=20) # create frame
details.grid(column=1, row=0, padx=30, pady=(30,15))

disclaimer = ttk.Label(details,text="Image details appear here once you select an image.\n\nTo choose an image, navigate to File > Open")
disclaimer.grid(column=1, row=0)

#preview
preview = ttk.LabelFrame(root, text="Preview", padding=20) # create frame
preview.grid(column=1, row=1, padx=30, pady=(0,30))

preview_text = ttk.Label(preview,text="No image selected.")
preview_text.grid(column=1, row=1)

#buttons
buttons = ttk.Frame(root, padding=20) # create frame
buttons.grid(column=0, row=1, padx=(30,0), pady=(0,30))

# WIDGETS
#white point settings
white_point_var = IntVar(value=50)
white_point_label = ttk.Label(main, text="White Point")
white_point_label.grid(column=0,row=0)
white_point_slider = ttk.Scale(main, from_=0, to=100, variable=white_point_var, state="disabled")
white_point_slider.grid(column=0,row=1, pady=(0,10))

white_point_value_label = ttk.Label(main, textvariable=white_point_var)
white_point_value_label.grid(column=1, row=1, padx=(5,0))

#black point settings
black_point_var = IntVar(value=99)
black_point_label = ttk.Label(main, text="Black Point")
black_point_label.grid(column=0,row=2, pady=(10,0))
black_point_slider = ttk.Scale(main, from_=0, to=100, variable=black_point_var, state="disabled")
black_point_slider.grid(column=0,row=3)

black_point_value_label = ttk.Label(main, textvariable=black_point_var)
black_point_value_label.grid(column=1, row=3, padx=(5,0))

#scan button
scan = ttk.Button(buttons,text="Scan", command=scanImage, state="disabled", style="Accent.TButton")
scan.grid(column=0,row=0, padx=(0,5))
#save button
save = ttk.Button(buttons,text="Save", command=saveFile, state="disabled")
save.grid(column=1,row=0, padx=(5,0))

# THEMING

sv_ttk.set_theme(theme) # set theme depending on user choice

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

root.config(menu=menu)#display menu
root.mainloop()
