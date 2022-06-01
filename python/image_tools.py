import json, datetime, requests, os, time, random, getopt, sys

def compress_images():
    pass


if __name__ == '__main__':
    opts, args = getopt.getopt(sys.argv[1:], "m:h:f:", ["mode", "help", "folder"])

    for user_option, user_parameter in opts:
        if user_option in ("-h", "--help"):
            print("Usage: python3 image_tools.py -m method -f image_folder_path")
        if user_option in ("-m", "--method"):
            PROCESS_METHOD = user_parameter
        if user_option in ("-f", "--folder"):
            IMAGE_FOLDER = user_parameter

    if PROCESS_METHOD == 'compress':
        compress_images(PLOT_FOLDER)
