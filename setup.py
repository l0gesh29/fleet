from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in fleet/__init__.py
from fleet import __version__ as version

setup(
	name="fleet",
	version=version,
	description="Fleet Management",
	author="Shivansh",
	author_email="shivansh@simpel.in",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
