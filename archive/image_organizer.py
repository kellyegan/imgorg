import glob
import os
import re

def get_images_in_directory(directory,  recursive=True):
    # Get all the files in the current directory
    path = os.path.join(os.getcwd(), directory)
    image_types = ['png', 'jpeg', 'jpg', 'tif', 'tiff', 'webp']
    images = []
    for type in image_types:
        file_path = os.path.join(path, f"*.{type}")
        images.extend(glob.glob(file_path, recursive=recursive))
    return images

def find_flickr_images(image_list):
    flickr_images = []
    flickr_filename_pattern = r'(\d+)_\w+_\w{1,2}' 

    for image in images:
        print(image)
        filename = os.path.basename(image)
        results = re.search(flickr_filename_pattern, os.path.splitext(filename)[0])
        
        if results: 
            flickr_images.append((image, results.group(1)))
    
    return flickr_images

if __name__ == '__main__':
    # Get all the files in the current directory
    path = '/Users/kpegan/Desktop/Level_0/**'
    
    images = get_images_in_directory(path)

    flickr_images = find_flickr_images(images)

    print(len(flickr_images))
    print(len(images))