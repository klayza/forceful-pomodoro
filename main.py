import tkinter as tk
from tkinter import messagebox, simpledialog, font
import time
import threading
import json
import os
from datetime import datetime

class ForcefulPomodoro:
    def __init__(self, root):
        self.root = root
        self.root.title("Forceful Pomodoro Timer")
        self.root.attributes('-fullscreen', True)
        self.root.protocol("WM_DELETE_WINDOW", self.disable_close)
        self.root.focus_force()
        self.root.lift()
        self.root.attributes('-topmost', True)
        
        # Set color scheme
        self.bg_color = "#f5f5f5"  # Light gray background
        self.accent_color = "#3498db"  # Blue accent
        self.text_color = "#2c3e50"  # Dark blue-gray text
        self.success_color = "#2ecc71"  # Green for success
        self.warning_color = "#e74c3c"  # Red for warnings/breaks
        
        # Configure root with background color
        self.root.configure(bg=self.bg_color)
        
        # Bind escape key and alt-f4 to do nothing
        self.root.bind('<Escape>', lambda e: None)
        self.root.bind('<Alt-F4>', lambda e: None)
        self.root.bind('<Alt-Tab>', lambda e: None)
        
        # Initialize variables
        self.work_minutes = 0
        self.accumulated_work = 0
        self.current_task = ""
        self.timer_running = False
        self.session_start_time = None
        
        # Load or create JSON database
        self.db_file = "pomodoro_sessions.json"
        self.load_database()
        
        # Create UI elements
        self.create_widgets()
    
    def load_database(self):
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r') as file:
                    self.sessions = json.load(file)
            except json.JSONDecodeError:
                self.sessions = []
        else:
            self.sessions = []
    
    def save_session(self, task, duration, completed=True):
        session = {
            "task": task,
            "duration_minutes": duration,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "completed": completed
        }
        self.sessions.append(session)
        with open(self.db_file, 'w') as file:
            json.dump(self.sessions, file, indent=4)
    
    def create_widgets(self):
        # Create custom fonts
        self.title_font = ("Segoe UI", 28, "bold")
        self.header_font = ("Segoe UI", 16)
        self.text_font = ("Segoe UI", 12)
        self.button_font = ("Segoe UI", 14)
        
        # Main frame with rounded corners and shadow effect
        self.main_frame = tk.Frame(self.root, padx=60, pady=60, bg=self.bg_color)
        self.main_frame.pack(expand=True)
        
        # App container with white background
        self.app_container = tk.Frame(self.main_frame, bg="white", padx=40, pady=40)
        self.app_container.pack(expand=True)
        
        # Title with accent color
        title_label = tk.Label(self.app_container, text="Forceful Pomodoro Timer", 
                              font=self.title_font, bg="white", fg=self.accent_color)
        title_label.pack(pady=20)
        
        # Separator line
        separator = tk.Frame(self.app_container, height=2, width=400, bg=self.accent_color)
        separator.pack(pady=15)
        
        # Task entry
        tk.Label(self.app_container, text="What are you working on?", 
                font=self.header_font, bg="white", fg=self.text_color).pack(pady=(20, 10))
        self.task_entry = tk.Entry(self.app_container, width=50, font=self.text_font,
                                  bd=2, relief=tk.GROOVE)
        self.task_entry.pack(pady=10)
        
        # Time entry
        tk.Label(self.app_container, text="How many minutes? (max 30)", 
                font=self.header_font, bg="white", fg=self.text_color).pack(pady=(20, 10))
        self.time_entry = tk.Entry(self.app_container, width=10, font=self.text_font,
                                  bd=2, relief=tk.GROOVE, justify='center')
        self.time_entry.pack(pady=10)
        
        # Start button with hover effect
        self.start_button = tk.Button(self.app_container, text="Start Work Session", 
                                     command=self.start_work, font=self.button_font,
                                     bg=self.success_color, fg="white", 
                                     activebackground="#27ae60", activeforeground="white",
                                     padx=20, pady=10, bd=0, cursor="hand2")
        self.start_button.pack(pady=30)
        
        # Status label
        self.status_label = tk.Label(self.app_container, text="", font=self.text_font,
                                    bg="white", fg=self.text_color, wraplength=400)
        self.status_label.pack(pady=10)
        
        # Tiny override button in upper right with subtle styling
        self.override_button = tk.Button(self.root, text="×", command=self.override_timer, 
                                       font=("Segoe UI", 10), width=2, height=1,
                                       bg="#dddddd", fg="#666666", bd=0,
                                       activebackground="#cccccc", cursor="hand2")
        self.override_button.place(x=self.root.winfo_screenwidth()-30, y=10)
        
        # Break frame (initially hidden)
        self.break_frame = tk.Frame(self.root, bg=self.bg_color)
        
        # Break container with white background
        self.break_container = tk.Frame(self.break_frame, bg="white", padx=50, pady=50)
        self.break_container.pack(expand=True)
        
        tk.Label(self.break_container, text="BREAK TIME", 
                font=("Segoe UI", 36, "bold"), fg=self.warning_color, bg="white").pack(pady=30)
        
        self.break_timer_label = tk.Label(self.break_container, text="", 
                                        font=("Segoe UI", 48), bg="white", fg=self.text_color)
        self.break_timer_label.pack(pady=20)
        
        tk.Label(self.break_container, text="Step away from the computer!", 
                font=("Segoe UI", 18), bg="white", fg=self.text_color).pack(pady=20)
        
        # Add a motivational message
        tk.Label(self.break_container, text="Take a deep breath and relax your mind.", 
                font=("Segoe UI", 14, "italic"), bg="white", fg=self.accent_color).pack(pady=10)
    
    def disable_close(self):
        # Prevent window from closing
        pass
    
    def start_work(self):
        # Validate inputs
        self.current_task = self.task_entry.get().strip()
        if not self.current_task:
            messagebox.showerror("Error", "Please enter what you are working on.")
            return
        
        try:
            self.work_minutes = int(self.time_entry.get())
            if self.work_minutes <= 0 or self.work_minutes > 30:
                messagebox.showerror("Error", "Please enter a time between 1 and 30 minutes.")
                return
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number of minutes.")
            return
        
        # Hide the main window to allow work
        self.session_start_time = datetime.now()
        self.root.withdraw()
        
        # Start the work timer thread
        self.timer_running = True
        threading.Thread(target=self.work_timer, daemon=True).start()
    
    def work_timer(self):
        work_seconds = self.work_minutes * 60
        time.sleep(work_seconds)
        
        if self.timer_running:  # Check if timer wasn't overridden
            self.accumulated_work += self.work_minutes
            self.save_session(self.current_task, self.work_minutes)
            
            # Show window again for break
            self.root.deiconify()
            self.root.lift()
            self.root.attributes('-topmost', True)
            self.root.focus_force()
            
            # Hide main frame and show break frame
            self.main_frame.pack_forget()
            self.break_frame.pack(expand=True, fill="both")
            
            # Check if we need a break (accumulated 30+ minutes)
            if self.accumulated_work >= 30:
                self.accumulated_work = 0  # Reset accumulated work
                self.break_timer()
            else:
                # Not enough accumulated work for a break
                self.status_label.config(text=f"Work logged! You've accumulated {self.accumulated_work} minutes.")
                self.break_frame.pack_forget()
                self.main_frame.pack(expand=True)
    
    def break_timer(self):
        # Force a 5-minute break
        break_seconds = 5 * 60
        
        def countdown():
            nonlocal break_seconds
            minutes, seconds = divmod(break_seconds, 60)
            self.break_timer_label.config(text=f"{minutes:02d}:{seconds:02d}")
            if break_seconds > 0 and self.timer_running:
                break_seconds -= 1
                self.root.after(1000, countdown)
            elif break_seconds <= 0:
                self.end_break()
        
        countdown()
    
    def end_break(self):
        self.break_frame.pack_forget()
        self.main_frame.pack(expand=True)
        self.status_label.config(text="Break completed! Start a new work session.")
        self.task_entry.delete(0, tk.END)
        self.time_entry.delete(0, tk.END)
    
    def override_timer(self):
        # Ask three times to confirm override
        confirm1 = messagebox.askyesno("Confirm Override", "Are you SURE you want to override the timer?")
        if confirm1:
            confirm2 = messagebox.askyesno("Confirm Override", "Are you REALLY sure?")
            if confirm2:
                confirm3 = messagebox.askyesno("Final Confirmation", "This will disrupt your productivity. Last chance to cancel.")
                if confirm3:
                    # Stop the timer and return to main screen
                    self.timer_running = False
                    
                    # If we were in a work session, save it as incomplete
                    if self.session_start_time:
                        elapsed_minutes = (datetime.now() - self.session_start_time).seconds // 60
                        if elapsed_minutes > 0:
                            self.save_session(self.current_task, elapsed_minutes, completed=False)
                    
                    # Reset the UI
                    self.break_frame.pack_forget()
                    self.main_frame.pack(expand=True)
                    self.status_label.config(text="Timer overridden. Start a new session when ready.")
                    self.root.deiconify()

def main():
    root = tk.Tk()
    app = ForcefulPomodoro(root)
    root.mainloop()

if __name__ == "__main__":
    main()