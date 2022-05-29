# based on https://github.com/pypa/sampleproject
# MIT License

# Always prefer setuptools over distutils
from setuptools import setup, find_namespace_packages
from os import path
from io import open

import versioneer

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='asreview-datatools',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description=
    'Powerful command line tools for reference management with ASReview',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/asreview/asreview-datatools',
    author='Utrecht University',
    author_email='asreview@uu.nl',
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Pick your license as you wish
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    keywords='asreview datatools',
    packages=find_namespace_packages(include=['asreviewcontrib.*']),
    install_requires=[
        "asreview",  # ~=1.0
        "pandas"
    ],
    extras_require={},
    entry_points={
        "asreview.entry_points": [
            "data = asreviewcontrib.datatools.entrypoint:DataEntryPoint",

            # TODO: find a trick to link this without displaying in asreview -h
            # "datatools = asreviewcontrib.datatools.entrypoint:DataEntryPoint",
        ]
    },
    project_urls={
        'Bug Reports': "https://github.com/asreview/asreview-datatools/issues",
        'Source': "https://github.com/asreview/asreview-datatools",
    },
)
