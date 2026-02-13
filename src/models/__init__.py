"""
S2C Model Components

This module contains the core components of the Synergistic Self-Correction framework:
- S2CModel: Main model class implementing the three-stage process
- Generator: First stage for initial solution generation
- Critic: Second stage for solution analysis and error detection
- Synthesizer: Third stage for refined solution generation
"""

from .s2c_model import S2CModel
from .generator import Generator
from .critic import Critic
from .synthesizer import Synthesizer

__all__ = ["S2CModel", "Generator", "Critic", "Synthesizer"]