from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='iptables_xt_recent_parser',
      version='0.6.0-1',
      description=("Tool used for converting jiffies from iptables "
                   "xt_recent into timestamps."),
      long_description=readme(),
      long_description_content_type='text/markdown',
      classifiers=['Development Status :: 5 - Production/Stable',
                   'License :: OSI Approved :: BSD License',
                   'Programming Language :: Python :: 3'],
      url='https://github.com/peppelinux/iptables_xt_recent_parser',
      author='Giuseppe De Marco',
      author_email='giuseppe.demarco@unical.it',
      license='BSD',
      scripts=['iptables_xt_recent_parser/ipt_recents'],
      #packages=['iptables_xt_recent_parser'],
      install_requires=[],
     )
