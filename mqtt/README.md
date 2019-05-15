## Pushing Sensor Data to Castor using MQTT - Sample Code

Sample [MQTT](http://mqtt.org/) client that parses sensor device ID, timestamp, and value readings from a `./sample.csv` file 
and publishes to a remote [MQTT](http://mqtt.org/) broker specified by a [JSON](https://www.json.org/) configuration file.

## Install

#### git

[git](https://git-scm.com/) is a free open source distributed version control system used to manage and maintain the 
`castor-messaging` sample source code.

Follow [these instructions](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) to install 
[git](https://git-scm.com/) on your local machine.

After [git](https://git-scm.com/) is installed, run the following command:

```
git clone https://github.com/IBM/castor-messaging.git
```

which creates a copy of the sample source code in this repository in a directory named `castor-messaging` on your local machine.

#### Python

This sample code uses [Python](https://www.python.org/). A minimum version of `3.5` is required; version `3.7` is preferred.

###### Linux
Python is typically pre-installed on Linux. Execute the following command to determine what version is installed:

```
python -V 
```

If the version of Python installed on your Linux machine is less than `3.5`, update Python using your Linux distribution's package manager. 

###### Windows & Mac OS X

Follow [these instructions](https://www.python.org/downloads/) to download and install Python on Windows and Mac OS X. 



#### Python Packages
The Python sample code in this repository depends on several external packages.

To install these packages on your local machine, execute the following command from within the `castor-messaging/mqtt` directory:

```
pip install -r requirements.txt
```

## Configure

Additional configuration will be required to parse sensor device ID, timestamp, and value readings from CSV files that 
differ in format from the `sample.csv` file provided in this repository.

These configuration changes relate to:
- timestamp format,
- timestamp time zone, and
- CSV file column ordering.

#### Coordinated Universal Time 

Castor uses [Coordinated Universal Time (UTC)](https://en.wikipedia.org/wiki/Coordinated_Universal_Time) exclusively for timestamp values - all timestamps submitted to Castor via MQTT must conform to UTC.

The sample code can be configured with the format & local time zone of the timestamps in the CSV being parsed, allowing them to 
be converted to UTC prior to submission to Castor.

#### Timestamp Format

The sample code provided is [currently configured](https://github.com/IBM/castor-messaging/blob/dff155f2b6b2202a1bf9e48a0484502ce3e17dfd/mqtt/mqtt_client.py#L65) 
to parse timestamps in `sample.csv` of the following format: `2018-12-31 22:39:50`.

To change this timestamp format, edit [line 65 of `mqtt_client.py`](https://github.com/IBM/castor-messaging/blob/dff155f2b6b2202a1bf9e48a0484502ce3e17dfd/mqtt/mqtt_client.py#L65) 
to match your CSV file's timestamp format. [See here for an in-depth description of Python's `datetime` parsing syntax](https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior).

#### Timestamp Time Zone

The sample code provided is [currently configured](https://github.com/IBM/castor-messaging/blob/dff155f2b6b2202a1bf9e48a0484502ce3e17dfd/mqtt/mqtt_client.py#L70) to treat timestamps in `sample.csv` as local times in the following time zone: `Europe/Zurich`.

To change the local time zone, edit [line 70 of `mqtt_client.py`](https://github.com/IBM/castor-messaging/blob/dff155f2b6b2202a1bf9e48a0484502ce3e17dfd/mqtt/mqtt_client.py#L70) 
to match your CSV file's timestamp time zone. [See here for a list of time zone names](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones). For example, if the timestamps in the CSV represent local times in Norway, use: `Europe/Oslo`, or for Nova Scotia, use: `America/Halifax`.

#### CSV File Column Ordering

The sample code provided is currently configured to parse the three-column `sample.csv` file where:
 - the first column contains the sensor device ID,
 - the second column contains the local timestamp, and
 - the third column contains the value.
 
 If your CSV file's column ordering differs, or is interleaved with other unrelated columns, edit 
 [lines 93 & 97 of `mqtt_client.py`](https://github.com/IBM/castor-messaging/blob/dff155f2b6b2202a1bf9e48a0484502ce3e17dfd/mqtt/mqtt_client.py#L93-L97)
 to configure the appropriate CSV file columns and order.
 
**NB:** Python uses zero-based indexing - the first column is referenced using `values[0]`, the second column using `values[1]`, and so on.

**NB:** CSV file headers, if present, should be removed from  files before submitting sensor device data to Castor. 
 
## Run 

To submit sensor data to Castor, update the command line arguments, and execute the following command from 
within the `castor-messaging/mqtt` directory:

```
python -m mqtt_client --broker=broker-config.json --dir=./ --pattern=*.csv --state=state-sample.json --flavour=1 --batch=10 
```

#### Command Line Arguments

`--broker`: 
Path to the configuration file that contains all the required information to connect to the IBM Cloud MQTT Broker. 
This file will be supplied to you by IBM and its permission should be `read-only`. 
Store the broker configuration file and the MQTT broker certificate provided by IBM in the `castor-messaging/mqtt` directory.

`--dir`: 
The directory where the CSV files for processing are located.

`--pattern`: A regular expression defining the CSV files to process. For example, `s*.csv` specifies only those filenames starting with `s` and ending with `.csv`.

`--state`:
A JSON file identifying the last file processed and the last line processed in that file. The file will be automatically created if not found.

`--flavour`:
Defaults to 1.

`--batch`:
How many parsed lines extracted from a CSV file will be sent with every MQTT message. A bigger batch number means that fewer MQTT messages will be sent to the Service Platform per file.

`--max`:
The maximum number of lines that will be processed per file per invocation of `mqtt_client.py`. When the sample code is run, it will process any number of files, but it will stop at the first file that it encounters that has more than `max` lines of data.

`--v`:
Optional. Changes the logging level to `verbose` and all actions will be logged. This is for development and testing purposes.




