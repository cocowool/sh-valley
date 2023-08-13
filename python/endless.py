# -*- coding: utf-8 -*-
import subprocess
import time
import sched

# 说明：放入后台执行，并在指定时间段，指定频率下，执行指定的 shell 命令
# Author：cocowool

def execute_shell_command(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()
    if process.returncode != 0:
        print("Error executing command: {command}")
        print("Error message: {error.decode('utf-8')}")
    else:
        print("Command executed successfully: {command}")
        print("Output: {output.decode('utf-8')}")

def run_scheduled_commands(commands, start_time, end_time, interval):
    scheduler = sched.scheduler(time.time, time.sleep)
    current_time = time.time()

    # 计算下一个开始时间
    next_start_time = start_time + (interval - (current_time - start_time) % interval)
    
    while current_time < end_time:
        for command in commands:
            scheduler.enterabs(next_start_time, 1, execute_shell_command, argument=(command,))
        scheduler.run()
        
        current_time = time.time()
        next_start_time += interval

# 设置执行的命令列表
commands = ['echo `date` >> a.txt', 'ps -ef >> a.txt']

# 设置开始时间、结束时间和执行频率
start_time = time.mktime(time.strptime('2023-08-13 15:25:00', '%Y-%m-%d %H:%M:%S'))
end_time = time.mktime(time.strptime('2023-08-13 15:30:00', '%Y-%m-%d %H:%M:%S'))
interval = 60  # 60秒间隔

# 执行计划任务
run_scheduled_commands(commands, start_time, end_time, interval)