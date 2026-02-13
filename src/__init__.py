"""
Synergistic Self-Correction (S2C) Framework

A hierarchical framework for multi-stage reasoning and error recovery in Large Language Models.
"""

__version__ = "1.0.0"
__author__ = "Pratham Patel, Abhishek Jindal"
__email__ = "patel292@gannon.edu"

from .models import S2CModel
from .training import S2CTrainer, RewardTrainer, PPOTrainer
from .evaluation import S2CEvaluator
from .utils import DataUtils, VisualizationUtils

__all__ = [
    "S2CModel",
    "S2CTrainer",
    "RewardTrainer",
    "PPOTrainer",
    "S2CEvaluator",
    "DataUtils",
    "VisualizationUtils"
]