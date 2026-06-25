from setuptools import setup, find_packages

setup(
    name='gcloudui',
    version='1.0.0',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'gcloudui=gcloudui.main:main',
        ],
    },
    author='Nama Kamu',
    description='GUI mini untuk mempermudah gcloud CLI',
)