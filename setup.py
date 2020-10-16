import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()
REQUIREMENTS = (HERE / "requirements.txt").read_text().split('\n')

setup(
    name='nordvpn-connect',
    version='0.0.6',
    packages=['nordvpn_connect'],
    package_data={'nordvpn_connect': ['NordVPN_options/*.txt']},
    url='https://github.com/sorasful/nordvpn-connect',
    license='MIT',
    author='Sorasful',
    author_email='',
    description='A Python library to connect to NordVPN, works on Windows and Linux',
    long_description=README,
    long_description_content_type="text/markdown",
    install_requires=REQUIREMENTS,
)
