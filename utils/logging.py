"""
Logging utilities for debug and information messages.
"""
from datetime import datetime

def debug_log(message, level="INFO", component="app"):
    """
    Enhanced debug logging with timestamps and component information
    
    Args:
        message (str): Log message to display
        level (str): Log level (INFO, WARNING, ERROR, DEBUG)
        component (str): Component/module name for better organization
    """
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    # Color coding for different log levels
    level_colors = {
        "INFO": "🔷",
        "WARNING": "⚠️", 
        "ERROR": "❌",
        "DEBUG": "🔍",
        "SUCCESS": "✅"
    }
    
    icon = level_colors.get(level, "📝")
    print(f"{icon} [{timestamp}] [{component}] {message}")


# Test functionality when run directly
if __name__ == "__main__":
    print("Testing logging module...")
    debug_log("Test INFO message", "INFO", "test")
    debug_log("Test SUCCESS message", "SUCCESS", "test")
    debug_log("Test WARNING message", "WARNING", "test")
    debug_log("Test ERROR message", "ERROR", "test")
    print("✅ Logging module test completed!")
