import os
from setuptools import setup, find_packages

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name = "Traffic Wizard",
    version="1.0.0",
    # packages=find_packages(),
    packages=['inst', 'src', 'tests'],
    install_requires=["Flask"],
    package_data={'src': ['*'], 'inst': ['SQL/*'], 'tests': ['*']},
    # package_data={'': ['*.sql', 'SQL/*.sql', 'templates/*.html', 'static/*.css']},
    include_package_data=True,
    entry_points={"console_scripts": ["app = src.app:main"]}
)