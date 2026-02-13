# Synergistic Self-Correction (S2C): A Hierarchical Framework for Multi-Stage Reasoning and Error Recovery in Large Language Models

<div align="center">

[![arXiv](https://img.shields.io/badge/arXiv-2409.12345-b31b1b.svg)](https://arxiv.org/abs/2409.12345)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/release/python-380/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

*Empowering LLMs with metacognitive reasoning capabilities through structured self-correction*

</div>

---

## 🚀 Overview

**Synergistic Self-Correction (S2C)** is a novel hierarchical framework that endows Large Language Models with intrinsic metacognitive capabilities through a structured three-stage inference process. Our approach addresses the fundamental limitation of autoregressive generation where early reasoning errors propagate through subsequent steps.

### 🎯 Key Achievements
- **60% relative improvement** on GSM8K mathematical reasoning (31.2% → 49.9%)
- **71% relative improvement** on MATH dataset (12.4% → 21.3%)
- **Superior computational efficiency** compared to ensemble methods
- **Statistically significant improvements** across multiple reasoning benchmarks (p < 0.001)

---

## 📊 The S2C Framework

Our framework decomposes problem-solving into three distinct computational personas:

```
Input Problem → Generator → Critic → Synthesizer → Final Answer
                    ↓         ↓         ↓
               Initial    Critical   Refined
               Solution   Analysis   Solution
```

### 🧠 Three-Stage Process

1. **🔧 Generator**: Produces initial solutions with explicit critical point identification
2. **🔍 Critic**: Systematically analyzes potential errors and logical inconsistencies
3. **⚡ Synthesizer**: Integrates feedback to produce refined solutions

### 🏋️ Training Methodology: Cognitive Dissonance Training (CDT)

Our novel three-phase training approach:

1. **Phase 1**: Structural Alignment via Supervised Fine-Tuning
2. **Phase 2**: Specialized Reward Model Training
3. **Phase 3**: Hierarchical Process-Based Reward Optimization (HPBR)

---

## 📈 Results

### Mathematical Reasoning Performance

| Method | GSM8K | MATH | AQuA | MathQA | StrategyQA | CSQA | Average |
|--------|-------|------|------|--------|------------|------|---------|
| CoT Prompting | 31.2% | 12.4% | 23.7% | 18.9% | 68.9% | 72.1% | 37.9% |
| Self-Consistency | 38.7% | 15.2% | 28.4% | 22.1% | 73.4% | 75.3% | 42.2% |
| **S2C (Ours)** | **49.9%** | **21.3%** | **35.6%** | **28.4%** | **76.4%** | **78.1%** | **48.3%** |
| **Improvement** | **+60%** | **+71%** | **+50%** | **+50%** | **+11%** | **+8%** | **+27%** |

### 📊 Visualizations

<div align="center">
  <img src="graphs/gsm8k_main_results.pdf" alt="GSM8K Results" width="45%">
  <img src="graphs/training_performance_curves.pdf" alt="Training Curves" width="45%">
</div>

---

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- CUDA-compatible GPU (recommended)
- 16GB+ RAM

### Quick Start

```bash
# Clone the repository
git clone https://github.com/pratham/Self-Correcting-LLM-Research.git
cd Self-Correcting-LLM-Research

# Install dependencies
pip install -r requirements.txt

# Install additional packages
pip install torch transformers datasets peft trl bitsandbytes accelerate
```

### Hugging Face Authentication

```bash
# Login to Hugging Face
huggingface-cli login

# Or set environment variable
export HF_TOKEN="your_hf_token_here"
```

---

## 🚀 Usage

### Quick Evaluation

```bash
# Evaluate S2C model on GSM8K
python evaluate_s2c.py --model_path ./s2c_llama3_8b_final --dataset gsm8k

# Generate benchmark comparison
python benchmark_models.py
```

### Training from Scratch

```bash
# Phase 1: Supervised Fine-Tuning
python train_s2c_sft.py --config configs/sft_config.yaml

# Phase 2: Reward Model Training
python train_reward_models.py --config configs/reward_config.yaml

# Phase 3: PPO Training with HPBR
python train_s2c_rl.py --config configs/ppo_config.yaml
```

### Inference Example

```python
from src.s2c_model import S2CModel

# Load trained model
model = S2CModel.from_pretrained("./s2c_llama3_8b_final")

# Solve a math problem
problem = "Sarah has 3 apples. She buys 2 more apples and gives 1 to her friend. How many apples does Sarah have now?"
solution = model.solve_with_s2c(problem)

print(f"Problem: {problem}")
print(f"Solution: {solution}")
```

---

## 📁 Repository Structure

```
Self-Correcting-LLM-Research/
├── 📄 README.md                           # This file
├── 📋 requirements.txt                    # Python dependencies
├── 📜 LICENSE                            # MIT License
├── 🎯 .gitignore                         # Git ignore patterns
│
├── 📊 paper/                             # Research paper and documentation
│   ├── final_report_comprehensive.tex   # Complete LaTeX source
│   ├── final_report_comprehensive.pdf   # Final paper PDF
│   └── arxiv_submission.tar.gz          # ArXiv submission package
│
├── 🧠 src/                              # Source code
│   ├── models/                          # Model implementations
│   │   ├── s2c_model.py                # Main S2C framework
│   │   ├── generator.py                # Generation stage
│   │   ├── critic.py                   # Critique stage
│   │   └── synthesizer.py              # Synthesis stage
│   ├── training/                        # Training scripts
│   │   ├── sft_trainer.py              # Supervised fine-tuning
│   │   ├── reward_trainer.py           # Reward model training
│   │   └── ppo_trainer.py              # PPO with HPBR
│   ├── evaluation/                      # Evaluation utilities
│   │   ├── evaluator.py                # Model evaluation
│   │   └── metrics.py                  # Performance metrics
│   └── utils/                           # Utility functions
│       ├── data_utils.py               # Data processing
│       └── visualization.py            # Results visualization
│
├── 📊 graphs/                           # Generated visualizations
│   ├── s2c_framework_architecture.pdf  # Framework diagram
│   ├── gsm8k_main_results.pdf         # Main results chart
│   ├── training_performance_curves.pdf # Training curves
│   ├── ablation_study_results.pdf     # Ablation analysis
│   ├── error_analysis_comprehensive.pdf# Error analysis
│   ├── computational_efficiency.pdf    # Efficiency comparison
│   └── qualitative_s2c_example.pdf    # Example walkthrough
│
├── 📁 configs/                          # Configuration files
│   ├── sft_config.yaml                # SFT hyperparameters
│   ├── reward_config.yaml             # Reward model config
│   └── ppo_config.yaml                # PPO training config
│
├── 💾 models/                           # Trained models
│   ├── s2c_llama3_8b_final/           # Final S2C model
│   ├── s2c_llama3_8b_checkpoints/     # Training checkpoints
│   └── reward_models/                  # Trained reward models
│
├── 📊 data/                            # Datasets and preprocessed data
│   ├── gsm8k/                         # GSM8K dataset
│   ├── math/                          # MATH dataset
│   └── processed/                     # Preprocessed data
│
├── 🧪 experiments/                     # Experimental scripts
│   ├── ablation_studies.py           # Ablation experiments
│   ├── scaling_analysis.py           # Scaling behavior analysis
│   └── error_analysis.py             # Error pattern analysis
│
├── 📊 logs/                           # Training logs and metrics
│   ├── tensorboard/                  # TensorBoard logs
│   └── wandb/                        # Weights & Biases logs
│
└── 🧪 scripts/                       # Utility scripts
    ├── evaluate_s2c.py              # Model evaluation script
    ├── benchmark_models.py          # Benchmark comparison
    ├── train_s2c_rl.py             # PPO training script
    └── create_visualizations.py     # Generate paper figures
```

---

## 🔬 Reproducing Results

### Complete Reproduction Pipeline

```bash
# 1. Data Preparation
python scripts/prepare_datasets.py

# 2. Train S2C Model (Full Pipeline)
bash scripts/train_full_pipeline.sh

# 3. Evaluate on All Benchmarks
python scripts/evaluate_all_benchmarks.py

# 4. Generate Paper Figures
python scripts/create_visualizations.py

# 5. Run Ablation Studies
python experiments/ablation_studies.py
```

### Key Experimental Results

- **Ablation Study**: Each component contributes significantly to performance
- **Error Analysis**: 78% success rate on computational errors, 71% on missing steps
- **Efficiency Analysis**: 74% fewer resources than Self-Consistency with 29% higher accuracy
- **Statistical Significance**: All improvements confirmed with p < 0.001

---

## 📚 Citation

If you use this work in your research, please cite our paper:

```bibtex
@article{patel2024synergistic,
  title={Synergistic Self-Correction: A Hierarchical Framework for Multi-Stage Reasoning and Error Recovery in Large Language Models},
  author={Patel, Pratham and Jindal, Abhishek},
  journal={arXiv preprint arXiv:2409.12345},
  year={2024},
  institution={Dhirubhai Ambani Institute of Information and Communication Technology}
}
```

---

## 👥 Authors

**Pratham Patel** - Gannon University
📧 [patel292@gannon.edu](mailto:patel292@gannon.edu)

**Abhishek Jindal** - DA-IICT *(Corresponding Author)*
📧 [abhishek_jindal@daiict.ac.in](mailto:abhishek_jindal@daiict.ac.in)

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Student Research Initiative (SRI)** program at DA-IICT for funding and support
- **High Performance Computing facility** at DA-IICT for computational resources
- **Hugging Face** for model hosting and infrastructure
- **OpenAI** and **Anthropic** for inspiring the self-correction paradigm

---

## 📞 Contact & Support

- 🐛 **Issues**: [GitHub Issues](https://github.com/pratham/Self-Correcting-LLM-Research/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/pratham/Self-Correcting-LLM-Research/discussions)
- 📧 **Email**: [patel292@gannon.edu](mailto:patel292@gannon.edu)

---

<div align="center">
  <p><strong>⭐ If you find this work helpful, please consider starring the repository! ⭐</strong></p>
  <p><em>Advancing AI through metacognitive reasoning capabilities</em></p>
</div>
