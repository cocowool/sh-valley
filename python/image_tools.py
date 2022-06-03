import json, datetime, requests, os, time, random, getopt, sys
from PIL import Image
from PIL import ImageFile
import libimagequant as liq
# from pillow import Image

# Compress Images Under folder in place
# 原地压缩替换某一文件夹下的图片文件
def compress_images(image_input_folder = '', image_output_folder = False):

    if not image_input_folder:
        print("No Image Folder Given, Exit!")
        return

    # Check Folder
    if not os.path.exists(image_input_folder):
        print("Input Folder doesn't exists! ")

    # Check Folder
    if not os.path.exists(image_output_folder):
        print("Output Folder doesn't exists! ")

    total_size = 0
    compress_size = 0
    for parent, _, file_names in os.walk(image_input_folder):
        for file_name in file_names:
            output_file_name = image_output_folder + file_name
            file_name = os.path.join(parent, file_name)

            if file_name.endswith(('jpg','bmp')):
                image_info = compress_single_image(file_name, output_file_name)
                if image_info:
                    total_size += image_info['original_size']
                    compress_size += image_info['compress_size']
            elif file_name.endswith(('png')):
                image_info = compress_png_image( file_name, output_file_name)
                if image_info:
                    total_size += image_info['original_size']
                    compress_size += image_info['compress_size']

    print('Total original size : ' + str(total_size))
    print('Total compress size : ' + str(compress_size))


def to_liq( image, attr):
    if image.mode != 'RGBA':
        image = image.convert('RGBA')

        return attr.create_rgba(image.tobytes(), image.width, image.height, image.info.get('gamma', 0))

def from_liq(result, image):
    out_img = PIL.Image.frombytes('P', (image.width, image.height), result.remap_image(image))

    palette_data = []
    for color in result.get_palette():
        palette_data.extend(color[:3])
    out_img.putpalette(palette_data)

    return out_img

# Compress Png Image use libimagequant
def compress_png_image( image_path, output_file_name = False, quality = 80):
    # Object Store Detail Inforamtion
    c_obj = {}

    try:
        im = Image.open(image_path)
        x, y = im.size
        c_obj['img_x'] = x
        c_obj['img_y'] = y

        attr = liq.Attr()
        liq_image = to_liq(im, attr)
        result = liq_image.quantize(attr)
        pil_image = from_liq(result, liq_image)
        pil_image.save(output_file_name, optimize = True, quality = quality)
        c_obj['compress_size'] = os.path.getsize(output_file_name)


        print(image_path)
        print(c_obj)
        # time.sleep(1)

        return c_obj
    except:
        print("Compress Png Image Error : " + image_path)
        return False

# Compress Single Image And Replace the original image
# 压缩单张图片并替换保存
# @TODO 小于一定大小的图片不处理；长度、宽度超过一定限度的，处理为适合 Web；默认为只压缩图片不缩放
def compress_single_image( image_path, output_file_name = False, in_replace = True, quality = 80, size_scale = 0.8 ):
    image_x_threshold = 1024
    image_size_threshold = 10240

    # Object Store Detail Inforamtion
    c_obj = {}
    small_x = 0

    original_size = os.path.getsize( image_path )
    c_obj['original_size'] = original_size

    ImageFile.LOAD_TRUNCATED_IMAGES = True

    try:
        im = Image.open(image_path)
        x, y = im.size
        c_obj['img_x'] = x
        c_obj['img_y'] = y

        # If image size is small, direct return
        if original_size < image_size_threshold:
            return False

        # If image is too wide, scale down
        while x > image_x_threshold:
            small_x = int(x * size_scale)
            small_y = int(y * small_x / x)
            c_obj['s_x'] = small_x
            c_obj['s_y'] = small_y

            x = small_x
            y = small_y

        if small_x > 0:
            # im = im.resize( (small_x, small_y), Image.CUBIC)
            im = im.resize( (small_x, small_y), Image.ANTIALIAS)

        if output_file_name:
            # print( "input file : " + image_path)
            # print( "output file : " + output_file_name )
            # time.sleep(10)
            im.save(output_file_name, optimize = True, quality = quality)
            c_obj['compress_size'] = os.path.getsize(output_file_name)
        else:
            im.save(image_path, optimize = True, quality = quality)
            c_obj['compress_size'] = os.path.getsize(image_path)
            
        print(image_path)
        print(c_obj)
        # time.sleep(1)

        return c_obj
    except:
        print("Image Read Error : " + image_path)
        return False


if __name__ == '__main__':
    opts, args = getopt.getopt(sys.argv[1:], "m:h:f:o:", ["mode", "help", "folder", "output"])
    IMAGE_FOLDER = ''
    OUTPUT_FOLDER = False

    for user_option, user_parameter in opts:
        if user_option in ("-h", "--help"):
            print("Usage: python3 image_tools.py -m method -f image_folder_path [-o output_folder]")
        if user_option in ("-m", "--method"):
            PROCESS_METHOD = user_parameter
        if user_option in ("-f", "--folder"):
            IMAGE_FOLDER = user_parameter
        if user_option in ("-o", "--output"):
            OUTPUT_FOLDER = user_parameter

    if PROCESS_METHOD == 'compress':
        compress_images(IMAGE_FOLDER, OUTPUT_FOLDER)
