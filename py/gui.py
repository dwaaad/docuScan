from tkinter import * # for GUI
from tkinter import ttk # provides access to the Tk themed widget set
from tkinter import filedialog # for picking file
from tkinter import messagebox # for popup update dialog
import pywinstyles, sys # for black title bar WINDOWS ONLY
import sv_ttk # tkinter sun valley theme
import darkdetect # for detecting what theme OS is set to
from PIL import ImageTk,Image # image processing
import webbrowser # for opening links
import os # for extracting just the file name of the image
import requests # for checking updates through GitHub API
import re # regex for extracting version number from APP_VERSION and GitHub tag

global APP_VERSION
APP_VERSION = "v0.3.1-beta"

# retrieve windows system accent colour
win_accent = pywinstyles.get_accent_color()

white_point = 0.99 * 255 # 99% - the upper bound degree to which a white pixel is turned black

def scanImage():
    global new_image # for the saveFile() function

    # set Black Point based on slider
    slider_black_point = black_point_slider.get()
    black_point = (slider_black_point / 100) * 255 # 0 (black) to 255 (white)

    # Open image and convert it to greyscale
    og_img = Image.open(filepath).convert('L') # L = luminance | A = alpha
    mode=og_img.mode # get the mode again because we've now switched to Luminance
    
    og_pixel_map = og_img.load()# Load all pixels from the image.

    new_image = Image.new(mode, (width, height))# Create a new image matching the original image's color mode, and size.
    new_pixel_map = new_image.load() # Load all the pixels from this new image as well.

    for x in range(width):
        for y in range(height):
            # Copy the original pixel to the new pixel map.
            og_pixel = og_pixel_map[x, y]
            
            if og_pixel < black_point:
                new_pixel = 0
                new_pixel_map[x, y] = new_pixel
            if og_pixel > black_point and og_pixel < white_point:
                new_pixel = 255
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

    if not filepath: # user closed file dialog popup
        return # exit the function safely
    
    # if the user selects an openable file but an unsavable one then offer a convertion
    unsupported_exts = [ext.lower() for ext, fmt in all_exts.items() if fmt in Image.OPEN]
    filename, extension = os.path.splitext(filepath)# splits ('C:/Users/Dwad/Downloads/Doc1', '.pdf') into two variables
    if extension.lower() in unsupported_exts and extension.lower() not in supported_exts:
        convert_response = messagebox.askokcancel("Unsupported file type!", f"File type unsupported. Do you want to convert to .PNG and continue?\n\nNote: the converted file will be saved to {filename + '.png'}", icon="warning")
        if convert_response == True:
            new_path = filename + ".png"
            filepath = Image.open(filepath).convert("RGB").save(new_path, "PNG")
            filepath = new_path # switch to new path
        else:
            return # exit the function safely

    try:# Open image and display info
        og_img = Image.open(filepath)

        filename = os.path.basename(og_img.filename)

        # Grab and store img info
        size_bytes = os.path.getsize(filepath)
        width,height=og_img.size
        mode=og_img.mode

        # Show information about the original image.
        clearFrame(details)
        display_filepath = ttk.Label(details,text=f"Original image: {filepath}").grid(column=0, row=0)
        display_size = ttk.Label(details,text=f"Size: {width} x {height} pixels").grid(column=0, row=1)
        display_mode = ttk.Label(details,text=f"Colour Mode: {mode}").grid(column=0, row=2)
        display_bytes = ttk.Label(details,text=f"File Size: {size_bytes} bytes").grid(column=0, row=3)

        # activate buttons so that they are clickable
        black_point_slider.config(state="normal")
        black_point_spin.config(state="normal")
        scan.config(state="normal")

    except Image.UnidentifiedImageError:
        clearFrame(details)
        filename, extension = os.path.splitext(filepath)# splits ('C:/Users/Dwad/Downloads/Doc1', '.pdf') into two variables
        if extension.lower() == ".pdf":
            ttk.Label(details,text=f"Error: PDF must have image metadata, not text.").grid(column=0, row=0)
        else:
            ttk.Label(details,text=f"Error: File is either corrupted or unsupported.").grid(column=0, row=0)

def openRepo():
    webbrowser.open("https://github.com/dwaaad/docuScan")

def openWebsite():
    webbrowser.open("https://dwaaad.github.io/docuScan/")

def themeDark():
    theme = "dark"#save this preference to a .txt
    sv_ttk.set_theme(theme)
    apply_theme_to_titlebar(root)
    menubar.reload()

def themeLight():
    theme = "light"#save this preference to a .txt
    sv_ttk.set_theme(theme)
    apply_theme_to_titlebar(root)
    menubar.reload()

def themeAuto():
    theme = darkdetect.theme()#save this preference to a .txt
    sv_ttk.set_theme(theme)
    apply_theme_to_titlebar(root)
    menubar.reload()

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

def extractVersion(tag):
    match = re.search(r"\d+\.\d+\.\d+", tag)
    return match.group(0) if match else None

