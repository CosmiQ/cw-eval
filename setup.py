from setuptools import setup, find_packages

with open('cw_eval/__init__.py') as f:
    for line in f:
        if line.find("__version__") >= 0:
            version = line.split("=")[1].strip()
            version = version.strip('"')
            version = version.strip("'")
            continue


readme = ''

# Runtime requirements.
inst_reqs = ["shapely", "rtree", "tqdm", "geopandas", "pandas"]


extra_reqs = {
    'test': ['mock', 'pytest', 'pytest-cov', 'codecov']}

setup(name='cw_eval',
      version=version,
      description=u"""Provide Evaluation Metrics for Machine Learning Challenges""",
      long_description=readme,
      classifiers=[
          'Intended Audience :: Information Technology',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: BSD License',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 2.7',
          'Topic :: Scientific/Engineering :: GIS'],
      keywords='spacenet machinelearning iou aws',
      author=u"David Lindenbaum",
      author_email='dlindenbaum@iqt.org',
      url='https://github.com/CosmiQ/cw_eval',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      zip_safe=False,
      install_requires=inst_reqs,
      extras_require=extra_reqs)