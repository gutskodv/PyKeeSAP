from setuptools import setup
import pykeesap

with open('requirements.txt') as f:
    required = f.read().splitlines()

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='PyKeeSAP',
    version=pykeesap.__version__,
    packages=['pykeesap'],
    url='https://github.com/gutskodv/PyKeeSAP',
    license='GPL v2',
    author='Dmitry Gutsko',
    author_email='gutskodv@gmail.com',
    description='SAP password manager with KeePass',
    long_description_content_type="text/markdown",
    long_description=long_description,
    entry_points={'console_scripts': ['pykeesap = pykeesap.commands:cmd', ], },
    install_requires=required,
    include_package_data=True
)
