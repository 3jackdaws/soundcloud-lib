from setuptools import setup


setup(
    name='soundcloud-lib',
    version='0.1.0',
    description='Python Soundcloud API',
    url='https://github.com/3jackdaws/soundcloud-lib',
    author='Ian Murphy',
    author_email='3jackdaws@gmail.com',
    license='MIT',
    packages=['sclib'],
    install_requires=['mutagen'],
    test_suite='pytest',
    tests_require=['pytest'],
)