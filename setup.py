import os
from setuptools import setup, find_packages

version = '0.1.dev0'

setup(name='i18ndude.autotranslate',
      version=version,
      description="Autotranslate",
      long_description=open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
          "Programming Language :: Python",
      ],
      keywords='i18ndude autotranslate',
      author='FBruynbroeck',
      author_email='francois.bruynbroeck@hotmail.com',
      url='https://github.com/FBruynbroeck/i18ndude.autotranslate',
      license='gpl',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['i18ndude', 'i18ndude.autotranslate'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'i18ndude',
          'bs4',
      ],
      entry_points={
          'console_scripts': [
              'autotranslate = i18ndude.autotranslate.autotranslate:main',
          ],
      }
      )
