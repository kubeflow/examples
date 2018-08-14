from __future__ import print_function
import subprocess
from distutils.command.build import build as distutils_build #pylint: disable=no-name-in-module
from setuptools import setup, find_packages, Command as SetupToolsCommand

VERSION = '0.1.dev0'

with open('requirements.txt', 'r') as f:
  install_requires = f.readlines()

CUSTOM_COMMANDS = [
  ['python', '-m', 'spacy', 'download', 'en'],
  # TODO(sanyamkapoor): This isn't ideal but no other way for a seamless install right now.
  ['pip', 'install', 'https://github.com/kubeflow/batch-predict/tarball/master']
]


class Build(distutils_build):
  sub_commands = distutils_build.sub_commands + [('CustomCommands', None)]


class CustomCommands(SetupToolsCommand):
  def initialize_options(self):
    pass

  def finalize_options(self):
    pass

  @staticmethod
  def run_custom_command(command_list):
    print('Running command: %s' % command_list)
    p = subprocess.Popen(command_list, stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout_data, _ = p.communicate()
    print('Command output: %s' % stdout_data)
    if p.returncode != 0:
      raise RuntimeError('Command %s failed: exit code: %s' % (command_list, p.returncode))

  def run(self):
    for command in CUSTOM_COMMANDS:
      self.run_custom_command(command)


setup(name='code-search',
      description='Kubeflow Code Search Demo',
      url='https://www.github.com/kubeflow/examples',
      author='Google',
      author_email='sanyamkapoor@google.com',
      version=VERSION,
      license='MIT',
      packages=find_packages(),
      install_requires=install_requires,
      extras_require={},
      cmdclass={
          'build': Build,
          'CustomCommands': CustomCommands,
      })
