from setuptools import setup, find_packages
from pathlib import Path


def get_long_description():
    this_directory = Path(__file__).parent
    return (this_directory / "README.md").read_text()


setup(name='huskytools',
      version='0.2.0',
      description='Tools for interacting with the HuskyLens AI camera',
      long_description=get_long_description(),
      long_description_content_type='text/markdown',
      license='MIT',
      url='https://github.com/Andreasdahlberg/husky-tools',
      author='Andreas Dahlberg',
      author_email='andreas.dahlberg90@gmail.com',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3'
      ],
      keywords='huskylens face-recognition camera',
      packages=find_packages(),
      python_requires='>=3.8',
      install_requires=['pyserial>=3.4'],
      project_urls={
        'Bug Reports': 'https://github.com/Andreasdahlberg/husky-tools/issues',
        'Source': 'https://github.com/Andreasdahlberg/husky-tools/'
      }
      )
