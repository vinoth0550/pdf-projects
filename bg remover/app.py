import os
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from rembg import remove

class BackgroundRemoverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Background Remover")
        self.root.geometry("800x600")
        
        # Create folders
        os.makedirs("upload_images", exist_ok=True)
        os.makedirs("bgremoved_images", exist_ok=True)
        
        # UI Elements
        self.create_widgets()
        
    def create_widgets(self):
        # Frame for images
        self.image_frame = tk.Frame(self.root)
        self.image_frame.pack(pady=10)
        
        # Labels for original and processed images
        self.original_label = tk.Label(self.image_frame, text="Original Image")
        self.original_label.grid(row=0, column=0, padx=20)
        
        self.processed_label = tk.Label(self.image_frame, text="Processed Image")
        self.processed_label.grid(row=0, column=1, padx=20)
        
        # Image display areas
        self.original_image_label = tk.Label(self.image_frame, bg="lightgray", width=40, height=20)
        self.original_image_label.grid(row=1, column=0, padx=20)
        
        self.processed_image_label = tk.Label(self.image_frame, bg="lightgray", width=40, height=20)
        self.processed_image_label.grid(row=1, column=1, padx=20)
        
        # Buttons
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(pady=20)
        
        self.upload_btn = tk.Button(self.button_frame, text="Upload Image", command=self.upload_image)
        self.upload_btn.grid(row=0, column=0, padx=10)
        
        self.process_btn = tk.Button(self.button_frame, text="Remove Background", command=self.process_image)
        self.process_btn.grid(row=0, column=1, padx=10)
        self.process_btn.config(state=tk.DISABLED)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = tk.Label(self.root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def upload_image(self):
        self.image_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff")])
        
        if self.image_path:
            # Save to upload folder
            filename = os.path.basename(self.image_path)
            self.upload_path = os.path.join("upload_images", filename)
            
            # Display image
            img = Image.open(self.image_path)
            img.save(self.upload_path)
            
            # Resize for display
            img = img.resize((300, 300), Image.LANCZOS)
            self.tk_img = ImageTk.PhotoImage(img)
            self.original_image_label.config(image=self.tk_img)
            
            # Get filename for output
            name, ext = os.path.splitext(filename)
            self.output_filename = f"{name}_nobg.png"
            self.output_path = os.path.join("bgremoved_images", self.output_filename)
            
            # Enable process button
            self.process_btn.config(state=tk.NORMAL)
            self.status_var.set(f"Image loaded: {filename}")
    
    def process_image(self):
        try:
            # Remove background
            input_img = Image.open(self.upload_path)
            output_img = remove(input_img)
            output_img.save(self.output_path)
            
            # Display processed image
            display_img = output_img.resize((300, 300), Image.LANCZOS)
            self.tk_processed = ImageTk.PhotoImage(display_img)
            self.processed_image_label.config(image=self.tk_processed)
            
            self.status_var.set(f"Background removed! Saved to {self.output_path}")
        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = BackgroundRemoverApp(root)
    root.mainloop()
