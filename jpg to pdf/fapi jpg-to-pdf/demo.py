from PIL import Image
import os
import shutil

def jpg_to_pdf(input_path):
  
    input_folder = 'input'
    output_folder = 'output'
    os.makedirs(input_folder, exist_ok=True)
    os.makedirs(output_folder, exist_ok=True)


    filename = os.path.basename(input_path)
    name, ext = os.path.splitext(filename)

    # Ensure it's a JPG file
    
    if ext.lower() not in ['.jpg', '.jpeg']:
        print("Error: The selected file is not a JPG image.")
        return

    # Copy the input file into input folder
    input_dest = os.path.join(input_folder, filename)
    shutil.copy(input_path, input_dest)

    # Convert JPG to PDF
    image = Image.open(input_path)
    rgb_image = image.convert('RGB')  # Ensure it's in RGB mode

    output_path = os.path.join(output_folder, f"{name}.pdf")
    rgb_image.save(output_path, "PDF")

    print(f" Conversion complete!\nInput saved in: {input_dest}\nOutput saved in: {output_path}")

# Example usage:
# Change 'your_image.jpg' to your actual JPG file path
jpg_to_pdf("C:\\Users\\ADMIN\\Pictures\\5d7912ec-ee51-4f87-8c99-3a5ab5a2ba26.jpg")
