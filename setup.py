from setuptools import setup, find_packages

setup(
    name='pycloudmessenger',
    version='0.2.1',
    description='Package for interacting with messaging based cloud services from IBM Research Ireland',
    author='Mark Purcell',
    author_email='markpurcell@ie.ibm.com,mkpurcell@yahoo.com',
    license='Apache 2.0',
    packages=find_packages('.'),
    install_requires=[
        'pika==0.13.0'
    ],
    url='https://github.com/IBM/pycloudmessenger'
)
