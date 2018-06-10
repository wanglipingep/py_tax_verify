#!/bin/bash

app_name="app_tax"
cd /pyapp/${app_name}
if [ "$?" != "0" ]; then
    echo "目录不存在!"
else
    pid=$(cat ./pid)
    if [ "$?" != "0" ]; then
        echo "pid不存在!"
    else
        kill -9 "$pid"
        if [ "$?" = "0" ]; then
           echo $(date "+%Y-%m-%d %H:%M:%S") "成功停止服务[pid=$pid] !"
        else
           echo $(date "+%Y-%m-%d %H:%M:%S") "进程不存在[pid=$pid] !"
        fi
    fi
fi