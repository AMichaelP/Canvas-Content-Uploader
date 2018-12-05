import setuptools
setuptools.setup(
    name='Canvas Content Uploader',
    version='1.0',
    packages=setuptools.find_packages(),
    author='Anthony Michael Pruitt',
    description='A graphical desktop application to assist Canvas LMS course designers in quickly uploading, removing, '
                'and viewing course pages and files.',
    entry_points={
        'console_scripts': [
            'canvas_content_uploader = canvas_content_uploader.main:main'
        ]
    }
)
