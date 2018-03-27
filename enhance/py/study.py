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

import logging
import argparse


class Study(object):
    pass


class Studies(object):
    pass


def study_runner(study_id):
    """Run a study with id `study_id`
    
    study_id (str): The ID of the study, existing in study registry.
    
    """
    logging.info("Running study with ID: %s" % study_id)

    
if __name__ == "__main__":
    
    logging.getLogger().setLevel(logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument("--study_id", dest="study_id",
                        help="The ID of the study to run.")    
    args, _ = parser.parse_known_args()

    logging.info("Parsed args: %s" % args.__dict__)
    
    study_runner(args.study_id)
    