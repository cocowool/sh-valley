#!bin/bash

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
