#!bin/bash

# 统计一个目录下指定类型或限制某种类型以外的文件的大小，包括子目录

help() {
  echo "Usage: sh count_file.sh -p folder_path [ -t jpg ] [ -x html ] "
  echo "       -p : 需要查找的文件路径"
  echo "       -t : 需要查找的文件类型"
  echo "       -x : 需要排除的文件类型"
}

if [[ $# == 0 ]] || [[ "$1" == "-h" ]]; then
  help
  exit 1
fi

echo "Count Specific File under folder"

FOLDER_PATH="/Users/shiqiang/Projects/edulinks-blog/public"

#list=`find $FOLDER_PATH | grep "jpg"`
list=`find $FOLDER_PATH -type f ! -name "*.html"`
for i in $list
  do
  echo $i
  fileSize=$(du -k ${i} | cut -f1)
  echo $fileSize
  ((totalSize=fileSize+totalSize))
done

echo "文件总大小为：$((totalSize/1024))M"
echo $FOLDER_PATH
