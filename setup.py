from setuptools import setup


setup(
    name='psf_star_pedestal',
    version='0.0.1',
    description='Estimate the optical PSF from a star passage through the camera',
    url='http://github.com/fact-project/psf_star_pedestal',
    author='Maximilian Nöthe',
    author_email='maximilian.noethe@tu-dortmund.de',
    license='MIT',
    packages=[
        'psf_star_pedestal',
    ],
    install_requires=[
        'numpy',
        'scipy',
        'pandas',
        'astropy',
        'matplotlib>=2.0',
        'pyfact>=0.10',
    ],
    entry_points={
        'console_scripts': [
            'star_pedestal_fit_psf=psf_star_pedestal.scripts.fit_psf:main'
        ]
    },
    zip_safe=False,
)
