from setuptools import setup

import os.path
import sys


# We need the path to setup.py to be able to run
# the setup from a different folder
def setup_path(path=""):
    # get the path to the setup file
    setup_path = os.path.abspath(os.path.split(__file__)[0])

    return os.path.join(setup_path, path)


# add it to the system path
sys.path.append(setup_path())

if sys.platform == 'win32':
    install_requires = ['enum34']
    try:
        import win32api # check if it was already installed manually
    except ImportError:
        install_requires.append('pywin32')

with open("README.rst", "r") as fh:
    long_description = fh.read()

setup(
    name='overlay_arrows_and_more',
    version='0.3.9',
    packages=['overlay_arrows_and_more'],
    url='https://github.com/beuaaa/overlay_arrows_and_more',
    license='MIT',
    author='david pratmarty',
    author_email='david.pratmarty@gmail.com',
    description='overlay arrows and more',
    long_description=long_description,
    long_description_content_type="text/x-rst",
    install_requires=install_requires,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: Win32 (MS Windows)',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: User Interfaces',
        'Topic :: Software Development :: Testing',
    ]
)
