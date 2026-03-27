from prompts.base_system import get_base_system_prompt
from prompts.task_rules import build_task_rules
from prompts.output_rules import get_output_rules_prompt
from prompts.general_teaching_example import get_general_teaching_example

def build_full_prompt(mode, task_type):

    base_system_prompt = get_base_system_prompt(mode)
    task_rules = build_task_rules(mode, task_type)
    output_rules = get_output_rules_prompt()
    general_teaching_example = get_general_teaching_example(mode, task_type)

    return base_system_prompt+ "\n" + task_rules+ "\n" + output_rules+ "\n" + general_teaching_example     # + teaching_example