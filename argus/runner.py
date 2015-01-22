# Copyright 2014 Cloudbase Solutions Srl
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import sys
import time


class _WritelnDecorator(object):
    """Used to decorate file-like objects with a handy 'writeln' method"""
    def __init__(self, stream):
        self.stream = stream

    def __getattr__(self, attr):
        if attr in ('stream', '__getstate__'):
            raise AttributeError(attr)
        return getattr(self.stream, attr)

    def writeln(self, arg=None):
        if arg:
            self.write(arg)
        self.write('\n')  # text-mode streams translate to \r\n if needed


class Runner(object):
    def __init__(self, scenarios, stream=None):
        self._scenarios = scenarios
        self._stream = _WritelnDecorator(stream or sys.stderr)

    def run(self):
        results = []
        start_time = time.time()
        tests_run = 0
        expected_failures = unexpected_successes = skipped = 0
        failures = errors = 0
        for scenario in self._scenarios:
            result = scenario.run_tests()
            result.printErrors()
            tests_run += result.testsRun
            expected_failures += result.expectedFailures
            unexpected_successes += result.unexpectedSuccesses
            skipped += result.skipped
            failures += len(result.failures)
            errors += len(result.errors)
            results.append(result)

        time_taken = time.time() - start_time

        self._stream.writeln("Ran %d test%s in %.3fs" %
                             (tests_run,
                              tests_run != 1 and "s" or "", time_taken))
        self._stream.writeln()

        infos = []
        if any(not result.wasSuccesful()
               for result in results):
            self._stream.write("FAILED")
        else:
            self._stream.write("OK")

        infos = [
            "failures=%d" % failures,
            "errors=%d" % errors,
            "skipped=%d" % skipped,
            "expected failures=%d" % expected_failures,
            "unexpected successes=%d" % unexpected_successes
        ]
        if infos:
            self._stream.writeln(" (%s)" % (", ".join(infos),))
        else:
            self._stream.write("\n")
        return result