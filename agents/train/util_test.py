# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import os
import tempfile
import unittest

from . import util


class TestCommandWrapper(unittest.TestCase):

  def test_run_command(self):

    # Make a file in a tempdir
    d = tempfile.mkdtemp()
    with open("%s/foo.txt" % d, 'w') as f:
      f.write("foo")

    expected = "foo.txt"
    result = util.run_and_output(["ls", d]).strip()

    self.assertEqual(result, expected)


if __name__ == "__main__":
  logging.getLogger().setLevel(logging.INFO)
  unittest.main()
