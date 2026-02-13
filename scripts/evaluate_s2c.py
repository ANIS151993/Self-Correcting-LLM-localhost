# --- evaluate_s2c.py (To be run AFTER training is complete) ---

import torch
import os
import re
import time
import matplotlib.pyplot as plt
from tqdm import tqdm

from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel
from datasets import load_dataset

# --- 1. CONFIGURATION ---
HF_TOKEN = "HUGGING_FACE_TOKEN"
BASE_MODEL_ID = "meta-llama/Meta-Llama-3-8B-Instruct"

# --- Define all the models/adapters you want to test ---
MODELS_TO_BENCHMARK = {
    "Llama-3-8B-Instruct (Base)": BASE_MODEL_ID,
    "S2C Checkpoint (Step 200)": "s2c_llama3_8b_checkpoints/step_200",
    "S2C Final Model": "s2c_llama3_8b_final"
}

# --- Benchmark Settings ---
DATASET_ID = "gsm8k"
DATASET_CONFIG = "main"
NUM_SAMPLES = 50 # Use a larger sample size for more reliable results
OUTPUT_PLOT_FILE = "s2c_benchmark_results.png"

# --- 2. PROMPT & HELPER FUNCTIONS ---
def build_eval_prompt(question: str) -> str:
    # Use the same prompt structure you trained with
    return f"""You are a hyper-intelligent AI that solves math problems through a rigorous, three-step process: Generate, Critique, and Synthesize.
### INSTRUCTIONS ###
1.  **Generate:** Provide a step-by-step solution. Label your reasoning steps as "Critical Points".
2.  **Critique:** Review your own solution. Find potential flaws or unstated assumptions in your "Critical Points".
3.  **Synthesize:** Produce a final, verified answer. State the final numerical result clearly inside "#### <number>".
### PROBLEM ###
{question}
### RESPONSE ###"""

def extract_final_answer(text: str) -> str:
    matches = re.findall(r'####\s*(-?\d+\.?\d*)', text)
    return matches[-1] if matches else None

def load_and_benchmark_model(model_name, model_path, dataset, num_samples, token):
    print("\n" + "="*50)
    print(f"> Loading Model: {model_name}")
    start_time = time.time()
    
    quantization_config = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.bfloat16)
    
    # Load the base model
    base_model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL_ID, quantization_config=quantization_config,
        device_map="auto", token=token
    )
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_ID, token=token)
    tokenizer.pad_token = tokenizer.eos_token

    # If the path is not the base model, it must be a PEFT adapter
    if model_path != BASE_MODEL_ID:
        print(f"> Applying LoRA adapter from: {model_path}")
        model = PeftModel.from_pretrained(base_model, model_path)
    else:
        model = base_model # It's just the base model

    load_time = time.time() - start_time
    print(f"> Successfully loaded in {load_time:.2f} seconds.")
    
    # Run benchmark
    correct_answers = 0
    print(f"> Benchmarking on {num_samples} samples...")
    for i in tqdm(range(num_samples)):
        example = dataset[i]
        question = example['question']
        true_answer_text = example['answer']
        # The true answer for gsm8k is always in the #### format.
        true_answer = re.findall(r'####\s*(-?\d+\.?\d*)', true_answer_text)[-1]

        prompt = build_eval_prompt(example['question'])
        inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
        
        output_ids = model.generate(**inputs, max_new_tokens=600, pad_token_id=tokenizer.eos_token_id)
        generated_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)
        
        model_answer = extract_final_answer(generated_text)
        if model_answer and true_answer and float(model_answer) == float(true_answer):
            correct_answers += 1
            
    # Clean up memory
    del model
    del base_model
    torch.cuda.empty_cache()
    
    return correct_answers

def plot_results(results, num_samples):
    # (Plotting function is the same as your original benchmark script)
    model_names = list(results.keys())
    scores = list(results.values())
    plt.style.use('seaborn-v0_8-darkgrid')
    fig, ax = plt.subplots(figsize=(12, 8))
    colors = ['#4C72B0', '#55A868', '#C44E52', '#8172B2']
    bars = ax.bar(model_names, scores, color=colors[:len(model_names)])
    ax.set_ylabel(f'Correct Answers (out of {num_samples})', fontsize=12)
    ax.set_title('S2C Model Performance on GSM8K', fontsize=16, pad=20)
    ax.set_ylim(0, max(scores) * 1.2 if scores else 10)
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height}', xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points",
                    ha='center', va='bottom', fontsize=12)
    plt.xticks(rotation=10, ha='center')
    plt.tight_layout()
    plt.savefig(OUTPUT_PLOT_FILE)
    print(f"\n✅ Benchmark plot saved to '{OUTPUT_PLOT_FILE}'")

# --- 3. MAIN EXECUTION ---
if __name__ == "__main__":
    gsm8k_test = load_dataset(DATASET_ID, DATASET_CONFIG, split='test')
    benchmark_scores = {}

    for model_name, model_path in MODELS_TO_BENCHMARK.items():
        score = load_and_benchmark_model(model_name, model_path, gsm8k_test, NUM_SAMPLES, HF_TOKEN)
        benchmark_scores[model_name] = score
        print(f"> Result for {model_name}: {score}/{NUM_SAMPLES} correct.")

    print("\n--- Final Benchmark Scores ---")
    for model_id, score in benchmark_scores.items():
        print(f"{model_id}: {score}/{NUM_SAMPLES}")

    plot_results(benchmark_scores, NUM_SAMPLES)
    print("-" * 50)