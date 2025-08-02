import tkinter as tk
from screeninfo import get_monitors
from ui.grid import Grid
from ui.floatinggrid import FloatingGrid
import pyautogui
import utils.utilities as utils

from keys.chrome import ChromeKeysBindings

from tkinter import colorchooser, ttk
import os
import json

import math
import time
from utils.mdebug import mprint, debug_section

arrow_keys = ['up', 'down', 'left', 'right']

class GridDimension:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return f"{self.x}x{self.y}"

class Geometry:
    def __init__(self, width, height, x=0, y=0):
        self.width = width
        self.height = height
        self.x = x
        self.y = y

    def __str__(self):
        return f"{self.width}x{self.height}+{self.x}+{self.y}"

class SettingsPopup:

    @debug_section(enabled=True)
    def __init__(self, parent, load_callback=None, save_callback=None):
        self.parent = parent
        self.config = parent.config
        self.load_callback = load_callback
        self.save_callback = save_callback


        # Create popup window
        self.popup = tk.Toplevel(parent)
        self.popup.title("Settings")
        self.popup.geometry("500x700")
        self.popup.configure(bg='#1e1e1e')

        # Make popup modal
        self.popup.transient(parent)
        self.popup.grab_set()
        
        # Center the popup
        self.popup.update_idletasks()
        x = (self.popup.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.popup.winfo_screenheight() // 2) - (700 // 2)
        self.popup.geometry(f"500x900+{x}+{y}")

        settings_popup = self.popup


        # Create style for the dropdown
        style = ttk.Style()
        style.configure('TCombobox', background='#1e1e1e', fieldbackground='#1e1e1e', foreground='white')

        # Get list of config files
        config_files = []
        config_dir = "./userconfig"
        try:
            for file in os.listdir(config_dir):
                if file.endswith(".json"):
                    config_files.append(os.path.splitext(file)[0])
        except FileNotFoundError:
            config_files = ["easy"]  # Fallback to default
        except Exception as e:
            print(f"Error reading config directory: {e}")
            config_files = ["easy"]


        
        # Create dropdown box
        self.dropdown_var = tk.StringVar()
        self.dropdown = ttk.Combobox(settings_popup, height=20, textvariable=self.dropdown_var, values=config_files, state="readonly")
        self.dropdown.bind('<<ComboboxSelected>>', lambda e: self.reload_config())
        self.dropdown.pack(pady=10, padx=10)




        popup_main_frame = ttk.Frame(settings_popup, padding="10 10 10 10")
        settings_popup.grid_rowconfigure(0, weight=0)
        settings_popup.grid_columnconfigure(0, weight=0)
        popup_main_frame.pack(fill=tk.BOTH, expand=True)
        # --- Grid Properties Container ---
        grid_frame = ttk.LabelFrame(popup_main_frame, text="Grid Properties", padding=(15, 15))
        grid_frame.pack(pady=10, padx=10, fill=tk.X, expand=False)

        # Configure columns for better alignment within grid_frame
        grid_frame.columnconfigure(0, weight=1)
        grid_frame.columnconfigure(1, weight=1)
        grid_frame.columnconfigure(2, weight=0) # For color display label

        # 1. Transparent Checkbox
        self.transparent_var = tk.BooleanVar()
        self.transparent_var.set(self.config['grid_transparent'])
        transparent_cb = ttk.Checkbutton(grid_frame, text="Transparent", variable=self.transparent_var,)
        transparent_cb.grid(row=0, column=0, columnspan=3, pady=5, sticky=tk.W)

        # 2. Opacity Slider
        self.opacity_var = tk.DoubleVar()
        self.opacity_var.set(self.config['grid_opacity'])
        ttk.Label(grid_frame, text="Opacity (0.0 - 1.0):").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        opacity_slider = ttk.Scale(grid_frame, from_=0.0, to=1.0, variable=self.opacity_var, orient=tk.HORIZONTAL, length=200,)
        opacity_slider.set(self.config['grid_opacity'])
        opacity_slider.grid(row=2, column=0, columnspan=3, pady=(0, 5), sticky=tk.W)
        self.opacity_slider_value_label = ttk.Label(grid_frame, text=f"{self.opacity_var.get():.2f}")
        self.opacity_slider_value_label.grid(row=2, column=3, sticky=tk.W, padx=5)
        opacity_slider.bind("<Motion>", lambda e: self.opacity_slider_value_label.config(text=f"{self.opacity_var.get():.2f}"))




        # grid type drop down
        grid_type_frame = ttk.LabelFrame(popup_main_frame, text="Grid Type", padding=(15, 15))
        grid_type_frame.pack(pady=10, padx=10, fill=tk.X, expand=False)
        grid_type_frame.columnconfigure(0, weight=1)
        grid_type_frame.columnconfigure(1, weight=1)
        grid_type_frame.columnconfigure(2, weight=1)
        

        print(self.config['grid_label_type'])
        self.grid_type_var = tk.StringVar(value=self.config['grid_label_type'])
        self.grid_type_dropdown = tk.OptionMenu(grid_type_frame, self.grid_type_var, self.config['grid_label_type'], 
        "numeric", "alpha", "leftkeyboard", "rightkeyboard", "homerow")
        self.grid_type_dropdown.grid(row=0, column=0, columnspan=3, pady=(5, 0), sticky=tk.W)
        
        
        

        # Colors ---------------------------------------------
        # --- Color Properties Container ---
        color_frame = ttk.LabelFrame(popup_main_frame, text="Grid Colors", padding=(15, 15))
        color_frame.pack(pady=10, padx=10, fill=tk.X, expand=False)

        # Configure columns for better alignment within color_frame
        color_frame.columnconfigure(0, weight=1)
        color_frame.columnconfigure(1, weight=1)
        color_frame.columnconfigure(2, weight=1)

        # Grid lines
        ttk.Label(color_frame, text="lines:", style='Modern.TLabel').grid(row=0, column=0, sticky='n', pady=(5, 0))
        self.grid_color = self.config['grid_color']
        self.grid_color_btn = tk.Button(color_frame, text="     ", bg=self.grid_color,
                                       command=lambda: self.choose_color('grid_color'))
        self.grid_color_btn.grid(row=1, column=0, padx=10, pady=(0, 5))

        # Grid text
        ttk.Label(color_frame, text="text", style='Modern.TLabel').grid(row=0, column=1, sticky='n', pady=(5, 0))
        self.grid_text_color = self.config['grid_text_color']
        self.grid_text_color_btn = tk.Button(color_frame, text="     ", bg=self.grid_text_color,
                                       command=lambda: self.choose_color('grid_text_color'))
        self.grid_text_color_btn.grid(row=1, column=1, padx=10, pady=(0, 5))

        # Grid background
        ttk.Label(color_frame, text="background", style='Modern.TLabel').grid(row=0, column=2, sticky='n', pady=(5, 0))
        self.grid_background_color = self.config['grid_background_color']
        self.grid_background_color_btn = tk.Button(color_frame, text="     ", bg=self.grid_background_color,
                                       command=lambda: self.choose_color('grid_background_color'))
        self.grid_background_color_btn.grid(row=1, column=2, padx=10, pady=(0, 5))
        # Colors ---------------------------------------------

        # Grid dimensions ---------------------------------------------

        dims_frame = ttk.LabelFrame(popup_main_frame, text="Default Grid Dimensions", padding=(15, 15))
        dims_frame.pack(pady=10, padx=10, fill=tk.X, expand=False)

        # Configure columns for better alignment within color_frame
        dims_frame.columnconfigure(0, weight=1)
        dims_frame.columnconfigure(1, weight=1)
        dims_frame.columnconfigure(2, weight=1)
        
        
        ttk.Label(dims_frame, text="X:", style='Modern.TLabel').grid(row=0, column=0, sticky='w', pady=(5, 0))
        self.grid_x_var = tk.StringVar(value=str(self.config['grid_dimension'][0]))
        grid_x_entry = ttk.Entry(dims_frame, textvariable=self.grid_x_var, width=5,
                                style='Modern.TEntry')
        grid_x_entry.grid(row=0, column=1, padx=(10, 20), pady=(5, 0), sticky='w')
        
        ttk.Label(dims_frame, text="Y:", style='Modern.TLabel').grid(row=0, column=2, sticky='w', pady=(5, 0))  
        self.grid_y_var = tk.StringVar(value=str(self.config['grid_dimension'][1]))
        grid_y_entry = ttk.Entry(dims_frame, textvariable=self.grid_y_var, width=5,
                                style='Modern.TEntry')
        grid_y_entry.grid(row=0, column=3, padx=(10, 0), pady=(5, 0), sticky='w')
        # Grid dimensions ---------------------------------------------

        # Monitor dimensions ---------------------------------------------
        monitor_frame = ttk.LabelFrame(popup_main_frame, text="Monitor Dimensions", padding=(15, 15))
        monitor_frame.pack(pady=10, padx=10, fill=tk.X, expand=False)
        # Monitor dimensions ---------------------------------------------


        #monitor listings
        monitor_listings_frame = ttk.LabelFrame(popup_main_frame, text="Monitor Listings", padding=(15, 15))
        monitor_listings_frame.pack(pady=10, padx=10, fill=tk.X, expand=False)
        
        # Configure columns for monitor listings
        monitor_listings_frame.columnconfigure(0, weight=0)  # Monitor label
        monitor_listings_frame.columnconfigure(1, weight=0)  # Enabled checkbox
        monitor_listings_frame.columnconfigure(2, weight=0)  # X label
        monitor_listings_frame.columnconfigure(3, weight=0)  # X entry
        monitor_listings_frame.columnconfigure(4, weight=0)  # Y label
        monitor_listings_frame.columnconfigure(5, weight=0)  # Y entry


        self.monitor_vars = {}
        self.monitor_grid_vars = {}  # Store grid dimension variables for each monitor

        print(f"Total monitors detected: {len(parent.monitors)}")
        for monitor_index, monitor in enumerate(parent.monitors):
            print(f"Processing monitor {monitor_index + 1}: {monitor}")
            ttk.Label(monitor_listings_frame, text=f"Monitor {monitor_index+1}:").grid(row=monitor_index, column=0, sticky='w', pady=(5, 0))

            # see if this monitor is listed in the config files

            this_monitor_config = self.config['monitors'].get(str(monitor_index + 1), {})
            enabled = this_monitor_config.get('enabled', False)
            mprint("v2", f"enabled: {enabled}")
            grid_dimension = this_monitor_config.get('grid_dimension', (10, 10))
            print(grid_dimension)
            
            # Create and store the checkbox variable
            monitor_var = tk.BooleanVar(value=enabled)
            self.monitor_vars[str(monitor_index + 1)] = monitor_var
            
            monitor_cb = ttk.Checkbutton(monitor_listings_frame, text=" ", variable=monitor_var)
            monitor_cb.grid(row=monitor_index, column=1, sticky='w', pady=(5, 0))

            ttk.Label(monitor_listings_frame, text="X:", style='Modern.TLabel').grid(row=monitor_index, column=2, sticky='w', pady=(5, 0))
            grid_x_var = tk.StringVar(value=str(grid_dimension[0]))
            grid_x_entry = ttk.Entry(monitor_listings_frame, textvariable=grid_x_var, width=5, style='Modern.TEntry')
            grid_x_entry.grid(row=monitor_index, column=3, padx=(10, 20), pady=(5, 0), sticky='w')
            
            ttk.Label(monitor_listings_frame, text="Y:", style='Modern.TLabel').grid(row=monitor_index, column=4, sticky='w', pady=(5, 0))  
            grid_y_var = tk.StringVar(value=str(grid_dimension[1]))
            grid_y_entry = ttk.Entry(monitor_listings_frame, textvariable=grid_y_var, width=5, style='Modern.TEntry')
            grid_y_entry.grid(row=monitor_index, column=5, padx=(10, 0), pady=(5, 0), sticky='w')
            
            # Store the grid dimension variables for this monitor
            self.monitor_grid_vars[str(monitor_index + 1)] = {
                'x': grid_x_var,
                'y': grid_y_var
            }
        #monitor listings


        # save and close buttons
        button_frame = ttk.Frame(popup_main_frame)
        button_frame.pack(pady=10, padx=10, fill=tk.X, expand=False)

        # Place buttons to the right
        button_frame.columnconfigure(0, weight=1) # Spacer column
        apply_btn = ttk.Button(button_frame, text="Apply", command=self.apply_settings, style="Accent.TButton") # Accent button
        apply_btn.grid(row=0, column=1, padx=5)

        cancel_btn = ttk.Button(button_frame, text="Cancel", command=settings_popup.destroy)
        cancel_btn.grid(row=0, column=2)

    @debug_section(enabled=True)
    def apply_settings(self):

        self.config['grid_transparent'] = self.transparent_var.get()
        self.config['grid_opacity'] = self.opacity_var.get()
        self.config['grid_label_type'] = self.grid_type_var.get()
        self.config['grid_color'] = self.grid_color
        self.config['grid_text_color'] = self.grid_text_color
        self.config['grid_background_color'] = self.grid_background_color
        self.config['grid_dimension'] = [int(self.grid_x_var.get()), int(self.grid_y_var.get())]
        
        # Convert monitor_vars to JSON-serializable primitives
        monitor_settings = {}
        for monitor_id in self.monitor_vars.keys():
            enabled = self.monitor_vars[monitor_id].get()
            x_dim = int(self.monitor_grid_vars[monitor_id]['x'].get())
            y_dim = int(self.monitor_grid_vars[monitor_id]['y'].get())
            
            monitor_settings[str(monitor_id)] = {
                'enabled': enabled,
                'grid_dimension': [x_dim, y_dim]
            }
        
        # Update the config with the JSON-serializable monitor settings
        self.config['monitors'] = monitor_settings
        
        self.parent.create_grid_components(self.config)
        print("done applying settings")
        # self.popup.destroy()


    def reload_config(self):
        config_name = self.dropdown_var.get()
        config_path = f"userconfig/{config_name}.json"
        self.config = json.load(open(config_path))
        self.parent.config = self.config

        # Update all UI elements with new config values
        self.transparent_var.set(self.config['grid_transparent'])
        self.opacity_var.set(self.config['grid_opacity'])
        self.opacity_slider_value_label.config(text=f"{self.opacity_var.get():.2f}")
        self.grid_type_var.set(self.config['grid_label_type'])
        
        # Update grid dimensions
        self.grid_x_var.set(self.config['grid_dimension'][0])
        self.grid_y_var.set(self.config['grid_dimension'][1])

        # Update monitor settings
        for monitor_id in self.monitor_vars.keys():
            monitor_config = self.config['monitors'].get(str(monitor_id), {'enabled': False, 'grid_dimension': [10, 10]})
            self.monitor_vars[monitor_id].set(monitor_config['enabled'])
            self.monitor_grid_vars[monitor_id]['x'].set(monitor_config['grid_dimension'][0])
            self.monitor_grid_vars[monitor_id]['y'].set(monitor_config['grid_dimension'][1])

        # Update colors
        self.grid_color = self.config['grid_color']
        self.grid_text_color = self.config['grid_text_color'] 
        self.grid_background_color = self.config['grid_background_color']
        
        # Update color button backgrounds
        self.grid_color_btn.config(bg=self.grid_color)
        self.grid_text_color_btn.config(bg=self.grid_text_color)
        self.grid_background_color_btn.config(bg=self.grid_background_color)
        # self.parent.create_grid_components(self.config)


    @debug_section(enabled=True)
    def choose_color(self, color_type):
        current_color = getattr(self, f"{color_type}")
        color = colorchooser.askcolor(color=current_color, parent=self.popup)[1]
        if color:
            setattr(self, f"{color_type}", color)
            btn = getattr(self, f"{color_type}_btn")
            btn.config(bg=color)




class GridCellCounter():
    def __init__(self, sequence_length, label_type='alpha'):
        self.sequence_length = sequence_length
        self.grid_cell_counter = 0
        self.grid_cell_dict = []
        self.label_type = label_type

    def reset(self):
        self.grid_cell_counter = 0
        self.grid_cell_dict = {}

    def next(self):
        result = self.grid_cell_counter
        self.grid_cell_counter += 1
        return result
    
    def grid_next_cell_label(self):
        if self.label_type == 'numeric':
            return self.grid_next_cell_label_numeric()
        elif self.label_type == 'alpha':
            return self.grid_next_cell_label_alpha()
        elif self.label_type == 'leftkeyboard':
            return self.grid_next_cell_label_leftkeyboard()
        elif self.label_type == 'rightkeyboard':
            return self.grid_next_cell_label_rightkeyboard()
        elif self.label_type == 'homerow':
            return self.grid_next_cell_label_homerow()
        else:
            raise ValueError(f"Invalid label type: {self.label_type}")

    def grid_next_cell_label_numeric(self):
        result = str(self.next()).zfill(self.sequence_length)
        return result

    def grid_next_cell_label_alpha(self):
        """
        Converts a number to base-26 where each digit is represented by a letter (A=0, B=1, ..., Z=25).
        Returns a string left-padded with 'A's to reach the specified length.
        
        Args:
            number: Integer to convert
            length: Desired length of the output string
            
        Returns:
            String of specified length in base-26 with letters
        """
        number = self.next()
        
        # Convert number to base-26 digits
        digits = []
        temp_number = number
        
        while temp_number > 0:
            digits.append(temp_number % 26)
            temp_number //= 26
        
        # Convert digits to letters (0=A, 1=B, ..., 25=Z)
        letters = [chr(ord('A') + digit) for digit in digits]
        
        # Reverse to get correct order and join
        result = ''.join(reversed(letters))
        
        # Left-pad with 'A's to reach desired length
        result = result.rjust(self.sequence_length, 'A')
        
        return result

    def grid_next_cell_label_leftkeyboard(self):
        allowed_keys = "ASDFGERTCVBQWZX"
        number = self.next()
        
        # Convert number to base-15 digits
        digits = []
        temp_number = number
        
        while temp_number > 0:
            digits.append(temp_number % 15)
            temp_number //= 15
        
        # Convert digits to letters (0=A, 1=B, ..., 14=O)
        letters = [allowed_keys[digit] for digit in digits]
        
        # Reverse to get correct order and join
        result = ''.join(reversed(letters))
        
        # Left-pad with 'Q's to reach desired length
        result = result.rjust(self.sequence_length, allowed_keys[0])
        
        return result

    def grid_next_cell_label_rightkeyboard(self):
        allowed_keys = "HJKLNMYUIOP"
        number = self.next()
        
        # Convert number to base-11 digits
        digits = []
        temp_number = number
        
        while temp_number > 0:
            digits.append(temp_number % 11)
            temp_number //= 11
        
        # Convert digits to letters (0=A, 1=B, ..., 10=K)
        letters = [allowed_keys[digit] for digit in digits]
        
        # Reverse to get correct order and join
        result = ''.join(reversed(letters))
        
        # Left-pad with 'H's to reach desired length
        result = result.rjust(self.sequence_length, allowed_keys[0])
        
        return result

    def grid_next_cell_label_homerow(self):
        allowed_keys = "ASDFGHJKL"
        number = self.next()
        
        # Convert number to base-11 digits
        digits = []
        temp_number = number
        
        while temp_number > 0:
            digits.append(temp_number % 9)
            temp_number //= 9
        
        # Convert digits to letters (0=A, 1=B, ..., 10=K)
        letters = [allowed_keys[digit] for digit in digits]
        
        # Reverse to get correct order and join
        result = ''.join(reversed(letters))
        
        # Left-pad with 'H's to reach desired length
        result = result.rjust(self.sequence_length, allowed_keys[0])
        
        return result

    def get_grid_cell_dict(self, grid_label):
        return self.grid_cell_dict.get(grid_label, [])

    def grid_cell_dict_add(self, grid_label, data):
        self.grid_cell_dict[grid_label] = data


class MainTk(tk.Tk):
    @debug_section(enabled=True)
    def __init__(self, config):

        super().__init__()

        self.title("Keyboard Status")


        self.config(bg="black")
        self.create_widgets()
        self.overrideredirect(True)

        self.position_bottom_right()
        self.attributes('-topmost', True)
        self.make_draggable()


        self.resizable(True, True)



        self.protocol("WM_DELETE_WINDOW", self.on_closing)
    

        self.keysbindings = ChromeKeysBindings()


        self.monitor_grids = []
        self.floating_grid = None
        self.floating_overlay = False
        self.grid_visible = False
        self.hotkey_sequence = []
        self.sequence_length = 3
        self.config = config
        self.grid_cell_counter = None
        self.create_grid_components(config)



    # ----------------------------------------------------------------------------------------
    @debug_section(enabled=True)
    def position_bottom_right(self):
        """Position window at bottom right of screen"""
        self.update_idletasks()

        widget_width = 300
        widget_height = 60
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # Account for taskbar (approximate)
        taskbar_height = 40
        
        x = screen_width - widget_width - 10  # window width + margin
        y = screen_height - widget_height - taskbar_height - 10  # window height + taskbar + margin
        print(f"Positioning window at {x}, {y}")
        self.after(0, lambda: self.geometry(f"{widget_width}x{widget_height}+{x}+{y}"))

    @debug_section(enabled=True)
    def make_draggable(self):
        """Make the window draggable"""
        def start_drag(event):
            self.x = event.x
            self.y = event.y
        
        def drag(event):
            x = (event.x_root - self.x)
            y = (event.y_root - self.y)
            self.geometry(f"+{x}+{y}")
        
        # Button-3 is the right mouse button click event
        # B3-Motion is when the right mouse button is held down and the mouse is moved
        self.bind('<Button-3>', start_drag)
        self.bind('<B3-Motion>', drag)

    @debug_section(enabled=True)
    def create_widgets(self):
        # main frame
        main_frame = tk.Frame(self, bg="black")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Top frame for main buttons
        top_frame = tk.Frame(main_frame, bg='#000000')
        top_frame.pack(fill='x', pady=(0, 5))


        # keyboard toggle button(s)
        self.toggle_state = False
        self.toggle_btn = tk.Button(top_frame, text="keyboard", font=('Arial', 10),
                                   bg='#dc3545', fg='white', bd=0,
                                   command=self.toggle_button, relief='flat',
                                   width=10, height=1)
        self.toggle_btn.pack(side='left', padx=(0, 5), pady=(5, 0))  # Add 5px padding to top, 0px to bottom

        # Settings button
        settings_btn = tk.Button(top_frame, text="⚙", font=('Arial', 10),
                               bg='#6c757d', fg='white', bd=0,
                               command=self.open_settings, relief='flat',
                               width=3, height=1)
        settings_btn.pack(side='left', padx=(0, 5), pady=(5, 0))

        # Close button
        close_btn = tk.Button(top_frame, text="x", font=('Arial', 10),
                            bg='#dc3545', fg='white', bd=0,
                            command=self.on_closing, relief='flat',
                            width=4, height=1)
        close_btn.pack(side='right', pady=(5, 0))

        

    @debug_section(enabled=True)
    def toggle_button(self):
        self.toggle_state = not self.toggle_state
        if self.toggle_state:
            self.toggle_btn.config(bg='#28a745')
            self.keysbindings.activate()
        else:
            self.toggle_btn.config(bg='#dc3545')
            self.keysbindings.deactivate()


    @debug_section(enabled=True)
    def load_settings_for_popup(self):
        pass

    @debug_section(enabled=True)
    def save_settings_from_popup(self):
        pass

    @debug_section(enabled=True)
    def open_settings(self):
        SettingsPopup(self, self.load_settings_for_popup, self.save_settings_from_popup)

    # ----------------------------------------------------------------------------------------






    @debug_section(enabled=True)
    def create_grid_components(self, config):

        # First destroy all grid and floating overlays
        if self.monitor_grids and len(self.monitor_grids) > 0:
            for grid in self.monitor_grids:
                grid.destroy()
        if self.floating_grid:
            self.floating_grid.destroy()


        self.config = config

        self.monitor_grids = []

        self.monitors = []
        for monitor in get_monitors():
            self.monitors.append(monitor)

        cell_count = 0
        for monitor_index, monitor in enumerate(get_monitors()):
            if config['monitors'].get(str(monitor_index + 1), {}).get('enabled', False):
                grid_dimension = config['monitors'].get(str(monitor_index + 1), {}).get('grid_dimension', config['grid_dimension'])
                cell_count += grid_dimension[0] * grid_dimension[1]

        mprint("v2", f"Cell count: {cell_count}")
        if config['grid_label_type'] == 'alpha':
            # self.sequence_length = math.floor(math.log(cell_count)/math.log(26) + 1)
            self.sequence_length = math.ceil(math.log(cell_count)/math.log(26))
        elif config['grid_label_type'] == 'numeric':
            self.sequence_length = math.ceil(math.log(cell_count)/math.log(10))
        elif config['grid_label_type'] == 'leftkeyboard':
            self.sequence_length = math.ceil(math.log(cell_count)/math.log(15))
        elif config['grid_label_type'] == 'rightkeyboard':
            self.sequence_length = math.ceil(math.log(cell_count)/math.log(11))
        elif config['grid_label_type'] == 'homerow':
            self.sequence_length = math.ceil(math.log(cell_count)/math.log(9))
        else:
            raise ValueError(f"Invalid grid label type: {config['grid_label_type']}")
        mprint("v2", f"Sequence length: {self.sequence_length}")

        self.grid_cell_counter = GridCellCounter(self.sequence_length, config['grid_label_type'])
        self.grid_cell_counter_test = GridCellCounter(1, 'alpha')
        self.grid_dict = {}

        for monitor_index, monitor in enumerate(get_monitors()):

            m_index = str(monitor_index + 1)

            if config['monitors'].get(m_index, {}).get('enabled', False):
                self.monitor_grids.append(
                    Grid(
                        Geometry(monitor.width, monitor.height, monitor.x, monitor.y), 
                        GridDimension(
                            config['monitors'].get(m_index, {}).get('grid_dimension', config['grid_dimension'])[0], 
                            config['monitors'].get(m_index, {}).get('grid_dimension', config['grid_dimension'])[1]
                        ), 
                        self.sequence_length,
                        config,
                        self.grid_cell_counter
                    )
                )
        self.floating_grid = FloatingGrid(100, 100, 100, 100, config)
        self.floating_overlay = False
        self.after(200, self.draw_grids)
        self.grid_visible = False

    @debug_section(enabled=True)
    def draw_grids(self):

        self.grid_dict = {}

        self.grid_cell_counter.reset()


        for grid in self.monitor_grids:
            l_grid_dict = grid.draw_grid()
            self.grid_dict.update(l_grid_dict)
            self.hide_grids()


    @debug_section(enabled=True)
    def show_grids(self):
        for grid in self.monitor_grids:
            grid.show()
        self.grid_visible = True
    
    @debug_section(enabled=True)
    def hide_grids(self):
        for grid in self.monitor_grids:
            grid.hide()
            grid.hide_everything()
        self.floating_grid.hide_window()
        self.floating_overlay = False
        self.grid_visible = False

    @debug_section(enabled=True)
    def toggle_grids(self):
        if self.grid_visible:
            self.hide_grids()
        else:
            self.show_grids()
    def hide_main_grids(self):
        for grid in self.monitor_grids:
            grid.hide()
        self.grid_visible = False
    def show_main_grids(self):
        for grid in self.monitor_grids:
            grid.show()
        self.grid_visible = True

    @debug_section(enabled=True)
    def hide_floating_grid(self):
        self.after(0, self.floating_grid.hide_window)
        self.floating_overlay = False

    @debug_section(enabled=True)
    def on_closing(self):
        """Handle window close event - exit the entire application"""
        print("Closing application...")
        for overlay in self.monitor_grids:
            overlay.hide()
            overlay.destroy()
        self.quit()
        self.destroy()

    @debug_section(enabled=True)
    def process_sub_key(self, key):
        mprint("v3", f"Processing sub key: {key}")
        x_offset, y_offset = 0, 0
        if key in "WERSDFXCV123456789":
            left, top, width, height = self.suboverlay_location
            if key in "WER789":
                y_offset = -round(height/3)
            if key in 'XCV123':
                y_offset = round(height/3)
            if key in "WSX147":
                x_offset = -round(width/3)
            if key in "RFV369":
                x_offset = round(width/3)
            x, y = round(left + width/2), round(top + height/2)

            mprint("v3", f"offset: {x_offset}, {y_offset}")

        redraw_or_not = False
        n_width = width
        n_height = height
        if width > 25:
            n_width = round(width / 3)
            redraw_or_not = True
        if height > 25:
            n_height = round(height / 3)
            redraw_or_not = True



        if redraw_or_not:

            # left changes only 852 and 963
            # top changes only on 456 and 123

            n_left, n_top = left, top
            if key in "EDC852":
                n_left = n_left + round(width/3)
            if key in "RFV963":
                n_left = n_left + round(width/3*2)
            if key in "SDF456":
                n_top = n_top + round(height/3)
            if key in "XCV123":
                n_top = n_top + round(height/3*2)

            # mprint("v2", f"overlay was {left}, {top}")
            # mprint("v2", f"overlay moving to {n_left}, {n_top}")

            self.after(0, lambda: self.floating_grid.redraw_window(n_left, n_top, n_width, n_height))
            self.suboverlay_location = (n_left, n_top, n_width, n_height)
            self.after(0, lambda: self.hide_main_grids())
            self.floating_overlay = True
            self.update_idletasks()

        pyautogui.moveTo(x + x_offset, y + y_offset, duration=.2, tween=pyautogui.easeOutQuad)
        print(f"sub Moving to {x_offset}, {y_offset}")

        return

    @debug_section(enabled=True)
    def process_hotkey_sequence(self, keysequence):
        if keysequence in self.grid_dict:
            x, y, left, top, right, bottom = self.grid_dict[keysequence]
            # self.floating_grid.redraw_window(x, y, right - left, bottom - top)
            mprint("v2", f"Moving to {x}, {y}")
            # self.floating_grid.redraw_window(x, y, right - left, bottom - top)

            left, top, width, height = utils.scale_coordinates(
                left, top, right - left, bottom - top,
            )

            self.after(0, lambda: self.floating_grid.redraw_window(left, top, width, height))
            self.suboverlay_location = (left, top, width, height)
            self.floating_overlay = True
            self.after(0, self.hide_main_grids)
            pyautogui.moveTo(x, y, duration=.5, tween=pyautogui.easeOutQuad)

    @debug_section(enabled=True)
    def process_menu_key(self, key):
        if key == 'a':
            print("toggling keyboard status")
            self.toggle_keyboard_status()

    @debug_section(enabled=True)
    def toggle_keyboard_status(self):
        self.toggle_button()
        pass
        # """Toggle the keyboard status when button is clicked"""
        # new_status = not self.keyboard_active
        # self.set_keyboard_active(new_status)
        
        # status_text = "active" if new_status else "inactive"
        # self.append_log(f"Keyboard status: {status_text}")


    @debug_section(enabled=True)
    def process_single_key(self, key):

        if self.floating_overlay:
            if key == 'backspace':
                self.hide_floating_grid()
                self.after(0, self.show_grids)
                return

        if self.floating_overlay:
            # if key.upper() in "ABCDEFGHI123456789":
            if key.upper() in "WERSDFXCV123456789":
                self.process_sub_key(key.upper())
                # self.after(0, self.hide_grids)
            return


        # hotkey sequence processing....
        if not hasattr(self, 'hotkey_sequence'):
            self.hotkey_sequence = []
        if not hasattr(self, 'sequence_length'):
            self.sequence_length = 3
        current_time = time.time()
        
        # Check if sequence timed out
        if len(self.hotkey_sequence) > 0 and current_time - self.hotkey_sequence[0][1] >= self.config['hotkey_timeout']:
            self.hotkey_sequence = []
        
        # Add new key to sequence
        self.hotkey_sequence.append((key.upper(), current_time))
        
        # If we've reached desired sequence length
        if len(self.hotkey_sequence) == self.sequence_length:
            # Build the key sequence string
            keysequence = ''.join(key[0] for key in self.hotkey_sequence)
            mprint("v2", f"Hotkey sequence: {keysequence}")

            if keysequence in self.grid_dict:
                x, y, left, top, right, bottom = self.grid_dict[keysequence]
                # pyautogui.moveTo(x, y)
                # pyautogui.click()
                self.process_hotkey_sequence(keysequence)

            # self.process_hotkeys(keysequence)
            self.hotkey_sequence = []



