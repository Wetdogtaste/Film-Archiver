"""
Film Archiver - macOS-style Toggle Switch Widget
"""
import tkinter as tk


class ToggleSwitch(tk.Canvas):
    """A macOS-style toggle switch widget"""
    
    def __init__(self, parent, width=44, height=24, on_color="#34C759", off_color="#E5E5EA",
                 knob_color="#FFFFFF", command=None, initial_state=False, bg=None, **kwargs):
        """
        Initialize the toggle switch.
        
        Args:
            parent: Parent widget
            width: Width of the toggle switch
            height: Height of the toggle switch
            on_color: Background color when toggled on (green by default)
            off_color: Background color when toggled off (gray by default)
            knob_color: Color of the circular knob
            command: Callback function when toggle state changes
            initial_state: Initial state of the toggle (False = off, True = on)
            bg: Background color (should match parent's background)
        """
        # Get parent's background color if not specified
        if bg is None:
            try:
                bg = parent.cget('background')
            except:
                bg = '#FFFFFF'
        
        super().__init__(parent, width=width, height=height, 
                        highlightthickness=0, borderwidth=0, bg=bg, **kwargs)
        
        self._bg_color = bg
        
        self.width = width
        self.height = height
        self.on_color = on_color
        self.off_color = off_color
        self.knob_color = knob_color
        self.command = command
        self._state = initial_state
        
        # Calculate dimensions
        self.padding = 2
        self.knob_radius = (height - 2 * self.padding) // 2
        self.corner_radius = height // 2
        
        # Animation state
        self._animating = False
        self._animation_steps = 8
        self._animation_delay = 12  # milliseconds
        
        # Draw initial state
        self._draw()
        
        # Bind click event
        self.bind("<Button-1>", self._on_click)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        
        # Store hover state
        self._hovering = False
        
    def _draw(self):
        """Draw the toggle switch"""
        self.delete("all")
        
        # Calculate knob position
        if self._state:
            knob_x = self.width - self.padding - self.knob_radius
            bg_color = self.on_color
        else:
            knob_x = self.padding + self.knob_radius
            bg_color = self.off_color
            
        # Draw background pill shape
        self._draw_pill(self.padding, self.padding, 
                       self.width - self.padding, self.height - self.padding,
                       self.corner_radius - self.padding, bg_color)
        
        # Draw knob
        knob_y = self.height // 2
        
        # Draw knob (clean, no shadow for macOS native look)
        self.create_oval(
            knob_x - self.knob_radius,
            knob_y - self.knob_radius,
            knob_x + self.knob_radius,
            knob_y + self.knob_radius,
            fill=self.knob_color, outline="#D1D1D6" if not self._state else ""
        )
        
    def _draw_pill(self, x1, y1, x2, y2, radius, color):
        """Draw a pill-shaped rounded rectangle"""
        # Draw the pill shape using multiple components
        # Left semicircle
        self.create_arc(x1, y1, x1 + 2 * radius, y2, 
                       start=90, extent=180, fill=color, outline="")
        # Right semicircle
        self.create_arc(x2 - 2 * radius, y1, x2, y2,
                       start=270, extent=180, fill=color, outline="")
        # Center rectangle
        self.create_rectangle(x1 + radius, y1, x2 - radius, y2, 
                            fill=color, outline="")
        
    def _on_click(self, event):
        """Handle click event"""
        if self._animating:
            return
            
        self._state = not self._state
        self._animate_toggle()
        
        if self.command:
            self.command(self._state)
            
    def _on_enter(self, event):
        """Handle mouse enter"""
        self._hovering = True
        self.config(cursor="hand2")
        
    def _on_leave(self, event):
        """Handle mouse leave"""
        self._hovering = False
        self.config(cursor="")
        
    def _animate_toggle(self):
        """Animate the toggle transition"""
        self._animating = True
        
        if self._state:
            # Animating from off to on
            start_x = self.padding + self.knob_radius
            end_x = self.width - self.padding - self.knob_radius
        else:
            # Animating from on to off
            start_x = self.width - self.padding - self.knob_radius
            end_x = self.padding + self.knob_radius
            
        step_size = (end_x - start_x) / self._animation_steps
        current_step = [0]  # Use list to allow modification in nested function
        
        def animate_step():
            if current_step[0] < self._animation_steps:
                current_step[0] += 1
                progress = current_step[0] / self._animation_steps
                
                # Use ease-out curve for smoother animation
                eased_progress = 1 - (1 - progress) ** 2
                
                knob_x = start_x + (end_x - start_x) * eased_progress
                
                # Interpolate background color
                if self._state:
                    bg_color = self._interpolate_color(self.off_color, self.on_color, eased_progress)
                else:
                    bg_color = self._interpolate_color(self.on_color, self.off_color, eased_progress)
                
                self._draw_animated_state(knob_x, bg_color)
                self.after(self._animation_delay, animate_step)
            else:
                self._animating = False
                self._draw()
                
        animate_step()
        
    def _draw_animated_state(self, knob_x, bg_color):
        """Draw the toggle at a specific animation state"""
        self.delete("all")
        
        # Draw background
        self._draw_pill(self.padding, self.padding,
                       self.width - self.padding, self.height - self.padding,
                       self.corner_radius - self.padding, bg_color)
        
        # Draw knob
        knob_y = self.height // 2
        
        # Knob (clean, no shadow for macOS native look)
        self.create_oval(
            knob_x - self.knob_radius,
            knob_y - self.knob_radius,
            knob_x + self.knob_radius,
            knob_y + self.knob_radius,
            fill=self.knob_color, outline=""
        )
        
    def _interpolate_color(self, color1, color2, progress):
        """Interpolate between two colors"""
        # Convert hex to RGB
        r1, g1, b1 = self._hex_to_rgb(color1)
        r2, g2, b2 = self._hex_to_rgb(color2)
        
        # Interpolate
        r = int(r1 + (r2 - r1) * progress)
        g = int(g1 + (g2 - g1) * progress)
        b = int(b1 + (b2 - b1) * progress)
        
        return f"#{r:02x}{g:02x}{b:02x}"
        
    def _hex_to_rgb(self, hex_color):
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
    def get_state(self):
        """Get current toggle state"""
        return self._state
        
    def set_state(self, state, animate=False):
        """Set toggle state"""
        if state != self._state:
            self._state = state
            if animate:
                self._animate_toggle()
            else:
                self._draw()
