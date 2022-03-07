#!/usr/bin/env python3
#author mark_purcell@ie.ibm.com

"""Utility helpers.
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

Please note that the following code was developed for the project MUSKETEER
in DRL funded by the European Union under the Horizon 2020 Program.
"""

import os
import shutil
import tempfile
import weakref
import base64
import requests
import tenacity


class TempFile():
    """
        Download a file from a url
    """

    def __init__(self, auto_delete: bool = True):
        self.descriptor, self.filename = tempfile.mkstemp()
        os.close(self.descriptor)

        #Ensure the file is deleted
        fn_clean = os.unlink if auto_delete else lambda *args: None
        self._finalizer = weakref.finalize(self, fn_clean, self.filename)

    def name(self):
        return self.filename

    def remove(self):
        self._finalizer()

    @property
    def removed(self):
        return not self._finalizer.alive


class FileDownloader(TempFile):
    """
        Download a file from a url
    """

    def __init__(self, url: str, filename: str = None):
        if filename:
            self.filename = filename
        else:
            super().__init__(auto_delete=False)

        with requests.get(url, stream=True) as request:
            with open(self.filename, 'wb') as new_file:
                shutil.copyfileobj(request.raw, new_file)


class Certificate(TempFile):
    """
        Convert b64 string to PEM file
    """
    def __init__(self, b64string: str, filename: str = None):
        if filename:
            self.filename = filename
        else:
            super().__init__()

        #Convert the b64 cert string to a local PEM file
        self.pem = Certificate.pem(b64string)

        if filename:
            with open(self.filename, 'w') as pem_file:
                pem_file.write(self.pem)

    @classmethod
    def pem(cls, b64string: str):
        return base64.b64decode(b64string).decode('utf-8')


class Timer:
    @classmethod
    def retry(cls, timeout: float, callback, throw: Exception, *args, **kwargs) -> any:
        @tenacity.retry(wait=tenacity.wait_random(min=timeout/1000, max=timeout/100),
                        stop=tenacity.stop_after_delay(timeout),
                        reraise=True)
        def retry_impl(callback, *args, **kwargs):
            result = callback(*args, **kwargs)
            if result:
                return result
            raise throw('Operation timed out')
        return retry_impl(callback, *args, **kwargs)

