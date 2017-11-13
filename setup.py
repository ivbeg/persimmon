__author__ = "Ivan Begtin (ibegtin@gmail.com)"
__version__ = "1.0.1"
__copyright__ = "Copyright (c) 2017 Ivan Begtin"
__license__ = "MPL"

from setuptools import setup, find_packages



setup(name='persimmon',
      version='1.0',
      description='Python Persimmon module',
      author='Ivan Begtin',
      author_email='ibegtin@gmail.com',
      url='',
      download_url='',
      packages=find_packages(),
      license='MPL',
      keywords='persimmon unstructured',
      classifiers=["Development Status :: 3 - Alpha",
                   "Intended Audience :: Developers",
                   "Intended Audience :: Science/Research",
                   "License :: OSI Approved :: MIT License",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python",
                   "Topic :: Software Development :: Libraries :: Python Modules"
                   ], requires=['lxml', 'html5lib', 'bs4'],

     )
