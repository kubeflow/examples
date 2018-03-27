# coding=utf-8
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests of Study, Studies, study_runner and supporting utils."""

import unittest
from study import Study, Studies, study_runner


class TestStudy(self):
    """Tests of Study"""
    
    def test_instantiate(self):
        
        study = Study()


class TestStudies(self):
    """Tests of Studies."""
    
    def test_e2e(self):
        
        studies = Studies(redis connection info)
        
        cases = [
            Study()
        ]
        
        for case in cases:
            study_id = case.create()
            study = studies.get(study_id)
            self.assertEqual(case, study)


class TestStudyRunner(self):
    """Tests of study_runner"""
    
    def test_study_runner(self):
        
        study = Study()
        study_id = study.create()
        
        status = study_runner(study_id)


if __name__ == "__main__":
    unittest.main()