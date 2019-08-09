## Pushing Sensor Data to Castor using MQTT - Sample Code

Sample [MQTT](http://mqtt.org/) client that parses sensor device ID, timestamp, and value readings from a `./sample.csv` file 
and publishes to a remote [MQTT](http://mqtt.org/) broker specified by a [JSON](https://www.json.org/) configuration file.

## Install
The Python sample code in this directory depends on several external packages.

To install these packages on your local machine, execute the following command from within the `pycloudmessenger/castor/mqtt` directory:

```
pip install -r requirements.txt
```

## Configure

Additional configuration will be required to parse sensor device ID, timestamp, and value readings from CSV files that 
differ in format from the `sample.csv` file provided in this repository.

These configuration changes relate to:
- timestamp format,
- timestamp time zone, and
- multiple values & column ordering.

#### Coordinated Universal Time 

Castor uses [Coordinated Universal Time (UTC)](https://en.wikipedia.org/wiki/Coordinated_Universal_Time) exclusively for timestamp values - all timestamps submitted to Castor via MQTT must conform to UTC.

The sample code can be configured with the format & local time zone of the timestamps in the CSV being parsed, allowing them to 
be converted to UTC prior to submission to Castor.

#### Timestamp Format

The sample code provided is [currently configured](https://github.com/IBM/pycloudmessenger/blob/master/pycloudmessenger/castor/mqtt/csv_config.json) 
to parse timestamps in `sample.csv` of the following format: `2018-12-31 22:39:50`.

To change this timestamp format, update the `timestamp_format` value in the [`csv_config.json`](https://github.com/IBM/pycloudmessenger/blob/master/pycloudmessenger/castor/mqtt/csv_config.json) 
to match your CSV file's timestamp format. [See here for an in-depth description of Python's `datetime` parsing syntax](https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior).

#### Timestamp Time Zone

The sample code provided is [currently configured](https://github.com/IBM/pycloudmessenger/blob/master/pycloudmessenger/castor/mqtt/csv_config.json) to treat timestamps in `sample.csv` as local times in the following time zone: `Europe/Zurich`.

To change the local time zone, update the `timestamp_timezone` value in the [`csv_config.json`](https://github.com/IBM/pycloudmessenger/blob/master/pycloudmessenger/castor/mqtt/csv_config.json)
to match your CSV file's timestamp time zone. [See here for a list of time zone names](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones). For example, if the timestamps in the CSV represent local times in Norway, use: `Europe/Oslo`, or for Nova Scotia, use: `America/Halifax`.

#### Multiple Values & Column Ordering

The sample code provided is [currently configured](https://github.com/IBM/pycloudmessenger/blob/master/pycloudmessenger/castor/mqtt/csv_config.json) to parse the three-column [`sample.csv`](https://github.com/IBM/pycloudmessenger/blob/master/pycloudmessenger/castor/mqtt/sample.csv) file where:
 - the first column contains the sensor device ID (configured by `sensor_id_idx` in [`csv_config.json`](https://github.com/IBM/pycloudmessenger/blob/master/pycloudmessenger/castor/mqtt/csv_config.json)),
 - the second column contains the local timestamp (configured by `timestamp_idx` in [`csv_config.json`](https://github.com/IBM/pycloudmessenger/blob/master/pycloudmessenger/castor/mqtt/csv_config.json)), and
 - the third column contains the value (configured by `value_column_names` & `value_column_idxs` in [`csv_config.json`](https://github.com/IBM/pycloudmessenger/blob/master/pycloudmessenger/castor/mqtt/csv_config.json)).
 
 **NB:** Python uses zero-based indexing - the first CSV column is referenced using index `0`, the second column using index `1`, and so on.
 
If your CSV file:
 - contains multiple sensor values per row, for example, a CDT sensor measuring conductivity, temperature, and depth similar to [`sample_composite.csv`](https://github.com/IBM/pycloudmessenger/blob/master/pycloudmessenger/castor/mqtt/sample_composite.csv), and/or
 - has column ordering that differs from that described above for [`sample.csv`](https://github.com/IBM/pycloudmessenger/blob/master/pycloudmessenger/castor/mqtt/csv_config.json)
 
 update the `sensor_id_idx`, `timestamp_idx`, `value_column_names`, and `value_column_idxs` fields in [`csv_config.json`](https://github.com/IBM/pycloudmessenger/blob/master/pycloudmessenger/castor/mqtt/csv_config.json) to conform to your CSV file's format.
 
 For example, [`csv_config_composite.json`](https://github.com/IBM/pycloudmessenger/blob/master/pycloudmessenger/castor/mqtt/csv_config_composite.json)
 is configured to parse the [`sample_composite.csv`](https://github.com/IBM/pycloudmessenger/blob/master/pycloudmessenger/castor/mqtt/sample_composite.csv)
 containing multiple sensor values per row.
 
**NB:** CSV file headers, if present, should be removed from  files before submitting sensor device data to Castor. 
 
## Run 

To submit sensor data to Castor, update the command line arguments, and execute the following command from 
within the `pycloudmessenger/castor/mqtt` directory:

```
python -m mqtt_client --broker=broker-config.json --dir=./ --pattern=sample.csv --state=state-sample.json --batch=10 
```

#### Command Line Arguments

`--broker`: 
Path to the configuration file that contains all the required information to connect to the IBM Cloud MQTT Broker. 
This file will be supplied to you by IBM and its permission should be `read-only`. 
Store the broker configuration file and the MQTT broker certificate provided by IBM in the `pycloudmessenger/castor/mqtt` directory.

`--dir`: 
The directory where the CSV files for processing are located.

`--pattern`: A regular expression defining the CSV files to process. For example, `s*.csv` specifies only those filenames starting with `s` and ending with `.csv`.

`--state`:
A JSON file identifying the last file processed and the last line processed in that file. The file will be automatically created if not found.

`--batch`:
How many parsed lines extracted from a CSV file will be sent with every MQTT message. A bigger batch number means that fewer MQTT messages will be sent to the Service Platform per file.

`--max`:
(Optional) The maximum number of lines that will be processed per file per invocation of `mqtt_client.py`. When the sample code is run, it will process any number of files, but it will stop at the first file that it encounters that has more than `max` lines of data. Defaults to `100000`.

`--csv_config_path`:
(Optional) Path to CSV configuration file. Defaults to `csv_config.json`

`--v`:
(Optional) Changes the logging level to `verbose` and all actions will be logged. This is for development and testing purposes.




