#!/usr/bin/env python
#author mark_purcell@ie.ibm.com

"""Castor message formmatter.
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

import uuid

# pylint: disable=R0903, R0913


class MessageCatalog():
    def __init__(self, reply_to: str = None):
        self.correlation = 0
        self.reply_to = reply_to
        self.client_id = str(uuid.uuid4())

    def _msg_template(self, service_name: str = 'TimeseriesService'):
        """
            Format message template - internal only

            Throws:
                Nothing

            Returns:
                The requestor sub-info
        """
        message = {
            'serviceRequest': {
                'requestor': self._requestor(),
                'service': {
                    'name': service_name,
                    'args': {
                    }
                }
            }
        }
        return message, message['serviceRequest']['service']['args']

    def _requestor(self):
        """
            Format message for requestor information - internal only

            Throws:
                Nothing

            Returns:
                The requestor sub-info
        """

        self.correlation += 1
        req = {'correlationID': self.correlation}

        if self.reply_to:
            req.update({'replyTo': self.reply_to,
                        'clientID': self.client_id, 'transient': True})
        return req

    def request_sensor_data(self, meter, from_date, to_date):
        """
            Format message for retrieving sensor data

            Throws:
                An exception if not successful

            Returns:
                Dict - The message to send
        """
        template, args = self._msg_template()
        args.update({'cmd':'ts/get_timeseries_values', 'device_id': meter,
                     'from': from_date, 'to': to_date})
        return template

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
        template, args = self._msg_template()
        args.update({'cmd':'ts/get_timeseries_values_batch', 
                     'ts_ids': meter_ids,
                     'from': from_date, 'to': to_date})
        if asof is not None:
           args.update({'asof': asof})
        if asof_all:
           args.update({'all': asof_all})
        return template

    def request_sensor_list(self):
        """
            Format message for retrieving sensor listing

            Throws:
                An exception if not successful

            Returns:
                Dict - The message to send
        """
        template, args = self._msg_template()
        args.update({'cmd':'ts/get_time_series'})
        return template

    def store_time_series(self, values):
        """
            Format message for storing sensor observations

            Throws:
                An exception if not successful

            Returns:
                Dict - The message to send
        """
        template, args = self._msg_template()
        args.update({'cmd':'ts/store_timeseries_values', 'values': values})
        return template

    def average_time_series(self, meter, from_date, to_date):
        """
            Format message for averaging sensor observations

            Throws:
                An exception if not successful

            Returns:
                Dict - The message to send
        """
        template, args = self._msg_template()
        args.update({'cmd':'ts/average_timeseries_values', 'device_id': meter,
                     'from': from_date, 'to': to_date})
        return template

    def register_model(self, model_name, entity_name, signal_name):
        """
            Format message for registering an external model

            Throws:
                An exception if not successful

            Returns:
                Dict - The message to send
        """
        template, args = self._msg_template()
        args.update({'cmd':'register_model', 'model_name': model_name,
                     'entity': entity_name, 'signal': signal_name})
        return template

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
        context = {"entity_name": entity_name, "signal_name": signal_name}
        model_json = {"name": model_name,
                      "description": model_description,
                      "model_data": {
                         "environment": environment,
                         "code": "NULL",
                         "training_deployment": deployment
                     }}

        template, args = self._msg_template()
        args.update({'cmd':'store_model', 
                     'context': context,
                     'model': model_json
                    })
        return template


    def request_model_time_series(self, model_name, entity_name, signal_name):
        """
            Format message for retrieving a models timeseries is

            Throws:
                An exception if not successful

            Returns:
                Dict - The message to send
        """
        template, args = self._msg_template()
        args.update({'cmd':'get_model_time_series',
                     'model_name': model_name, 'entity': entity_name,
                     'signal': signal_name})
        return template

    def key_value_service(self, cmd, keys):
        """
            Format message for interacting with the key/value service

            Throws:
                An exception if not successful

            Returns:
                Dict - The message to send
        """
        template, args = self._msg_template('KeyValueService')
        args.update({'cmd': cmd, 'keys': keys})
        return template

    def weather_service_hourly(self, api_key, lat, lng):
        """
            Format message for interacting with the weather service

            Throws:
                An exception if not successful

            Returns:
                Dict - The message to send
        """
        template, args = self._msg_template('WeatherService-TwoDayHourlyForecast-External')
        args.update({'apiKey': api_key, 'latitude': lat, 'longitude': lng})
        return template

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

        template, args = self._msg_template()
        args.update({'cmd':'context/get_entity_types'})
        return template

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

        template, args = self._msg_template()
        args.update({'cmd':'context/get_signal_types'})
        return template

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
        
        template, args = self._msg_template()
        if entity_type is None:
           args.update({'cmd':'context/get_entities'})
        else:
           args.update({'cmd':'context/get_entities','entity_type_name':entity_type})
        return template

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
        template, args = self._msg_template()
        if signal_type is None:
           args.update({'cmd':'context/get_signals'})
        else:
           args.update({'cmd':'context/get_signals','signal_type_name':signal_type})
        return template

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
        
        template, args = self._msg_template()
        args.update({'cmd':'context/get_connectivity','entity_names':entity_names})
        return template

    def get_timeseries_id(self, contexts):
        """
        Retrieve ts_id for a given list of contexts
        Parameters:
            contexts (list)    : list of objects [{'entity_name':<val>,'signal_name':<val>},...]
        Returns:
            A list: [{'context':{'entity_name':<val>,'signal_name':<val>,'ts_id':<val>},...]
        """
        template, args = self._msg_template()
        args.update({'cmd':'get_timeseries','context':contexts})
        return template

    def get_timeseries_context(self, ts_ids):
        """
        Retrieve the context for a list of ts_ids
        Parameters:
            ts_ids (list)      : List of ts_id (string) ['ts_id1','ts_id2',...]
        Returns:
            output (list): [{'ts_id':'ts_id1','context':{'entity_name':<val>,'signal_name':<val>},...]
        """
        template, args = self._msg_template()
        args.update({'cmd':'get_timeseries_context','ts_ids':ts_ids})
        return template


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

        template, args = self._msg_template()
        args.update({'cmd':'get_timeseries_values', 
                     'context': {
                        'signal_name': signal,
                        'entity_name': entity
                     },
                     'from': from_date, 
                     'to': to_date})
        if asof is not None:
           args['asof'] = asof
        if asof_all:
           args['all'] = asof_all
        return template
   
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

        template, args = self._msg_template()
        args.update({'cmd':'get_models_hierarchy', 
                     'context': contexts})
        return template

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
        template, args = self._msg_template()
        args.update({'cmd':'get_model',
                     'context': {'signal_name':signal,'entity_name':entity},
                     'model_name': model_name
        })
        return template

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
        
        template, args = self._msg_template()
        args.update({'cmd':'get_forecast_values', 
                     'context': {
                        'signal_name': signal,
                        'entity_name': entity
                     },
                     'model_name':model_name,
                     'from': from_date, 
                     'to': to_date})
        if model_version is not None:
           args['model_version'] = model_version
        if asof is not None:
           args['asof'] = asof
        if asof_all:
           args['all'] = asof_all
        return template


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
        template, args = self._msg_template()
        args.update({'cmd':'get_model_version',
                     'context': {'signal_name':signal,'entity_name':entity},
                     'model_name': model_name,
                     'model_version': model_version,
                     'core': True
        })
        return template

