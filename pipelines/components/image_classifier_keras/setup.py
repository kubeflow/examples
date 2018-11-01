"""Install dependencies. Usage: python setup.py install
# Copyright 2018 Google LLC. All Rights Reserved.
#
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
# ==============================================================================
"""

from setuptools import find_packages
from setuptools import setup

with open('requirements.txt') as f:
  requirements = [l.strip('\n') for l in f if
                  l.strip('\n') and not l.startswith('#')]

setup(
  name='image_classifier_keras',
  version='0.1',
  install_requires=requirements,
  packages=find_packages(),
  include_package_data=True,
  description='ML pipelines'
)
