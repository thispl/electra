from setuptools import setup, find_packages

with open('requirements.txt') as f:
	install_requires = f.read().strip().split('\n')

# get version from __version__ variable in electra/__init__.py
from electra import __version__ as version

setup(
	name='electra',
	version=version,
	description='Electra',
	author='Abdulla',
	author_email='abdulla.pi@groupteampro.com',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
