from setuptools import find_packages, setup

setup(
    name='museum_app',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=False,
    zip_safe=False,
    install_requires=[
        'flask', 'graphene', 'mongoengine', 'werkzeug'
    ],
)