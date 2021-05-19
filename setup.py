from distutils.core import setup

setup(
    name='Swit',
    packages=['Swit'],
    version='0.1',
    license='MIT',
    description='Swit is a basic open-source implementation of Git, meant for experimenting and studying Git\'s concepts and core design.',
    author='Noga Osin',
    author_email='nogaos97@gmail.com',
    url='https://github.com/NogaOs/Swit',
    download_url='https://github.com/user/reponame/archive/v_01.tar.gz',
    keywords=['git', 'version control', 'source control'],
    install_requires=[
        'wheel',
        'loguru',
        'networkx',
        'matplotlib',
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
