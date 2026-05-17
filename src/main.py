from PIL import Image

white_point = 0.5 * 255 # 0 (black) to 255 (white)
black_point = 0.99 * 255 # 99%

# open img
filename = 'image.png'
filepath = f"original_images/{filename}"

# processing
og_img = Image.open(filepath).convert('L') # L = Luminance | A = alpha
width,height=og_img.size
mode=og_img.mode

# Show information about the original image.
print(f"Original image: {filename}")
print(f"Size: {width} x {height} pixels")
print(f"Mode: {mode}")

#og_img.save('modified_images/greyscale.png')

og_pixel_map = og_img.load()# Load all pixels from the image.

new_image = Image.new(mode, (width, height))# Create a new image matching the original image's color mode, and size.
new_pixel_map = new_image.load() # Load all the pixels from this new image as well.

for x in range(width):
    for y in range(height):
        # Copy the original pixel to the new pixel map.
        og_pixel = og_pixel_map[x, y]
        
        if og_pixel < white_point:
            new_pixel = 0
            new_pixel_map[x, y] = new_pixel
        if og_pixel > white_point and og_pixel < black_point:
            new_pixel = 255
            new_pixel_map[x, y] = new_pixel

new_image.show()

new_filename = f"scanned_{filename}"
new_filepath = f"modified_images/{new_filename}"
new_image.save(new_filepath)
