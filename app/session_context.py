"""Session context manager for tracking user state during a CLI session.

This module maintains state like current year/semester, last calculated values,
and course entries to enable smart auto-population and pre-filling of form fields.
"""

class SessionContext:
    """Manages session state for logged-in users during a CLI session."""
    
    def __init__(self):
        """Initialize empty session context."""
        self.user_id = None
        self.username = None
        self.current_year = None
        self.current_semester = None
        self.last_gpa = None
        self.last_cgpa = None
        self.last_cu = None
        self.last_entry_type = None  # "calculation", "manual_entry", "saved", etc.
        self.current_courses_being_entered = []
    
    def set_user(self, user_id: int, username: str):
        """Set current user info."""
        self.user_id = user_id
        self.username = username
    
    def set_last_calculation(self, gpa: float = None, cgpa: float = None, cu: int = None, entry_type: str = None):
        """Record the result of the last calculation."""
        if gpa is not None:
            self.last_gpa = gpa
        if cgpa is not None:
            self.last_cgpa = cgpa
        if cu is not None:
            self.last_cu = cu
        if entry_type is not None:
            self.last_entry_type = entry_type
    
    def set_semester_context(self, year: int, semester_num: int):
        """Set the current year and semester being worked with."""
        self.current_year = year
        self.current_semester = semester_num
    
    def get_semester_context(self) -> tuple:
        """Get current year and semester, or (None, None) if not set."""
        return (self.current_year, self.current_semester)
    
    def set_current_courses(self, courses: list):
        """Store courses currently being entered in this session."""
        self.current_courses_being_entered = courses
    
    def get_current_courses(self) -> list:
        """Get the courses being entered."""
        return self.current_courses_being_entered
    
    def clear(self):
        """Clear all session data (usually on logout)."""
        self.user_id = None
        self.username = None
        self.current_year = None
        self.current_semester = None
        self.last_gpa = None
        self.last_cgpa = None
        self.last_cu = None
        self.last_entry_type = None
        self.current_courses_being_entered = []
    
    def get_summary(self) -> dict:
        """Get a summary of current session state for debugging/display."""
        return {
            'user': self.username,
            'current_year': self.current_year,
            'current_semester': self.current_semester,
            'last_gpa': self.last_gpa,
            'last_cgpa': self.last_cgpa,
            'last_cu': self.last_cu,
            'last_entry_type': self.last_entry_type,
            'courses_in_progress': len(self.current_courses_being_entered)
        }


# Global session context instance
_session_context = SessionContext()

def get_session() -> SessionContext:
    """Get the current session context."""
    return _session_context

def reset_session():
    """Reset the session context."""
    _session_context.clear()
