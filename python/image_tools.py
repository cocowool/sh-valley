import json, datetime, requests, os, time, random, getopt, sys
from PIL import Image
from PIL import ImageFile

# Compress Images Under folder in place
# 原地压缩替换某一文件夹下的图片文件
def compress_images(image_folder = ''):

    if not image_folder:
        print("No Image Folder Given, Exit!")
        return

    total_size = 0
    compress_size = 0
    for parent, _, file_names in os.walk(image_folder):
        for file_name in file_names:
            if file_name.endswith(('jpg','bmp','png')):
                file_name = os.path.join(parent, file_name)
                image_info = compress_single_image(file_name)
                if image_info:
                    total_size += image_info['original_size']
                    compress_size += image_info['compress_size']

    print('Total original size : ' + str(total_size))
    print('Total compress size : ' + str(compress_size))


# Compress Single Image And Replace the original image
# 压缩单张图片并替换保存
# @TODO 小于一定大小的图片不处理；长度、宽度超过一定限度的，处理为适合 Web；默认为只压缩图片不缩放
def compress_single_image( image_path, in_replace = True, quality = 50, size_scale = 0.8 ):
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

        if small_x > 0:
            im = im.resize( (small_x, small_y), Image.ANTIALIAS)

        im.save(image_path,quality = quality)

        c_obj['compress_size'] = os.path.getsize(image_path)

        print(image_path)
        print(c_obj)
        # time.sleep(1)

        return c_obj
    except:
        print("Image Read Error : " + image_path)
        return False


if __name__ == '__main__':
    opts, args = getopt.getopt(sys.argv[1:], "m:h:f:", ["mode", "help", "folder"])
    IMAGE_FOLDER = ''

    for user_option, user_parameter in opts:
        if user_option in ("-h", "--help"):
            print("Usage: python3 image_tools.py -m method -f image_folder_path")
        if user_option in ("-m", "--method"):
            PROCESS_METHOD = user_parameter
        if user_option in ("-f", "--folder"):
            IMAGE_FOLDER = user_parameter

    if PROCESS_METHOD == 'compress':
        compress_images(IMAGE_FOLDER)
