"""
Native macOS Drag and Drop Support using PyObjC

This module provides drag-and-drop functionality for tkinter windows
on macOS using native Cocoa APIs through PyObjC, without requiring
tkinterdnd2 or the tkdnd Tcl extension.
"""
import logging
import sys
import threading

logger = logging.getLogger(__name__)

# Check if we're on macOS
IS_MACOS = sys.platform == 'darwin'

# Flag to track if native DnD is available
NATIVE_DND_AVAILABLE = False

if IS_MACOS:
    try:
        import objc
        from AppKit import (
            NSView, NSWindow, NSFilenamesPboardType, NSDragOperationCopy,
            NSDragOperationNone, NSMakeRect, NSBorderlessWindowMask,
            NSColor, NSApp, NSBackingStoreBuffered
        )
        from Foundation import NSObject, NSArray
        from Quartz import CGWindowListCopyWindowInfo, kCGWindowListOptionOnScreenOnly, kCGNullWindowID
        NATIVE_DND_AVAILABLE = True
        logger.info("PyObjC available for native drag and drop")
    except ImportError as e:
        logger.warning(f"PyObjC not available for native drag and drop: {e}")
        NATIVE_DND_AVAILABLE = False


class DropTargetView(NSView):
    """Custom NSView that handles drag and drop operations."""
    
    @objc.python_method
    def initWithCallback_(self, callback):
        """Initialize with a Python callback function."""
        self = objc.super(DropTargetView, self).init()
        if self is None:
            return None
        self._drop_callback = callback
        self._drag_enter_callback = None
        self._drag_leave_callback = None
        # Register for file drags
        self.registerForDraggedTypes_([NSFilenamesPboardType])
        return self
    
    @objc.python_method
    def setDragCallbacks_(self, enter_callback, leave_callback):
        """Set drag enter/leave callbacks."""
        self._drag_enter_callback = enter_callback
        self._drag_leave_callback = leave_callback
    
    def draggingEntered_(self, sender):
        """Called when a drag enters the view."""
        if self._drag_enter_callback:
            try:
                self._drag_enter_callback()
            except Exception as e:
                logger.debug(f"Error in drag enter callback: {e}")
        return NSDragOperationCopy
    
    def draggingExited_(self, sender):
        """Called when a drag exits the view."""
        if self._drag_leave_callback:
            try:
                self._drag_leave_callback()
            except Exception as e:
                logger.debug(f"Error in drag leave callback: {e}")
    
    def draggingUpdated_(self, sender):
        """Called when a drag is updated within the view."""
        return NSDragOperationCopy
    
    def prepareForDragOperation_(self, sender):
        """Prepare for the drop operation."""
        return True
    
    def performDragOperation_(self, sender):
        """Perform the actual drop operation."""
        try:
            pasteboard = sender.draggingPasteboard()
            if pasteboard.types().containsObject_(NSFilenamesPboardType):
                files = pasteboard.propertyListForType_(NSFilenamesPboardType)
                if files and self._drop_callback:
                    # Convert NSArray to Python list
                    paths = list(files)
                    logger.debug(f"Dropped files: {paths}")
                    # Call the callback on the main thread
                    self._drop_callback(paths)
                    return True
        except Exception as e:
            logger.error(f"Error in drop operation: {e}")
        return False


