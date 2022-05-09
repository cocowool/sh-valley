import matplotlib as matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import getopt, sys

# 画单折线图
def single_line():
    pass

if __name__ == '__main__':
    opts, args = getopt.getopt(sys.argv[1:], "t:", ["type"])
    LINE_TYPE = ''

    for o, a in opts:
        if o in ("-t", "--type"):
            print("Usage: python3 plot_example.py -t 1")
        if o in ("-t", "--type"):
            LINE_TYPE = a

    if LINE_TYPE == '1':
        single_line()
    elif LINE_TYPE == '2':
        pass