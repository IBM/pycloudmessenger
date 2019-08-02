# Retrieving Sensor Data from Castor using RabbitMQ (AMQP) - Sample Code

Sample [RabbitMQ](https://www.rabbitmq.com/) (AMQP) client that retrieves a sensor device list and a subset of sensor values from Castor.

## Install
The Python sample code in this repository depends on several external packages.

To install these packages on your local machine, execute the following command from within the `pycloudmessenger/rabbitmq` directory:

```
pip install -r requirements.txt
```

## Configure

RabbitMQ (AMQP) broker connection details, credentials, & broker certificate are provided by IBM, and are configured on 
your local machine using environmental variables.

## Run Castor Sample Application

When credentials are available from the IBM Research Castor team, the Castor sample application can be executed.

```
creds=YOUR_CREDENTIAL_FILE make castor
```

This retrieves a list of sensor IDs and a subset of sensor values from Castor and the sample code is available in `tests/castor`.


