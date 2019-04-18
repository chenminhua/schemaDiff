from distutils.core import setup
import os

setup(
    name="schemaDiff",
    version="0.2",
    author="chenminhua",
    author_email="chenmhgo@gmail.com",
    license="GPL3",
    description="diff your mysql schema in different db",
    url="https://github.com/chenminhua/schemaDiff",
    packages=[

    ],
    scripts=['bin/schemaDiff'],
    install_requires=[
        'prettytable >= 0.7',
        'pymysql'
    ]
)
