from setuptools import setup

import overlay_arrows_and_more

with open("README.rst", "r") as fh:
    long_description = fh.read()

setup(
    name='overlay_arrows_and_more',
    version= overlay_arrows_and_more.__version__,
    packages=['overlay_arrows_and_more'],
    url='https://github.com/beuaaa/overlay_arrows_and_more',
    license='MIT',
    author='david pratmarty',
    author_email='david.pratmarty@gmail.com',
    description='overlay arrows and more',
    long_description=long_description,
    long_description_content_type="text/x-rst",
    install_requires=['pywin32, enum34, setuptools'],
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
