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
from contextlib import suppress
import pytest
import basetest
from pycloudmessenger.ffl import fflapi
from pycloudmessenger.ffl import abstractions as fflabc


# pylint: disable=W0106,C0116,C0301

LOGGER = logging.getLogger(__package__)

millis = lambda: str(int(round(time.time() * 1000)))
model_size = lambda: (10)#24*1024*1)
min_model = 0#1024*1024*5


class TrainTests(basetest.BaseTest):
    def setUp(self):
        self.num_users = 2
        super().setUp()

    def tearDown(self):
        LOGGER.info("Teardown - start...")

        LOGGER.info("Teardown - quitting task")
        with suppress(Exception):
            [self.quit(ctx) for ctx in self.user_ctx]
        LOGGER.info("Teardown - quit task")

        LOGGER.info("Teardown - stopping task")
        aggr_creds = fflapi.Context(self.credentials, self.aggregator, self.password)

        with suppress(Exception):
            aggr = fflapi.Aggregator(aggr_creds, task_name=self.task)
            with aggr:
                with suppress(Exception):
                    aggr.stop_task()
        LOGGER.info("Teardown - stopped task")

        super().tearDown()
        LOGGER.info("Teardown - done.")

    def quit(self, ctx):
        user = fflabc.Factory.participant(ctx, task_name=self.task)
        with user:
            result = user.leave_task()

    def join(self, ctx):
        user = fflabc.Factory.user(ctx)
        with user:
            result = user.join_task(self.task)
            LOGGER.debug(result)
            LOGGER.info("Worker user has successfully joined the task")
        return fflabc.Factory.participant(ctx, task_name=self.task)

    #@unittest.skip("temporarily skipping")
    def test_star(self):
        aggr_user = fflabc.Factory.user(self.aggr_ctx)
        with aggr_user:
            result = aggr_user.create_task(self.task, fflabc.Topology.star, {'alg':'test'})
            LOGGER.debug(result)
            LOGGER.info("Task successfully created")

        workers = []
        [workers.append(self.join(ctx)) for ctx in self.user_ctx]
        aggr = fflabc.Factory.aggregator(self.aggr_ctx, task_name=self.task)

        #Joining
        participants = []
        [participants.append({'value': [], 'id':
            self.aggr_wait(aggr, idx, fflabc.Notification.participant_joined)}) for idx, _ in enumerate(self.uname, start=1)]
        LOGGER.info("Aggregator has a quorum")

        #Round 1 - all participants
        LOGGER.info("Training round 1")
        self.aggr_start(aggr, topology=fflabc.Topology.star)

        #Workers all expecting the same initial model
        [self.worker(worker, 0, idx) for idx, worker in enumerate(workers, start=1)]

        #Aggregator expecting the same model from all workers
        [self.aggr_wait(aggr, idx, fflabc.Notification.participant_updated) for idx, _ in enumerate(self.uname, start=1)]
        LOGGER.info("Aggregator consolidates worker updates")
        
        LOGGER.info(f"Participants: {participants}")

        with aggr:
            for idx, party in enumerate(participants, start=0):
                LOGGER.info(f"Party - {party}")
                #value = party.get('value', [])
                party['value'].append(1.10+idx)
                #party['value'] = value
                aggr.assign_value(party['id'], party['value'])

        LOGGER.info(f"Participants: {participants}")

        #Round 2 - specific participant
        LOGGER.info("Training round 2")
        self.aggr_start(aggr, participants[0]['id'])

        self.worker(workers[0], 0, 1)

        self.aggr_wait(aggr, 1, fflabc.Notification.participant_updated)
        LOGGER.info("Aggregator consolidates worker updates")

        with aggr:
            party = participants[0]
            #value = party.get('value', [])
            party['value'].append(1.12)
            #party['value'] = value
            aggr.assign_value(party['id'], party['value'])

        LOGGER.info(f"Participants: {participants}")

        #Aggregator now closes the task
        with aggr:
            LOGGER.info("Aggregator stopping the task...")
            aggr.stop_task({'the_model':'the final model'})
            LOGGER.info("Aggregator successfully completes the task")

        LOGGER.info("***** FL now complete *****")
        LOGGER.info("***** Retrospectively recall model lineage *****")

        LOGGER.info("--------------------------------------------------------")
        LOGGER.info("User1 Model Lineage")

        with self.user[0] as worker:
            result = worker.model_lineage(self.task)
            if not min_model:
                self.assertEqual(len(result), 2)
            self.print_lineage(result)

        LOGGER.info("--------------------------------------------------------")
        LOGGER.info("User2 Model Lineage")

        with self.user[1] as worker:
            result = worker.model_lineage(self.task)
            if not min_model:
                self.assertEqual(len(result), 1)
            self.print_lineage(result)

        LOGGER.info("--------------------------------------------------------")
        LOGGER.info("Aggregator Full Model Lineage")
        with aggr_user:
            result = aggr_user.model_lineage(self.task)
            if not min_model:
                self.assertEqual(len(result), 6)
            self.print_lineage(result)

        #Should work because of ACL
        with self.user[1] as worker:
            result = worker.get_model(self.task)
            self.assertEqual(result, {'the_model':'the final model'})

            #Should fail because of ACL
            with self.assertRaises(fflabc.ServerException):
                result = worker.delete_model(self.task)

    def aggr_wait(self, aggr, worker_id, wanted, timeout=0.1):
        #Aggregator enters listening mode and waits for notifications
        with aggr:
            result = aggr.receive(timeout)
            LOGGER.debug(f"Aggregator received: {result.content}")
            #LOGGER.info(f"Aggregator received: {result.notification}")
            participant = result.notification['participant']

            if wanted is fflabc.Notification.participant_updated:
                expected_model = {'the_model' : str(worker_id) * model_size()}
                #LOGGER.info(f"Aggregator expecting: {expected_model}")
                #LOGGER.info(f"Received: {result.content}")
                self.assertTrue(expected_model == result.content)

            self.assertTrue('type' in result.notification)
            self.assertTrue(fflabc.Notification(result.notification['type']) is wanted)

            result = aggr.get_participants()
            if not result:
                self.fail()

            #participant = next(iter(result))
            LOGGER.info(f"Received update from: {participant}")
            return participant

    def aggr_start(self, aggr, participant: str = None, topology: str = None):
        with aggr:
            #Model size 1024 triggers send to COS
            model = '0' * model_size()
            aggr.send({'the_model': model}, participant, topology)
            LOGGER.info("Task successfully started by aggregator")

    def worker(self, worker, source_id, worker_id, timeout=0.1):
        #Worker enters listening mode and waits for notifications
        with worker:
            result = worker.receive(timeout)
            #LOGGER.debug(f"Worker received: {result.content}")
            LOGGER.debug(result.notification)
            expected_model = {'the_model' : str(source_id) * model_size()}
            #LOGGER.info(f"Worker expecting: {expected_model}")
            #LOGGER.info(result.content)
            self.assertTrue(expected_model == result.content)
            self.assertTrue('type' in result.notification)
            self.assertTrue(fflabc.Notification.is_aggregator_started(result.notification))
            LOGGER.info("Worker successfully received start request")

            #Received message from aggregator
            #We could now train etc.....
            #But close the connection to the platform first

        #Now carry out local work
        LOGGER.info("Worker commences training")

        #The local work is complete
        #Worker updates task assignment
        with worker:
            model = str(worker_id) * model_size()
            meta = millis()
            worker.send({'the_model': model}, metadata=meta)
            LOGGER.info(f"Worker metadata {meta}")
            LOGGER.info("Worker successfully completes work and dispatches updates")

    def print_lineage(self, result: dict):
        training_round = 0

        LOGGER.info(f"{'Round':5} {'Date':30} {'Origin':20} {'Id':11} {'Hash':11} {'Value Estimate':20} {'Reward':10}")

        for line in result:
            if 'genre' in line:
                if line['genre'] == 'INTERIM':
                    training_round += 1
                    LOGGER.info(f"{training_round:^5d} {line['added']:30} {'AGGREGATOR':20} " +
                                f"...{str(line['external_id'][-7:]):8} ...{str(line['xsum'][-7:]):8}")
                elif line['genre'] == 'COMPLETE':
                    LOGGER.info(f"Final {line['added']:30} {'AGGREGATOR':20} " +
                                f"...{str(line['external_id'][-7:]):8} ...{str(line['xsum'][-7:]):8}")
                else:
                    LOGGER.info(f"{training_round:^5d} {line['added']:30} {line['participant']:20} " +
                                f"...{str(line['external_id'][-7:]):8} ...{str(line['xsum'][-7:]):8} " +
                                f"{str(line['contribution']):20} {str(line['reward']):10}")
            else:
                training_round += 1
                LOGGER.info(f"{training_round:^5d} {line['added']:30} {line['metadata']:20} " +
                            f"{str(''):11} ...{str(line['xsum'][-7:]):8} " +
                            f"{str(line['contribution']):20} {str(line['reward']):10}")
