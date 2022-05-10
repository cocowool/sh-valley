import matplotlib as matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import getopt, sys
import pandas as pd
import numpy as np

# 画单折线图
def single_line():
    df = pd.read_csv('data.csv')
    # 只取一个 cmdb_id 值
    df = df[ df['cmdb_id'].str.contains('node-1')]
    # 只取一个 kpi_name 值
    df = df[ df['kpi_name'].str.contains('system.load.5') ]
    df.sort_values('timestamp')
    
    # df['value'].plot(x=df['timestamp'])
    # plt.show()
 
    colors = ['red', 'blue', 'green', 'orange', 'black', 'purple', 'lime', 'magenta', 'cyan', 'maroon', 'teal', 'silver', 'gray', 'navy', 'pink', 'olive', 'rosybrown', 'brown', 'darkred', 'sienna', 'chocolate', 'seagreen', 'indigo', 'crimson', 'plum', 'hotpink', 'lightblue', 'darkcyan', 'gold', 'darkkhaki', 'wheat', 'tan', 'skyblue', 'slategrey', 'blueviolet', 'thistle', 'violet', 'orchid', 'steelblue', 'peru', 'lightgrey']

    fig = plt.figure(figsize=(14,8))
    plt.rcParams["figure.autolayout"] = True
    plt.rcParams['font.sans-serif'] = ['Songti SC']
    plt.rcParams['axes.unicode_minus'] = False

    plt.plot(df['timestamp'], df['value'], c = colors[ 3 ], label='node-1')
    plt.xlabel( 'Timestamp' )
    plt.ylabel( df['kpi_name'].iloc[1] )
    plt.legend( loc = 'best' )
    plt.show()

# 画多折线图
def multi_line():
    df = pd.read_csv('data.csv')
    
    # df['value'].plot(x=df['timestamp'])
    # plt.show()
 
    colors = ['red', 'blue', 'green', 'orange', 'black', 'purple', 'lime', 'magenta', 'cyan', 'maroon', 'teal', 'silver', 'gray', 'navy', 'pink', 'olive', 'rosybrown', 'brown', 'darkred', 'sienna', 'chocolate', 'seagreen', 'indigo', 'crimson', 'plum', 'hotpink', 'lightblue', 'darkcyan', 'gold', 'darkkhaki', 'wheat', 'tan', 'skyblue', 'slategrey', 'blueviolet', 'thistle', 'violet', 'orchid', 'steelblue', 'peru', 'lightgrey']

    fig = plt.figure(figsize=(14,8))
    plt.rcParams["figure.autolayout"] = True
    plt.rcParams['font.sans-serif'] = ['Songti SC']
    plt.rcParams['axes.unicode_minus'] = False

    # 只取一个 cmdb_id 值
    adf = df[ df['cmdb_id'].str.contains('node-1')]
    # 只取一个 kpi_name 值
    adf = adf[ df['kpi_name'].str.contains('system.load.5') ]
    adf.sort_values('timestamp')
    plt.plot(adf['timestamp'], adf['value'], c = 'teal', label='node-1')

    # 只取一个 cmdb_id 值
    bdf = df[ df['cmdb_id'].str.contains('node-2')]
    # 只取一个 kpi_name 值
    bdf = bdf[ df['kpi_name'].str.contains('system.load.5') ]
    bdf.sort_values('timestamp')
    plt.plot( bdf['timestamp'], bdf['value'], c = 'red', label='node-2')

    plt.xlabel( 'Timestamp' )
    plt.ylabel( df['kpi_name'].iloc[1] )
    plt.legend( loc = 'best' )
    plt.show()

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
        multi_line()