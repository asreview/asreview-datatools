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
    name='asreview-statistics',
    version=versioneer.get_version(),
    cmd_class=versioneer.get_cmdclass(),
    description='Statistical tools for the ASReview project',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/msdslab/ASReview-statistics',
    author='Utrecht University',
    author_email='asreview@uu.nl',
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Pick your license as you wish
        'License :: OSI Approved :: Apache Software License',

        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='asreview statistics',
    packages=find_namespace_packages(include=['asreviewcontrib.*']),
    install_requires=[
        "asreview>=0.7"
    ],

    extras_require={
    },

    entry_points={
        "asreview.entry_points": [
            "stat = asreviewcontrib.statistics.entrypoint:StatEntryPoint",
        ]
    },

    project_urls={
        'Bug Reports':
            "https://github.com/asreview/ASReview-statistics/issues",
        'Source':
            "https://github.com/asreview/ASReview-statistics",
    },
)
