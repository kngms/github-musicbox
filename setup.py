from setuptools import setup, find_packages

setup(
    name="music-track-generator",
    version="0.1.0",
    description="Music track generation with CLI and API interface",
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
        "fastapi>=0.109.0",
        "uvicorn[standard]>=0.27.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "httpx>=0.26.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "music-gen=music_generator.cli:main",
        ],
    },
    python_requires=">=3.9",
)
