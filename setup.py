from setuptools import find_packages, setup

setup(
    name='gm_datatools',
    packages=find_packages(include=['gm_datatools']),
    version='0.1.0',
    description='gm systematic macro lib',
    author='Ryan Yost',
    license='',
    install_requires=[],
    setup_requires=['pytest-runner', 'pandas'],
    tests_require=['pytest==4.4.1', 'pandas'],
    test_suite='tests',
)

