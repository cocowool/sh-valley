#!/bin/bash

# 子进程，定时输出当前时间

echo "PID of this script: $$"
echo "PPID of this script: $PPID"
echo "UID of this script: $UID"

while :
do
  sleep 1
  date
done