from dataclasses import dataclass
from typing import Dict


@dataclass
class Profile:
    profile_id: str
    label: str
    summary: str
    attitude_indicators: Dict
    background_text: str


@dataclass
class PromptItem:
    prompt_id: str
    text: str
    topic: str
    task_type: str
    sensitivity_level: str


@dataclass
class Condition:
    condition_id: str
    use_neutral_system_prompt: bool
    type: str


@dataclass
class RunSpec:
    run_id: str
    experiment_id: str
    profile_id: str
    prompt_id: str
    condition_id: str
    model_name: str
    repeat_index: int

