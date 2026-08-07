from tkinter import * # for GUI
from tkinter import ttk # provides access to the Tk themed widget set
from tkinter import filedialog # for picking file
from tkinter import messagebox # for popup update dialog
from tkinterdnd2 import DND_FILES, TkinterDnD # for drag & dropping files
import pywinstyles, sys # for black title bar WINDOWS ONLY
import sv_ttk # tkinter sun valley theme
import darkdetect # for detecting what theme OS is set to
from PIL import ImageTk,Image # image processing
import webbrowser # for opening links
import os # for extracting just the file name of the image
import requests # for checking updates through GitHub API
import re # regex for extracting version number from APP_VERSION and GitHub tag
import platform # for checking which OS platform user is on

global APP_VERSION
APP_VERSION = "v0.4.0-beta"

white_point = 0.99 * 255 # 99% - the upper bound degree to which a white pixel is turned black

def scanImage():
    global new_image # for the saveImage() function

    # set Black Point based on slider
    slider_black_point = black_point_slider.get()
    black_point = (slider_black_point / 100) * 255 # 0 (black) to 255 (white)

    og_img = Image.open(filepath)# open img
    new_image = og_img.copy().convert('L') # create a greyscale copy of the original image to be downscaled for faster processing as this is only a preview
    new_image = new_image.point(lambda pixel: 0 if pixel < black_point else (255 if pixel < white_point else pixel)) # convert pixels

    saveImage()

def previewImage(event):
    openBtn.config(state="disabled")# if user changes black point settings once again after saving then Open btn should grey out again to prevent user from opening the previous image instead
    # set Black Point based on slider
    slider_black_point = black_point_slider.get()
    black_point = (slider_black_point / 100) * 255 # 0 (black) to 255 (white)

    og_img = Image.open(filepath)# open img
    prev_img = og_img.copy().convert('L') # create a greyscale copy of the original image to be downscaled for faster processing as this is only a preview
    prev_img.thumbnail((450,450), Image.Resampling.LANCZOS)# resize
    prev_img = prev_img.point(lambda pixel: 0 if pixel < black_point else (255 if pixel < white_point else pixel)) # convert pixels

    og_img_preview = ImageTk.PhotoImage(prev_img)
    preview_image.image_ref = og_img_preview # to stop Python deleting the photo as soon as the function ends
    preview_image.configure(image=og_img_preview)

def openImageFile():
    new_image.show()