def updateCheck():
    # get latest version by loading the latest repo link
    url = "https://github.com/dwaaad/docuScan/releases/latest"

    # request without redirecting
    request = requests.get(url, allow_redirects=False)

    # extract version number tag from URL redirect
    latest_tag = request.headers["Location"].split("/")[-1]# GitHub should return a redirect with a Location header
    latest_version = extractVersion(latest_tag)
    current_version = extractVersion(APP_VERSION)

    # compare version numbers
    if latest_version > current_version:
        update_response = messagebox.askyesno("New version available!", f"docuScan {latest_tag} is available. You're using {APP_VERSION}.\n\nOpen link to download page?")
        if update_response == True:
            webbrowser.open("https://github.com/dwaaad/docuScan/releases/latest")

# custom menubar
class MenuBar(Frame): # a lot of this class was written with the help of Copilot
    # Source: https://stackoverflow.com/a/74974555
    # Author: user4136999
    # Retrieved: 2026-05-20
    # License: CC BY-SA 4.0
    #
    # This class contains derivative work based on the above source.
    # It is therefore licensed under CC BY-SA 4.0.
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master=master

        # get theme
        self.theme = sv_ttk.get_theme()

        # Theme colours
        self.dark = {
            "bg": "#1c1c1c",
            "fg": "white",
            "activebackground": "#2a2a2a",
            "activeforeground": "white"
        }

        self.light = {
            "bg": "white",
            "fg": "black",
            "activebackground": "#e5f3ff",
            "activeforeground": "black"
        }

        # Pick theme
        if self.theme == "dark": self.colours = self.dark
        if self.theme == "light": self.colours = self.light

        # Update background
        self.configure(bg=self.colours["bg"])

        border = Frame(self, height=1, bg=self.colours["activebackground"])
        border.pack(side="bottom", fill="x")

        # container for buttons
        self.button_area = Frame(self, bg=self.colours["bg"])
        self.button_area.pack(side="top", fill="x")

        # bottom border
        self.border = Frame(self, height=1, bg=self.colours["activebackground"])
        self.border.pack(side="bottom", fill="x")

        # Build menus using helper functions
        self.build_menus()

    def make_button(self, parent, text):
        btn = Menubutton(
            parent,
            text=text,
            bg=self.colours["bg"],
            fg=self.colours["fg"],
            activebackground=self.colours["activebackground"],
            activeforeground=self.colours["activeforeground"],
            padx=10
        )
        return btn

    def make_menu(self, parent):
        return Menu(
            parent,
            tearoff=0,
            bg=self.colours["bg"],
            fg=self.colours["fg"],
            activebackground=self.colours["activebackground"],
            activeforeground=self.colours["activeforeground"]
        )

    def build_menus(self):

        # FILE
        file_btn = self.make_button(self, "File")
        file_menu = self.make_menu(file_btn)

        file_menu.add_command(label="Open", command=openFile)
        file_menu.add_command(label="Recent Files")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=root.destroy)

        file_btn.config(menu=file_menu)
        file_btn.pack(in_=self.button_area,side="left")

        # VIEW
        view_btn = self.make_button(self, "View")
        view_menu = self.make_menu(view_btn)

        # Appearance submenu
        theme_menu = self.make_menu(view_menu)
        theme_menu.add_command(label="[x] Auto", command=themeAuto)# make this a checked/unchecked button
        theme_menu.add_command(label="[ ] Dark Mode", command=themeDark)# make this a checked/unchecked button
        theme_menu.add_command(label="[ ] Light Mode", command=themeLight)# make this a checked/unchecked button

        view_menu.add_cascade(label="Appearance", menu=theme_menu)
        view_menu.add_separator()
        view_menu.add_command(label="[x] Show Details")# make this a checked/unchecked button

        view_btn.config(menu=view_menu)
        view_btn.pack(in_=self.button_area,side="left")

        # HELP
        help_btn = self.make_button(self, "Help")
        help_menu = self.make_menu(help_btn)

        help_menu.add_command(label="Web Version", command=openWebsite)
        help_menu.add_command(label="GitHub Repository", command=openRepo)
        help_menu.add_separator()

        # Updates submenu
        updates_menu = self.make_menu(help_menu)
        updates_menu.add_command(label="Check Now", command=updateCheck)
        updates_menu.add_checkbutton(label="Check on Start", variable=startup_update)

        help_menu.add_cascade(label="Check for Updates...", menu=updates_menu)
        help_menu.add_separator()
        help_menu.add_command(label="About")

        help_btn.config(menu=help_menu)
        help_btn.pack(in_=self.button_area,side="left")

    def reload(self):
        # Get theme again
        self.theme = sv_ttk.get_theme()

        # Pick theme
        if self.theme == "dark": self.colours = self.dark
        if self.theme == "light": self.colours = self.light

        # Update background
        self.configure(bg=self.colours["bg"])

        # Destroy old menu buttons
        for widget in self.winfo_children():
            widget.destroy()

        # recreate button area
        self.button_area = Frame(self, bg=self.colours["bg"])
        self.button_area.pack(side="top", fill="x")

        # recreate border
        self.border = Frame(self, height=1, bg=self.colours["activebackground"])
        self.border.pack(side="bottom", fill="x")

        # rebuild menus
        self.build_menus()

