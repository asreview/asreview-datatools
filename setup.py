from setuptools import setup, find_namespace_packages
from os import path
from io import open

import versioneer

fp_root = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(fp_root, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='asreview-datatools',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description=
    'Powerful command line tools for data handling in ASReview',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/asreview/asreview-datatools',
    author='Utrecht University',
    author_email='asreview@uu.nl',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    keywords='asreview datatools',
    packages=find_namespace_packages(include=['asreviewcontrib.*']),
    python_requires='>=3.7',
    install_requires=[
        "asreview>=1,<2",
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
