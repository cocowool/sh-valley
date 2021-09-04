#!/bin/bash

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

if [[ $# == 0 ]] || [[ "$1" == "-h" ]]; then
  help
  exit 0
fi

# INCLUDE_FILE_TYPE=""
# EXCLUDE_FILE_TYPE=""

# echo $*
while getopts "p:t:x:" opt
do
  case "$opt" in
    p) 
      FOLDER_PATH=$OPTARG ;;
    t) 
      # echo "Found t option"
      INCLUDE_FILE_TYPE=$OPTARG ;;
    x)
      # echo "Found x option"
      EXCLUDE_FILE_TYPE=$OPTARG ;;
    # getopts doesn't support long option, such as --option
    # debug)
    #   echo "Found debug option"
    #   echo $OPTARG ;;
    *) echo "$opt is invalid option" ;;
  esac
done

# FOLDER_PATH="/Users/shiqiang/Projects/edulinks-blog/public"
# 解决文件中含有空格的问题
IFS=$(echo "\n\b")

echo "查找的文件路径为：$FOLDER_PATH"

if [ -n $FOLDER_PATH ]; then
  #list=`find $FOLDER_PATH | grep "jpg"`
  if [ -n "$INCLUDE_FILE_TYPE" ]; then
    echo "查找的文件后缀为：$INCLUDE_FILE_TYPE."
    list=`find $FOLDER_PATH -type f -name "*.$INCLUDE_FILE_TYPE"`
  elif [ -n "$EXCLUDE_FILE_TYPE" ]; then
    echo "查找文件后缀不是：$EXCLUDE_FILE_TYPE 的文件"
    list=`find $FOLDER_PATH -type f ! -name "*.$EXCLUDE_FILE_TYPE"`
  fi
 
  count=0
  for i in $list
    do
    # echo $i
    fileSize=$(du -k "${i}" | cut -f1)
    ((count=count+1))
    # echo $fileSize
    ((totalSize=fileSize+totalSize))
  done

  echo "文件总大小为：$((totalSize/1024))M"
  echo "文件总数为：$count"
fi