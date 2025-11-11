from PIL import Image
import os

def convert_to_bw(input_path, output_folder="converted"):
    try:
    
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
    
        img = Image.open(input_path)
        
        # Convert to black and white (grayscale)
        bw_img = img.convert('L')
        
     
        filename = os.path.basename(input_path)
        output_path = os.path.join(output_folder, filename)
        
     
        bw_img.save(output_path)
        
        print(f"Converted image saved to: {output_path}")
        return True
        
    except Exception as e:
        print(f"Error converting image: {e}")
        return False

image_path = "C:\\Users\\ADMIN\\Pictures\\5d7912ec-ee51-4f87-8c99-3a5ab5a2ba26.jpg"
convert_to_bw(image_path)
