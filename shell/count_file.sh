#!bin/bash

echo "Count Specific File under folder"

FOLDER_PATH="/Users/shiqiang/Projects/edulinks-blog/public"

list=`find $FOLDER_PATH | grep "jpg"`
for i in $list
  do
  echo $i
done


echo $FOLDER_PATH
