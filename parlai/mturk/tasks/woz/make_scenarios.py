import re
from collections import defaultdict

import copy
import json
import os
import random
import string
from typing import Optional, Text

from parlai.mturk.tasks.woz.task_config import WIZARD_TUTORIAL_URL

template_dir = 'templates/'
scenario_dir = 'scenarios/'
scenario_file = 'scenarios/all_scenarios.txt'
db_dir = 'templates/dbs/'
scenarios_per = 5

def sample(parameter):
  if parameter.get("Type") == "Integer":
      _min = parameter.get("Min", 0)
      _max = parameter.get("Max", 100)
      return random.randint(_min, _max)
  elif parameter.get("Type") == "Categorical":
      return random.choice(parameter.get("Categories"))
  elif parameter.get("Type") == "Boolean":
      return random.choice([False, True])

def populate(desc: Optional[Text], db_path: Text) -> Optional[Text]:
  if not desc:
    return None
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


def get_value_from_db(slot: Text, filename: Text) -> Text:
  with open(filename, "r", encoding="utf-8") as file:
    db = json.load(file)
    db_params = {e['Name']: e for e in db}

  if re.match(slot, ".*-\d*"):
    slot, v = slot.split("-")
    variation = int(v)
  else:
    variation = None

  return sample(db_params.get(slot))


class DatabaseCollection:

  def __init__(self):
    self.databases = {}
    self.filled_slots = defaultdict(list)

  def _load_db_if_necessary(self, db_name: Text) -> None:
    if db_name not in self.databases:
      filename = os.path.join(db_dir, db_name + ".json")
      with open(filename, "r", encoding="utf-8") as file:
        self.databases[db_name] = json.load(file)

  def _new_sample(self, db_name: Text, slot_name: Text):
    self._load_db_if_necessary(db_name)
    db_params = {param["Name"]: param for param in self.databases[db_name]}
    candidate_sample = None
    while not candidate_sample or candidate_sample in self.filled_slots[slot_name]:
      candidate_sample = sample(db_params.get(slot_name))
    self.filled_slots[slot_name].append(candidate_sample)
    return candidate_sample

  def _existing_sample(self, db_name: Text, slot_name: Text, variation: int) -> Optional[Text]:
    if db_name not in self.databases:
      return None
    elif slot_name not in self.filled_slots:
      return None
    elif len(self.filled_slots[slot_name]) < variation + 1:
      return None
    else:
      return self.filled_slots[slot_name][variation]

  def get_value(self, slot: Text, db_name: Text) -> Text:
    if re.match(r".+\-\d+", slot):
      name, v = slot.split("-")
      variation = int(v) - 1
    else:
      name = slot
      variation = 0

    result = self._existing_sample(db_name, name, variation)
    if not result:
      result = self._new_sample(db_name, name)

    return result

  def populate(self, desc: Optional[Text]) -> Optional[Text]:
    if not desc:
      return None
    slots = re.findall(r"\`([\w\-]+)@([\w]+)\`", desc)
    for slot, db_name in slots:
      original = f"`{slot}@{db_name}`"
      desc = desc.replace(
        original,
        self.get_value(slot, db_name)
      )
    return desc


if __name__ == '__main__':
  open(scenario_file, 'w+').write("")
  for fn in os.listdir(template_dir):
    if not fn.endswith('json'):
      continue

    template = json.load(open(template_dir + fn))
    for i,desc in enumerate(template['instructions']['User']['task_descriptions']):
      for j in range(scenarios_per):
        new_scenario = copy.deepcopy(template)
        del new_scenario['instructions']['User']['task_descriptions']
        new_scenario['instructions']['User']['task_description'] = populate(desc, db_dir + template['db'])
        new_scenario['instructions']['Wizard']['task_description'] = new_scenario['instructions']['Wizard']['task_description'].replace("@wizard-tutorial-url", WIZARD_TUTORIAL_URL)
        if "linear_guide" in new_scenario['instructions']['User']:
          dc = DatabaseCollection()
          new_scenario['instructions']['User']["linear_guide"] = [
            dc.populate(instruction)
            for instruction in new_scenario['instructions']['User']["linear_guide"]
          ]
        new_fn = "{0}/{1}_v{2}.json".format(scenario_dir, fn.split('.')[0], i*scenarios_per + j)
        new_name = "{0}_v{1}\n".format(fn.split('.')[0], i*scenarios_per + j)
        json.dump(new_scenario, open(new_fn, 'w+'), indent=True)
        open(scenario_file, 'a+').write(new_name)
