# Setup Guide for S2C Framework

This guide will help you set up the Synergistic Self-Correction (S2C) framework for research and development.

## 🛠️ Prerequisites

### Hardware Requirements
- **GPU**: NVIDIA GPU with CUDA support (recommended: RTX 3090/4090 or A100)
- **Memory**: 16GB+ RAM, 24GB+ GPU memory for full model training
- **Storage**: 50GB+ free space for models and datasets

### Software Requirements
- **Python**: 3.8 or higher
- **CUDA**: 11.8 or 12.1 (compatible with PyTorch)
- **Git**: For cloning repositories
- **conda** or **virtualenv**: For environment management

## 🚀 Quick Setup

### 1. Clone Repository

```bash
git clone https://github.com/ANIS151993/Self-Correcting-LLM-localhost.git
cd Self-Correcting-LLM-localhost
```

### 2. Create Environment

Using conda (recommended):
```bash
conda create -n s2c python=3.10
conda activate s2c
```

Using virtualenv:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Install PyTorch with CUDA support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Install core dependencies
pip install -r requirements.txt

# Install additional development tools
pip install pre-commit wandb jupyterlab
```

### 4. Set Up Pre-commit Hooks

```bash
pre-commit install
```

### 5. Configure Hugging Face Authentication

```bash
# Login to Hugging Face
huggingface-cli login

# Or set environment variable
echo "export HF_TOKEN='your_token_here'" >> ~/.bashrc
source ~/.bashrc
```

### 6. Verify Installation

```bash
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
python -c "from src import S2CModel; print('S2C import successful')"
```

## 🔧 Detailed Setup Instructions

### Environment Variables

Create a `.env` file in the project root:

```bash
# Required
HF_TOKEN=your_huggingface_token

# Optional
WANDB_API_KEY=your_wandb_key
WANDB_PROJECT=s2c_framework
CUDA_VISIBLE_DEVICES=0
PYTHONPATH=/path/to/Self-Correcting-LLM-Research
```

### Download Required Models

```bash
# Download base model (cached locally)
python -c "from transformers import AutoTokenizer; AutoTokenizer.from_pretrained('meta-llama/Meta-Llama-3-8B-Instruct')"
```

### Prepare Datasets

```bash
# Download and prepare GSM8K dataset
python scripts/prepare_datasets.py --dataset gsm8k

# Download MATH dataset
python scripts/prepare_datasets.py --dataset math

# Verify data preparation
ls -la data/gsm8k/
ls -la data/math/
```

## 📊 Configuration

### Model Configuration

Edit `configs/sft_config.yaml` for your setup:

```yaml
model:
  base_model: "meta-llama/Meta-Llama-3-8B-Instruct"
  load_in_4bit: true  # Set to false if you have enough GPU memory

training:
  per_device_train_batch_size: 1  # Adjust based on GPU memory
  gradient_accumulation_steps: 16  # Increase if reducing batch size
```

### GPU Memory Optimization

For limited GPU memory:

```yaml
# Enable memory optimizations
model:
  load_in_4bit: true
  bnb_4bit_compute_dtype: "float16"
  bnb_4bit_quant_type: "nf4"

training:
  per_device_train_batch_size: 1
  gradient_accumulation_steps: 32
  dataloader_pin_memory: false
  dataloader_num_workers: 0
```

## 🧪 Verification Tests

### Test Model Loading

```python
from src.models import S2CModel

# Load model
model = S2CModel(base_model_name="meta-llama/Meta-Llama-3-8B-Instruct")
print("✅ Model loaded successfully")

# Test inference
problem = "What is 2 + 2?"
result = model.solve_with_s2c(problem)
print(f"✅ Inference test: {result['final_answer']}")
```

### Test Training Pipeline

```bash
# Quick training test (1 step)
python scripts/test_training.py --max_steps 1 --output_dir ./test_output
```

### Run Evaluation

```bash
# Test evaluation on small sample
python scripts/evaluate_s2c.py --model_path ./models/s2c_llama3_8b_final --num_samples 10
```

## 🐛 Troubleshooting

### Common Issues

#### CUDA Out of Memory
```bash
# Reduce batch size and enable optimizations
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:128
```

#### Hugging Face Authentication
```bash
# Re-authenticate
huggingface-cli logout
huggingface-cli login
```

#### Model Loading Errors
```python
# Check model availability
from transformers import AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3-8B-Instruct")
print("✅ Model accessible")
```

#### Import Errors
```bash
# Ensure proper PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/path/to/Self-Correcting-LLM-Research"
pip install -e .
```

### Memory Requirements by Configuration

| Configuration | GPU Memory | Training Speed | Accuracy |
|---------------|------------|----------------|----------|
| Full FP16 | 24GB+ | Fast | Best |
| 8-bit | 16GB | Medium | Good |
| 4-bit | 12GB | Slow | Acceptable |

### Performance Optimization

#### For Training:
```bash
# Use mixed precision
export CUDA_LAUNCH_BLOCKING=1
export TORCH_USE_CUDA_DSA=1
```

#### For Inference:
```python
# Enable optimizations
torch.backends.cuda.matmul.allow_tf32 = True
torch.backends.cudnn.allow_tf32 = True
```

## 📈 Monitoring and Logging

### Weights & Biases Setup

```bash
# Install and login
pip install wandb
wandb login

# Configure project
wandb init --project s2c_framework
```

### TensorBoard Setup

```bash
# Start TensorBoard
tensorboard --logdir ./logs/tensorboard --port 6006
```

### Log Analysis

```bash
# View training logs
tail -f logs/training.log

# Monitor GPU usage
watch -n 1 nvidia-smi
```

## 🔄 Next Steps

After successful setup:

1. **Train Models**: `bash scripts/train_full_pipeline.sh`
2. **Evaluate Results**: `python scripts/evaluate_all_benchmarks.py`
3. **Analyze Performance**: `jupyter lab notebooks/analysis.ipynb`
4. **Generate Visualizations**: `python scripts/create_visualizations.py`

## 💡 Tips for Development

- **Use tmux/screen** for long training sessions
- **Monitor GPU memory** with `nvidia-smi`
- **Set up automated backups** for model checkpoints
- **Use wandb** for experiment tracking
- **Profile code** with PyTorch Profiler for optimization

## 📞 Getting Help

If you encounter issues:

1. **Check logs**: `./logs/setup.log`
2. **Search issues**: GitHub Issues tab
3. **Ask questions**: GitHub Discussions
4. **Contact authors**: [patel292@gannon.edu](mailto:patel292@gannon.edu)

## 📋 Setup Checklist

- [ ] Python 3.8+ installed
- [ ] CUDA toolkit installed
- [ ] Repository cloned
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] Hugging Face authentication configured
- [ ] Environment variables set
- [ ] Pre-commit hooks installed
- [ ] Model loading verified
- [ ] GPU memory sufficient
- [ ] Datasets downloaded
- [ ] Configuration files customized
- [ ] Test training completed
- [ ] Evaluation pipeline tested

---

*Setup complete! You're ready to train and evaluate S2C models. 🚀*