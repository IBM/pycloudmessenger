from setuptools import setup

setup(
    name='cloud-messaging',
    version='0.1.0',
    description='Package for interacting with messaging based cloud services from IBM Research Ireland',
    author='Mark Purcell',
    author_email='markpurcell@ie.ibm.com,mkpurcell@yahoo.com',
    license='MIT',
    packages=['rabbitmq, mqtt'],
    install_requires=[
        'pika==0.13.0'
    ],
    url='https://github.com/IBM/castor-messaging'
)
