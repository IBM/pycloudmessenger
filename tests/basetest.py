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
import unittest
from contextlib import suppress
import pytest
from pycloudmessenger.ffl import fflapi
from pycloudmessenger.ffl import abstractions as fflabc


#Set up logger
logging.basicConfig(
    #level=logging.INFO,
    level=logging.DEBUG,
    format='%(asctime)s.%(msecs)03d %(levelname)-6s %(name)-16s :: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

LOGGER = logging.getLogger(__package__)

@pytest.mark.usefixtures("credentials")
class BaseTest(unittest.TestCase):
    credentials: dict
    num_users: int = 1
    uname: list
    user: list
    user_ctx: list
    aggr_ctx: fflapi.Context
    reg_url: str
    reg_api_key: str

    @classmethod
    def setUpClass(cls):
        fflabc.Factory.register('cloud', fflapi.Context, fflapi.User, fflapi.Aggregator, fflapi.Participant)

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.uname = [f'test-user{i}' for i in range(self.num_users)]
        LOGGER.info(self.uname)

        self.aggregator = 'test-aggregator'
        self.password = 'users_password%'
        self.task = 'UNIT-TEST-TASK-1'

        self.reg_url = self.credentials.get('register_url', None)
        self.reg_api_key = self.credentials.get('register_api_key', None)

        #self.aggr_ctx = fflabc.Factory.context('cloud', self.credentials, self.aggregator, self.password, dispatch_threshold = 0)
        #self.user_ctx = [fflabc.Factory.context('cloud', self.credentials, name, self.password, dispatch_threshold = 0) for name in self.uname]
        #self.tearDown()
        #return

        #Register the aggregator and participant users
        for username in self.uname:
            #with suppress(Exception):
            fflapi.create_user(username, self.password, 'ibm', url=self.reg_url, api_key=self.reg_api_key)

        #with suppress(Exception):
        result = fflapi.create_user(self.aggregator, self.password, 'ibm', url=self.reg_url, api_key=self.reg_api_key)
        self.assertTrue('connection' in result)
        self.credentials.update(result['connection'])

        self.aggr_ctx = fflabc.Factory.context('cloud', self.credentials, self.aggregator, self.password, dispatch_threshold = 0)
        self.user_ctx = [fflabc.Factory.context('cloud', self.credentials, name, self.password, dispatch_threshold = 0) for name in self.uname]

        self.user = [fflabc.Factory.user(ctx) for ctx in self.user_ctx]

    def tearDown(self):
        LOGGER.info("BaseTests:teardown - start...")

        for ctx in self.user_ctx:
            LOGGER.info(f"Removing: {ctx.user()}")
            user = fflapi.User(ctx)
            with user:
                with suppress(Exception):
                    user.deregister()
                    LOGGER.info(f"Removed: {ctx.user()}")

        LOGGER.info("Removed users")

        user = fflapi.User(self.aggr_ctx)
        with user:
            with suppress(Exception):
                user.deregister()

        LOGGER.info("BaseTests:teardown - done.")
