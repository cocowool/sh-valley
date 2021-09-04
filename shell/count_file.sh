#!bin/bash

# 统计一个目录下指定类型或限制某种类型以外的文件的大小，包括子目录

help() {
  echo "Description: 用于查找某个目录下特定类型文件的数量和总的大小，或者查找某种类型以外的文件数量和总的大小"
  echo "Author: cocowool <cocowool@qq.com>, Blog: http://www.edulinks.cn"
  echo "Usage: sh count_file.sh -p folder_path [ -t jpg ] [ -x html ] "
  echo "       -p : 需要查找的文件路径"
  echo "       -t : 需要查找的文件类型"
  echo "       -x : 需要排除的文件类型"
  exit 0
}

# use set command to parse option and parameter
set -- $(getopt p:t:x: "$@")

if [[ $# == 0 ]] || [[ "$1" == "-h" ]]; then
  help
  exit 0
fi

while [ -n "$1" ]
do
  case $1 in
    -p) echo "Found -p option" ;;
    -t) echo "Found -t option" ;;
    -x) echo "Found -x option" ;;
    *) echo "$1 is invalid option" ;;
  esac
  shift
done

count=1
for param in $@
do
  echo "Parameter #$count: $param"
  count=$[$count + 1]
done

exit 0

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
