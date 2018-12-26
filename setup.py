import io
import re
from setuptools import setup

try:
    with open('README.md') as f:
        readme = f.read()
except IOError:
    readme = ''


with io.open('doccov/__init__.py', 'rt', encoding='utf8') as f:
    version = re.search(r'__version__ = \'(.*?)\'', f.read()).group(1)


def _requires_from_file(filename):
    return open(filename).read().splitlines()


setup(
    name='doc-cov',
    version=version,
    url='https://github.com/cocodrips/doc-cov',
    license='MIT',
    author='ku-mu',
    author_email='cocodrips@gmail.com',
    description='doc-cov is a tool for measuring docstring coverage of Python project',
    long_description=readme,
    long_description_content_type='text/markdown',
    packages=['doccov'],
    include_package_data=True,
    python_requires='>=3.6',
    install_requires=[],
    extras_require={
        'dev': [
            'pytest>=3',
        ],
    },
    entry_points={
        'console_scripts': [
            'doccov = doccov.main:entry_point',
        ],
    },
)