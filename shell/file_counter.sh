#!/bin/bash

# 统计文件夹下文件的个数
# 支持处理文件名中带空格的文件

# 推荐的方法，这个改动只在当前脚本生效，确保脚本正常执行，但是 local 只能用在函数中
function file_count {
    local IFS=$'\n'

    count=1
    # 使用文件后缀，只能处理固定类型的场景
    # for name in *doc
    # 只能找到带空格的文件的写法
    # for name in *\ *
    # 通用的写法，遇到文件名中有空格的场景会发生异常
    for name in $(ls .)
    do
        echo "File #$count = $name"
        count=$(( $count + 1))
    done

    echo "There are $(($count-1)) files under this folder"
}

count=1
# 使用文件后缀，只能处理固定类型的场景
# for name in *doc
# 只能找到带空格的文件的写法
# for name in *\ *
# 通用的写法，遇到文件名中有空格的场景会发生异常
for name in $(ls .)
do
    echo "File #$count = $name"
    count=$(( $count + 1))
done

echo "There are $(($count-1)) files under this folder"

file_count