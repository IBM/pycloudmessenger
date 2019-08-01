# Retrieving Sensor Data from Castor using RabbitMQ (AMQP) - Sample Code

Sample [RabbitMQ](https://www.rabbitmq.com/) (AMQP) client that retrieves a sensor device list and a subset of sensor values from Castor.

## Install
The Python sample code in this repository depends on several external packages.

To install these packages on your local machine, execute the following command from within the `cloud-messaging/rabbitmq` directory:

```
pip install -r requirements.txt
```

## Configure

RabbitMQ (AMQP) broker connection details, credentials, & broker certificate are provided by IBM, and are configured on 
your local machine using environmental variables.

Store the broker certificate in the `cloud-messaging/rabbitmq` directory.

On a Linux or Mac OS X command line `export` the following environmental variables:

```
export RABBIT_BROKER=CASTOR_HOST
export RABBIT_PORT=CASTOR_PORT
export RABBIT_VHOST=CASTOR_VIRTUAL_HOST
export RABBIT_USER=YOUR_CASTOR_USERNAME
export RABBIT_PWD=YOUR_CASTOR_PASSWORD
export CERT=PATH_TO_BROKER_CERTIFICATE
export PUBLISH_QUEUE=CASTOR/v1/Request
```

On a Windows command line `set` the following environmental variables:

```
set RABBIT_BROKER=CASTOR_HOST
set RABBIT_PORT=CASTOR_PORT
set RABBIT_VHOST=CASTOR_VIRTUAL_HOST
set RABBIT_USER=YOUR_CASTOR_USERNAME
set RABBIT_PWD=YOUR_CASTOR_PASSWORD
set CERT=PATH_TO_BROKER_CERTIFICATE
set PUBLISH_QUEUE=CASTOR/v1/Request
```

## Run

To retrieve a list of sensor IDs and a subset of sensor values from Castor, execute the following command from within the `cloud-messaging/rabbitmq` directory:

```
python -m castor.sample_client
``` 

