from distutils.core import setup

desc = """\
InsteonLocal allows local (non-cloud) control of the Insteon Hub 2245-222
"""

setup(name='insteonlocal',
      version='0.1',
      py_modules=['insteonlocal'],
      author='phareous',
      author_email='mplong@gmail.com',
      url='https://github.com/phareous/insteonlocal',
      long_description=desc,
      data_files=[('', ['device_models.json', 'device_categories.json'])],
      requires=['requests', 'time', 'pprint', 'logging', 'logging.handlers', 'sys', 'json', 'collections'],
      provides=['insteonlocal']
      )
