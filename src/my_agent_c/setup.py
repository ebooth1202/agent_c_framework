from setuptools import setup, find_namespace_packages

setup(
    name="my_agent_c",
    packages=find_namespace_packages(include=["agent_c.*"]),
    package_dir={'': 'src'},
    author="Centric Consulting",
    author_email="email@centricconsulting.com",
    description="Your personal Agent C playground",
    long_description=open('README.md').read(),
    long_description_content_type="text_iter/markdown",
    url="https://github.com/centricconsulting/agent_c",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10',
)

