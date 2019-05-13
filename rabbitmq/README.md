# Retrieving Sensor Data from Castor using RabbitMQ (AMQP) - Sample Code

Sample [RabbitMQ](https://www.rabbitmq.com/) (AMQP) client that retrieves a sensor device list and a subset of sensor values from Castor.

#### Install

##### git

[git](https://git-scm.com/) is a free open source distributed version control system used to manage and maintain the 
`castor-messaging` sample source code.

Follow [these instructions](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) to install 
[git](https://git-scm.com/) on your local machine.

After [git](https://git-scm.com/) is installed, run the following command:

```
git clone https://github.com/IBM/castor-messaging.git
```

which creates a copy of the sample source code in this repository in a directory named `castor-messaging` on your local machine.

##### Python

This sample code uses [Python](https://www.python.org/). A minimum version of `3.5` is required; version `3.7` is preferred.

###### Linux
Python is typically pre-installed on Linux. Execute the following command to determine what version is installed:

```
python -V 
```

If the version of Python installed on your Linux machine is less than `3.5`, update Python using your Linux distribution's package manager. 

###### Windows & Mac OS X

Follow [these instructions](https://www.python.org/downloads/) to download and install Python on Windows and Mac OS X. 



##### Python Packages
The Python sample code in this repository depends several external packages.

To install these packages on your local machine, execute the following command from within the `castor-messaging/rabbitmq` directory:

```
pip install -r requirements.txt
```

#### Configure

RabbitMQ (AMQP) broker connection details, credentials, & certificate are provided by IBM, and are configured on your local machine using environmental variables.

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

To retrieve a list of sensor IDs and a subset of sensor values from Castor, execute the following command from within the `castor-messaging/rabbitmq` directory:

```
python -m castor.sample_client
``` 

