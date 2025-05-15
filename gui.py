import serial
import mysql.connector
import os
from tkinter import Tk, Label, Frame, messagebox, Text, Scrollbar, RIGHT, Y, LEFT, BOTH
from tkinter.ttk import Style, Button
from PIL import Image, ImageTk  # For image display

class ThemeManager:
    def _init_(self):
        self.is_dark = False
        self.themes = {
            'light': {
                'bg': "#f3f6fb",
                'fg': "#39406f",
                'header_bg': "#6a80c7",
                'header_fg': "#f3f6fb",
                'content_bg': "#e4e9f5",
                'content_border': "#cfd9ee",
                'text_primary': "#39406f",
                'text_secondary': "#4d59ac"
            },
            'dark': {
                'bg': "#421408",  # Darker background for pumpkin
                'fg': "#fff7ed",  # Light text color
                'header_bg': "#f77419",  # Bright pumpkin orange header
                'header_fg': "#fff7ed",  # Light header text
                'content_bg': "#993513",  # Dark pumpkin content background
                'content_border': "#f9923e",  # Border color for content
                'text_primary': "#fff7ed",  # Light primary text color
                'text_secondary': "#fdd7ab"  # Secondary text color
            }
        }

    def get_theme(self):
        return self.themes['dark'] if self.is_dark else self.themes['light']

    def toggle_theme(self):
        self.is_dark = not self.is_dark
        return self.get_theme()

# Database connection setup
def fetch_sculpture_data(rfid_uid):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="KhushiBC@2005",
            database="rfid_sculpture"
        )
        cursor = conn.cursor()
        query = "SELECT sculpture_name, sculpture_id, description, image_path FROM sculptures WHERE rfid_uid = %s"
        cursor.execute(query, (rfid_uid,))
        result = cursor.fetchone()
        conn.close()
        return result
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", f"Error connecting to the database: {e}")
        return None

# Serial connection setup
try:
    ser = serial.Serial("COM3", 9600, timeout=1)
except Exception as e:
    messagebox.showerror("Serial Error", f"Error connecting to the serial port: {e}")
    exit()

# GUI setup
root = Tk()
root.title("Sculpture Information System")
root.geometry("800x800")  # Initial window size

theme_manager = ThemeManager()
current_theme = theme_manager.get_theme()

# Configure style
style = Style()
style.configure("ThemeToggle.TButton", font=("Helvetica", 10))

# Create main container
main_frame = Frame(root)
main_frame.pack(fill="both", expand=True)

# Header with theme toggle
header_frame = Frame(main_frame)
header_frame.pack(fill="x", pady=10)

header_label = Label(header_frame, text="RFID Sculpture Scanner", 
                    font=("Helvetica", 24, "bold"))
header_label.pack(side="top", pady=10)

theme_button = Button(header_frame, text="Toggle Theme", style="ThemeToggle.TButton")
theme_button.pack(side="right", pady=10)

# Content frame
content_frame = Frame(main_frame)
content_frame.pack(fill="both", expand=True, padx=40, pady=20)