def openImage(event=None):

    global filepath, width, height, filename
    
    all_exts = Image.registered_extensions()# Get all registered Pillow extensions
    supported_exts = [ext.lower() for ext, fmt in all_exts.items()]# list all open-able files and save-able file extensions that are supported by pillow

    # if a file was dropped
    if event is not None and hasattr(event, 'data') and event.data: # if an event deffo happened and it has a data attribute attached with some data in it then...
        # take the first file if multiple are dropped
        files = root.tk.splitlist(event.data) # to correctly handle file paths containing spaces
        filepath = files[0].strip('{}') # remove surrounding braces if present
    else: # if a file was opened manually
        #join list of supported files into one string for the open file dialog
        img_filter = " ".join(f"*{ext}" for ext in supported_exts)
        
        filepath = filedialog.askopenfilename(parent=root, title="Select Image to be Scanned", filetypes=(("Image files", img_filter), ("All files", "*.*")))
        #askopenfilenames for multiple
        if not filepath: # user closed file dialog popup
            reset()# reset everything if nothing was selected
            return # exit the function safely
    
    # if the user selects an openable file but an unsavable one then offer a conversion
    unsupported_exts = [ext.lower() for ext, fmt in all_exts.items() if fmt in Image.OPEN and fmt not in Image.SAVE] # list extensions if the file is open-able but not save-able by pillow
    filename, extension = os.path.splitext(filepath)# splits ('C:/Users/Dwad/Downloads/Doc1', '.pdf') into two variables
    if extension.lower() in unsupported_exts:
        convert_warning = messagebox.askyesnocancel("Unsupported File Type", f"File type unsupported. Do you want to convert to .PNG and continue?\n\nNote: the converted file will be saved to {filename + '.png'}", icon="warning")
        if convert_warning == True: # if user pessed "Yes"
            # NOTE - this takes a fair bit to process. Maybe put it on a seperate thread and show a ttk.Progressbar?
            new_path = filename + ".png"
            filepath = Image.open(filepath).convert("RGB").save(new_path, "PNG")
            filepath = new_path # switch to new path
        elif convert_warning == False: # if user pessed "No"
            openImage() # re-open file dialog
            return # exit function safely
        else: # if user pessed "Cancel"
            reset()# reset everything if nothing was selected
            return # exit function safely

    try:# Open image and display info
        og_img = Image.open(filepath) # open image

        if og_img.has_transparency_data:
            alpha_warning = messagebox.askyesnocancel("Transparency Detected", "Transparent pixels will be converted to black. Are you sure you want to continue?", icon="warning")
            if alpha_warning == False: # if user pessed "No"
                openImage() # re-open file dialog
                return # exit function safely
            if alpha_warning == None: # if user pessed "Cancel"
                reset()# reset everything if nothing was selected
                return # exit function safely

        filename = os.path.basename(og_img.filename) # extract image file name

        # Grab and store img info
        size_bytes = os.path.getsize(filepath) # image size
        width,height=og_img.size # image width & height
        mode=og_img.mode # image colour mode

        # Show information about the original image.
        clearFrame(details)
        display_filepath = ttk.Label(details,text=f"Original image: {filepath}").grid(column=0, row=0)
        display_size = ttk.Label(details,text=f"\nSize: {width} x {height} pixels").grid(column=0, row=1)
        display_mode = ttk.Label(details,text=f"\nColour Mode: {mode}").grid(column=0, row=2)
        display_bytes = ttk.Label(details,text=f"\nFile Size: {size_bytes} bytes").grid(column=0, row=3)

        # Preview image
        previewImage(None)

        # Activate buttons so that they are clickable
        black_point_slider.config(state="normal")
        black_point_spin.config(state="normal")
        save.config(state="normal")

        calcMinWindowSize()# recalculate minimum window size based on newly loaded image preview

    except Image.UnidentifiedImageError:
        clearFrame(details)
        displayDefaultImage(None,True)#True = don't check for an existing loaded preview image this time (reset preview image no matter what)
        filename, extension = os.path.splitext(filepath)# splits ('C:/Users/Dwad/Downloads/Doc1', '.pdf') into two variables
        if extension.lower() == ".pdf":
            ttk.Label(details,text=f"Error: PDF must have only image data, not text.").grid(column=0, row=0)
        else:
            ttk.Label(details,text=f"Error: File is either corrupted or unsupported.").grid(column=0, row=0)

def openRepo():
    webbrowser.open("https://github.com/dwaaad/docuScan")

def openWebsite():
    webbrowser.open("https://dwaaad.github.io/docuScan/")

def themeDark():
    current_theme = "dark"#save this preference to a .txt
    sv_ttk.set_theme(current_theme)#set base theme
    menubar.reload()
    apply_theme_to_titlebar(root)
    displayDefaultImage(None)#refresh default image

def themeLight():
    current_theme = "light"#save this preference to a .txt
    sv_ttk.set_theme(current_theme)#set base theme
    menubar.reload()
    apply_theme_to_titlebar(root)
    displayDefaultImage(None)#refresh default image

def themeAuto():
    current_theme = darkdetect.theme()#save this preference to a .txt
    sv_ttk.set_theme(current_theme)#set base theme
    menubar.reload()
    apply_theme_to_titlebar(root)
    displayDefaultImage(None)#refresh default image

def reset():
    displayDefaultImage(None,True)#reset preview image
    # reset everthing else
    black_point_slider.config(state="disabled")
    black_point_spin.config(state="disabled")
    save.config(state="disabled")
    clearFrame(details)
    disclaimer = ttk.Label(details,text="No image selected.\n\nSelect an image by navigating to File > Open\nor drag & drop into preview box.")
    disclaimer.grid(column=0, row=0)
    calcMinWindowSize()

def displayDefaultImage(event,check=False): # displays default image for drag & drop
    preview_image.config(cursor="arrow")
    #if an image isnt already in the preview frame then do not change out its image
    if check == False: 
        image_name = preview_image.cget('image') # get internal image name (e.g pyimage3)
        if image_name:
            prev_img_name = root.call(image_name, "cget", "-file") # query file path from the Tcl/Tk image object
            if prev_img_name != "default_preview_light.png" and prev_img_name != "default_preview_dark.png" and prev_img_name != "default_preview_dark_hover.png" and prev_img_name != "default_preview_light_hover.png":
                return

    #load preview image depending on current theme
    if sv_ttk.get_theme() == "light":
        default_preview_image = PhotoImage(file="default_preview_light.png")#ImageTk.PhotoImage(Image.open("default_preview_light.png"))
    if sv_ttk.get_theme() == "dark":
        default_preview_image = PhotoImage(file="default_preview_dark.png")#ImageTk.PhotoImage(Image.open("default_preview_dark.png"))

    preview_image.image_ref = default_preview_image # to stop Python deleting the photo as soon as the function ends
    preview_image.configure(image=default_preview_image)