class Limiter(ttk.Scale):
    # Source - https://stackoverflow.com/a/54318377
    # Posted by martineau, modified by community. See post 'Timeline' for change history
    # Retrieved 2026-05-21, License - CC BY-SA 4.0
    #
    # This class contains modified work based on the above source.
    # It is therefore licensed under CC BY-SA 4.0.
    """ ttk.Scale sublass that limits the precision of values. """

    def __init__(self, *args, **kwargs):
        self.precision = kwargs.pop('precision')  # Remove non-std kwarg.
        self.chain = kwargs.pop('command', lambda *a: None)  # Save if present.
        super(Limiter, self).__init__(*args, command=self._value_changed, **kwargs)

    def _value_changed(self, newvalue):
        newvalue = float(newvalue)
        newvalue = round(newvalue, self.precision)

        # If precision is 0, convert to int so you get "50" not "50.0"
        if self.precision == 0:
            newvalue = int(newvalue)

        self.winfo_toplevel().globalsetvar(self.cget('variable'), newvalue)
        self.chain(newvalue)

root = Tk() # create window

sv_ttk.set_theme(darkdetect.theme())#replace darkdetect.theme() with accessing a save.txt in which the default value is set to darkdetect.theme()

startup_update = BooleanVar(value=True)#auto update on start set to True by default
# this jsut has to = true inside a function when I end up saving it to a .txt

# METADATA SETUP
root.resizable(False, False)
root.title("docuScan") # set title
small_icon = PhotoImage(file="icons/docuScan_favicon_x16.png")
large_icon = PhotoImage(file="icons/docuScan_favicon_x32.png")
root.iconphoto(False, large_icon, small_icon)

#navbar menu
menubar = MenuBar(root)
menubar.pack(side="top", fill="x")

content = Frame(root)
content.pack(fill="both", expand=True)

# OPTIONS FRAME

options = ttk.LabelFrame(content, text="Options", padding=20) # create frame
options.grid(column=0, row=0, padx=(30,0), pady=(30,0))

#Black Point settings
black_point_var = IntVar(value=50)
black_point_label = ttk.Label(options, text="Black Point")
black_point_label.grid(column=0, columnspan=2, row=2, pady=(0,10))
black_point_slider = Limiter(options, from_=0, to=100, precision=0, variable=black_point_var, state="disabled")
black_point_slider.grid(column=0, columnspan=2, row=3)

black_point_value_label = ttk.Label(options, textvariable=black_point_var)
black_point_value_label.grid(column=1, columnspan=2, row=3, padx=(5,0))

def validateBlackPoint(new_value):
    if new_value == "":
        return True  # allow empty while typing
    if new_value.isdigit():
        num = int(new_value)
        return 0 <= num <= 100
    return False

# "validatecommand" and "invalidcommand" both use a Tcl/Tk command, which cannot call Python functions directly.
# So we need to register a Tcl command that represents the validateBlackPoint() function
vcmd = (root.register(validateBlackPoint), "%P")# "%P" Tcl placeholder representing any new value after a key press
# the above becomes something like: validatecommand="pyfunc12345 %P"
# Tcl will call: pyfunc12345 <new_value>
# which Tkinter translates into: validateBlackPoint("<new_value>")
black_point_spin = ttk.Spinbox(options, from_=0, to=100, textvariable=black_point_var, state="disabled", validate="key", validatecommand=vcmd)# validate="key" means run the validatecommand everytime there is a key input
black_point_spin.grid(column=0, columnspan=2, row=4, pady=(10,0))

# VERTICAL SEPARATOR

separator = ttk.Separator(content, orient="vertical")
separator.grid(column=1, row=0, rowspan=2, sticky="ns", padx=30, pady=10)

# PREVIEW FRAME

preview = ttk.LabelFrame(content, text="Preview", padding=20) # create frame
preview.grid(column=2, row=0, padx=(0,30), pady=(30,15))

preview_text = ttk.Label(preview,text="No image selected.")
preview_text.grid(column=2, row=0)

# IMAGE DETAILS FRAME

details = ttk.LabelFrame(content, text="Details", padding=20) # create frame
details.grid(column=2, row=1, padx=(0,30), pady=(0,30))

disclaimer = ttk.Label(details,text="Image details appear here once you select an image.\n\nTo choose an image, navigate to File > Open")
disclaimer.grid(column=2, row=1)

# BUTTONS FRAME

buttons = ttk.Frame(content, padding=20) # create frame
buttons.grid(column=0, row=1, padx=(30,0), pady=(0,30))

#scan button
scan = ttk.Button(buttons,text="Scan", command=scanImage, state="disabled", style="Accent.TButton")
scan.grid(column=0,row=0, padx=(0,5))
#save button
save = ttk.Button(buttons,text="Save", command=saveFile, state="disabled")
save.grid(column=1,row=0, padx=(5,0))

# THEMING

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

# check for updates once the whole gui has loaded
if startup_update.get(): 
    updateCheck()

root.mainloop()
