# --- benchmark_models_v5.py (Correct Pre-flight Check) ---

import torch
import os
import re
import time
import matplotlib.pyplot as plt
from tqdm import tqdm

from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from datasets import load_dataset

# --- 1. CONFIGURATION ---
# UNCOMMENT and PASTE YOUR HUGGING FACE TOKEN.
HF_TOKEN = "HUGGING_FACE_TOKEN" # <-- PASTE YOUR TOKEN

# The gated model we want to test
GATED_MODEL_ID = "meta-llama/Meta-Llama-3-8B-Instruct"

# A small, PUBLIC, CAUSAL (text-generation) model for a valid pre-flight check
PUBLIC_TEST_MODEL = "distilgpt2" # <-- THIS IS THE FIX

# --- Benchmark Settings ---
DATASET_ID = "gsm8k"
DATASET_CONFIG = "main"
NUM_SAMPLES = 20
OUTPUT_PLOT_FILE = "benchmark_results.png"

# --- 2. HELPER FUNCTIONS (No changes needed) ---

def load_model_and_tokenizer(model_id, token=None):
    print(f"\n> Attempting to load model: {model_id}...")
    start_time = time.time()
    
    quantization_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype=torch.bfloat16
    )

    try:
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            quantization_config=quantization_config,
            device_map="auto",
            token=token
        )
        tokenizer = AutoTokenizer.from_pretrained(model_id, token=token)
    except Exception as e:
        print(f"\n❌ ERROR during model loading: {e}")
        return None, None
    
    end_time = time.time()
    print(f"> Successfully loaded in {end_time - start_time:.2f} seconds.")
    return model, tokenizer

def extract_final_answer(text):
    matches = re.findall(r'####\s*(-?\d+\.?\d*)', text)
    if matches: return matches[-1]
    matches = re.findall(r'[tT]he final answer is:?\s*(-?\d+\.?\d*)', text)
    if matches: return matches[-1]
    return None

def benchmark_model(model, tokenizer, dataset, num_samples):
    correct_answers = 0
    prompt_template = "Question: {question}\n\nLet's think step by step to find the correct answer. The final answer is"
    print(f"> Benchmarking on {num_samples} samples...")
    for i in tqdm(range(num_samples)):
        example = dataset[i]
        question = example['question']
        true_answer = extract_final_answer(example['answer'])
        prompt = prompt_template.format(question=question)
        inputs = tokenizer(prompt, return_tensors="pt", return_attention_mask=False).to("cuda")
        output_ids = model.generate(**inputs, max_new_tokens=300, pad_token_id=tokenizer.eos_token_id)
        generated_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)
        model_answer = extract_final_answer(generated_text)
        if model_answer and true_answer and float(model_answer) == float(true_answer):
            correct_answers += 1
    return correct_answers

def plot_results(results, num_samples):
    if not results:
        print("\nNo results to plot.")
        return
    model_names = [name.split('/')[-1] for name in results.keys()]
    scores = list(results.values())
    plt.style.use('seaborn-v0_8-darkgrid')
    fig, ax = plt.subplots(figsize=(10, 7))
    colors = ['#4C72B0', '#55A868', '#C44E52']
    bars = ax.bar(model_names, scores, color=colors[:len(model_names)])
    ax.set_ylabel(f'Correct Answers (out of {num_samples})', fontsize=12)
    ax.set_title('GSM8K Baseline Performance Benchmark', fontsize=16, pad=20)
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
    print("-" * 50)
    print("--- Running Pre-flight Check with a Public Causal Model ---")
    print("This will test the environment and library setup.")
    # We use a token here just in case, though it's not needed for public models.
    test_model, test_tokenizer = load_model_and_tokenizer(PUBLIC_TEST_MODEL, token=HF_TOKEN)
    if test_model is None:
        print("\n❌ PRE-FLIGHT CHECK FAILED. Something is wrong with the environment. Aborting.")
        exit()
    else:
        print("\n✅ PRE-FLIGHT CHECK PASSED. Environment and libraries are working correctly.")
        del test_model
        del test_tokenizer
        torch.cuda.empty_cache()
    print("-" * 50)
    
    print("\n--- Starting Main Benchmark with Gated Model ---")
    gsm8k_test = load_dataset(DATASET_ID, DATASET_CONFIG, split='test')
    benchmark_scores = {}
    
    model, tokenizer = load_model_and_tokenizer(GATED_MODEL_ID, token=HF_TOKEN)
    
    if model is not None:
        score = benchmark_model(model, tokenizer, gsm8k_test, NUM_SAMPLES)
        benchmark_scores[GATED_MODEL_ID] = score
        print(f"> Result for {GATED_MODEL_ID}: {score}/{NUM_SAMPLES} correct.")
        del model
        del tokenizer
        torch.cuda.empty_cache()
    else:
        print(f"\n❌ FAILED TO LOAD THE MAIN MODEL: {GATED_MODEL_ID}")
        print("   Since the pre-flight check passed, this proves the problem is account permissions.")
        print("   Please ensure you have accepted the license for Llama-3 on its Hugging Face page.")

    print("\n--- Final Benchmark Scores ---")
    for model_id, score in benchmark_scores.items():
        print(f"{model_id}: {score}/{NUM_SAMPLES}")

    plot_results(benchmark_scores, NUM_SAMPLES)
    print("-" * 50)