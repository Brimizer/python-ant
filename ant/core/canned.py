# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2011, Martín Raúl Villalba
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
##############################################################################



from ant.core.message import *
from ant.core.driver import Driver

from ant.core.exceptions import DriverError

from array import *

import logging
logger = logging.getLogger(__name__)



class CannedDriver(Driver):
    def __init__(self, device, log=None, debug=False):
        Driver.__init__(self, device, log, debug)
        # self.input_file_name = '/Users/dbrim/Development/python-ant-develop/src/inputfile.ant'
        # self.output_file_name = '/Users/dbrim/Development/python-ant-develop/src/outputfile.ant'
        # self.input_file = None
        # self.outut_file = None
        self.responses = {}

        self._next_read_buffer = None

    def _open(self):
        pass
        # self.input_file = open(self.input_file_name, 'r')
        # self.output_file = open(self.output_file_name, 'w+')

    def _close(self):
        pass
        # self.input_file.close()
        # self.output_file.close()

    def _read(self, count):
        # print('calling read')
        if self._next_read_buffer:
            local = self._next_read_buffer
            self._next_read_buffer = None
            return local

        read = b''
        return read

    def _write(self, data):
        if data in self.responses:
            self._next_read_buffer = self.responses[data]() # Call the response generator
        # count = self.output_file.write(data)
        return len(data)

