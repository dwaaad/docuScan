from tkinter import *
from tkinter import ttk # provides access to the Tk themed widget set
from tkinter import filedialog
import pywinstyles, sys # for black title bar WINDOWS ONLY
import sv_ttk # tkinter sun valley theme
import darkdetect # for detecting what theme OS is set to
from PIL import ImageTk,Image # image processing

white_point = 0.5 * 255 # 0 (black) to 255 (white)
black_point = 0.99 * 255 # 99%

def scanImage():
    og_img = Image.open(filepath).convert('L') # L = Luminance | A = alpha
    mode=og_img.mode # get the mode again because we've now switched to Luminance
    
    og_pixel_map = og_img.load()# Load all pixels from the image.

    new_image = Image.new(mode, (width, height))# Create a new image matching the original image's color mode, and size.
    new_pixel_map = new_image.load() # Load all the pixels from this new image as well.

    for x in range(width):
        for y in range(height):
            # Copy the original pixel to the new pixel map.
            og_pixel = og_pixel_map[x, y]
            
            if og_pixel < white_point:
                new_pixel = 0
                new_pixel_map[x, y] = new_pixel
            if og_pixel > white_point and og_pixel < black_point:
                new_pixel = 255
                new_pixel_map[x, y] = new_pixel

    # both of these should be in the preview frame
    new_image.show()#do this with a "preview" button

    # do the following in a "save button"
    new_filename = f"scanned_{filename}"
    new_filepath = f"modified_images/{new_filename}"
    new_image.save(new_filepath)

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

    # Open image and convert it to greyscale
    og_img = Image.open(filepath)

    # Grab and store img info
    filename = og_img.filename
    width,height=og_img.size
    mode=og_img.mode

    # Show information about the original image.
    display_filepath = ttk.Label(preview,text=f"Original image: {filepath}").grid(column=0, row=0)
    display_size = ttk.Label(preview,text=f"Size: {width} x {height} pixels").grid(column=0, row=1)
    display_mode = ttk.Label(preview,text=f"Colour Mode: {mode}").grid(column=0, row=2)

    scan = ttk.Button(main,text="Scan", command=scanImage).grid(column=0,row=4)

root = Tk() # create window

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
file.add_separator()
file.add_command(label="Exit", command=root.destroy)

menu.add_cascade(label="File", menu=file) # add file sub-menu to menu bar

# View
# Appearence > Dark Mode
#              Light Mode

# Help
# Web Version
# Github Repository
# ---
# Check for Updates...
# ---
# About

#options
main = ttk.LabelFrame(root, text="Options", padding=10) # create frame
main.grid(column=0, row=0)

#image preview
preview = ttk.LabelFrame(root, text="Preview", padding=10) # create frame
preview.grid(column=1, row=0)

# METADATA SETUP

root.title("docuScan") # set title
small_icon = PhotoImage(file="../images/docuScan_favicon_x16.png")
large_icon = PhotoImage(file="../images/docuScan_favicon_x32.png")
root.iconphoto(False, large_icon, small_icon)

# WIDGETS

white_point_var = IntVar(value=50)
white_point_label = ttk.Label(main, text="White Point").grid(column=0,row=0)
white_point_slider = ttk.Scale(main, from_=0, to=100, variable=white_point_var).grid(column=0,row=1)

white_point_value_label = ttk.Label(main, textvariable=white_point_var)
white_point_value_label.grid(column=1, row=1)

print(white_point_var.get())

black_point_var = IntVar(value=99)
black_point_label = ttk.Label(main, text="Black Point").grid(column=0,row=2)
black_point_slider = ttk.Scale(main, from_=0, to=100, variable=black_point_var).grid(column=0,row=3)

black_point_value_label = ttk.Label(main, textvariable=black_point_var)
black_point_value_label.grid(column=1, row=3)

# THEMING

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

root.config(menu=menu)#display menu
root.mainloop()
