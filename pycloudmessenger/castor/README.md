# Retrieving Sensor Data from Castor using RabbitMQ (AMQP) - Sample Code

Sample [RabbitMQ](https://www.rabbitmq.com/) (AMQP) client that retrieves a sensor device list and a subset of sensor values from Castor.

## Install
The Python sample code in this repository depends on several external packages.

To install these packages on your local machine, execute the following command from within the `pycloudmessenger/castor` directory:

```
pip install -r ../requirements.txt
```

## Configure

RabbitMQ (AMQP) broker connection details, credentials, & broker certificate are provided by IBM.

## Run Castor Sample Application

Using the credentials provided by IBM Research, the Castor sample code can be invoked from within the `pycloudmessenger` root directory:

```
creds=<CREDENTIAL_FILE> make castor
```

The sample code (`tests/castor`) retrieves a list of sensor IDs and a subset of sensor values from the IBM Castor platform.