def dragEnter(event): # replaces image with a highlighted version when a file is dragged onto it
    preview_image.config(cursor="hand2")
    #if an image isnt already in the preview frame then do not change out its image
    image_name = preview_image.cget('image') # get internal image name (e.g pyimage3)
    if image_name:
        prev_img_name = root.call(image_name, "cget", "-file") # query file path from the Tcl/Tk image object
        if prev_img_name != "default_preview_light.png" and prev_img_name != "default_preview_dark.png" and prev_img_name != "default_preview_dark_hover.png" and prev_img_name != "default_preview_light_hover.png":
           return

    #load preview image depending on current theme
    if sv_ttk.get_theme() == "light":
        default_preview_image = PhotoImage(file="default_preview_light_hover.png")#ImageTk.PhotoImage(Image.open("default_preview_light_hover.png"))
    if sv_ttk.get_theme() == "dark":
        default_preview_image = PhotoImage(file="default_preview_dark_hover.png")#ImageTk.PhotoImage(Image.open("default_preview_dark_hover.png"))

    preview_image.image_ref = default_preview_image # to stop Python deleting the photo as soon as the function ends
    preview_image.configure(image=default_preview_image)

def clearFrame(frame):
    for widget in frame.winfo_children():
        widget.destroy()

def saveImage():
    new_filename = f"scanned_{filename}"
    new_filepath = f"modified_images/{new_filename}"
    try:
        new_image.save(new_filepath)
    except FileNotFoundError:
        os.mkdir("modified_images/")
        new_image.save(new_filepath)
    exe_dir = os.path.dirname(os.path.abspath(__file__))
    exe_dir = exe_dir.replace("\\", "/") # replace backslashes with forward slashes for consistency
    display_save = ttk.Label(details,text=f"\nSucessfully saved new image to: {exe_dir}/{new_filepath}",foreground="#4285f4").grid(column=0, row=4)
    openBtn.config(state="normal")# give some kind of option to open the image either by double clicking as a link or using button or what
    calcMinWindowSize()# recalculate minimum window size to make room for "Successfully saved..." text label

def extractVersion(tag):
    match = re.search(r"\d+\.\d+\.\d+", tag)
    return match.group(0) if match else None

def updateCheck(silent=False): # silent determins if user is notified when there are no new updates
    # get latest version by loading the latest repo link
    url = "https://github.com/dwaaad/docuScan/releases/latest"

    # request without redirecting
    request = requests.get(url, allow_redirects=False)

    # extract version number tag from URL redirect
    latest_tag = request.headers["Location"].split("/")[-1]# GitHub should return a redirect with a Location header
    latest_version = extractVersion(latest_tag)
    current_version = extractVersion(APP_VERSION)
    
    if latest_version > current_version:# compare version numbers
        update_warning = messagebox.askyesno("New version available!", f"docuScan {latest_tag} is available. You're using {APP_VERSION}.\n\nOpen link to download page?")
        if update_warning == True:
            webbrowser.open("https://github.com/dwaaad/docuScan/releases/latest")
    else:
        if silent == False:
            messagebox.showinfo("No Updates", f"No new updates were found.\nYou are running the latest version {APP_VERSION}.")

# custom menubar (for dark mode support)
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

        file_menu.add_command(label="Open", command=openImage)
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

root = TkinterDnD.Tk() # create window

sv_ttk.set_theme(darkdetect.theme())#replace darkdetect.theme() with accessing a user.config in which the default value is set to darkdetect.theme()

startup_update = BooleanVar(value=True)#auto update on start set to True by default
# this jsut has to = true inside a function when I end up saving it to a .txt

# WINDOW SETUP
root.title("docuScan") # set title
small_icon = PhotoImage(file="icons/docuScan_favicon_x16.png")
large_icon = PhotoImage(file="icons/docuScan_favicon_x32.png")
root.iconphoto(False, large_icon, small_icon)

#navbar menu
menubar = MenuBar(root)
menubar.pack(side="top", fill="x")

content = ttk.Frame(root)
content.pack(fill="both", expand=True)

content.grid_columnconfigure(0,weight=1)
content.grid_rowconfigure(0,weight=1)

content.grid_columnconfigure(2,weight=3)
content.grid_rowconfigure(2,weight=1)

