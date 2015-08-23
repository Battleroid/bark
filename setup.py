from setuptools import setup, find_packages

setup(
        name='bark-ssg',
        version='1.0',
        url='https://github.com/battleroid/bark',
        description='Single file static site generator.',
        license='MIT License',
        keywords='bark static site generator jinja blog python markdown',
        author='Casey Weed',
        author_email='me@caseyweed.net',
        download_url='https://github.com/battleroid/bark/tarball/master',
        packages = find_packages(),
        install_requires=[
            'Jinja2>=2.8',
            'python-frontmatter>=0.2.1',
            'python-slugify>=1.1.3',
            'python-dateutil>=2.4.2',
            'misaka>=1.0.2'
            ],
        setup_requires=[],
        entry_points={
            'console_scripts': ['bark = bark.bark:main']
            },
        platforms=['any'],
        classifiers=[
            'Programming Language :: Python',
            'Topic :: Internet',
            'Topic :: Internet :: WWW/HTTP :: Site Management',
            'Topic :: Text Processing',
            'Topic :: Text Processing :: Markup',
            'Topic :: Text Processing :: Markup :: HTML'
            ]
        )
