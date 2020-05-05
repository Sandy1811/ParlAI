import re
from collections import defaultdict

import copy
import json
import os
import random
import string

from parlai import PROJECT_PATH
from parlai.mturk.tasks.woz.task_config import WIZARD_TUTORIAL_URL

template_dir = os.path.join(PROJECT_PATH, 'parlai/mturk/tasks/woz/templates/')
scenario_dir = os.path.join(PROJECT_PATH, 'parlai/mturk/tasks/woz/scenarios/')
scenario_file = os.path.join(PROJECT_PATH, 'parlai/mturk/tasks/woz/scenarios/all_scenarios.txt')
db_dir = os.path.join(PROJECT_PATH, 'parlai/mturk/tasks/woz/templates/dbs/')
scenarios_per = 5

def sample(parameter):
  if parameter.get("Type") == "Integer":
      _min = int(parameter.get("Min", 0))
      _max = int(parameter.get("Max", 100))
      return random.randint(_min, _max)
  elif parameter.get("Type") == "Categorical":
      return random.choice(parameter.get("Categories"))
  elif parameter.get("Type") == "Boolean":
      return random.choice([False, True])

def populate(desc, db_path):
  db = json.load(open(db_path))
  db_params = {e['Name']: e for e in db}

  # Detect all slots
  slots = [s[:-1] if s[-1] in string.punctuation else s 
           for s in re.split(r"[ '(]", desc) if s.startswith('@')]
  slots = list(set(slots))

  # Sample slots
  slot_values = {}
  param_selected = defaultdict(list)
  for slot in slots:
    param = slot.split('-')[0][1:]
    value = sample(db_params.get(param))

    # Resample if already selected
    while value in param_selected[param]:
      value = sample(db_params.get(param))

    param_selected[param].append(value)
    slot_values[slot] = value
    
  # Replace description
  for slot,value in slot_values.items():
    desc = desc.replace(slot, str(value))

  return desc

if __name__ == '__main__':
  open(scenario_file, 'w+').write("")
  for fn in os.listdir(template_dir):
    if not fn.endswith('json'):
      continue

    print(f'Processing {fn}...')

    template = json.load(open(template_dir + fn))
    for i,desc in enumerate(template['instructions']['User']['task_descriptions']):
      for j in range(scenarios_per):
        new_scenario = copy.deepcopy(template)
        del new_scenario['instructions']['User']['task_descriptions']
        new_scenario['instructions']['User']['task_description'] = populate(desc, db_dir + template['db'])
        new_scenario['instructions']['Wizard']['task_description'] = new_scenario['instructions']['Wizard']['task_description'].replace("@wizard-tutorial-url", WIZARD_TUTORIAL_URL)
        new_fn = "{0}/{1}_v{2}.json".format(scenario_dir, fn.split('.')[0], i*scenarios_per + j)
        new_name = "{0}_v{1}\n".format(fn.split('.')[0], i*scenarios_per + j)
        json.dump(new_scenario, open(new_fn, 'w+'))
        open(scenario_file, 'a+').write(new_name)
