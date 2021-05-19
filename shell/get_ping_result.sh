#!/bin/sh
 
# Find the fastest apple store hosts
 
printf "%-20s\t%-16s\t%-10s\n" "Domain" "Ip" "Avg Ping"
#printf "Domain\tIp\tAvg Ping\n"
for ((I=1 ;I < 2001; I++ ));do
    HOST="a$I.phobos.apple.com"
    TEMP=$(ping -c 4 $HOST)
    IP=$(echo $TEMP | grep -oE '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}' | uniq)
    TIME=$(echo $TEMP | grep -oE '\/([0-9]*\.[0-9]*)\/' | grep -oE '[0-9]*\.[0-9]*')
    printf "%-20s\t%-16s\t%-10s\n" $HOST $IP $TIME
done
