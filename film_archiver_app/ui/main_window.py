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
                                    columns=("Filename", "Original Date", "New Name", "New Date"),
                                    show="headings",
                                    selectmode="browse")
        
        # Configure columns
        self.file_list.heading("Filename", text="Original Filename")
        self.file_list.heading("Original Date", text="Original Date")
        self.file_list.heading("New Name", text="New Filename")
        self.file_list.heading("New Date", text="New Date")
        
        # Set column widths
        self.file_list.column("Filename", width=200)
        self.file_list.column("Original Date", width=100)
        self.file_list.column("New Name", width=250)
        self.file_list.column("New Date", width=100)
        
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
            
        for file in files_to_show:
            filename = os.path.basename(file)
            original_date = self.file_manager.get_image_date(file)
            new_name = self.generate_new_filename(file)
            new_date = self.date_entry.get()
            
            self.file_list.insert("", "end", values=(
                filename, original_date, new_name, new_date
            ))
            
    def generate_new_filename(self, filepath):
        """Generate new filename based on current settings"""
        try:
            roll_num = int(self.roll_number.get())
            camera = self.camera_model.get().strip().upper()
            film = self.film_type.get().strip().upper()
            
            if all([roll_num, camera, film]):
                idx = self.files.index(filepath) + 1
                if self.reverse_var.get():
                    idx = len(self.files) - idx + 1
                    
                ext = os.path.splitext(filepath)[1]
                return f"{roll_num:03d}-{idx:02d}-{camera}-{film}{ext}"
                
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
        top.title("Select Date")
        top.transient(self.root)
        
        # Create calendar with fixed configuration
        cal = Calendar(top, 
                      selectmode='day', 
                      date_pattern='mm/dd/y',
                      showweeknumbers=False,  # Remove the extra column
                      firstweekday='sunday'   # Start week on Sunday
                     )
        cal.pack(padx=10, pady=10)
        
        def set_date():
            self.date_entry.delete(0, tk.END)
            self.date_entry.insert(0, cal.get_date())
            self.update_file_list()
            top.destroy()
        
        def on_click_outside(event=None):
            if event.widget == top:
                top.destroy()
        
        # Bind events
        top.bind('<FocusOut>', on_click_outside)
        cal.bind('<<CalendarSelected>>', lambda e: set_date())
        
        # Position calendar near date entry
        x = self.date_entry.winfo_rootx() + 10
        y = self.date_entry.winfo_rooty() + self.date_entry.winfo_height() + 10
        top.geometry(f"+{x}+{y}")
        
        # Make window float on top
        top.lift()
        top.focus_force()
        
    def clear_files(self):
        """Clear all files"""
        self.files = []
        self.thumbnail_cache.clear()
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
            
            # Create new folder name
            new_folder = f"{roll_num:03d}-{camera}-{film}-{selected_date.strftime('%b%y').upper()}"
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
                    new_name = f"{roll_num:03d}-{idx:02d}-{camera}-{film}{ext}"
                    new_path = os.path.join(output_path, new_name)
                    
                    # Copy file and update date
                    shutil.copy2(file, new_path)
                    
                    # Update file dates if possible
                    try:
                        date_str = selected_date.strftime("%Y:%m:%d %H:%M:%S")
                        
                        # Update EXIF date
                        try:
                            exif_dict = piexif.load(new_path)
                            exif_dict['0th'][piexif.ImageIFD.DateTime] = date_str.encode()
                            exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = date_str.encode()
                            exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized] = date_str.encode()
                            exif_bytes = piexif.dump(exif_dict)
                            piexif.insert(exif_bytes, new_path)
                        except:
                            pass
                            
                        # Update file modification time
                        os.utime(new_path, (selected_date.timestamp(), selected_date.timestamp()))
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