# Third Party
from setuptools import find_packages, setup


setup(
    name="moneymaker_rl_trainer",
    version="0.1.0",
    description="Training models from Rocket League replay data",
    author="rmalde",
    packages=find_packages(),
    install_requires=[
        "moneymaker_rl",  # Reference to root package
        "wandb",
        "scikit-learn",
        "matplotlib",
        "seaborn",
    ],
    python_requires=">=3.7,<=3.9",
)
