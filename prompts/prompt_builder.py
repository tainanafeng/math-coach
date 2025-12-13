from prompts.base_system import get_base_system_prompt
from prompts.dialogue_rules import build_dialogue_rules

def build_full_prompt(context_type, teaching_example):

    system_prompt = get_base_system_prompt()
    dialogue_rules = build_dialogue_rules(context_type)

    #print(f"{system_prompt}{dialogue_rules}{teaching_example}")

    return system_prompt + "\n" + dialogue_rules + "\n" + teaching_example