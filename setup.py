from setuptools import setup

setup(
    name='jsoncut',
    author='Brian Peterson',
    author_email='bpeterso2000@yahoo.com',
    version='0.2.0',
    url='http://github.com/bpeterso2000/jsoncut',
    packages=['jsoncut'],
    description='A JSON inspection & pruning tool.',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],
    install_requires=['click'],
    extras_require={
        'colors': ['colorama'],
        'json_higlighting': ['pygments']
    },
    entry_points={
        'console_scripts': ['jsoncut=jsoncut.cli:main']
    }
)
