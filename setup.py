from setuptools import setup, find_packages

setup(
    name="music-track-generator",
    version="0.1.0",
    description="GCP-powered music track generation with CLI interface",
    author="GitHub Dev Sandbox",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "google-cloud-aiplatform>=1.38.0",
        "google-auth>=2.23.0",
        "click>=8.1.7",
        "pydantic>=2.5.0",
        "pyyaml>=6.0.1",
        "rich>=13.7.0",
        "python-dotenv>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "music-gen=music_generator.cli:main",
        ],
    },
    python_requires=">=3.9",
)
