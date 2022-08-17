#!/bin/bash
#Author: Mark Purcell (markpurcell@ie.ibm.com)
#Instantiate a local RabbitMQ container for testing
#Uses "local.json" for queue name settings etc.
#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# 
#
# Please note that the following code was developed for the project MUSKETEER
# in DRL funded by the European Union under the Horizon 2020 Program.
#

image=rabbitmq:3-management-alpine

#Stop existing container, if running
container=`docker ps -a | grep rabbit_mq | cut -d' ' -f1`
if [ -n "$container" ]; then
    docker rm -f $container
fi

echo "Reading local configuration..."
for var in $(cat local.json | jq -r "to_entries|map(\"\(.key)=\(.value|tostring)\")|.[]" ); do
    export $var
done

#Takes a few seconds until RabbitMQ is available
echo "Starting RabbitMQ container..."
docker run -d --hostname my-rabbit --name rabbit_mq -p $broker_port:$broker_port -p $broker_admin_port:$broker_admin_port $image

#Download the rabbitmq admin tool
wget -q 'https://raw.githubusercontent.com/rabbitmq/rabbitmq-management/v3.7.15/bin/rabbitmqadmin' -O ./rabbitmqadmin
chmod +x rabbitmqadmin
sed -i 's|#!/usr/bin/env python|#!/usr/bin/env python3|' rabbitmqadmin

echo "Waiting for RabbitMQ container to initialize..."
rc=1
creds="-u $broker_user -p $broker_password"

#Periodically poll with the admin tool, upon success, RabbitMQ is up
while [ "$rc" -ne 0 ];
do
    sleep 1
    ./rabbitmqadmin $creds list exchanges >>/dev/null 2>&1
    rc=$?
done

echo "RabbitMQ started. Configuring..."
./rabbitmqadmin $creds declare queue --vhost=$broker_vhost name=$broker_request_queue durable=true
./rabbitmqadmin $creds declare queue --vhost=$broker_vhost name=$broker_response_queue durable=true
#./rabbitmqadmin $creds -f raw_json list queues

rm ./rabbitmqadmin

