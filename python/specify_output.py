#-*- coding:utf-8 -*-
# 输出固定长度的随机字符串或生成固定长度的文件
# 参考文档：
# 1.[Python生成指定大小文件](https://blog.csdn.net/surp2011/article/details/53228387?locationNum=5&fps=1)
import os
import random

# 生成固定大小的文件
# 大小默认为KB
def output_file(file_name = 'test.txt', file_size = '1024'):
    file_path = 
    pass

# 输出固定长度的文本
def output_content(len = 10):
    s = ''
    for i in range(len):
        s += s.join(output_character())
    
    return s

# 输出随机的字符串
def output_character():
    alphabet = 'abcdefghijklmnopqrstuvwxyz!@#$%^&*()ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    char = random.choice(alphabet)
    return char

# 测试字符输出
print(output_content(100))