#!/bin/sh

# 目的是将一个文件夹中的小文件，每100个放入一个单独的文件夹，避免单个文件夹中文件太多

C=0
F=1
# 因为文件名中有空格，但都是JPG文件，采用这种方式，复杂情况需要使用IFS
for i in *JPG
do
        echo $i
        C=$(($C+1))
        FOLDER="Folder_$F"
        if [[ ! -d $FOLDER ]]; then
                mkdir $FOLDER
        fi
        # 将文件移动到文件夹中
        mv "$i" $FOLDER

        if [[ $C -eq 250 ]]; then
                F=$(($F+1))

                # 如果不存在就创建文件夹
                if [[ ! -d $FOLDER ]]; then
                        mkdir $FOLDER
                fi

                C=0
        fi

        echo $C
        echo $F
        echo $FOLDER
done
