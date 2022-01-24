#!/usr/bin/env python3

from setuptools import find_packages, setup

setup(
    name="voipms_forward",
    version="1.0.0",
    description="VoIP.MS forwarding manager",
    author="Tris Emmy Wilson",
    author_email="tris@tris.fyi",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "flask",
        "requests",
    ],
)
