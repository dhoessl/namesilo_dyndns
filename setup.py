from setuptools import setup

setup(
    name='namesilo_dyndns',
    version='0.1-1',
    description='A Tool to set up a dyndns using the namesilo python api',
    url='https://github.com/dhoessl/namesilo_dyndns',
    author="Dominic Hößl",
    author_email="dominichoessl@gmail.com",
    license="",
    packages=['namesilo_dyndns'],
    install_requires=[
        "requests",
        "logging",
        "PyYAML",
        "python_namesilo_api"
    ],
    dependency_links=[
        "git+https://github.com/dhoessl/python_namesilo_api"
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
    ]
)
