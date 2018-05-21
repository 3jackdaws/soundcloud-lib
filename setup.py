from setuptools import setup


setup(
    name='soundcloud-lib',
    version='0.3.3',
    description='Python Soundcloud API',
    url='https://github.com/3jackdaws/soundcloud-lib',
    author='Ian Murphy',
    author_email='3jackdaws@gmail.com',
    license='MIT',
    packages=['sclib'],
    python_requires='>=3.6',
    install_requires=['mutagen', 'bs4'],
    test_suite='pytest',
    tests_require=['pytest', 'pytest-asyncio'],
)