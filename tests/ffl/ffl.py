#!/usr/bin/env python3
#author markpurcell@ie.ibm.com

"""
IBM-Review-Requirement: Art30.3 - DO NOT TRANSFER OR EXCLUSIVELY LICENSE THE FOLLOWING CODE UNTIL 30/11/2025!
Please note that the following code was developed for the project MUSKETEER in DRL funded by the European Union
under the Horizon 2020 Program.
The project started on 01/12/2018 and was completed on 30/11/2021. Thus, in accordance with article 30.3 of the
Multi-Beneficiary General Model Grant Agreement of the Program, the above limitations are in force until 30/11/2025.
"""

import logging
import time
import json
import unittest
import pytest
import pycloudmessenger.ffl.fflapi as fflapi


#Set up logger
logging.basicConfig(
    level=logging.INFO,
    #level=logging.DEBUG,
    format='%(asctime)s.%(msecs)03d %(levelname)-6s %(name)-16s :: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

LOGGER = logging.getLogger(__package__)



class FFLTests(unittest.TestCase):
    #@unittest.skip("temporarily skipping")
    def test_enum(self):
        self.assertTrue(fflapi.Notification('aggregator_started') is fflapi.Notification.aggregator_started)

        with self.assertRaises(ValueError):
            self.assertTrue(fflapi.Notification('start') is fflapi.Notification.started)
        
        with self.assertRaises(ValueError):
            self.assertTrue(fflapi.Notification('started') is fflapi.Notification.start)

        #Check list searching
        arr = [fflapi.Notification.aggregator_started, fflapi.Notification.aggregator_stopped]
        self.assertTrue(fflapi.Notification('aggregator_started') in arr)
        self.assertTrue(fflapi.Notification('participant_joined') not in arr)

        #Ensure json serializability
        notify = {'type': fflapi.Notification.participant_joined}
        serialized = json.dumps(notify)

        deserialized = json.loads(serialized)
        self.assertTrue(fflapi.Notification(deserialized['type']) is fflapi.Notification.participant_joined)
