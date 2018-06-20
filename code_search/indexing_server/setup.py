from setuptools import setup, find_packages

with open('requirements.txt', 'r') as f:
  install_requires = f.readlines()

VERSION = '0.1.0'

setup(name='code-search-index-server',
      description='Kubeflow Code Search Demo - Index Server',
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
          'nmslib-serve=nmslib_flask.cli:server',
          'nmslib-create=nmslib_flask.cli:creator',
        ]
      })
