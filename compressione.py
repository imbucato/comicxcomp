import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import rarfile
import zipfile
import tempfile
import shutil

def compress_cb(input_file, output_file, max_size, dpi, jpg_quality, color_bits):
    archive = None
    archive_type = None
    if input_file.lower().endswith('.cbr'):
        archive = rarfile.RarFile
        archive_type = 'cbr'
    elif input_file.lower().endswith('.cbz'):
        archive = zipfile.ZipFile
        archive_type = 'cbz'
    else:
        raise ValueError("Unsupported file type. Only CBR and CBZ files are supported.")
    
    with archive(input_file, 'r') as af:
        temp_dir = tempfile.mkdtemp()
        af.extractall(temp_dir)

        new_temp_dir = tempfile.mkdtemp()
        for root, _, files in os.walk(temp_dir):
            for file in files:
                if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    image_path = os.path.join(root, file)
                    output_image_path = os.path.join(new_temp_dir, file)

                    img = Image.open(image_path)

                    if max(img.size) > max_size:
                        scale_factor = max_size / max(img.size)
                        new_size = tuple(int(x * scale_factor) for x in img.size)
                        img = img.resize(new_size, Image.LANCZOS)

                    #img = img.quantize(colors=2**color_bits) if color_bits < 8 else img.convert('RGB')
                    #img = img.convert("1")

                    img.save(output_image_path, 'JPEG', dpi=(dpi, dpi), quality=jpg_quality)

        if archive_type == 'cbr':
            with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as out_zip:
                for root, _, files in os.walk(new_temp_dir):
                    for file in files:
                        out_zip.write(os.path.join(root, file), arcname=file)
        elif archive_type == 'cbz':
            with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as out_zip:
                for root, _, files in os.walk(new_temp_dir):
                    for file in files:
                        out_zip.write(os.path.join(root, file), arcname=file)

        shutil.rmtree(temp_dir)
        shutil.rmtree(new_temp_dir)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python compress_cbz.py <input_cbr> <output_cbz> [max_size] [dpi] [jpg_quality] [color bit]')
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    max_size = int(sys.argv[3]) if len(sys.argv) > 3 else 1024
    dpi = int(sys.argv[4]) if len(sys.argv) > 4 else 72
    jpg_quality = int(sys.argv[5]) if len(sys.argv) > 5 else 75
    color_bits = int(sys.argv[6]) if len(sys.argv) > 0 else 8

    compress_cb(input_file, output_file, max_size, dpi, jpg_quality, color_bits)