# OPTIONS FRAME

options = ttk.LabelFrame(content, text="Options", padding=20) # create frame
options.grid(column=0, row=0, padx=(30,0), pady=(30,0))

#Img source dir
img_dir = ttk.Entry(options)
img_dir.insert(0, "Enter image source directory")
img_dir.grid(column=0, columnspan=2, row=0, pady=(0,35))

#Black Point settings
black_point_var = IntVar(value=50) # set default value to 50
black_point_label = ttk.Label(options, text="Black Point")
black_point_label.grid(column=1, columnspan=2, row=1, pady=(0,10))
black_point_slider = Limiter(options, from_=0, to=100, precision=0, variable=black_point_var, state="disabled")
black_point_slider.grid(column=1, columnspan=2, row=2)
# bind all 3 mouse buttons to update the preview (because sliders support all 3 buttons)
black_point_slider.bind("<ButtonRelease-1>", previewImage)# left-click
black_point_slider.bind("<ButtonRelease-2>", previewImage)# middle-click
black_point_slider.bind("<ButtonRelease-3>", previewImage)# right-click

black_point_value_label = ttk.Label(options, textvariable=black_point_var)
black_point_value_label.grid(column=2, columnspan=2, row=2, padx=(5,0))

def validateBlackPoint(new_value): # presence check & int check
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
black_point_spin.grid(column=1, columnspan=2, row=3, pady=(10,0))

black_point_spin.bind("<ButtonRelease-1>", previewImage)

# VERTICAL SEPARATOR

separator = ttk.Separator(content, orient="vertical")
separator.grid(column=1, row=0, rowspan=3, sticky="ns", padx=30, pady=10)

# PREVIEW FRAME

preview = ttk.LabelFrame(content, text="Preview", padding=20) # create frame
preview.grid(column=2, row=0, padx=(0,30), pady=(30,15))

preview_image = ttk.Label(preview)
preview_image.grid(column=2, row=0)

# drag & drop
root.drop_target_register(DND_FILES) # register the label as a drop target for files

root.dnd_bind('<<Drop>>', openImage) # drop file
preview_image.bind("<ButtonRelease-1>", openImage) # left-click

root.dnd_bind('<<DropEnter>>', dragEnter) # drag file in
root.dnd_bind('<<DropLeave>>', displayDefaultImage) # drag file out

preview_image.bind('<Enter>', dragEnter) # for mouse entry
preview_image.bind('<Leave>', displayDefaultImage) # for mouse exit

displayDefaultImage(None)# set inital preview img as default

# IMAGE DETAILS FRAME

details = ttk.LabelFrame(content, text="Details", padding=20) # create frame
details.grid(column=2, row=1, padx=(0,30), pady=(0,30))

disclaimer = ttk.Label(details,text="No image selected.\n\nSelect an image by navigating to File > Open\nor drag & drop into preview box.")
disclaimer.grid(column=0, row=0)

# BUTTONS FRAME

buttons = ttk.Frame(content, padding=20) # create frame
buttons.grid(column=0, row=1, padx=(30,0), pady=(0,30))

#save button
save = ttk.Button(buttons,text="Save", command=scanImage, state="disabled", style="Accent.TButton")
save.grid(column=0,row=0)
#open button
openBtn = ttk.Button(buttons,text="Open", command=openImageFile, state="disabled")
openBtn.grid(column=1,row=0)
# CHANGE THE SURFACES OF BUTTON TO BE ON THE SAME SURFACE AS OPTIONS SO THAT COLUMNSPAN WORKS
note = ttk.Label(buttons, text="Note: Images scan best with minimal shadows visible",foreground="grey")
note.grid(column=0, columnspan=2, row=1, pady=(50,0))

# Calculate min window size
def calcMinWindowSize():
    root.update_idletasks() # force widgets to be drawn and calculated early instead of at root.mainloop()
    width = root.winfo_reqwidth() # Returns the requested width based on the widgets inside. This works immediately after update_idletasks() because it relies on the geometry manager's calculations, not the window manager's rendering.
    height = root.winfo_reqheight() # get height
    root.minsize(width, height) # set minimum window size to width and height of all loaded widgets
calcMinWindowSize()

# THEMING

def apply_theme_to_titlebar(root): # windows only
    
    if platform.system() != "Windows":
        return  # do nothing on macOS & Linux
    
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

# check for software updates once the whole gui has loaded
if startup_update.get(): 
    updateCheck(True)# True = silently check for updates on startup

root.mainloop()
