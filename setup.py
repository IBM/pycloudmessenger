from setuptools import setup, find_packages

setup(
    name='pycloudmessenger',
    version='0.7.1',
    description='Package for interacting with messaging based cloud services from IBM Research Ireland',
    author='Mark Purcell',
    author_email='markpurcell@ie.ibm.com,mkpurcell@yahoo.com',
    license='Apache 2.0',
    packages=find_packages('.'),
    python_requires='>=3.6',
    install_requires=[
        'pika==0.13.0',
        'requests>=2.18.4',
        'jsonpickle',
        'tenacity'
    ],
    url='https://github.com/IBM/pycloudmessenger'
)
