#!/usr/bin/env python
from setuptools import setup
LONG_DESCRIPTION = "Tool to sync a github repo based on a config file"

exec(open('dothub/_version.py').read())

try:
    # attempt to build a long description from README.md
    # run sudo apt-get install pandoc and pip install pypandoc first
    import pypandoc
    LONG_DESCRIPTION=pypandoc.convert('README.md', 'rst')
except (ImportError, RuntimeError, OSError):
    pass


setup(
    name='dothub',
    packages=['dothub'],
    version=__version__,
    description='Manage your github repo as code!',
    long_description=LONG_DESCRIPTION,
    author='Mario Corchero',
    author_email='mariocj89@gmail.com',
    url='https://github.com/Mariocj89/dothub',
    keywords=['configuration', 'github', 'code'],
    license='MIT',
    use_2to3=True,
    install_requires=['requests', 'click', 'github_token', 'pyyaml'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    entry_points={
        'console_scripts': [
            'dothub=dothub.__main__:main'
        ]
    },
)
