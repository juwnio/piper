import pyautogui
from math import exp, log

class CursorController:
    def __init__(self):
        self.base_speed = 1.0
        self.min_speed = 0.3
        self.max_speed = 8.0
        self.smoothing_window = []
        self.window_size = 3
        
    def apply_adaptive_smoothing(self, dx, dy):
        """Apply adaptive smoothing based on movement velocity"""
        # Add new movement to window
        self.smoothing_window.append((dx, dy))
        if len(self.smoothing_window) > self.window_size:
            self.smoothing_window.pop(0)
            
        # Calculate velocity-based weights
        velocity = sum(abs(x) + abs(y) for x, y in self.smoothing_window)
        weights = [exp(i/self.window_size) for i in range(len(self.smoothing_window))]
        
        # Apply weighted smoothing
        smooth_x = sum(p[0] * w for p, w in zip(self.smoothing_window, weights))
        smooth_y = sum(p[1] * w for p, w in zip(self.smoothing_window, weights))
        total_weight = sum(weights)
        
        return smooth_x/total_weight, smooth_y/total_weight
    
    def calculate_adaptive_speed(self, dx, dy):
        """Calculate speed based on movement magnitude"""
        magnitude = (dx * dx + dy * dy) ** 0.5
        
        if magnitude < 1:
            return self.min_speed
        elif magnitude > 100:
            return self.max_speed
            
        # Logarithmic scaling for natural feel
        speed = self.base_speed * (1 + 0.5 * log(magnitude + 1))
        return min(self.max_speed, max(self.min_speed, speed))
    
    def move_cursor(self, dx, dy, relative=True):
        """Move cursor with improved precision"""
        if abs(dx) < 0.1 and abs(dy) < 0.1:
            return
            
        # Apply smoothing
        smooth_x, smooth_y = self.apply_adaptive_smoothing(dx, dy)
        
        # Apply speed scaling
        speed = self.calculate_adaptive_speed(smooth_x, smooth_y)
        final_x = smooth_x * speed
        final_y = smooth_y * speed
        
        # Execute movement
        if relative:
            pyautogui.moveRel(final_x, final_y)
        else:
            pyautogui.moveTo(final_x, final_y)