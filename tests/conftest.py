#!/usr/bin/env python3
#author markpurcell@ie.ibm.com

"""
IBM-Review-Requirement: Art30.3 - DO NOT TRANSFER OR EXCLUSIVELY LICENSE THE FOLLOWING CODE UNTIL 30/11/2025!
Please note that the following code was developed for the project MUSKETEER in DRL funded by the European Union
under the Horizon 2020 Program.
The project started on 01/12/2018 and was completed on 30/11/2021. Thus, in accordance with article 30.3 of the
Multi-Beneficiary General Model Grant Agreement of the Program, the above limitations are in force until 30/11/2025.
"""

import pytest


def pytest_addoption(parser):
    parser.addoption("--credentials", required=True)
    parser.addoption("--feed_queue", required=False)
    parser.addoption("--reply_queue", required=False)

@pytest.fixture
def credentials(request):
    value = request.config.getoption('credentials')
    if request.cls:
        request.cls.credentials = value
    return value

@pytest.fixture
def feed_queue(request):
    value = request.config.getoption('feed_queue')
    if request.cls:
        request.cls.feed_queue = value
    return value

@pytest.fixture
def reply_queue(request):
    value = request.config.getoption('reply_queue')
    if request.cls:
        request.cls.reply_queue = value
    return value

