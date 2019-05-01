### Code sample

Sample mqtt client. Reads the contents of `./sample.csv` and publishes each line to an MQTT broker, as specified via a configuration file.

#### Requirements
```
Python 3.5
```

Install package dependencies
```
pip3 install -r requirements.txt
```

#### Run 

```
python3 mqtt_client.py --broker=broker-config.json --dir=./ --pattern=s*.csv --state=state-sample.json --flavour=1 --batch=10 
```

#### Parameters

--broker
A json file that contains all the required information to connect to the IBM Service Platform MQTT Broker. This file will be supplied to you by IBM and it should be Read Only.

--dir
The source directory where the files for processing are located.

--pattern
The filenames to process from the source directory. `L*.csv` specifies CSV files starting with 'L'.

--state
A json file containing the last file processed and the last line processed in this file. The file will be automatically created if not found.

--flavour
Defaults to 1.

--batch
How many parsed lines extracted from a CSV file will be sent with every MQTT message. A bigger batch number means that fewer MQTT messages will be sent to the Service Platform per file.

--max
The maximum number of lines that will be processed per file per run. When the program is run it will process any number of files but it will stop at the first file that it encounters that has more than `max` lines of data.

--v
Optional. Changes the logging level to Verbose and all actions will be logged. This is for development and testing purposes.




