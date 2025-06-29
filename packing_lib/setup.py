from setuptools import setup, find_packages

setup(
    name='packing_lib',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'opencv-python>=4.8.0',
        'opencv-contrib-python>=4.8.0',
        'ultralytics>=8.0.0',
        'pymunk>=6.0.0',
        'pygame>=2.0.0',
        'numpy>=1.20.0',
        'matplotlib>=3.5.0',
        'scipy>=1.7.0',
        'ortools>=9.0.0',
    ],
    author='Anis Sadykov',
    description='Library of two-dimensional orthogonal packing of rectangular objects.',
)