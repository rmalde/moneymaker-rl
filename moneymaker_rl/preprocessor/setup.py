# Third Party
from setuptools import find_packages, setup


setup(
    name="moneymaker_rl_preprocessor",
    version="0.1.0",
    description="Data preprocessing for Rocket League replays",
    author="rmalde",
    packages=find_packages(),
    install_requires=[
        "moneymaker_rl",  # Reference to root package
        "python-dotenv",
        "requests",
        "numba",
        "scipy",
        "pandas",
        "pyarrow",
        "rlgym[all]>=2.0.0rc0",
        "python-ballchasing",
        "rlgym-tools @ git+https://github.com/RLGym/rlgym-tools.git@v2",
    ],
    python_requires=">=3.7,<=3.9",
)
