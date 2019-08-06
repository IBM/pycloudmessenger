#!/usr/bin/env python
#author markpurcell@ie.ibm.com

# pylint: disable=W1203

import json


class Serializer:
    @staticmethod
    def serialize(message):
        return json.dumps(message)

    @staticmethod
    def deserialize(message):
        return json.loads(message)
