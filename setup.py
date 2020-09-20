import setuptools

setuptools.setup(
    name='flysight',
    version="0.0.1",
    author='CjHanks',
    author_email="web@cjhanks.name",
    description="Fly Tracker visualizer",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'matplotlib==3.3.0',
        'numpy==1.18.5',
        'opencv-python==4.4.0.42',
        'protobuf==3.12.4',
        'pyside2==5.14.0',
        'pyyaml==5.3.1',
        'pyzmq==19.0.2',
        'tensorflow==2.3.0',
    ],
    entry_points = {
        'console_scripts': ['flysight=flysight.run:main'],
    },
    data_files=[

        ('flysight', [
            'flysight/config.yml'
        ]),
        ('flysight/client/resource',    [
            'flysight/client/resource/lcd.css',
            'flysight/client/resource/slider.css'
        ]),
    ],
    python_requires='>=3.6',
    zip_safe=False,
)