# Create info containers with smaller sizes
def create_info_section(parent, title, has_scroll=False):
    frame = Frame(parent, pady=5, padx=20)  # Reduced padding for smaller boxes
    frame.pack(fill="x", pady=5)  # Reduced vertical padding
    
    label = Label(frame, text=title, font=("Helvetica", 10, "bold"))  # Smaller font size
    label.pack(anchor="w")
    
    if has_scroll:
        text_frame = Frame(frame)
        text_frame.pack(fill="both", expand=True)
        scrollbar = Scrollbar(text_frame, orient="vertical")
        text_widget = Text(
            text_frame, height=3, wrap="word", yscrollcommand=scrollbar.set,  # Reduced height
            font=("Helvetica", 12), borderwidth=0
        )
        scrollbar.config(command=text_widget.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        text_widget.pack(side=LEFT, fill=BOTH, expand=True)
        return frame, label, text_widget
    else:
        value_label = Label(frame, text="", font=("Helvetica", 12), wraplength=700)
        value_label.pack(anchor="w", pady=(5, 0))
        return frame, label, value_label

# Create all info sections with smaller size
rfid_frame, rfid_title, rfid_label = create_info_section(content_frame, "RFID UID")
name_frame, name_title, sculpture_name_label = create_info_section(content_frame, "Sculpture Name")
id_frame, id_title, sculpture_id_label = create_info_section(content_frame, "Sculpture ID")
desc_frame, desc_title, description_text = create_info_section(content_frame, "Description", has_scroll=True)

# Image Frame with larger size
image_frame = Frame(content_frame)
image_frame.pack(pady=20, anchor="center", fill="both", expand=True)  # Fill the remaining space

image_label = Label(image_frame, text="Sculpture Image", font=("Helvetica", 12, "bold"))
image_label.pack()

image_canvas = Label(image_frame)  # For displaying the image
image_canvas.pack(pady=10, fill="both", expand=True)

# Status bar
status_frame = Frame(root)
status_frame.pack(fill="x", side="bottom")
status_label = Label(status_frame, text="Ready to scan...", pady=5)
status_label.pack()

def apply_theme(theme):
    # Update main window
    root.configure(bg=theme['bg'])
    main_frame.configure(bg=theme['bg'])
    content_frame.configure(bg=theme['bg'])
    
    # Update header
    header_frame.configure(bg=theme['header_bg'])
    header_label.configure(bg=theme['header_bg'], fg=theme['header_fg'])
    
    # Update info sections
    for frame, title, value in [
        (rfid_frame, rfid_title, rfid_label),
        (name_frame, name_title, sculpture_name_label),
        (id_frame, id_title, sculpture_id_label)
    ]:
        frame.configure(bg=theme['content_bg'], 
                       highlightbackground=theme['content_border'],
                       highlightthickness=1)
        title.configure(bg=theme['content_bg'], fg=theme['text_primary'])
        value.configure(bg=theme['content_bg'], fg=theme['text_secondary'])
    
    # Update description section
    desc_frame.configure(bg=theme['content_bg'])
    desc_title.configure(bg=theme['content_bg'], fg=theme['text_primary'])
    description_text.configure(bg=theme['content_bg'], fg=theme['text_secondary'])

    # Update image section
    image_frame.configure(bg=theme['content_bg'])
    image_label.configure(bg=theme['content_bg'], fg=theme['text_primary'])

    # Update status bar
    status_frame.configure(bg=theme['header_bg'])
    status_label.configure(bg=theme['header_bg'], fg=theme['header_fg'])

def toggle_theme():
    new_theme = theme_manager.toggle_theme()
    apply_theme(new_theme)

theme_button.configure(command=toggle_theme)

# Initial theme application
apply_theme(current_theme)

def update_display():
    try:
        if ser.in_waiting > 0:
            rfid_uid = ser.readline().decode("utf-8").strip()
            rfid_label.configure(text=rfid_uid)
            status_label.configure(text="Scanning...")

            # Fetch data from database
            result = fetch_sculpture_data(rfid_uid)
            if result:
                sculpture_name, sculpture_id, description, image_path = result
                sculpture_name_label.configure(text=sculpture_name)
                sculpture_id_label.configure(text=sculpture_id)
                description_text.delete("1.0", "end")
                description_text.insert("1.0", description)
                
                # Show image only if description is available
                if description != "Not Found":
                    try:
                        # Ensure image_path is a valid path
                        if image_path and os.path.exists(image_path):  # Check if file exists
                            image = Image.open(image_path)
                            image.thumbnail((root.winfo_width(), root.winfo_height()))  # Scale image proportionally
                            photo = ImageTk.PhotoImage(image)
                            image_canvas.configure(image=photo)
                            image_canvas.image = photo  # Keep a reference to avoid garbage collection
                        else:
                            image_canvas.configure(image='', text="Image not available")
                            print("Image file does not exist or path is incorrect")
                    except Exception as e:
                        image_canvas.configure(image='', text="Error loading image")
                        print(f"Error loading image: {e}")
                else:
                    image_canvas.configure(image='', text="Image not available")
                status_label.configure(text="Sculpture information found")
            else:
                sculpture_name_label.configure(text="Not Found")
                sculpture_id_label.configure(text="Not Found")
                description_text.delete("1.0", "end")
                description_text.insert("1.0", "Not Found")
                image_canvas.configure(image='', text="Image not available")
                status_label.configure(text="No sculpture information found")
    except Exception as e:
        messagebox.showerror("Error", f"Error reading RFID: {e}")
        status_label.configure(text="Error reading RFID")
    
    root.after(1000, update_display)

# Start the display update loop
update_display()
root.mainloop()
