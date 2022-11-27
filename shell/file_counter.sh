#!/bin/bash

# 统计文件夹下文件的个数
# 支持处理文件名中带空格的文件

count=1
for name in $(ls .)
do
    echo "File #$count = $name"
    count=$(( $count + 1))
done

echo "There are $(($count-1)) files under this folder"