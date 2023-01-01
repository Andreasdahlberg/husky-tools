from setuptools import setup, find_packages

setup(name='huskytools',
      version='0.1.0',
      description='Tools for interacting with the HuskyLens AI camera',
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
      python_requires='>=3',
      install_requires=['pyserial>=3'],
      project_urls={
        'Bug Reports': 'https://github.com/Andreasdahlberg/husky-tools/issues',
        'Source': 'https://github.com/Andreasdahlberg/husky-tools/'
      }
      )
