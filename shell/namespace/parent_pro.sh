#!/bin/bash

# 每隔 5s 读取一个配置文件，当文件中内容为 1 的时候，拉起一个后台进程，验证 namespace 共享的问题
# 配置文件 config.txt

while :
do
  sleep 10
  startchild=$(cat config.txt)
  echo $startchild
  date

  if [ $startchild="1" ]
  then
    echo "Start child process..."
    nohup sh child_loop.sh > loop.log 2>&1 &
  fi

done