class MacOSDragDropHandler:
    """
    Handles native macOS drag and drop for a tkinter window.
    
    Uses a transparent overlay NSWindow to capture drag events.
    """
    
    def __init__(self, tk_widget, on_drop_callback, on_drag_enter=None, on_drag_leave=None):
        """
        Initialize the drag-and-drop handler.
        
        Args:
            tk_widget: The tkinter widget to enable drag-and-drop on
            on_drop_callback: Function called when files are dropped. 
                              Receives a list of file paths.
            on_drag_enter: Optional callback when drag enters the area
            on_drag_leave: Optional callback when drag leaves the area
        """
        self.tk_widget = tk_widget
        self.on_drop_callback = on_drop_callback
        self.on_drag_enter = on_drag_enter
        self.on_drag_leave = on_drag_leave
        self._overlay_window = None
        self._drop_view = None
        self._is_setup = False
        self._update_timer = None
        
    def setup(self):
        """Set up the drag-and-drop functionality."""
        if not IS_MACOS or not NATIVE_DND_AVAILABLE:
            logger.info("Native macOS drag-and-drop not available")
            return False
            
        try:
            # Wait for the tkinter window to be fully ready
            self.tk_widget.after(500, self._create_overlay)
            self._is_setup = True
            return True
        except Exception as e:
            logger.warning(f"Failed to set up native drag-and-drop: {e}")
            return False
    
    def _call_drop_callback(self, paths):
        """Call the drop callback safely on the tkinter main thread."""
        if self.on_drop_callback:
            # Use tkinter's after() to call on the main thread
            self.tk_widget.after(0, lambda: self.on_drop_callback(paths))
    
    def _call_enter_callback(self):
        """Call the drag enter callback safely."""
        if self.on_drag_enter:
            self.tk_widget.after(0, self.on_drag_enter)
    
    def _call_leave_callback(self):
        """Call the drag leave callback safely."""
        if self.on_drag_leave:
            self.tk_widget.after(0, self.on_drag_leave)
    
    def _create_overlay(self):
        """Create a transparent overlay window for drag-and-drop."""
        try:
            # Get the tkinter window's root
            root = self.tk_widget.winfo_toplevel()
            
            # Get window geometry
            x = root.winfo_rootx()
            y = root.winfo_rooty()
            width = root.winfo_width()
            height = root.winfo_height()
            
            # Adjust for screen coordinates (macOS y is from bottom)
            screen_height = root.winfo_screenheight()
            ns_y = screen_height - y - height
            
            # Create the overlay window
            rect = NSMakeRect(x, ns_y, width, height)
            
            # Create a borderless, transparent window
            self._overlay_window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
                rect,
                NSBorderlessWindowMask,
                NSBackingStoreBuffered,
                False
            )
            
            # Make it transparent
            self._overlay_window.setBackgroundColor_(NSColor.clearColor())
            self._overlay_window.setOpaque_(False)
            self._overlay_window.setIgnoresMouseEvents_(True)  # Let clicks through
            self._overlay_window.setLevel_(1)  # Above normal windows
            self._overlay_window.setHasShadow_(False)
            
            # Create the drop target view
            self._drop_view = DropTargetView.alloc().initWithCallback_(self._call_drop_callback)
            self._drop_view.setDragCallbacks_(self._call_enter_callback, self._call_leave_callback)
            self._drop_view.setWantsLayer_(True)
            self._drop_view.layer().setBackgroundColor_(NSColor.clearColor().CGColor())
            
            # Set the view as the content view
            self._overlay_window.setContentView_(self._drop_view)
            
            # Enable mouse events only for drag operations
            # The trick is to have the window ignore regular mouse events
            # but still receive drag events
            self._overlay_window.setAcceptsMouseMovedEvents_(False)
            
            # Show the window
            self._overlay_window.orderFront_(None)
            
            # Start updating position
            self._start_position_updates()
            
            logger.debug("Created overlay window for drag-and-drop")
            
        except Exception as e:
            logger.warning(f"Error creating overlay window: {e}")
    
    def _start_position_updates(self):
        """Start periodic updates to keep overlay aligned with tkinter window."""
        self._update_position()
    
    def _update_position(self):
        """Update the overlay window position to match tkinter window."""
        if not self._overlay_window:
            return
            
        try:
            root = self.tk_widget.winfo_toplevel()
            
            # Get current tkinter window geometry
            x = root.winfo_rootx()
            y = root.winfo_rooty()
            width = root.winfo_width()
            height = root.winfo_height()
            
            # Convert to macOS coordinates
            screen_height = root.winfo_screenheight()
            ns_y = screen_height - y - height
            
            # Update overlay position and size
            rect = NSMakeRect(x, ns_y, width, height)
            self._overlay_window.setFrame_display_(rect, True)
            
        except Exception as e:
            logger.debug(f"Error updating position: {e}")
        
        # Schedule next update
        if self._is_setup:
            self._update_timer = self.tk_widget.after(100, self._update_position)
    
    def destroy(self):
        """Clean up the overlay window."""
        self._is_setup = False
        if self._update_timer:
            try:
                self.tk_widget.after_cancel(self._update_timer)
            except:
                pass
        if self._overlay_window:
            try:
                self._overlay_window.close()
            except:
                pass
            self._overlay_window = None


def setup_native_drag_drop(tk_widget, on_drop_callback, on_drag_enter=None, on_drag_leave=None):
    """
    Convenience function to set up native drag-and-drop on a tkinter widget.
    
    Returns True if setup was successful, False otherwise.
    """
    if not IS_MACOS or not NATIVE_DND_AVAILABLE:
        return False
        
    handler = MacOSDragDropHandler(
        tk_widget, 
        on_drop_callback,
        on_drag_enter,
        on_drag_leave
    )
    return handler.setup()


def get_dropped_files_from_pasteboard():
    """
    Try to get dropped files from the macOS pasteboard.
    This can be used as a fallback method.
    """
    if not IS_MACOS or not NATIVE_DND_AVAILABLE:
        return []
    
    try:
        from AppKit import NSPasteboard, NSFilenamesPboardType
        
        pasteboard = NSPasteboard.generalPasteboard()
        if pasteboard.types().containsObject_(NSFilenamesPboardType):
            files = pasteboard.propertyListForType_(NSFilenamesPboardType)
            if files:
                return list(files)
    except Exception as e:
        logger.debug(f"Error reading pasteboard: {e}")
    
    return []
