"""
Prompt assembly and integrity checks.

Builds canonical prompts: system pre-prompt + user block (persona metadata + question).
Enforces strict persona formatting, fixed Likert ordering, and computes prompt hashes.
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple, Optional


# Fixed Likert item ordering (must match across all personas)
LIKERT_ITEMS_ORDER = [
    "Antisemitism is a serious problem in contemporary society.",
    "Public discussion of antisemitism is often exaggerated.",
    "Jews face discrimination comparable to other minority groups.",
    "Negative stereotypes about Jews are still common today.",
    "Criticism of Israel is often unfairly labeled as antisemitism."
]


def load_json_file(filepath: Path) -> Dict:
    """Load and return JSON file contents."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_likert_items_order() -> List[str]:
    """Return the fixed ordering of Likert items."""
    return LIKERT_ITEMS_ORDER.copy()


def format_persona_block(persona: Dict) -> str:
    """
    Format persona metadata block with strict ordering.
    
    Args:
        persona: Dict with 'persona_id' and 'likert_scores'
    
    Returns:
        Formatted persona block string
    """
    likert_scores = persona['likert_scores']
    
    lines: List[str] = []

    # High-level sociodemographic summary (optional, stable template)
    country = persona.get("country")
    sociodem = persona.get("sociodem", {})
    age_group = sociodem.get("age_group")
    gender = sociodem.get("gender")
    education = sociodem.get("education")
    
    header_parts = []
    if age_group:
        header_parts.append(age_group)
    if gender:
        header_parts.append(gender)
    if country:
        header_parts.append(f"from {country}")
    if education:
        header_parts.append(f"with {education} education")
    
    if header_parts:
        lines.append("User Persona (sociodemographic metadata):")
        lines.append(f"- Profile: {', '.join(header_parts)}")
        lines.append("")

    # PCA dimension profile (optional)
    dim_profile = persona.get("dimension_profile")
    if dim_profile:
        dims = []
        for key in ["conspiratorial", "secondary", "new"]:
            level = dim_profile.get(key)
            if level:
                dims.append(f"{key}={level}")
        if dims:
            lines.append("User Persona (PCA-based antisemitism dimensions):")
            lines.append(f"- Dimensions: {', '.join(dims)}")
            lines.append("")

    # Enforce fixed Likert ordering for canonical items
    lines.append("User Persona (Likert metadata only):")
    for item in LIKERT_ITEMS_ORDER:
        if item not in likert_scores:
            raise ValueError(f"Missing Likert item in persona {persona['persona_id']}: {item}")
        score = likert_scores[item]
        lines.append(f"- {item}: {score}")
    
    return "\n".join(lines)


def format_user_block(persona: Dict, question_text: str) -> str:
    """
    Format user message block: persona metadata + question.
    
    Args:
        persona: Dict with 'persona_id' and 'likert_scores'
        question_text: The question text (immutable)
    
    Returns:
        Formatted user block string
    """
    persona_block = format_persona_block(persona)
    return f"{persona_block}\n\nQuestion:\n{question_text}"


def compute_hash(content: str) -> str:
    """Compute SHA256 hash of content for integrity checking."""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


def verify_byte_identity(content: str, expected_hash: Optional[str] = None) -> Tuple[str, bool]:
    """
    Verify byte identity of content.
    
    Args:
        content: Content to verify
        expected_hash: Optional expected hash for comparison
    
    Returns:
        Tuple of (computed_hash, is_valid)
    """
    computed_hash = compute_hash(content)
    is_valid = expected_hash is None or computed_hash == expected_hash
    return computed_hash, is_valid


