|travis-badge|_

.. |travis-badge| image:: https://travis-ci.com/IBM/pycloudmessenger.svg?branch=master
.. _travis-badge: https://travis-ci.com/IBM/pycloudmessenger/

========================
pycloudmessenger
========================

The purpose of this project is to provide sample code for interacting with various messaging based cloud platforms provided by IBM Research Ireland.


Prerequisites
---------------------------------

It is assumed that all development takes place in Python, using at least version 3.6.


Testing
---------------------------------

Unit tests are contained in the tests_ directory.

To run the unit tests, a local RabbitMQ container is launched automatically. Settings and credentials to match the latest RabbitMQ docker image are also provided. To run the test:

.. code-block::

	creds=local.json make test 


Examples
---------------------------------

Sample code for basic messaging as well as federated learning and castor are contained in the examples_ directory.

.. code-block::

	creds=local.json make basic

.. code-block::

	creds=credentials.json make ffl

.. code-block::

	creds=credentials.json make castor

**Note:** For live platforms, **credentials.json** must be available. Please request from the IBM team.


References 
---------------------------------

* [IBM Research Blog](https://www.ibm.com/blogs/research/2018/11/forecasts-iot/)
* [Castor: Contextual IoT Time Series Data and Model Management at Scale](https://arxiv.org/abs/1811.08566) Bei Chen, Bradley Eck, Francesco Fusco, Robert Gormally, Mark Purcell, Mathieu Sinn, Seshu Tirupathi. 2018 IEEE International Conference on Data Mining (ICDM workshops).
