from pkg_resources import parse_requirements
from setuptools import setup, find_packages


def load_requirements(fname: str) -> list:
    requirements = []
    with open(fname, 'r', encoding='utf-8') as fp:
        for req in parse_requirements(fp.read()):
            extras = '[{}]'.format(','.join(req.extras)) if req.extras else ''
            requirements.append(
                '{}{}{}'.format(req.name, extras, req.specifier)
            )
    return requirements


setup(
    name='class-based-fastapi',
    version='1.0.4',
    author='XDeepZeroX',
    license='MIT',
    description='Class based routing for FastAPI',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url='https://github.com/XDeepZeroX/class-based-fastapi',
    platforms='all',
    keywords=["FastAPI", "Class", "Instance", "Routing"],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        "Framework :: FastAPI",
        "Framework :: AsyncIO",
        'Operating System :: OS Independent',
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3 :: Only",
        'Topic :: Internet :: WWW/HTTP',
        "Topic :: Internet :: WWW/HTTP :: Session",
        "Typing :: Typed",
    ],
    python_requires='>=3.8, <4',
    packages=find_packages(exclude=['tests']),
    install_requires=load_requirements('requirements.txt'),
    extras_require={
        'dev': load_requirements('requirements.dev.txt'),
        'docs': load_requirements('requirements.docs.txt'),
        'test': load_requirements('requirements.test.txt'),
        'all': load_requirements('requirements.txt') +
               load_requirements('requirements.dev.txt') +
               load_requirements('requirements.docs.txt') +
               load_requirements('requirements.test.txt'),
    },
    # entry_points={
    #     'console_scripts': [
    #         '{0}-api = {0}.api.__main__:main'.format(module_name),
    #         '{0}-db = {0}.db.__main__:main'.format(module_name)
    #     ]
    # },
    include_package_data=True
)
