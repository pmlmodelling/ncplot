from setuptools import Command, find_packages, setup

DESCRIPTION = "Automatic plotting of NetCDF files in Python"
LONG_DESCRIPTION = """


"""

PROJECT_URLS = {
    "Bug Tracker": "https://github.com/r4ecology/ncplot/issues",
    #"Documentation": "https://nctoolkit.readthedocs.io/en/stable",
    "Source Code": "https://github.com/r4ecology/ncplot",
}

REQUIREMENTS = [i.strip() for i in open("requirements.txt").readlines()]


setup(name='ncplot',
      version='0.0.1',
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      python_requires='>=3.6.1',
      classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],

      project_urls=PROJECT_URLS,
      url = "https://github.com/r4ecology/ncplot",
      author='Robert Wilson',
      maintainer='Robert Wilson',
      author_email='rwi@pml.ac.uk',

      packages = ["ncplot"],
      setup_requires=[
        'setuptools',
        'setuptools-git',
        'wheel',
    ],
      install_requires = REQUIREMENTS,
      zip_safe=False)




