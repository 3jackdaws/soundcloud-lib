from setuptools import setup

try:
    long_description = open("README.md").read()
except:
    long_description = ""


requirements = [
    'mutagen',
    'aiohttp'
]

setup(
    name='soundcloud-lib',
    version='0.6.1',
    description='Python Soundcloud API',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/3jackdaws/soundcloud-lib',
    author='Ian Murphy',
    author_email='3jackdaws@gmail.com',
    license='MIT',
    packages=['sclib'],
    python_requires='>=3.6',
    install_requires=requirements,
    test_suite='pytest',
    tests_require=['pytest', 'pytest-asyncio'],
)
