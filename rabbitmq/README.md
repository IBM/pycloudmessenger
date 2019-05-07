# Sample code for RabbitMQ messaging

The sample code is written in Python, version 3.6 was used for testing.
Assuming Python and pip are already installed, run:

``` 
pip3 install -r requirements.txt
``` 


## Service Requests

A request to the Castor service platform takes the following form:

``` 
{
    "serviceRequest": {
        "requestor": {
            "replyTo": "the reply topic",
            "clientID": "your client id", 
            "correlationID": a number to help you identify the request
        },
        "service": {
            "args": {
               "device_id": the meter, 
               "from": "date range begin",
               "to": "date range end" 
            },
            "name": "MeterDataRetrievalService"
        }
    }
}

``` 

## Operation

The sample assumes a TLS enabled Castor service with a certificate file `cert.pem` available. To run the client sample code:

``` 
export RABBIT_BROKER=CASTOR_HOST
export RABBIT_PORT=CASTOR_PORT
export RABBIT_VHOST=CASTOR_VIRTUAL_HOST #if applicable
export RABBIT_USER=YOUR_CASTOR_USERNAME
export RABBIT_PWD=YOUR_CASTOR_PASSWORD
export PUBLISH_QUEUE=YOUR_QUEUE_NAME

python3 -m castor.sample_client
``` 

The credentials for the Castor service must be available prior to launch.

