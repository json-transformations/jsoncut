from setuptools import setup

setup(
    name='jsoncut',
    author='Brian Peterson',
    author_email='bpeterso2000@yahoo.com',
    version='0.6dev',
    url='http://github.com/bpeterso2000/jsoncut',
    packages=['jsoncut'],
    description='A JSON inspection & pruning tool.',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],
    install_requires=[
        'boltons>=18',
        'click>=6.7',
        'colorama>=0.3.9',
        'pygments>=2.2'
    ],
    entry_points={
        'console_scripts': [
            'jsoncut=jsoncut.cli:main'
        ]
    }
)
