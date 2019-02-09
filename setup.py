from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='iptables_xt_recent_parser',
      version='0.4',
      description="Tool used for converting jiffies from iptables xt_recent into timestamps.",
      long_description=readme(),
      classifiers=['Development Status :: 5 - Production/Stable',
                  'License :: OSI Approved :: BSD License',
                  'Programming Language :: Python :: 2',
                  'Programming Language :: Python :: 3'],
      url='https://github.com/peppelinux/iptables_xt_recent_parser',
      author='Giuseppe De Marco',
      author_email='giuseppe.demarco@unical.it',
      license='BSD',
      scripts=['iptables_xt_recent_parser/iptables_xt_recent_parser.py'],
      packages=['iptables_xt_recent_parser'],
      install_requires=[],
     )
