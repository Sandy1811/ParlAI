import datetime
import json
import os
import time
import mmap
from typing import Text, Optional, Tuple, Any

from parlai import PROJECT_PATH


TASK_LEVEL_SINGLE_HAPPY = "single_happy"
TASK_LEVEL_SINGLE_UNHAPPY = "single_unhappy"
TASK_LEVEL_MIXED = "mixed"


def file_system_scan(
    f: Any, dir_name: Text, file_extension: Optional[Text] = None
) -> None:
    for root, dirs, files in os.walk(dir_name):
        for file in files:
            if not file_extension or file.endswith(file_extension):
                f(os.path.join(root, file))


def file_contains_q(filename: Text, pattern: Text) -> bool:
    with open(filename, "rb", 0) as file, mmap.mmap(
        file.fileno(), 0, access=mmap.ACCESS_READ
    ) as s:
        return s.find(str.encode(pattern)) != -1


class WorkerDatabase:
    def __init__(
        self,
        work_filename: Optional[Text] = None,
        eval_filename: Optional[Text] = None,
        bonus_filename: Optional[Text] = None,
    ) -> None:
        self.work_filename = work_filename or os.path.join(
            PROJECT_PATH, "resources", "mturk_work.tsv"
        )
        self.eval_filename = eval_filename or os.path.join(
            PROJECT_PATH, "resources", "mturk_eval.tsv"
        )
        self.bonus_filename = bonus_filename or os.path.join(
            PROJECT_PATH, "resources", "mturk_bonus.tsv"
        )

    def get_worker_scores(self, worker_id: Text) -> Tuple[int, int]:
        user_score = 0
        wizard_score = 0
        with open(self.eval_filename, "r", encoding="utf-8") as file:
            for line in file:
                if line.startswith(f"{worker_id}\t"):
                    _, _, role, _, _, score, _ = line.split("\t")
                    if role == "User":
                        user_score += int(score)
                    elif role == "Wizard":
                        wizard_score += int(score)
                    else:
                        raise ValueError(
                            f"Unknown role '{role}' in {self.eval_filename}"
                        )
        return user_score, wizard_score

    def get_worker_evaluation(self, worker_id: Text) -> Optional[Text]:
        user_score = 0
        user_quality = 0.
        user_difficulty = 0.
        num_user = 0
        wizard_score = 0
        wizard_quality = 0.
        wizard_difficulty = 0.
        num_wizard = 0

        if not os.path.exists(self.eval_filename):
            return None

        with open(self.eval_filename, "r", encoding="utf-8") as file:
            for line in file:
                if line.startswith(f"{worker_id}\t"):
                    _, _, role, difficulty, quality, score, _ = line.split("\t")
                    if role == "User":
                        num_user += 1
                        user_score += int(score)
                        user_difficulty += float(difficulty)
                        user_quality += float(quality)
                    elif role == "Wizard":
                        num_wizard += 1
                        wizard_score += int(score)
                        wizard_difficulty += float(difficulty)
                        wizard_quality += float(quality)
                    else:
                        raise ValueError(
                            f"Unknown role '{role}' in {self.eval_filename}"
                        )

        if num_wizard + num_user == 0:
            return None

        if num_user > 0:
            user_difficulty = round(100 * user_difficulty / num_user)
            user_quality = round(100 * user_quality / num_user)
        else:
            user_difficulty = None
            user_quality = None

        if num_wizard > 0:
            wizard_difficulty = round(100 * wizard_difficulty / num_wizard)
            wizard_quality = round(100 * wizard_quality / num_wizard)
        else:
            wizard_difficulty = None
            wizard_quality = None

        performance_evaluation = f"We have evaluated {num_wizard + num_user} of your dialogues so far. "
        performance_evaluation += self._evaluate_role(num_user, "a user", user_difficulty, user_quality, user_score)
        performance_evaluation += self._evaluate_role(num_wizard, "an AI assistant", wizard_difficulty, wizard_quality, wizard_score)
        performance_evaluation += f"\n\nYour total score is: {user_score + wizard_score}."

        return performance_evaluation

    @staticmethod
    def _evaluate_role(num: int, role: Text, difficulty: int, quality: int, score: int):
        performance_evaluation = ""
        if num == 0:
            performance_evaluation += f"We haven't seen you as {role} yet. "
        else:
            performance_evaluation += f"As {role}, you have played in {num} dialogues and have "
            if difficulty < 33:
                performance_evaluation += "mostly seen easy situations. "
            elif 33 <= difficulty < 66:
                performance_evaluation += "seen some easy and some more challenging situations. "
            else:
                performance_evaluation += "mostly seen challenging situations. "
            performance_evaluation += "On average, we think "
            if quality < 33:
                performance_evaluation += "your work unfortunately does not quite reach the quality we need for our data set. "
            elif 33 <= quality < 66:
                performance_evaluation += "that some of your work is quite good, but some could be better. "
            else:
                performance_evaluation += "that you've been doing an excellent job so far! "
            performance_evaluation += f"So, as {role} you collected {score} points. "
        return performance_evaluation

    def store_work(
        self,
        worker_id: Text,
        hit_id: Text,
        sandbox: bool,
        role: Text,
        task: Text,
        task_level: Text,
        num_utterances: int,
        unix_time: Optional[int] = None,
    ) -> None:

        assert task_level in [
            TASK_LEVEL_SINGLE_HAPPY,
            TASK_LEVEL_SINGLE_UNHAPPY,
            TASK_LEVEL_MIXED,
        ]
        assert role in ["User", "Wizard"]
        assert num_utterances >= 0

        unix_time = unix_time or int(time.time())

        with open(self.work_filename, "a", encoding="utf-8") as file:
            file.write(
                f"{worker_id}\t{hit_id}\t{sandbox}\t{role}\t{task}\t{task_level}\t{num_utterances}\t{unix_time}\n"
            )

    def eval_work(
        self,
        worker_id: Text,
        hit_id: Text,
        role: Text,
        task_difficulty: float,
        work_quality: float,
        unix_time: Optional[int] = None,
    ) -> None:
        assert 0. <= task_difficulty <= 1.
        assert 0. <= work_quality <= 1.

        if self._work_has_been_evaluated(worker_id, hit_id):
            raise ValueError(
                f"HIT {hit_id} of worker {worker_id} has already been evaluated"
            )

        unix_time = unix_time or int(time.time())
        score = round(20 * task_difficulty * (work_quality - 0.5))

        with open(self.eval_filename, "a", encoding="utf-8") as file:
            file.write(f"{worker_id}\t{hit_id}\t{role}\t{task_difficulty}\t{work_quality}\t{score}\t{unix_time}\n")

    def _work_has_been_evaluated(self, worker_id: Text, hit_id: Text) -> bool:
        if os.path.exists(self.eval_filename):
            with open(self.eval_filename, "r", encoding="utf-8") as file:
                for line in file:
                    if line.startswith(f"{worker_id}\t{hit_id}"):
                        return True
        return False

    def unevaluated_work(
        self, include_sandbox: bool = False
    ) -> Tuple[Optional[Text], Optional[Text], Optional[Text]]:
        if not os.path.exists(self.work_filename):
            return None, None, None

        with open(self.work_filename, "r", encoding="utf-8") as file:
            for line in file:
                worker_id, hit_id, sandbox, role, *_ = line.split("\t")
                if (
                    include_sandbox or sandbox == "False"
                ) and not self._work_has_been_evaluated(worker_id, hit_id):
                    yield worker_id, hit_id, role

    def print_dialogue(self, hit_id: Text, show_metadata: bool = False) -> None:
        filename = self._custom_log_file(hit_id)
        if not filename:
            return

        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)
        if not "Events" in data:
            raise ImportError(f"File {filename} contains no 'Events' key.")

        print()
        if show_metadata:
            total_duration = datetime.timedelta(
                seconds=(
                    data["Events"][-1].get("UnixTime")
                    - data["Events"][0].get("UnixTime")
                )
            )
            num_user_turns = len(
                [0 for turn in data["Events"] if turn.get("Agent") == "User"]
            )
            num_kb_queries = len(
                [0 for turn in data["Events"] if turn.get("Agent") == "KnowledgeBase"]
            )
            duration_per_turn = datetime.timedelta(
                seconds=round(
                    (
                        data["Events"][-1].get("UnixTime")
                        - data["Events"][0].get("UnixTime")
                    )
                    / (num_user_turns * 2)
                )
            )
            print(f"Log file path: {filename}")
            print(
                f"Total duration:     {total_duration}  |  Number of user turns:  {num_user_turns}"
            )
            print(
                f"Mean turn duration: {duration_per_turn}  |  Number of KB queries:  {num_kb_queries}"
            )
            print(
                f"User:     https://requester.mturk.com/workers/{data.get('UserWorkerID')}  |  HIT {data.get('UserHITID')}"
            )
            print(
                f"Wizard:   https://requester.mturk.com/workers/{data.get('WizardWorkerID')}  |  HIT {data.get('WizardHITID')}"
            )
            print()
            print(f"User Task:   {data.get('UserTask')}")
            print(f"Schema URLs: {data.get('WizardSchemaURLs')}")
            print()

        for event in data["Events"]:
            agent = event.get("Agent")
            if agent == "User":
                print(f"USR {event.get('Action'):<15} {event.get('Text')}")
            elif agent == "Wizard":
                action = event.get('Action')
                if action in ["utter", "pick_suggestion", "request_suggestions"]:
                    print(f"WIZ {action[:15]:<15} {event.get('Text')}")
                elif action == "query":
                    print(f"WIZ {event.get('API'):<15} {event.get('Constraints')}")
                else:
                    print(f"WIZ {action[:15]:<15}")
            elif agent == "KnowledgeBase":
                print(f"KB  {event.get('TotalItems'):<15} {event.get('Item')}")

    def _custom_log_file(self, hit_id: Text) -> Optional[Text]:
        path = self._task_directory(hit_id)
        if not path:
            return None
        path = os.path.join(path, "custom", "data.json")
        if not os.path.exists(path):
            return None

        return path

    def _task_directory(self, hit_id: Text) -> Optional[Text]:
        base_dir = os.path.join(PROJECT_PATH, "parlai", "mturk", "run_data")

        result = None

        def look_for_hit_id(filename: Text) -> None:
            nonlocal result
            if result:
                return
            if file_contains_q(filename, hit_id):
                result = filename

        file_system_scan(look_for_hit_id, base_dir, ".json")

        if isinstance(result, str):
            result = os.path.dirname(os.path.dirname(result))

        return result


if __name__ == '__main__':
    wdb = WorkerDatabase()

    print(wdb.get_worker_evaluation("A1I1OIUHZLZRDO"))

    for id, hit, role in wdb.unevaluated_work(True):
        wdb.print_dialogue(hit, True)
        print()
        task_difficulty = float(input(f"Task difficulty for the {role} (0..1): "))
        work_quality = float(input(f"Work quality for the {role} (0..1): "))
        if task_difficulty < 0. or task_difficulty > 1. or work_quality < 0. or work_quality > 1.:
            print("Ok, skipping this.")
        else:
            wdb.eval_work(id, hit, role, task_difficulty, work_quality)
