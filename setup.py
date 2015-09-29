from distutils.core import setup

setup(
    name='bkrdoc',
    version='1.2',
    packages=['bkrdoc', 'bkrdoc.markup', 'bkrdoc.analysis'],
    url='https://github.com/rh-lab-q/bkrdoc',
    license='BSD',
    author='Jiri Kulda',
    author_email='Kulda12@seznam.cz, jkulda@redhat.com',
    description='This project aims to provide tools for automated documentation generation for BeakerLib tests. ',
    classifiers=["Programming Language :: Python",
                 "Programming Language :: Python :: 3",
                 "License :: OSI Approved :: BSD License",
                 "Development Status :: 4 - Beta",
                 "Topic :: Software Development :: Testing",
                 "Topic :: Software Development :: Documentation",
                 "Operating System :: OS Independent",
                 "Intended Audience :: Developers"]
)
