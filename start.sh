#!/bin/bash

app_name="app_tax"
cd /pyapp/${app_name}
BUILD_ID=DONTKILLME nohup bin/${app_name} &
echo "$!" > pid
echo "start server[pid=$!]"