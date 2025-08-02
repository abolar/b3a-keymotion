import tkinter as tk
from utils.mdebug import debug_section




class Grid(tk.Tk):
    @debug_section(enabled=True)
    def __init__(self, geometry, grid_dimension, seq_length, config, grid_cell_counter):
        super().__init__()
        self.geometry_object = geometry
        self.grid_dimension = grid_dimension
        self.seq_length = seq_length
        self.config = config
        self.grid_cell_counter = grid_cell_counter

        if True:

            self.background_layer = tk.Tk()
            self.background_layer.geometry(str(geometry))
            self.background_layer.overrideredirect(True)
            self.background_layer.attributes('-topmost', True)
            self.background_layer.attributes('-alpha', config['grid_opacity'])
            self.background_layer.configure(bg=config['grid_background_color']) 
            # self.background_layer.attributes("-transparentcolor", config['grid_background_color']) 
            self.background_layer.withdraw()



            self.geometry(str(geometry))
            self.overrideredirect(True)
            self.attributes('-topmost', True)
            # Use window alpha for overall transparency

            if config.get('grid_transparent', False):
                self.attributes('-alpha', config['grid_opacity'])
            else:
                # Use the background color - it will appear semi-transparent due to window alpha
                self.configure(bg=config['grid_background_color']) 
                self.attributes("-transparentcolor", config['grid_background_color']) 


            self.canvas = tk.Canvas(self, bg=config.get('grid_background_color', 'black'), highlightthickness=0)
            self.canvas.pack(fill=tk.BOTH, expand=True)
            
            # Show window temporarily to get real size
            # self.deiconify()
            self.update_idletasks()
            self.withdraw()  # Hide it again if needed


    @debug_section(enabled=True)
    def draw_grid(self,):
        # Need to update the canvas size before drawing
        self.update_idletasks() # Force geometry manager to calculate sizes

        self.deiconify()

        self.canvas.delete("all") # Clear any existing drawings on the canvas

        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        
        # No need to draw background rectangle since canvas already has the background color
        # The window alpha will make the entire canvas (including background) semi-transparent

        cols = self.grid_dimension.x
        rows = self.grid_dimension.y

        cell_width = w / cols
        cell_height = h / rows
        win_x_abs = self.geometry_object.x
        win_y_abs = self.geometry_object.y

        cell_w = w / cols
        cell_h = h / rows

        # Set the color for the grid lines (red)
        grid_color = self.config['grid_color'] 
        # Set the color for the text (white for contrast)
        text_color = self.config['grid_text_color'] 


        # Draw vertical lines
        for i in range(1, cols):
            x = int(i * cell_w)
            self.canvas.create_line(x, 0, x, h, fill=grid_color)  # Made invisible

        # Draw horizontal lines
        for i in range(1, rows):
            y = int(i * cell_h)
            self.canvas.create_line(0, y, w, y, fill=grid_color)
        # Draw outer border (slightly thicker for visibility)
        self.canvas.create_rectangle(0, 0, w, h, outline=grid_color, width=2)

        self.grid_cell_dict = {}

        for row in range(rows):
            for col in range(cols):
                # Calculate relative coordinates within the canvas
                cell_left_rel = col * cell_w
                cell_top_rel = row * cell_h
                cell_right_rel = (col + 1) * cell_w
                cell_bottom_rel = (row + 1) * cell_h

                # Calculate absolute center coordinates on screen
                center_x_abs = win_x_abs + int(cell_left_rel + cell_w / 2)
                center_y_abs = win_y_abs + int(cell_top_rel + cell_h / 2)
                
                # Calculate absolute bounding box coordinates on screen
                abs_cell_left = win_x_abs + int(cell_left_rel)
                abs_cell_top = win_y_abs + int(cell_top_rel)
                abs_cell_right = win_x_abs + int(cell_right_rel)
                abs_cell_bottom = win_y_abs + int(cell_bottom_rel)


                grid_label = self.grid_cell_counter.grid_next_cell_label()

                

                self.grid_cell_dict[grid_label] = (
                    center_x_abs, 
                    center_y_abs, 
                    abs_cell_left, 
                    abs_cell_top, 
                    abs_cell_right, 
                    abs_cell_bottom)

                text_size = max(min(24, int(cell_h/8)), 16)


                # Draw the text in the center of the cell
                # First create a black background rectangle for the text
                text_bbox = self.canvas.bbox(self.canvas.create_text(
                    center_x_abs - win_x_abs,
                    center_y_abs - win_y_abs,
                    text=grid_label,
                    fill=text_color,
                    font=('Consolas', text_size, 'bold')
                ))
                
                # Add padding around the text
                padding = 4
                bg_left = text_bbox[0] - padding
                bg_top = text_bbox[1] - padding
                bg_right = text_bbox[2] + padding
                bg_bottom = text_bbox[3] + padding
                
                # # Draw black background rectangle behind the text
                # self.canvas.create_rectangle(
                #     bg_left, bg_top, bg_right, bg_bottom,
                #     fill='#050505', outline='black'
                # )
                
                # Draw the text with a border by creating multiple offset copies
                offsets = [(-2,-2), (-2,2), (2,-2), (2,2), (-2,0), (2,0), (0,-2), (0,2)]
                for dx, dy in offsets:
                    self.canvas.create_text(
                        center_x_abs - win_x_abs + dx,
                        center_y_abs - win_y_abs + dy,
                        text=grid_label,
                        fill='blue',
                        font=('Consolas', text_size, 'bold')
                    )
                # Draw the main text on top
                self.canvas.create_text(
                    center_x_abs - win_x_abs,
                    center_y_abs - win_y_abs,
                    text=grid_label,
                    fill=text_color,
                    font=('Consolas', text_size, 'bold')
                )
                
                # # Store the absolute coordinates for this cell ID
                # all_cell_coordinates[unique_id] = (
                #     center_x_abs, center_y_abs,
                #     abs_cell_left, abs_cell_top, abs_cell_right, abs_cell_bottom
                # )
                # cell_counter += 1

        return self.grid_cell_dict

    @debug_section(enabled=True)
    def show(self):
        self.background_layer.deiconify()
        self.deiconify()
        self.update_idletasks()
    
    @debug_section(enabled=True)
    def hide(self):
        # Make grid invisible by setting opacity to 0
        print("hiding grid")
        # self.attributes('-alpha', 0.0)
        self.withdraw()

    @debug_section(enabled=True)
    def hide_everything(self):
        self.background_layer.withdraw()

