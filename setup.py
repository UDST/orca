from setuptools import setup, find_packages

# read README as the long description
with open('README.rst', 'r') as f:
    long_description = f.read()

setup(
    name='orca',
    version='1.7',
    description='Python library for task orchestration',
    long_description=long_description,
    author='UrbanSim Inc.',
    author_email='info@urbansim.com',
    license='BSD',
    url='https://github.com/udst/orca',
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'License :: OSI Approved :: BSD License'
    ],
    packages=find_packages(exclude=['*.tests']),
    install_requires=[
        'pandas >= 0.15.0',
        'tables >= 3.1',
        'toolz >= 0.8.1'
    ]
)
