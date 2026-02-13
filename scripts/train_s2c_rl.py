# --- train_s2c_final.py (v5 - Ready to Resume) ---

import torch
import os
import re
from tqdm import tqdm

from transformers import AutoTokenizer, BitsAndBytesConfig, DataCollatorWithPadding
from datasets import load_dataset
from peft import LoraConfig
from trl import PPOTrainer, PPOConfig, AutoModelForCausalLMWithValueHead

# --- 1. CONFIGURATION ---
class TrainingConfig:
    # --- MODIFICATION 1: Point MODEL_ID to your last saved checkpoint.
    # This will load the base Llama-3 model and then apply your LoRA adapter
    # weights from step 200, effectively resuming your progress.
    MODEL_ID = "s2c_llama3_8b_checkpoints/step_200"
    
    HF_TOKEN = "HUGGING_FACE_TOKEN"
    DATASET = "gsm8k"
    DATASET_CONFIG = "main"
    NUM_TRAIN_SAMPLES = 1000 # Keep this the same as the original run
    LEARNING_RATE = 1.41e-5
    PPO_EPOCHS = 4
    MINI_BATCH_SIZE = 2
    BATCH_SIZE = 4
    OUTPUT_DIR = "s2c_llama3_8b_final"
    CHECKPOINT_DIR = "s2c_llama3_8b_checkpoints"
    SAVE_FREQ = 50
    LOG_FREQ = 10

# --- 2. S2C PROMPT & REWARD ENGINEERING (Unchanged) ---
def build_s2c_prompt(question: str) -> str:
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

def get_reward(model_response: str, true_answer: str) -> float:
    model_answer = extract_final_answer(model_response)
    if model_answer and true_answer and float(model_answer) == float(true_answer):
        return 1.0
    return 0.0

# --- 3. MAIN TRAINING SCRIPT ---
if __name__ == "__main__":
    config = TrainingConfig()
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    os.makedirs(config.CHECKPOINT_DIR, exist_ok=True)
    print("✅ Directories created.")
    
    ppo_config = PPOConfig(
        learning_rate=config.LEARNING_RATE, ppo_epochs=config.PPO_EPOCHS,
        mini_batch_size=config.MINI_BATCH_SIZE, batch_size=config.BATCH_SIZE,
        log_with="tensorboard", project_kwargs={"logging_dir": "./logs"}
    )
    
    lora_config = LoraConfig(
        r=16, lora_alpha=32, lora_dropout=0.05,
        bias="none", task_type="CAUSAL_LM",
    )
    
    print(f"✅ Resuming training from checkpoint: {config.MODEL_ID}")
    quantization_config = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.bfloat16)
    
    # from_pretrained knows how to load the adapter on top of the base model
    model = AutoModelForCausalLMWithValueHead.from_pretrained(
        config.MODEL_ID, quantization_config=quantization_config,
        # peft_config is now loaded from the checkpoint, so it's not strictly needed here,
        # but it doesn't hurt to keep it for clarity.
        peft_config=lora_config, 
        device_map="auto", token=config.HF_TOKEN
    )
    model.gradient_checkpointing_enable()

    # The tokenizer is also loaded from the checkpoint path
    tokenizer = AutoTokenizer.from_pretrained(config.MODEL_ID, token=config.HF_TOKEN, padding_side='left')
    tokenizer.pad_token = tokenizer.eos_token
    data_collator = DataCollatorWithPadding(tokenizer=tokenizer)
    print("✅ Resumed Model and Tokenizer loaded.")

    dataset = load_dataset(config.DATASET, config.DATASET_CONFIG, split='train').shuffle(seed=42).select(range(config.NUM_TRAIN_SAMPLES))
    true_answers_list = [extract_final_answer(ans) for ans in dataset["answer"]]
    
    def tokenize(example):
        prompt = build_s2c_prompt(example['question'])
        return {'input_ids': tokenizer.encode(prompt)}
        
    dataset = dataset.map(tokenize, batched=False)
    dataset = dataset.remove_columns(['question', 'answer'])
    dataset.set_format(type="torch")
    print("✅ Dataset prepared and cleaned.")

    ppo_trainer = PPOTrainer(
        config=ppo_config, model=model, ref_model=None,
        tokenizer=tokenizer, dataset=dataset,
        data_collator=data_collator
    )
    print("✅ PPOTrainer initialized.")

    # --- MODIFICATION 2: Define starting step and skip completed batches ---
    starting_step = 200
    print(f"\n--- Resuming RL Training from step {starting_step} ---")
    
    generation_kwargs = {"max_new_tokens": 600, "pad_token_id": tokenizer.eos_token_id, "do_sample": True, "temperature": 0.7}
    
    for step, batch in tqdm(enumerate(ppo_trainer.dataloader), total=len(ppo_trainer.dataloader)):
        # This 'if' statement will fast-forward the loop to your starting point
        if step < starting_step:
            continue

        query_tensors = batch['input_ids']
        response_tensors = ppo_trainer.generate(list(query_tensors), **generation_kwargs)
        response_texts = [tokenizer.decode(r.squeeze()) for r in response_tensors]

        start_index = step * config.BATCH_SIZE
        end_index = start_index + len(response_texts)
        true_answers_for_batch = true_answers_list[start_index:end_index]

        rewards = [torch.tensor(get_reward(resp, true_ans)) for resp, true_ans in zip(response_texts, true_answers_for_batch)]
        stats = ppo_trainer.step(list(query_tensors), response_tensors, rewards)
        
        if (step + 1) % config.LOG_FREQ == 0:
            ppo_trainer.log_stats(stats, batch, rewards)
            print(f"\n--- Step {step+1}/{len(ppo_trainer.dataloader)} ---")
            print(f"Mean Reward: {stats['ppo/returns/mean']:.4f}")
            
        if (step + 1) % config.SAVE_FREQ == 0:
            checkpoint_path = os.path.join(config.CHECKPOINT_DIR, f"step_{step+1}")
            ppo_trainer.save_pretrained(checkpoint_path)
            print(f"\n✅ Checkpoint saved to {checkpoint_path}\n")

    print("\n--- Training Finished ---")
    print(f"Saving final model adapters to {config.OUTPUT_DIR}")
    ppo_trainer.save_pretrained(config.OUTPUT_DIR)
    print("✅ Final model saved successfully!")