## pycloudmessenger
The purpose of this project is to provide sample code for interacting with various messaging based cloud platforms provided by IBM Research Ireland.


## Install

#### git

[git](https://git-scm.com/) is a free open source distributed version control system used to manage and maintain the 
`pycloudmessenger` sample source code.

Follow [these instructions](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) to install 
[git](https://git-scm.com/) on your local machine.

After [git](https://git-scm.com/) is installed, run the following command:

```
git clone https://github.com/IBM/pycloudmessenger.git
```

which creates a copy of the sample source code in this repository in a directory named `pycloudmessenger` on your local machine.

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


## Examples and Testing

Unit tests are contained in the tests directory and example code for basic messaging as well as ffl and castor are contained in the examples directory.

To run the unit tests, a local RabbitMQ container is launched automatically. Settings and credentials to match the latest RabbitMQ docker image are also provided. To run the test:

```
creds=local.json make test 
```

## References 

* [IBM Research Blog](https://www.ibm.com/blogs/research/2018/11/forecasts-iot/)
* [Castor: Contextual IoT Time Series Data and Model Management at Scale](https://arxiv.org/abs/1811.08566) Bei Chen, Bradley Eck, Francesco Fusco, Robert Gormally, Mark Purcell, Mathieu Sinn, Seshu Tirupathi. 2018 IEEE International Conference on Data Mining (ICDM workshops).
