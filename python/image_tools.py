import json, datetime, requests, os, time, random, getopt, sys
from PIL import Image
from PIL import ImageFile

# Compress Images Under folder in place
# 原地压缩替换某一文件夹下的图片文件
def compress_images(image_folder = ''):

    if not image_folder:
        print("No Image Folder Given, Exit!")
        return

    for parent, _, file_names in os.walk(image_folder):
        for file_name in file_names:
            if file_name.endswith('jpg'):
                file_name = os.path.join(parent, file_name)
                compress_single_image(file_name)


# Compress Single Image And Replace the original image
# 压缩单张图片并替换保存
# @TODO 小于一定大小的图片不处理；长度、宽度超过一定限度的，处理为适合 Web；默认为只压缩图片不缩放
def compress_single_image( image_path, in_replace = True, quality = 60 ):
    # Object Store Detail Inforamtion
    c_obj = {}

    original_size = os.path.getsize( image_path )
    c_obj['original_size'] = original_size

    ImageFile.LOAD_TRUNCATED_IMAGES = True

    im = Image.open(image_path)
    x, y = im.size
    c_obj['img_x'] = x
    c_obj['img_y'] = y

    print(image_path)
    print(c_obj)
    time.sleep(10)
    pass


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
