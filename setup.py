from distutils.core import setup

setup(
    name='bkrdoc',
    version='1.0',
    packages=['bkrdoc', 'bkrdoc.markup', 'bkrdoc.analysis'],
    url='https://github.com/rh-lab-q/bkrdoc',
    license='BSD',
    author='Jiri Kulda',
    author_email='Kulda12@seznam.cz, jkulda@redhat.com',
    description='This project aims to provide tools for automated documentation generation for BeakerLib tests. '
)
