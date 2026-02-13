"""
Synergistic Self-Correction (S2C) Model

Main implementation of the S2C framework that coordinates the three-stage process:
Generator → Critic → Synthesizer
"""

import torch
import torch.nn as nn
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
from typing import Dict, List, Optional, Tuple, Union
import logging

logger = logging.getLogger(__name__)


class S2CModel(nn.Module):
    """
    Synergistic Self-Correction Model

    Implements the three-stage reasoning process:
    1. Generator: Produces initial solution with critical points
    2. Critic: Analyzes solution for potential errors
    3. Synthesizer: Produces refined final solution
    """

    def __init__(
        self,
        base_model_name: str = "meta-llama/Meta-Llama-3-8B-Instruct",
        adapter_path: Optional[str] = None,
        device: str = "auto",
        load_in_8bit: bool = False,
        load_in_4bit: bool = False
    ):
        super().__init__()

        self.base_model_name = base_model_name
        self.device = device

        # Load base model and tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(base_model_name)
        self.tokenizer.pad_token = self.tokenizer.eos_token

        self.base_model = AutoModelForCausalLM.from_pretrained(
            base_model_name,
            torch_dtype=torch.float16,
            load_in_8bit=load_in_8bit,
            load_in_4bit=load_in_4bit,
            device_map=device if device != "auto" else "auto"
        )

        # Load adapter if provided
        if adapter_path:
            self.model = PeftModel.from_pretrained(self.base_model, adapter_path)
            logger.info(f"Loaded S2C adapter from {adapter_path}")
        else:
            self.model = self.base_model
            logger.info("Using base model without adapter")

    @classmethod
    def from_pretrained(cls, model_path: str, **kwargs):
        """Load a pre-trained S2C model"""
        return cls(adapter_path=model_path, **kwargs)

    def solve_with_s2c(self, problem: str, max_length: int = 2048) -> Dict[str, str]:
        """
        Solve a problem using the complete S2C pipeline

        Args:
            problem: Input problem to solve
            max_length: Maximum generation length

        Returns:
            Dictionary containing all stage outputs
        """
        # Stage 1: Generation
        generation_output = self._generate_stage(problem, max_length)

        # Stage 2: Critique
        critique_output = self._critique_stage(problem, generation_output, max_length)

        # Stage 3: Synthesis
        synthesis_output = self._synthesis_stage(
            problem, generation_output, critique_output, max_length
        )

        return {
            "problem": problem,
            "generation": generation_output,
            "critique": critique_output,
            "synthesis": synthesis_output,
            "final_answer": self._extract_final_answer(synthesis_output)
        }

    def _generate_stage(self, problem: str, max_length: int) -> str:
        """Stage 1: Generate initial solution with critical points"""
        prompt = self._format_generation_prompt(problem)
        return self._generate_text(prompt, max_length)

    def _critique_stage(self, problem: str, solution: str, max_length: int) -> str:
        """Stage 2: Analyze solution for errors and inconsistencies"""
        prompt = self._format_critique_prompt(problem, solution)
        return self._generate_text(prompt, max_length)

    def _synthesis_stage(
        self, problem: str, solution: str, critique: str, max_length: int
    ) -> str:
        """Stage 3: Synthesize final solution incorporating critique"""
        prompt = self._format_synthesis_prompt(problem, solution, critique)
        return self._generate_text(prompt, max_length)

    def _generate_text(self, prompt: str, max_length: int) -> str:
        """Generate text using the model"""
        inputs = self.tokenizer(prompt, return_tensors="pt", padding=True)
        inputs = {k: v.to(self.model.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_length,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id
            )

        # Decode only the new tokens (excluding input)
        new_tokens = outputs[0][len(inputs["input_ids"][0]):]
        return self.tokenizer.decode(new_tokens, skip_special_tokens=True)

    def _format_generation_prompt(self, problem: str) -> str:
        """Format prompt for the generation stage"""
        return f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are a mathematical reasoning assistant. Generate a step-by-step solution to the given problem. Identify and mark critical points in your reasoning that are essential for the solution's validity.

<|eot_id|><|start_header_id|>user<|end_header_id|>

Problem: {problem}

Please provide a detailed step-by-step solution. Mark important logical steps or calculations as "Critical Point: [description]".

<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""

    def _format_critique_prompt(self, problem: str, solution: str) -> str:
        """Format prompt for the critique stage"""
        return f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are a critical reviewer of mathematical solutions. Analyze the given solution for potential errors, logical inconsistencies, or missing steps. Be thorough and constructive in your analysis.

<|eot_id|><|start_header_id|>user<|end_header_id|>

Problem: {problem}

Solution to analyze: {solution}

Please carefully review this solution and identify any potential issues, errors, or areas that need clarification. Focus on:
1. Logical consistency
2. Computational accuracy
3. Missing steps or assumptions
4. Alternative approaches that might be better

<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""

    def _format_synthesis_prompt(
        self, problem: str, solution: str, critique: str
    ) -> str:
        """Format prompt for the synthesis stage"""
        return f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are a mathematical reasoning expert. Given a problem, initial solution, and critique, provide a refined final solution that addresses any identified issues while preserving correct reasoning.

<|eot_id|><|start_header_id|>user<|end_header_id|>

Problem: {problem}

Initial Solution: {solution}

Critique: {critique}

Please provide a final, refined solution that incorporates the feedback from the critique while maintaining accuracy and clarity.

<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""

    def _extract_final_answer(self, synthesis: str) -> str:
        """Extract the final numerical answer from the synthesis"""
        # Simple heuristic to extract final answer
        lines = synthesis.strip().split('\n')
        for line in reversed(lines):
            if any(keyword in line.lower() for keyword in ['answer:', 'final answer:', 'result:']):
                return line.split(':')[-1].strip()

        # Fallback: return last line if it contains numbers
        last_line = lines[-1].strip() if lines else synthesis.strip()
        return last_line

    def forward(self, *args, **kwargs):
        """Forward pass for compatibility with PyTorch modules"""
        return self.model(*args, **kwargs)

    def save_pretrained(self, save_directory: str):
        """Save the model adapter"""
        if hasattr(self.model, 'save_pretrained'):
            self.model.save_pretrained(save_directory)
        else:
            logger.warning("Model does not support save_pretrained method")

    def train(self, mode: bool = True):
        """Set the model in training mode"""
        self.model.train(mode)
        return super().train(mode)

    def eval(self):
        """Set the model in evaluation mode"""
        self.model.eval()
        return super().eval()