from setuptools import setup, find_packages

with open('requirements.txt', 'r') as f:
  install_requires = f.readlines()

VERSION = '0.0.1'

setup(name='code-search',
      description='Kubeflow Code Search Demo',
      url='https://www.github.com/kubeflow/examples',
      author='Sanyam Kapoor',
      author_email='sanyamkapoor@google.com',
      version=VERSION,
      license='MIT',
      packages=find_packages(),
      install_requires=install_requires,
      extras_require={},
      entry_points={
        'console_scripts': [
          'nmslib-serve=code_search.nmslib.cli:server',
          'nmslib-create=code_search.nmslib.cli:creator',
        ]
      })
