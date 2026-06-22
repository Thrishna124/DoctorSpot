import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import shutil

# Set parameters
data_dir = '/Users/thrishna/Lungs_xray/data/The IQ-OTHNCCD lung cancer dataset'  # Path to your original dataset
output_dir = '/Users/thrishna/Lungs_xray/data/dataset'  # Path to where you want to create the new dataset
#augmented_dir = os.path.join(data_dir, 'benign_augmented')  # Path for augmented benign images
#malignant_augmented_dir = os.path.join(data_dir, 'malignant_augmented')  # Directory for augmented malignant images
normal_augmented_dir = os.path.join(data_dir, 'normal_augmented')  # Directory for augmented normal images

num_augmented = 50  # Number of augmented images to create

# Create a new directory for augmented images
#os.makedirs(augmented_dir, exist_ok=True)
#os.makedirs(malignant_augmented_dir, exist_ok=True)
os.makedirs(normal_augmented_dir, exist_ok=True)

# Set up the ImageDataGenerator for augmentation
datagen = ImageDataGenerator(
    rotation_range=20,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    fill_mode='nearest'
)

# Load benign images
#benign_path = os.path.join(data_dir, 'benign')
#benign_images = os.listdir(benign_path)
#malignant_path = os.path.join(data_dir, 'malignant')  # Path for original malignant images
#malignant_images = os.listdir(malignant_path)
normal_path = os.path.join(data_dir, 'normal')  # Path for original normal images
normal_images = os.listdir(normal_path)

# Oversample benign cases
#for img_name in benign_images:
#    img_path = os.path.join(benign_path, img_name)

for img_name in normal_images:
    img_path = os.path.join(normal_path, img_name)
    
    # Load the image
    img = tf.keras.preprocessing.image.load_img(img_path, target_size=(150, 150))
    img_array = tf.keras.preprocessing.image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)

    # Generate and save augmented images
    i = 0
    for batch in datagen.flow(img_array, batch_size=1, save_to_dir= normal_augmented_dir, # malignant_augmented_dir,#augmented_dir, 
                              save_prefix='aug', save_format='jpeg'):
        i += 1
        if i >= num_augmented:
            break  # Stop after generating the desired number of images

print("Augmented normal images created!")

# Create output directories for training, validation, and test splits
for folder in ['train', 'validation', 'test']:
    os.makedirs(os.path.join(output_dir, folder, 'normal'), exist_ok=True)
    os.makedirs(os.path.join(output_dir, folder, 'benign'), exist_ok=True)
    os.makedirs(os.path.join(output_dir, folder, 'malignant'), exist_ok=True)

# Define split ratios
split_ratios = {
    'train': 0.7,
    'validation': 0.2,
    'test': 0.1
}

# Function to split and move files
def split_and_move_files(category, category_path):
    files = os.listdir(category_path)
    np.random.shuffle(files)  # Shuffle the files for random splitting

    # Calculate split indices
    total_files = len(files)
    train_end = int(split_ratios['train'] * total_files)
    val_end = train_end + int(split_ratios['validation'] * total_files)

    # Split files
    train_files = files[:train_end]
    val_files = files[train_end:val_end]
    test_files = files[val_end:]

    # Move files to respective directories
    for file in train_files:
        shutil.copy(os.path.join(category_path, file), os.path.join(output_dir, 'train', category, file))
    for file in val_files:
        shutil.copy(os.path.join(category_path, file), os.path.join(output_dir, 'validation', category, file))
    for file in test_files:
        shutil.copy(os.path.join(category_path, file), os.path.join(output_dir, 'test', category, file))

# Split the benign, normal, and malignant images
for category in ['normal', 'benign', 'malignant']:
    category_path = os.path.join(data_dir, category)
    
    # If the category is 'benign', include both original and augmented images
    if category == 'normal': #'benign':
        category_path = normal_augmented_dir  # Use the augmented directory instead

    split_and_move_files(category, category_path)

print("Dataset split completed with normal!")
