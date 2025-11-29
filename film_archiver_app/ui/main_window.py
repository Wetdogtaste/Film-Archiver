"""
Film Archiver - Main Window
"""
import os
import logging
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from PIL import Image, ImageTk
from tkcalendar import Calendar
import shutil
import piexif
import sys

from core.file_manager import FileManager
from core.preferences import PreferenceManager
from config.settings import (
    APP_NAME, IS_MACOS, LIGHT_THEME, DARK_THEME,
    MAX_THUMBNAIL_SIZE, MAX_CACHE_ENTRIES
)

class FilmArchiverWindow:
    def validate_combobox_input(self, event):
        """Validate and auto-capitalize combobox input"""
        # Get the combobox that triggered the event
        combobox = event.widget
        current_text = combobox.get()
        
        if current_text:
            # Auto-capitalize
            capitalized_text = current_text.upper()
            if capitalized_text != current_text:
                combobox.set(capitalized_text)
            
            # Check for illegal characters
            illegal_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
            is_valid = not any(char in capitalized_text for char in illegal_chars)
            
            # Visual feedback
            if not is_valid:
                # Set text color to red for invalid input
                combobox.configure(foreground="red")
            else:
                # Reset to default color
                combobox.configure(foreground="")  # Default color

    def __init__(self, root):
        self.root = root
        self.root.title(APP_NAME)
        self.root.minsize(850, 500)
        self.root.geometry("1200x800")
        
        # Initialize managers
        self.file_manager = FileManager()
        self.pref_manager = PreferenceManager()
        
        # Initialize variables
        self.files = []
        self.thumbnail_cache = {}
        self.colors = LIGHT_THEME if not IS_MACOS else DARK_THEME
        self.file_lenses = {}  # Dictionary to store lens for each file
        self.active_combo = None  # Track active combobox
        self.dropdown_active = False  # Flag to prevent immediate reopening
        self.last_dropdown_time = 0  # Track when dropdown was last closed
        
        # Configure styles
        style = ttk.Style()
        style.configure("Dropdown.TFrame", relief="solid", borderwidth=1)
        
        # Create UI
        self.create_main_layout()
        
    def create_main_layout(self):
        """Create the main application layout"""
        # Main container
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill='both', expand=True)
        
        # Create UI sections
        self.create_input_frame()
        
        # Create preview and file list container
        preview_container = ttk.Frame(self.main_container)
        preview_container.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Configure grid weights for preview container
        preview_container.grid_columnconfigure(1, weight=1)
        preview_container.grid_rowconfigure(0, weight=1)
        
        # Create preview frame (left side)
        self.create_preview_frame(preview_container)
        
        # Create file list frame (right side)
        self.create_file_list_frame(preview_container)
        
        # Create control frame
        self.create_control_frame()
        
    def create_input_frame(self):
        """Create the input controls section"""
        input_frame = ttk.LabelFrame(self.main_container, text="Settings", padding="10")
        input_frame.pack(fill="x", padx=10, pady=5)
        
        # Roll Number
        roll_frame = ttk.Frame(input_frame)
        roll_frame.pack(fill='x', pady=5)
        ttk.Label(roll_frame, text="Roll Number:", width=12).pack(side='left')
        self.roll_number = ttk.Entry(roll_frame, width=10)
        self.roll_number.pack(side='left', padx=5)
        self.roll_number.insert(0, "1")
        self.roll_number.bind('<KeyRelease>', lambda e: self.update_file_list())
        
        # Camera Model
        camera_frame = ttk.Frame(input_frame)
        camera_frame.pack(fill='x', pady=5)
        ttk.Label(camera_frame, text="Camera Model:", width=12).pack(side='left')
        self.camera_model = ttk.Combobox(camera_frame, width=30)
        self.camera_model.pack(side='left', padx=5)
        self.camera_model['values'] = self.pref_manager.get_cameras()
        self.camera_model.bind('<<ComboboxSelected>>', lambda e: (self.validate_combobox_input(e), self.update_file_list()))
        self.camera_model.bind('<KeyRelease>', lambda e: (self.validate_combobox_input(e), self.update_file_list()))
        
        camera_buttons = ttk.Frame(camera_frame)
        camera_buttons.pack(side='left')
        
        self.camera_add = ttk.Button(camera_buttons, text="+", width=3,
                                   command=self.add_camera_to_list)
        self.camera_add.pack(side='left', padx=2)
        
        self.camera_remove = ttk.Button(camera_buttons, text="-", width=3,
                                      command=self.remove_camera_from_list)
        self.camera_remove.pack(side='left', padx=2)
        
        self.create_tooltip(self.camera_add, "Add to favorites")
        self.create_tooltip(self.camera_remove, "Remove from favorites")
        
        # Film Type
        film_frame = ttk.Frame(input_frame)
        film_frame.pack(fill='x', pady=5)
        ttk.Label(film_frame, text="Film Type:", width=12).pack(side='left')
        self.film_type = ttk.Combobox(film_frame, width=30)
        self.film_type.pack(side='left', padx=5)
        self.film_type['values'] = self.pref_manager.get_films()
        self.film_type.bind('<<ComboboxSelected>>', lambda e: (self.validate_combobox_input(e), self.update_file_list()))
        self.film_type.bind('<KeyRelease>', lambda e: (self.validate_combobox_input(e), self.update_file_list()))
        
        film_buttons = ttk.Frame(film_frame)
        film_buttons.pack(side='left')
        
        self.film_add = ttk.Button(film_buttons, text="+", width=3,
                                 command=self.add_film_to_list)
        self.film_add.pack(side='left', padx=2)
        
        self.film_remove = ttk.Button(film_buttons, text="-", width=3,
                                    command=self.remove_film_from_list)
        self.film_remove.pack(side='left', padx=2)
        
        self.create_tooltip(self.film_add, "Add to favorites")
        self.create_tooltip(self.film_remove, "Remove from favorites")
        
        # Push/Pull buttons
        push_pull_frame = ttk.Frame(film_frame)
        push_pull_frame.pack(side='left', padx=(5, 0))

        # Label for Push/Pull
        ttk.Label(push_pull_frame, text="Push/Pull:").pack(side='left')

        # Push/Pull value variable
        self.push_pull_value = tk.IntVar(value=0)
                
        # Display frame for the value
        display_frame = ttk.Frame(push_pull_frame)
        display_frame.pack(side='left', padx=2)
                
        # Label to display the current value
        self.push_pull_display = ttk.Label(display_frame, text="0", width=2)
        self.push_pull_display.pack(padx=2)
                
        # Buttons frame
        buttons_frame = ttk.Frame(push_pull_frame)
        buttons_frame.pack(side='left')
                
        # Minus button
        self.push_pull_minus = ttk.Button(buttons_frame, text="-", width=2,
                                       command=self.decrease_push_pull)
        self.push_pull_minus.pack(side='left', padx=1)
                
        # Plus button
        self.push_pull_plus = ttk.Button(buttons_frame, text="+", width=2,
                                      command=self.increase_push_pull)
        self.push_pull_plus.pack(side='left', padx=1)
                
        self.create_tooltip(self.push_pull_display, 
            "0: Normal development\n"
            "+1, +2, etc: Push process\n"
            "-1, -2, etc: Pull process")
            
        # Shot at ISO field
        shot_iso_frame = ttk.Frame(film_frame)
        shot_iso_frame.pack(side='left', padx=(10, 0))
        
        ttk.Label(shot_iso_frame, text="Shot at ISO:").pack(side='left')
        
        # Variable to store the shot ISO value
        self.shot_iso_var = tk.StringVar()
        self.shot_iso_var.trace_add("write", self.on_shot_iso_changed)
        
        # Entry field for shot ISO
        self.shot_iso_entry = ttk.Entry(shot_iso_frame, width=6, textvariable=self.shot_iso_var)
        self.shot_iso_entry.pack(side='left', padx=2)
        
        # Validate to ensure only numbers are entered
        vcmd = (self.root.register(self.validate_iso_input), '%P')
        self.shot_iso_entry.configure(validate="key", validatecommand=vcmd)
        
        self.create_tooltip(self.shot_iso_entry, 
            "Enter the ISO you shot this film at\n"
            "Example: For Portra 400 shot at 800, enter 800\n"
            "This will add (@800) to the filename\n"
            "Note: This disables Push/Pull when used")
            
        # Lens Model
        lens_frame = ttk.Frame(input_frame)
        lens_frame.pack(fill='x', pady=5)
        ttk.Label(lens_frame, text="Lens Model:", width=12).pack(side='left')
        self.lens_model = ttk.Combobox(lens_frame, width=30)
        self.lens_model.pack(side='left', padx=5)
        self.lens_model['values'] = self.pref_manager.get_lenses()
        self.lens_model.bind('<<ComboboxSelected>>', lambda e: (self.validate_combobox_input(e), self.update_file_list()))
        self.lens_model.bind('<KeyRelease>', lambda e: (self.validate_combobox_input(e), self.update_file_list()))
        
        lens_buttons = ttk.Frame(lens_frame)
        lens_buttons.pack(side='left')
        
        self.lens_add = ttk.Button(lens_buttons, text="+", width=3,
                                 command=self.add_lens_to_list)
        self.lens_add.pack(side='left', padx=2)
        
        self.lens_remove = ttk.Button(lens_buttons, text="-", width=3,
                                    command=self.remove_lens_from_list)
        self.lens_remove.pack(side='left', padx=2)
        
        # Apply to All button
        self.lens_apply_all = ttk.Button(lens_buttons, text="Apply to All",
                                      command=self.apply_lens_to_all)
        self.lens_apply_all.pack(side='left', padx=5)
        
        self.create_tooltip(self.lens_add, "Add to favorites")
        self.create_tooltip(self.lens_remove, "Remove from favorites")
        self.create_tooltip(self.lens_apply_all, "Apply this lens to all files")
        self.create_tooltip(self.lens_model, "Lens used for this roll (stored in EXIF metadata)")
        
        # Date
        date_frame = ttk.Frame(input_frame)
        date_frame.pack(fill='x', pady=5)
        ttk.Label(date_frame, text="Date:", width=12).pack(side='left')
        self.date_entry = ttk.Entry(date_frame, width=20)
        self.date_entry.pack(side='left', padx=5)
        self.date_entry.insert(0, datetime.now().strftime("%m/%d/%Y"))
        self.date_entry.bind('<KeyRelease>', lambda e: self.update_file_list())
        
        date_button = ttk.Button(date_frame, text="📅", width=3,
                               command=self.show_calendar)
        date_button.pack(side='left')
        
        # Reverse Order
        reverse_frame = ttk.Frame(input_frame)
        reverse_frame.pack(fill='x', pady=5)
        self.reverse_var = tk.BooleanVar()
        self.reverse_check = ttk.Checkbutton(reverse_frame,
                                           text="Reverse File Order",
                                           variable=self.reverse_var,
                                           command=self.update_file_list)
        self.reverse_check.pack(side='left', padx=(95, 0))
        
        self.create_tooltip(self.reverse_check,
            "Film labs often scan rolls in reverse.\n"
            "Selecting this corrects the order")
            
    def create_preview_frame(self, parent):
        """Create the image preview section"""
        preview_frame = ttk.LabelFrame(parent, text="Preview", padding="10")
        preview_frame.grid(row=0, column=0, padx=(0, 5), sticky="nsew")
        
        # Set minimum width for preview
        preview_frame.update()
        preview_frame.grid_propagate(False)
        preview_frame.configure(width=350)
        
        self.preview_label = ttk.Label(preview_frame)
        self.preview_label.pack(expand=True)
        
    def create_file_list_frame(self, parent):
        """Create the file list section"""
        list_frame = ttk.LabelFrame(parent, text="Files", padding="10")
        list_frame.grid(row=0, column=1, sticky="nsew")
        
        # Create treeview with all columns
        self.file_list = ttk.Treeview(list_frame,
                                    columns=("Filename", "Original Date", "New Name", "New Date", "Lens"),
                                    show="headings",
                                    selectmode="extended")  # Allow multiple selections
        
        # Configure columns
        self.file_list.heading("Filename", text="Original Filename")
        self.file_list.heading("Original Date", text="Original Date")
        self.file_list.heading("New Name", text="New Filename")
        self.file_list.heading("New Date", text="New Date")
        self.file_list.heading("Lens", text="Lens")
        
        # Configure lens column style
        style = ttk.Style()
        style.configure("Lens.TLabel", background="#f8f8f8")
        
        # Set column widths
        self.file_list.column("Filename", width=200)
        self.file_list.column("Original Date", width=100)
        self.file_list.column("New Name", width=250)
        self.file_list.column("New Date", width=100)
        self.file_list.column("Lens", width=150)
        
        # Add scrollbars
        y_scroll = ttk.Scrollbar(list_frame, orient="vertical",
                               command=self.file_list.yview)
        x_scroll = ttk.Scrollbar(list_frame, orient="horizontal",
                               command=self.file_list.xview)
        self.file_list.configure(yscrollcommand=y_scroll.set,
                               xscrollcommand=x_scroll.set)
        
        # Pack scrollbars and treeview
        y_scroll.pack(side="right", fill="y")
        x_scroll.pack(side="bottom", fill="x")
        self.file_list.pack(side="left", fill="both", expand=True)
        
        # Bind selection event
        self.file_list.bind('<<TreeviewSelect>>', self.on_file_select)
        
        # Bind click events for lens column dropdown
        self.file_list.bind('<ButtonPress-1>', self.on_file_list_press)
        self.file_list.bind('<ButtonRelease-1>', self.on_file_list_click)
        
    def create_control_frame(self):
        """Create the control buttons section"""
        # Progress bar container
        progress_frame = ttk.Frame(self.main_container)
        progress_frame.pack(fill='x', padx=10, pady=(0, 5))
    
        # Progress bar (hidden by default)
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, 
                                          mode='determinate',
                                          variable=self.progress_var)
    
        # Button container
        control_frame = ttk.Frame(self.main_container)
        control_frame.pack(fill="x", padx=10, pady=10)
    
        # Left button group container
        left_buttons = ttk.Frame(control_frame)
        left_buttons.pack(side="left")
    
        # Right button group container
        right_buttons = ttk.Frame(control_frame)
        right_buttons.pack(side="right")
    
        # Add Files button
        self.add_button = ttk.Button(left_buttons, text="Add Files",
                                   command=self.add_files)
        self.add_button.pack(side="left", padx=5)
    
        # Clear button
        self.clear_button = ttk.Button(left_buttons, text="Clear All",
                                     command=self.clear_files)
        self.clear_button.pack(side="left", padx=5)
    
        # Process button
        self.process_button = ttk.Button(right_buttons, text="Process Files",
                                       command=self.process_files)
        self.process_button.pack(side="right", padx=5)

    def create_tooltip(self, widget, text):
        """Create a tooltip for a widget"""
        tooltip = None
        
        def enter(event):
            nonlocal tooltip
            x, y, _, _ = widget.bbox("insert")
            x += widget.winfo_rootx() + 25
            y += widget.winfo_rooty() + 20
            
            tooltip = tk.Toplevel(widget)
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{x}+{y}")
            
            label = ttk.Label(tooltip, text=text, 
                            style='Tooltip.TLabel',
                            padding=5)
            label.pack()
            
        def leave(event):
            nonlocal tooltip
            if tooltip:
                tooltip.destroy()
                tooltip = None
                
        widget.bind('<Enter>', enter)
        widget.bind('<Leave>', leave)

    def add_camera_to_list(self):
        """Add current camera to saved list"""
        camera = self.camera_model.get().strip().upper()
        if camera:
            self.pref_manager.add_camera(camera)
            self.camera_model['values'] = self.pref_manager.get_cameras()

    def remove_camera_from_list(self):
        """Remove current camera from saved list"""
        camera = self.camera_model.get().strip().upper()
        if camera:
            self.pref_manager.remove_camera(camera)
            self.camera_model['values'] = self.pref_manager.get_cameras()

    def add_film_to_list(self):
        """Add current film to saved list"""
        film = self.film_type.get().strip().upper()
        if film:
            self.pref_manager.add_film(film)
            self.film_type['values'] = self.pref_manager.get_films()

    def remove_film_from_list(self):
        """Remove current film from saved list"""
        film = self.film_type.get().strip().upper()
        if film:
            self.pref_manager.remove_film(film)
            self.film_type['values'] = self.pref_manager.get_films()
            
    def add_lens_to_list(self):
        """Add current lens to saved list"""
        lens = self.lens_model.get().strip().upper()
        if lens:
            self.pref_manager.add_lens(lens)
            self.lens_model['values'] = self.pref_manager.get_lenses()

    def remove_lens_from_list(self):
        """Remove current lens from saved list"""
        lens = self.lens_model.get().strip().upper()
        if lens:
            self.pref_manager.remove_lens(lens)
            self.lens_model['values'] = self.pref_manager.get_lenses()
            
    def apply_lens_to_all(self):
        """Apply the current global lens to all files"""
        lens = self.lens_model.get().strip().upper()
        if lens and self.files:
            # Clear all per-file lens settings
            self.file_lenses.clear()
            
            # Update the file list to reflect changes
            self.update_file_list()
            
    def validate_iso_input(self, value):
        """Validate ISO input to ensure only numbers are entered"""
        if value == "":
            return True
        return value.isdigit()
        
    def on_shot_iso_changed(self, *args):
        """Handle changes to the Shot at ISO field"""
        shot_iso = self.shot_iso_var.get().strip()
        
        # If Shot at ISO has a value, disable Push/Pull
        if shot_iso:
            self.push_pull_minus.configure(state="disabled")
            self.push_pull_plus.configure(state="disabled")
            # Reset Push/Pull value to 0
            if self.push_pull_value.get() != 0:
                self.push_pull_value.set(0)
                self.push_pull_display.config(text="0")
        else:
            # Enable Push/Pull buttons
            self.push_pull_minus.configure(state="normal")
            self.push_pull_plus.configure(state="normal")
            
        # Update file list to reflect changes
        self.update_file_list()
        
    def increase_push_pull(self):
        """Increase the push/pull value"""
        current = self.push_pull_value.get()
        # Limit to maximum +5
        if current < 5:
            self.push_pull_value.set(current + 1)
            self.push_pull_display.config(text=str(current + 1))
            
            # Clear Shot at ISO field
            if self.shot_iso_var.get():
                self.shot_iso_var.set("")
                
            self.update_file_list()

    def decrease_push_pull(self):
        """Decrease the push/pull value"""
        current = self.push_pull_value.get()
        # Limit to minimum -5
        if current > -5:
            self.push_pull_value.set(current - 1)
            self.push_pull_display.config(text=str(current - 1))
            
            # Clear Shot at ISO field
            if self.shot_iso_var.get():
                self.shot_iso_var.set("")
                
            self.update_file_list()

    def add_files(self):
        """Handle adding new files"""
        new_files = self.file_manager.select_files()
        if not new_files:
            return
            
        # Add new files and update display
        self.files.extend(new_files)
        self.update_file_list()
        
        # Select first file
        if self.file_list.get_children():
            first_item = self.file_list.get_children()[0]
            self.file_list.selection_set(first_item)
            self.on_file_select()
            
    def update_file_list(self):
        """Update the file list display"""
        # Clear current list
        for item in self.file_list.get_children():
            self.file_list.delete(item)
            
        # Add files to list
        files_to_show = self.files.copy()
        if self.reverse_var.get():
            files_to_show.reverse()
            
        # Get global lens value
        global_lens = self.lens_model.get().strip().upper()
            
        for file in files_to_show:
            filename = os.path.basename(file)
            original_date = self.file_manager.get_image_date(file)
            
            # Get lens for this file (or use global lens if not set)
            lens = self.file_lenses.get(file, global_lens)
            
            # Add dropdown indicator to lens value
            lens_display = f"{lens} ▼"
            
            new_name = self.generate_new_filename(file)
            new_date = self.date_entry.get()
            
            # Insert item with lens as the last column
            item_id = self.file_list.insert("", "end", values=(
                filename, original_date, new_name, new_date, lens_display
            ))
            
            # Style the lens cell to indicate it's clickable with a border
            self.file_list.tag_configure("lens_cell", background="#e8e8e8", foreground="#000000")
            
            # Apply the tag to the item
            self.file_list.item(item_id, tags=("lens_cell",))
            
    def generate_new_filename(self, filepath):
        """Generate new filename based on current settings"""
        try:
            roll_num = int(self.roll_number.get())
            camera = self.camera_model.get().strip().upper()
            film = self.film_type.get().strip().upper()
            push_pull = self.push_pull_value.get()
            shot_iso = self.shot_iso_var.get().strip()
            
            if all([roll_num, camera, film]):
                idx = self.files.index(filepath) + 1
                if self.reverse_var.get():
                    idx = len(self.files) - idx + 1
                    
                ext = os.path.splitext(filepath)[1]
                
                # Create suffix based on Shot at ISO or Push/Pull
                suffix = ""
                if shot_iso:
                    # Use Shot at ISO value
                    suffix = f"(@{shot_iso})"
                elif push_pull != 0:
                    # Use Push/Pull value
                    sign = "+" if push_pull > 0 else ""
                    suffix = f"({sign}{push_pull})"
                
                return f"{roll_num:03d}-{idx:02d}-{camera}-{film}{suffix}{ext}"
                
        except (ValueError, IndexError):
            pass
            
        return os.path.basename(filepath)
        
    def on_file_select(self, event=None):
        """Handle file selection"""
        selection = self.file_list.selection()
        if not selection:
            return
            
        # Get selected file
        item = self.file_list.item(selection[0])
        filename = item['values'][0]
        
        # Find full path
        selected_file = None
        for file in self.files:
            if os.path.basename(file) == filename:
                selected_file = file
                break
                
        if selected_file:
            self.update_preview(selected_file)
            
    def update_preview(self, filepath=None):
        """Update the preview image"""
        if not filepath:
            self.preview_label.configure(image='')
            return
            
        # Check cache first
        if filepath in self.thumbnail_cache:
            self.preview_label.configure(image=self.thumbnail_cache[filepath])
            return
            
        # Create new thumbnail
        thumbnail = self.file_manager.create_thumbnail(filepath, MAX_THUMBNAIL_SIZE)
        if thumbnail:
            photo = ImageTk.PhotoImage(thumbnail)
            self.thumbnail_cache[filepath] = photo
            self.preview_label.configure(image=photo)
            
            # Limit cache size
            if len(self.thumbnail_cache) > MAX_CACHE_ENTRIES:
                # Remove oldest entries
                oldest = list(self.thumbnail_cache.keys())[:-MAX_CACHE_ENTRIES]
                for key in oldest:
                    del self.thumbnail_cache[key]
                    
    def show_calendar(self):
        """Show date picker calendar"""
        top = tk.Toplevel(self.root)
        top.overrideredirect(True)  # Remove window decorations (no stoplight buttons)
        top.configure(background='white')
        
        # Add a thin border frame to make the popup visually distinct
        border_frame = tk.Frame(top, background='#cccccc', padx=1, pady=1)
        border_frame.pack(fill='both', expand=True)
        
        inner_frame = tk.Frame(border_frame, background='white')
        inner_frame.pack(fill='both', expand=True)
        
        # Configure ttk styles for the calendar's month/year header
        cal_style = ttk.Style(top)
        cal_style.configure('TLabel', foreground='black', background='white')
        cal_style.configure('TButton', foreground='black')
        
        # Create calendar with fixed configuration
        cal = Calendar(inner_frame, 
                      selectmode='day', 
                      date_pattern='mm/dd/y',
                      showweeknumbers=False,  # Remove the extra column
                      firstweekday='sunday',  # Start week on Sunday
                      foreground='black',  # Main text color
                      background='white',  # Main background
                      headersforeground='black',  # Day name headers text color
                      headersbackground='#f0f0f0',  # Day name headers background
                      normalforeground='black',  # Normal day text color
                      normalbackground='white',  # Normal day background
                      weekendforeground='#555555',  # Weekend text color
                      weekendbackground='white',  # Weekend background
                      bordercolor='#cccccc'  # Border color
                     )
        cal.pack(padx=10, pady=10)
        
        # Try to directly configure the header label's foreground color
        try:
            # Access the internal header frame and configure text color
            for widget in cal.winfo_children():
                if hasattr(widget, 'winfo_children'):
                    for child in widget.winfo_children():
                        if isinstance(child, ttk.Label):
                            child.configure(foreground='black')
        except:
            pass
        
        # Track the click-outside binding ID for cleanup
        click_outside_id = None
        
        def cleanup_and_close():
            """Clean up bindings and close the calendar"""
            nonlocal click_outside_id
            if click_outside_id:
                try:
                    self.root.unbind('<Button-1>', click_outside_id)
                except:
                    pass
            top.destroy()
        
        def set_date():
            self.date_entry.delete(0, tk.END)
            self.date_entry.insert(0, cal.get_date())
            self.update_file_list()
            cleanup_and_close()
        
        def on_click_outside(event):
            """Close calendar when clicking outside of it"""
            # Check if the click is outside the calendar window
            try:
                # Get the widget that was clicked
                clicked_widget = event.widget
                
                # Check if click is on the calendar window or its children
                if clicked_widget == top or str(clicked_widget).startswith(str(top)):
                    return
                
                # Check if click is within calendar bounds
                cal_x = top.winfo_rootx()
                cal_y = top.winfo_rooty()
                cal_width = top.winfo_width()
                cal_height = top.winfo_height()
                
                if (cal_x <= event.x_root <= cal_x + cal_width and
                    cal_y <= event.y_root <= cal_y + cal_height):
                    return
                
                # Click was outside, close the calendar
                cleanup_and_close()
            except:
                pass
        
        # Bind date selection event (calendar closes when date is selected)
        cal.bind('<<CalendarSelected>>', lambda e: set_date())
        
        # Position calendar near date entry
        x = self.date_entry.winfo_rootx() + 10
        y = self.date_entry.winfo_rooty() + self.date_entry.winfo_height() + 10
        top.geometry(f"+{x}+{y}")
        
        # Update to get proper dimensions before binding click handler
        top.update_idletasks()
        
        # Bind click-outside handler after a short delay to prevent immediate closing
        def bind_click_outside():
            nonlocal click_outside_id
            click_outside_id = self.root.bind('<Button-1>', on_click_outside, add='+')
        
        top.after(100, bind_click_outside)
        
        # Make window float on top
        top.lift()
        top.focus_force()
        
    def on_file_list_press(self, event):
        """Handle mouse press on the file list to intercept lens column clicks"""
        # Check if dropdown was recently closed
        current_time = datetime.now().timestamp()
        if self.dropdown_active or (current_time - self.last_dropdown_time < 0.3):
            # Prevent immediate reopening
            return "break"  # Stop event propagation
            
        # Get the item and column that was clicked
        region = self.file_list.identify_region(event.x, event.y)
        if region != "cell":
            return
            
        item_id = self.file_list.identify_row(event.y)
        column = self.file_list.identify_column(event.x)
        
        # Only intercept lens column clicks
        if column == "#5" and item_id:  # Lens column
            # Store current selection to use later
            self.current_selection = self.file_list.selection()
            # Return "break" to prevent the default selection behavior
            return "break"
    
    def on_file_list_click(self, event):
        """Handle clicks on the file list"""
        # Check if dropdown was recently closed
        current_time = datetime.now().timestamp()
        if self.dropdown_active or (current_time - self.last_dropdown_time < 0.3):
            # Prevent immediate reopening
            return
            
        # Get the item and column that was clicked
        region = self.file_list.identify_region(event.x, event.y)
        if region != "cell":
            return
            
        item_id = self.file_list.identify_row(event.y)
        column = self.file_list.identify_column(event.x)
        
        # Only handle lens column clicks
        if column == "#5" and item_id:  # Lens column
            # Store current selection before doing anything
            current_selection = self.file_list.selection()
            
            # Get the file path for this item
            item_values = self.file_list.item(item_id, 'values')
            if not item_values:
                return
                
            filename = item_values[0]
            file_path = None
            for file in self.files:
                if os.path.basename(file) == filename:
                    file_path = file
                    break
                    
            if not file_path:
                return
                
            # For lens column clicks, we don't modify the selection at all
            # If the clicked item is not in the current selection, we'll still use it
            # as the target file for the lens dropdown, but won't change the selection
            
            # Restore the original selection to prevent any changes
            # This is crucial for cmd+click which might deselect items
            if current_selection:
                self.file_list.selection_set(current_selection)
            
            # Get file paths for all selected items
            selected_files = []
            for sel_item in current_selection:
                sel_values = self.file_list.item(sel_item, 'values')
                if sel_values:
                    sel_filename = sel_values[0]
                    for file in self.files:
                        if os.path.basename(file) == sel_filename:
                            selected_files.append(file)
                            break
            
            # If no files are selected, just use the clicked file
            if not selected_files:
                selected_files = [file_path]
            
            # Show inline dropdown for lens selection
            self.show_lens_dropdown(item_id, column, file_path, selected_files)
            
    def show_lens_dropdown(self, item_id, column, file_path, selected_files=None):
        """Show custom dropdown menu for lens selection"""
        # Store the current selection to restore it later
        current_selection = self.file_list.selection()
        
        # If there's already an active dropdown, destroy it
        if hasattr(self, 'active_dropdown') and self.active_dropdown and self.active_dropdown.winfo_exists():
            self.active_dropdown.destroy()
            self.active_dropdown = None
        
        # Get cell coordinates
        x, y, width, height = self.file_list.bbox(item_id, column)
        
        # Get current lens value (from per-file setting or global)
        current_lens = self.file_lenses.get(file_path, self.lens_model.get().strip().upper())
        
        # Get all lens values
        lens_values = self.pref_manager.get_lenses()
        
        # Create a custom dropdown menu
        dropdown = tk.Toplevel(self.root)
        dropdown.overrideredirect(True)  # Remove window decorations
        
        # Position the dropdown below the cell
        dropdown_x = self.file_list.winfo_rootx() + x
        dropdown_y = self.file_list.winfo_rooty() + y + height
        dropdown.geometry(f"{width}x{min(200, len(lens_values) * 25)}+{dropdown_x}+{dropdown_y}")
        
        # Restore the selection after creating the dropdown
        # This is crucial as the dropdown creation might affect the selection
        if current_selection:
            self.file_list.selection_set(current_selection)
        
        # Create a frame with a border
        frame = ttk.Frame(dropdown, style="Dropdown.TFrame")
        frame.pack(fill="both", expand=True)
        
        # Create a canvas with scrollbar for the dropdown items
        canvas = tk.Canvas(frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        
        # Configure the canvas
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Create a frame inside the canvas to hold the items
        items_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=items_frame, anchor="nw")
        
        # Set dropdown active flag
        self.dropdown_active = True
        
        # Function to handle item selection
        def on_select(lens, event=None):
            # If we have multiple files selected
            if selected_files and len(selected_files) > 0:
                # Apply the lens to all selected files
                for sel_file in selected_files:
                    self.file_lenses[sel_file] = lens
            else:
                # Just apply to the current file
                self.file_lenses[file_path] = lens
                
            # Add to favorites if not already there
            self.pref_manager.add_lens(lens)
            self.lens_model['values'] = self.pref_manager.get_lenses()
            
            # Update the file list
            self.update_file_list()
                
            # Clean up
            dropdown.destroy()
            self.active_dropdown = None
            
            # Set timestamp to prevent immediate reopening
            self.last_dropdown_time = datetime.now().timestamp()
            self.dropdown_active = False
            
            # Restore focus to the main window so input fields work
            self.root.focus_force()
            
            # Stop event propagation
            if event:
                return "break"
        
        # Add items to the dropdown
        for lens in lens_values:
            item_frame = ttk.Frame(items_frame)
            item_frame.pack(fill="x")
            
            # Create a label for each item
            label = ttk.Label(item_frame, text=lens, padding=(5, 2))
            label.pack(fill="x")
            
            # Highlight the current selection
            if lens == current_lens:
                label.configure(background="#e0e0e0")
            
            # Bind events
            label.bind("<Button-1>", lambda e, l=lens: on_select(l))
            
            # Add hover effect
            def on_enter(e, lbl=label):
                lbl.configure(background="#e0e0e0")
            
            def on_leave(e, lbl=label, selected=(lens == current_lens)):
                if not selected:
                    lbl.configure(background="")
            
            label.bind("<Enter>", on_enter)
            label.bind("<Leave>", on_leave)
        
        # Update the canvas scroll region
        items_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))
        
        # Store reference to active dropdown
        self.active_dropdown = dropdown
        
        # Handle click outside
        def on_click_outside(event):
            if event.widget != dropdown and not event.widget.winfo_toplevel() == dropdown:
                dropdown.destroy()
                self.active_dropdown = None
                self.root.unbind("<Button-1>", on_click_outside_id)
                
                # Set timestamp to prevent immediate reopening
                self.last_dropdown_time = datetime.now().timestamp()
                self.dropdown_active = False
                
                # Restore focus to the main window so input fields work
                self.root.focus_force()
        
        on_click_outside_id = self.root.bind("<Button-1>", on_click_outside, add="+")
        
        # Ensure dropdown is on top
        dropdown.lift()
        dropdown.focus_set()
    
    def clear_files(self):
        """Clear all files"""
        self.files = []
        self.thumbnail_cache.clear()
        self.file_lenses.clear()  # Clear lens data
        self.update_file_list()
        self.update_preview(None)

    def process_files(self):
        """Process and rename files"""
        if not self.files:
            messagebox.showwarning("Warning", "No files selected")
            return
            
        try:
            # Validate inputs
            roll_num = int(self.roll_number.get())
            camera = self.camera_model.get().strip().upper()
            film = self.film_type.get().strip().upper()
            date_str = self.date_entry.get()
            
            # Validate date
            try:
                selected_date = datetime.strptime(date_str, "%m/%d/%Y")
            except ValueError:
                messagebox.showerror("Error", "Invalid date format")
                return
            
            if not all([roll_num, camera, film]):
                messagebox.showwarning("Warning", "Please fill in all fields")
                return
                
            # Ask user for output directory
            output_dir = filedialog.askdirectory(
                title="Select Output Directory"
            )
            if not output_dir:  # User cancelled
                return
            
            # Create suffix based on Shot at ISO or Push/Pull
            suffix = ""
            shot_iso = self.shot_iso_var.get().strip()
            push_pull = self.push_pull_value.get()
            
            if shot_iso:
                # Use Shot at ISO value
                suffix = f"(@{shot_iso})"
            elif push_pull != 0:
                # Use Push/Pull value
                sign = "+" if push_pull > 0 else ""
                suffix = f"({sign}{push_pull})"
            
            # Create new folder name
            new_folder = f"{roll_num:03d}-{camera}-{film}{suffix}-{selected_date.strftime('%b%y').upper()}"
            output_path = os.path.join(output_dir, new_folder)
            
            # Create output directory
            os.makedirs(output_path, exist_ok=True)
            
            # Show progress bar
            self.progress_bar.pack(fill='x')
            
            # Process files
            files_to_process = self.files.copy()
            if self.reverse_var.get():
                files_to_process.reverse()
            
            # Save preferences
            if camera:
                self.pref_manager.add_camera(camera)
            if film:
                self.pref_manager.add_film(film)
            
            total_files = len(files_to_process)
            processed_files = 0
            
            # Process each file
            for idx, file in enumerate(files_to_process, start=1):
                try:
                    # Update progress
                    progress = (idx / total_files) * 100
                    self.progress_var.set(progress)
                    self.root.update_idletasks()
                    
                    # Generate new filename
                    ext = os.path.splitext(file)[1]
                    
                    # Create suffix based on Shot at ISO or Push/Pull
                    suffix = ""
                    shot_iso = self.shot_iso_var.get().strip()
                    push_pull = self.push_pull_value.get()
                    
                    if shot_iso:
                        # Use Shot at ISO value
                        suffix = f"(@{shot_iso})"
                    elif push_pull != 0:
                        # Use Push/Pull value
                        sign = "+" if push_pull > 0 else ""
                        suffix = f"({sign}{push_pull})"
                    
                    new_name = f"{roll_num:03d}-{idx:02d}-{camera}-{film}{suffix}{ext}"
                    new_path = os.path.join(output_path, new_name)
                    
                    # Copy file and update date
                    shutil.copy2(file, new_path)
                    
                    # Update file dates if possible
                    try:
                        date_str = selected_date.strftime("%Y:%m:%d %H:%M:%S")
                        
                        # Update EXIF date and lens
                        try:
                            exif_dict = piexif.load(new_path)
                            exif_dict['0th'][piexif.ImageIFD.DateTime] = date_str.encode()
                            exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = date_str.encode()
                            exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized] = date_str.encode()
                            
                            # Add lens information if available
                            lens = self.file_lenses.get(file, self.lens_model.get().strip().upper())
                            if lens:
                                # Set lens model in EXIF
                                exif_dict['Exif'][piexif.ExifIFD.LensModel] = lens.encode()
                                
                            exif_bytes = piexif.dump(exif_dict)
                            piexif.insert(exif_bytes, new_path)
                        except Exception as exif_error:
                            logging.warning(f"Error updating EXIF: {exif_error}")
                            
                        # Update file modification time
                        os.utime(new_path, (selected_date.timestamp(), selected_date.timestamp()))
                        
                        # Update macOS creation date if on macOS
                        if IS_MACOS:
                            try:
                                from Foundation import (
                                    NSFileManager,
                                    NSDate,
                                    NSFileCreationDate,
                                    NSNumber
                                )
                                
                                # Convert Python datetime to NSDate
                                timestamp = selected_date.timestamp()
                                ns_date = NSDate.dateWithTimeIntervalSince1970_(timestamp)
                                
                                # Create attributes dictionary with creation date
                                attrs = {NSFileCreationDate: ns_date}
                                
                                # Set file attributes
                                file_manager = NSFileManager.defaultManager()
                                result, error = file_manager.setAttributes_ofItemAtPath_error_(
                                    attrs, new_path, None
                                )
                                
                                if not result and error:
                                    logging.warning(f"Failed to set macOS creation date: {error}")
                            except Exception as e:
                                logging.warning(f"Error setting macOS creation date: {e}")
                    except:
                        pass
                        
                    processed_files += 1
                        
                except Exception as e:
                    messagebox.showerror("Error", f"Error processing {os.path.basename(file)}: {str(e)}")
                    return
            
            # Hide progress bar
            self.progress_bar.pack_forget()
            
            # Clear files after successful processing
            self.clear_files()
            
            # Update combobox values
            self.camera_model['values'] = self.pref_manager.get_cameras()
            self.film_type['values'] = self.pref_manager.get_films()
            
            # Show success message and open folder
            messagebox.showinfo("Success", f"Successfully processed {processed_files}/{total_files} files!")
            
            # Open output folder in Finder
            if IS_MACOS:
                os.system(f'open "{output_path}"')
            else:
                os.startfile(output_path)
                
        except Exception as e:
            messagebox.showerror("Error", f"Processing error: {str(e)}")
            # Hide progress bar on error
            self.progress_bar.pack_forget()