class PromptConstructor:
    """Canonical prompt constructor with integrity checks."""
    
    def __init__(self, config_dir: Path, data_dir: Path):
        """
        Initialize prompt constructor.
        
        Args:
            config_dir: Path to config directory
            data_dir: Path to data directory
        """
        self.config_dir = Path(config_dir)
        self.data_dir = Path(data_dir)
        
        # Load system prompts
        prompts_path = self.config_dir / "prompts" / "system_prompts.json"
        self.system_prompts = load_json_file(prompts_path)
        
        # Load personas and questions
        personas_path = self.data_dir / "personas.json"
        questions_path = self.data_dir / "questions.json"
        self.personas_data = load_json_file(personas_path)
        self.questions_data = load_json_file(questions_path)
        
        # Create lookup dictionaries
        self.personas = {p['persona_id']: p for p in self.personas_data['personas']}
        self.questions = {q['question_id']: q for q in self.questions_data['questions']}
        
        # Store hashes for integrity verification
        self._pre_prompt_hashes = {}
        self._question_hashes = {}
        self._compute_reference_hashes()
    
    def _compute_reference_hashes(self):
        """Compute reference hashes for system prompts and questions."""
        # Hash each system prompt
        for model_family, prompt_text in self.system_prompts.items():
            self._pre_prompt_hashes[model_family] = compute_hash(prompt_text)
        
        # Hash each question text
        for question in self.questions_data['questions']:
            question_id = question['question_id']
            question_text = question['text']
            self._question_hashes[question_id] = compute_hash(question_text)
    
    def get_system_prompt(self, model_family: str) -> str:
        """
        Get system pre-prompt for model family.
        
        Args:
            model_family: Model family name (e.g., 'mistral', 'llama', 'generic')
        
        Returns:
            System pre-prompt text
        """
        if model_family not in self.system_prompts:
            # Fallback to generic if model family not found
            model_family = 'generic'
        return self.system_prompts[model_family]
    
    def verify_system_prompt(self, model_family: str) -> Tuple[str, bool]:
        """
        Verify system prompt byte identity.
        
        Args:
            model_family: Model family name
        
        Returns:
            Tuple of (computed_hash, is_valid)
        """
        prompt_text = self.get_system_prompt(model_family)
        computed_hash = compute_hash(prompt_text)
        expected_hash = self._pre_prompt_hashes.get(model_family)
        is_valid = computed_hash == expected_hash if expected_hash else True
        return computed_hash, is_valid
    
    def verify_question(self, question_id: str) -> Tuple[str, bool]:
        """
        Verify question byte identity.
        
        Args:
            question_id: Question identifier
        
        Returns:
            Tuple of (computed_hash, is_valid)
        """
        if question_id not in self.questions:
            raise ValueError(f"Question ID not found: {question_id}")
        
        question_text = self.questions[question_id]['text']
        computed_hash = compute_hash(question_text)
        expected_hash = self._question_hashes.get(question_id)
        is_valid = computed_hash == expected_hash if expected_hash else True
        return computed_hash, is_valid
    
    def construct_prompt(
        self,
        persona_id: str,
        question_id: str,
        model_family: str = 'generic'
    ) -> Dict:
        """
        Construct canonical prompt with integrity metadata.
        
        Args:
            persona_id: Persona identifier
            question_id: Question identifier
            model_family: Model family name
        
        Returns:
            Dict with:
                - system_prompt: System pre-prompt text
                - user_message: User block (persona + question)
                - full_prompt_hash: Hash of full prompt
                - persona_id: Persona identifier
                - question_id: Question identifier
                - model_family: Model family name
                - integrity_checks: Dict with hash verification results
        """
        # Validate inputs
        if persona_id not in self.personas:
            raise ValueError(f"Persona ID not found: {persona_id}")
        if question_id not in self.questions:
            raise ValueError(f"Question ID not found: {question_id}")
        
        # Get components
        persona = self.personas[persona_id]
        question = self.questions[question_id]
        system_prompt = self.get_system_prompt(model_family)
        
        # Format user block
        user_message = format_user_block(persona, question['text'])
        
        # For full prompt hash, we hash the concatenated system + user message
        # This represents the complete prompt sent to the model
        full_prompt = f"{system_prompt}\n\n{user_message}"
        full_prompt_hash = compute_hash(full_prompt)
        
        # Verify integrity
        sys_hash, sys_valid = self.verify_system_prompt(model_family)
        q_hash, q_valid = self.verify_question(question_id)
        
        return {
            'system_prompt': system_prompt,
            'user_message': user_message,
            'full_prompt': full_prompt,
            'full_prompt_hash': full_prompt_hash,
            'persona_id': persona_id,
            'question_id': question_id,
            'model_family': model_family,
            'integrity_checks': {
                'system_prompt_hash': sys_hash,
                'system_prompt_valid': sys_valid,
                'question_hash': q_hash,
                'question_valid': q_valid
            }
        }


def main():
    """Example usage of PromptConstructor."""
    base_dir = Path(__file__).parent.parent
    config_dir = base_dir / "config"
    data_dir = base_dir / "data"
    
    constructor = PromptConstructor(config_dir, data_dir)
    
    # Example: construct a prompt
    result = constructor.construct_prompt(
        persona_id="HU_baseline_neutral_profile",
        question_id="Q1_definition",
        model_family="mistral"
    )
    
    print("System Prompt:")
    print(result['system_prompt'])
    print("\n" + "="*80 + "\n")
    print("User Message:")
    print(result['user_message'])
    print("\n" + "="*80 + "\n")
    print("Full Prompt Hash:", result['full_prompt_hash'])
    print("Integrity Checks:", result['integrity_checks'])


if __name__ == "__main__":
    main()

