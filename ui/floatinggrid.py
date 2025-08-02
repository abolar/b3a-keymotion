import tkinter as tk
from utils.mdebug import debug_section, mprint



class FloatingGrid(tk.Tk):
    @debug_section(enabled=True)
    def __init__(self, x, y, width, height, config):
        """
        Initializes the sub-grid overlay window.
        :param x, y: Absolute top-left coordinates of the selected cell.
        :param width, height: Dimensions of the selected cell.
        """
        super().__init__()
        self.overrideredirect(True)
        self.attributes('-topmost', True)
        self.config = config
        # Store the current cell's geometry for sub-cell calculations
        # These should be the scaled coordinates that were passed in
        self.parent_cell_x = x
        self.parent_cell_y = y
        self.parent_cell_width = width
        self.parent_cell_height = height

        # Use a different transparent color for the sub-overlay to avoid potential conflicts
        if config.get('grid_transparent', False):
            self.attributes('-alpha', config['grid_opacity'])
        else:
            self.configure(bg=config['grid_background_color']) 
            self.attributes("-transparentcolor", config['grid_background_color']) 
        
        self.geometry(f"{width}x{height}+{x}+{y}")
        
        self.canvas = tk.Canvas(self, bg=config.get('grid_background_color', 'black'), highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        # REMOVED: Canvas configure binding - we'll call draw_sub_grid explicitly
        self.canvas.bind('<Configure>', self.draw_sub_grid)
        self.withdraw() # Start hidden
        self.update_idletasks()
        self.withdraw()

        # Dictionary to store the absolute coordinates of sub-cells (A-I)
        self.sub_cell_coordinates = {}

    @debug_section(enabled=True)
    def draw_sub_grid(self, event=None):
        """
        Draws a 3x3 grid on the canvas and labels cells A-I.
        Also stores the absolute screen coordinates of each sub-cell.
        """
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        cols = 3
        rows = 3
        cell_w = w / cols
        cell_h = h / rows

        grid_color = self.config['grid_color'] 
        text_color = self.config['grid_text_color'] 

        # Draw vertical lines
        for i in range(1, cols):
            x = int(i * cell_w)
            self.canvas.create_line(x, 0, x, h, fill=grid_color)
        # Draw horizontal lines
        for i in range(1, rows):
            y = int(i * cell_h)
            self.canvas.create_line(0, y, w, y, fill=grid_color)
        # Draw outer border
        self.canvas.create_rectangle(0, 0, w, h, outline=grid_color, width=2)

        # Draw unique identifiers (A-I) in each cell and store their absolute coordinates
        self.sub_cell_coordinates.clear() # Clear previous sub-cell coordinates
        char_counter = 0

        text_size = max(min(24, int(cell_h/2)), 8)


        for row in range(rows):
            for col in range(cols):
                # Calculate relative coordinates within this sub-canvas
                sub_cell_left_rel = col * cell_w
                sub_cell_top_rel = row * cell_h
                sub_cell_right_rel = (col + 1) * cell_w
                sub_cell_bottom_rel = (row + 1) * cell_h

                # Calculate absolute center coordinates on screen for the sub-cell
                # Add parent cell's absolute position
                center_x_abs = self.parent_cell_x + int(sub_cell_left_rel + cell_w / 2)
                center_y_abs = self.parent_cell_y + int(sub_cell_top_rel + cell_h / 2)
                
                # Calculate absolute bounding box coordinates on screen for the sub-cell
                abs_sub_cell_left = self.parent_cell_x + int(sub_cell_left_rel)
                abs_sub_cell_top = self.parent_cell_y + int(sub_cell_top_rel)
                abs_sub_cell_right = self.parent_cell_x + int(sub_cell_right_rel)
                abs_sub_cell_bottom = self.parent_cell_y + int(sub_cell_bottom_rel)

                # label_char = chr(ord('A') + char_counter)
                label_char = {0:"w", 1:"e", 2:"r", 3:"s", 4:"d", 5:"f", 6:"x", 7:"c", 8:"v"}[char_counter]
                # {0:"w", 1:"e", 2:"r", 3:"s", 4:"d", 5:"f", 6:"x", 7:"c", 8:"v"}
                # Corrected: Use relative coordinates for canvas.create_text


                self.canvas.create_text(
                    sub_cell_left_rel + cell_w / 2, sub_cell_top_rel + cell_h / 2,
                    text=label_char,
                    fill=text_color,
                    font=('Arial', text_size, 'bold')
                )
                
                # Store the absolute coordinates for this sub-cell ID
                self.sub_cell_coordinates[label_char] = (
                    center_x_abs, center_y_abs,
                    abs_sub_cell_left, abs_sub_cell_top, abs_sub_cell_right, abs_sub_cell_bottom
                )

                char_counter += 1
                if char_counter >= 9: # Stop after 'I'
                    break
            if char_counter >= 9:
                break

    @debug_section(enabled=True)
    def hide_window(self):
        """Hides the sub-overlay window."""
        self.withdraw()

    @debug_section(enabled=True)
    def show_window(self):
        """Shows the sub-overlay window."""
        self.deiconify()

    @debug_section(enabled=True)
    def redraw_window(self, x, y, width, height):
        mprint("v2", f" INSIDE FLOATING GRID redrawing window to {width}x{height}+{x}+{y}")
        self.geometry(f"{width}x{height}+{x}+{y}")
        
        # wi = tk.Tk()
        # wi.geometry(f"{width}x{height}+{x}+{y}")
        # wi.update_idletasks()
        # self.after(200, self.draw_sub_grid)
        self.show_window()
