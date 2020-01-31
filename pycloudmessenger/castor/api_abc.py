#!/usr/bin/env python
#author mark_purcell@ie.ibm.com

"""Castor abstract base class
/*
 * Licensed to the Apache Software Foundation (ASF) under one or more
 * contributor license agreements.  See the NOTICE file distributed with
 * this work for additional information regarding copyright ownership.
 * The ASF licenses this file to You under the Apache License, Version 2.0
 * (the "License"); you may not use this file except in compliance with
 * the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
"""
from abc import ABC, abstractmethod
import pycloudmessenger.castor.message_catalog as catalog


class CastorABC(ABC):
    def __init__(self, context, publish_queue: str = None, subscribe_queue: str = None):
        self.catalog = None

    @abstractmethod
    def invoke_service(self, message, timeout=60):
        pass

    def request_sensor_data(self, meter, from_date, to_date):
        """
            Format message for retrieving sensor data

            Throws:
                An exception if not successful

            Returns:
                Dict - The message to send
        """
        return self.catalog.request_sensor_data(meter, from_date, to_date)

    def request_sensor_data_batch(self, meter_ids, from_date, to_date, asof=None, asof_all=False):
        """
           Format message for retrieving sensor data for a list of meter_ids
        Parameters:
            meter_ids (list of string): Timeseries IDs.
            from_date (string)      : Start of datetime range (inclusive); format: 'YYYY-MM-DDThh:mm:ss+00:00'
            to_date (string)        : End of datetime range (inclusive); format: 'YYYY-MM-DDThh:mm:ss+00:00'
            asof (string)    : Optional 'as of' dateime; format: 'YYYY-MM-DDThh:mm:ss+00:00'
            asof_all (Boolean) : If False (default) only most recent forecasts for every timestamp are returned, otherwise all.
        Returns:
            (dict): {
                      'fields' : [
                        'observed_timestamp',
                        'added_timestamp',
                        'value',
                        'adhoc'
                      ],
                      'batches' : [
                        {
                          'ts_id'  : (string) 'Timeseries ID',
                          'values' : [
                            (string) '2019-02-01T13:00:00+00:00',
                            (string) '2019-02-01T13:02:00+00:00',
                            (float)  239.2,
                            (string) 'SomeValueMetadata'
                          ],
                          ...more...
                        },
                        ... more...
                      ]
                    }
        """
        return self.catalog.request_sensor_data_batch(meter_ids, from_date, to_date, asof, asof_all)

    def request_sensor_list(self):
        """
            Format message for retrieving sensor listing

            Throws:
                An exception if not successful

            Returns:
                Dict - The message to send
        """
        return self.catalog.request_sensor_list()

    def store_time_series(self, values):
        """
            Format message for storing sensor observations

            Throws:
                An exception if not successful

            Returns:
                Dict - The message to send
        """
        return self.catalog.store_time_series(values)

    def average_time_series(self, meter, from_date, to_date):
        """
            Format message for averaging sensor observations

            Throws:
                An exception if not successful

            Returns:
                Dict - The message to send
        """
        return self.catalog.average_time_series(meter, from_date, to_date)

    def register_model(self, model_name, entity_name, signal_name):
        """
            Format message for registering an external model

            Throws:
                An exception if not successful

            Returns:
                Dict - The message to send
        """
        return self.catalog.register_model(model_name, entity_name, signal_name)

    def deploy_model(self, model_name, entity_name, signal_name, model_description="",deployment={},environment="default"):
        """
        Deploy Python-based CASTOR model for automatic training and scoring
        Parameters:
            signal_name (string)           : Modelled signal name.
            entity_name (string)           : Modelled entity name.
            model_name (string)       : Model name.
            deployment (dict): {
                                          'task'            : (string) 'train',
                                          'time'            : (string) Required initial training time: 'YYYY-MM-DDThh:mm:ss+00:00',
                                          'repeatEvery'     : (string) Optional repeat training schedule: 'N_minutes | N_hours | N_days | N_weeks',
                                          'until'           : (string) Optional final training time: 'YYYY-MM-DDThh:mm:ss+00:00',
                                          'user_parameters' : {
                                            'optional' : 'user',
                                            'defined'  : 'parameters'
                                            },
                                          'scoring_deployment': {
                                            'task'        : (string) 'score',
                                            'time'        : (string) Default initial scoring time: 'YYYY-MM-DDThh:mm:ss+00:00',
                                            'repeatEvery' : (string) Optional default repeat scoring schedule: 'N_minutes | N_hours | N_days | N_weeks',
                                            'until'       : (string) Optional default final scoring time: 'YYYY-MM-DDThh:mm:ss+00:00'
                                            }
                                        }
            environment (JSON string) : '{"type": "python_dist" or "python_dist_dl", "dist": {"name":"<distName>", "version":"<distVersion>", "module":"<distModule>"}}'
            model_description (string): Optional model description.
        Returns:
            dict: {
                    'model_id : (integer) Stored Python-based CASTOR model ID.
                  }
        """
        return self.catalog.deploy_model(model_name, entity_name, signal_name, model_description, deployment, environment)


    def request_model_time_series(self, model_name, entity_name, signal_name):
        """
            Format message for retrieving a models timeseries is

            Throws:
                An exception if not successful

            Returns:
                Dict - The message to send
        """
        return self.catalog.request_model_time_series(model_name, entity_name, signal_name)

    def key_value_service(self, cmd, keys):
        """
            Format message for interacting with the key/value service

            Throws:
                An exception if not successful

            Returns:
                Dict - The message to send
        """
        return self.catalog.key_value_service(cmd, keys)

    def weather_service_hourly(self, api_key, lat, lng):
        """
            Format message for interacting with the weather service

            Throws:
                An exception if not successful

            Returns:
                Dict - The message to send
        """
        return self.catalog.weather_service_hourly(api_key, lat, lng)

    def get_entity_types(self):
        """
        Get all entity types in Semantic Context store.
        Parameters:
            None
        Returns:
            (list): [
                      {
                        'name'        : (string) 'Entity Type name',
                        'description' : (string) 'Entity Type description',
                      }
                      ...more...
                    ]
        """
        return self.catalog.get_entity_types()

    def get_signal_types(self):
        """
        Get all signal types in Semantic Context store.
        Parameters:
            None
        Returns:
            (list): [
                      {
                        'name'        : (string) 'Signal Type name',
                        'description' : (string) 'Signal Type description',
                      }
                      ...more...
                    ]
        """
        return self.catalog.get_signal_types()


    def get_entities(self, entity_type=None):
        """
        Get all entities in Semantic Context store.
        Optionally, only retrieve entities of a specified type.
        Parameters:
            entity_type (string): Optional entity type.
        Returns:
            (list): [
                      {
                        'name'        : (string) 'Entity name',
                        'description' : (string) 'Entity description',
                        'entity_type' : {
                          'name'        : (string) 'Entity type name',
                          'description' : (string) 'Entity type description'}
                          },
                        'geography' : {
                          'geography_type' : (string) 'GIS_POINT',
                          'latitude'       : (float) Entity latitude,
                          'longitude'      : (float) Entity longitude
                          }
                      }
                      ...more...
                    ]
        """
        return self.catalog.get_entities(entity_type)

    def get_signals(self, signal_type=None):
        """
        Get all signals persisted in context store.
        Optionally, only retrieve signals of a specified type.
        Parameters:
            signal_type (string): Optional signal type.
        Returns:
            (dict): {
                      'signals: [
                        {
                          'name'        : (string) Signal name,
                          'description' : (string) Signal description,
                          'signal_type' : {
                            'name'        : (string) Signal type name,
                            'description' : (string) Signal type description,
                            },
                          'unit'        : (string) Signal unit of measurement
                        }
                      ]
                    }
        """   
        return self.catalog.get_signals(signal_type)

    def get_entities_connectivity(self, entity_names):
        """
        Get connectivity for a set of entity name(s).
        Parameters:
            entity_names (list of string): Entity name(s).
        Returns:
            (list): [
                      [(string) 'Entity name A connected', (string) 'to entity name B'],
                      [(string) 'Entity name A connected', (string) 'to entity name C'],
                      ...more...
                    ]
        """
        return self.catalog.get_entities_connectivity(entity_names)
        

    def get_timeseries_id(self, contexts):
        """
        Retrieve ts_id for a given list of contexts
        Parameters:
            contexts (list)    : list of objects [{'entity_name':<val>,'signal_name':<val>},...]
        Returns:
            A list: [{'context':{'entity_name':<val>,'signal_name':<val>,'ts_id':<val>},...]
        """
        return self.catalog.get_timeseries_id(contexts)

    def get_timeseries_context(self, ts_ids):
        """
        Retrieve the context for a list of ts_ids
        Parameters:
            ts_ids (list)      : List of ts_id (string) ['ts_id1','ts_id2',...]
        Returns:
            output (list): [{'ts_id':'ts_id1','context':{'entity_name':<val>,'signal_name':<val>},...]
        """
        return self.catalog.get_timeseries_context(ts_ids)


    def get_timeseries_data(self, signal, entity,from_date, to_date, asof=None,asof_all=False):
        """
        Get timeseries values for a signal & entity, over a specified time range.
        Parameters:
            signal (string)  : Context signal name.
            entity (string)  : Context entity name.
            fromDate (string): Start of time range (inclusive); format: 'YYYY-MM-DDThh:mm:ss+00:00'
            toDate (string)  : End of time range (inclusive); format: 'YYYY-MM-DDThh:mm:ss+00:00'
            asof (string)    : Optional 'as of' dateime; format: 'YYYY-MM-DDThh:mm:ss+00:00'
            asof_all (Boolean) : If False (default) only most recent forecasts for every timestamp are returned, otherwise all.
        Returns:
            (dict): {
                      'fields' : [
                        'observed_timestamp',
                        'added_timestamp',
                        'value',
                        'adhoc'
                      ],
                      'values' : [
                        [
                          (string) '2019-02-01T13:00:00+00:00',
                          (string) '2019-02-01T13:02:00+00:00',
                          (float)  239.2,
                          (string) 'SomeValueMetadata'
                        ],
                        ...more...
                      ]
                    }
        """
        return self.catalog.get_timeseries_data(signal, entity,from_date, to_date, asof, asof_all)

    def get_models(self, contexts):
        """
        Get CASTOR models, model versions for a given list of Semantic Context (entiyty_name, signal_name).
        Parameters:
            contexts (list of context dict): [{'entity_name': <ename1>, 'signal_name': <sname1>}, ... ]
        Returns:
            list: [ 
                    { 
                      'context': {ctx1},
                      'models': [ 
                         {
                           'model': m1,
                           'model_versions': [
                              {'model_version': mv11, 'ts_id': tsv11},
                              {'model_version': mv12, 'ts_id': tsv12},
                              ...
                           ]
                         },
                         {
                           'model': m2,
                           'model_versions': [
                              {'model_version': mv21, 'ts_id': tsv21},
                              {'model_version': mv22, 'ts_id': tsv22},
                              ...
                           ]
                         },
                         ...
                       ]
                    },
                    {
                      'context': {ctx2},
                      'moedls': [...]
                    },
                    ...
                  ]
        """
        return self.catalog.get_models(contexts)


    def get_model_deployment(self, signal, entity, model_name):
        """
        Get CASTOR model deployment data.
        Parameters:
            signal (string)        : Context signal name.
            entity (string)        : Context entity name.
            model_name (string)    : Model name.
        Returns:
            dict: {
                    'model' : {
                      'model_id'    : (integer) Model ID,
                      'name'        : (string) 'Model name',
                      'description' : (string) 'Model description',
                      'model_data' : {
                        'environment'         : (string) 'Model environment',
                        'code'                : (string) 'Model code in base64 format; used only for R-based models',
                        'training_deployment' : {
                          'task'            : (string) 'train',
                          'time'            : (string) Initial training time: 'YYYY-MM-DDThh:mm:ss+00:00',
                          'repeatEvery'     : (string) Optional repeat training schedule: 'N_minutes | N_hours | N_days | N_weeks',
                          'until'           : (string) Optional final training time: 'YYYY-MM-DDThh:mm:ss+00:00',
                          'user_parameters' : {
                            'optional' : 'user',
                            'defined'  : 'parameters'
                            }
                          }
                        }
                      }
                  }
        """
        return self.catalog.get_model_deployment(signal, entity, model_name)

    def get_model_data(self, signal, entity, model_name, model_version=None, from_date=None, to_date=None, asof=None, asof_all=False):
        """
        Get forecast values for a given signal, entity, model name, and model version.
        Parameters:
            signal (string)        : Context signal name.
            entity (string)        : Context entity name.
            model_name (string)    : Model name.
            model_version (integer): Model version ID.
            fromDate (string)      : Start of time range (inclusive); format: 'YYYY-MM-DDThh:mm:ss+00:00'
            toDate (string)        : End of time range (inclusive): format: 'YYYY-MM-DDTHH:mm:ss+00:00'
            asof (string)          : Forecasts produced as of time (inclusive): format: 'YYYY-MM-DDTHH:mm:ss+00:00'
            asof_all (Boolean)     : If False (default) only most recent forecasts for every timestamp are returned, otherwise all.
        Returns:
            (dict): {
                      'fields' : [
                        'observed_timestamp',
                        'added_timestamp',
                        'value',
                        'adhoc'
                      ],
                      'values' : [
                        [
                          (string) '2019-02-01T12:00:00+00:00',
                          (string) '2019-01-01T00:01:00+00:00',
                          (float)  239.2,
                          (string) 'SomeValueMetadata'
                        ],
                        ...more...
                      ]
                    }
        """
        return self.catalog.get_model_data(signal, entity, model_name, model_version, from_date, to_date, asof, asof_all)
        

    def get_model_version_deployment(self, signal, entity, model_name, model_version):
        """
        Get CASTOR model deployment data.
        Parameters:
            signal (string)        : Context signal name.
            entity (string)        : Context entity name.
            model_name (string)    : Model name.
            model_version (int)    : Trained model version
        Returns:
            dict: {
                    'model' : {
                      'model_id'    : (integer) Model ID,
                      'version'  :  (integer) Model version ID,
                      'model_version_data':{
                         'train_time'        : (string) When model version was trained: 'YYYY-MM-DDThh:mm:ss+00:00',
                         'scoring_deployment': {
                            'task'            : (string) 'score',
                            'time'            : (string) Initial scoring time: 'YYYY-MM-DDThh:mm:ss+00:00',
                            'repeatEvery'     : (string) Optional repeat scoring schedule: 'N_minutes | N_hours | N_days | N_weeks',
                            'until'           : (string) Optional final scoring time: 'YYYY-MM-DDThh:mm:ss+00:00',
                            'user_parameters' : {
                               'optional' : 'user',
                               'defined'  : 'parameters'
                            }
                         }
                      }
            }
           }
        """
        return self.catalog.get_model_version_deployment(signal, entity, model_name, model_version)


