#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from typing import Optional, Text, List

from parlai.core.worlds import validate
from parlai.mturk.core.agents import MTURK_DISCONNECT_MESSAGE, RETURN_MESSAGE, TIMEOUT_MESSAGE
from parlai.mturk.core.worlds import MTurkOnboardWorld


TUTORIAL_URL = "--URL--"


class TutorialFailedError(ValueError):
    pass


class GuideCommand:

    def __init__(self, text):
        self._text = text

    @property
    def message(self):
        return {"id": "MTurk System", "text": self._text}


def is_disconnected(act):
    return 'text' in act and act['text'] in [
        MTURK_DISCONNECT_MESSAGE,
        RETURN_MESSAGE,
        TIMEOUT_MESSAGE,
    ]


class TutorialWorld1(MTurkOnboardWorld):
    """
    Tutorial I
    """

    def __init__(self, opt, mturk_agent) -> None:
        super(TutorialWorld1, self).__init__(opt, mturk_agent=mturk_agent)

    def parley(self) -> None:
        self.mturk_agent.observe(
            GuideCommand(
                f"Hello {self.mturk_agent.worker_id}. In this task you have to answer a multiple-choice "
                f"test about a video tutorial. If you successfully answer the questions, you "
                f"earn a qualification to participate in the dialogue tasks that are described "
                f"in the video. Send any text to continue."
            ).message
        )
        hints_needed = 0
        try:
            while not self.check_response():
                pass
            self.mturk_agent.observe(
                GuideCommand(
                    f"If you are not interested in earning the qualification for the AI Dialogue "
                    f"tasks, please return the HIT immediately. Otherwise, please watch the following "
                    f"video tutorial carefully and be prepared to answer questions: {TUTORIAL_URL} . "
                    f"Send any text when you're ready to answer questions. "
                ).message
            )
            while not self.check_response():
                pass
            self.mturk_agent.observe(
                GuideCommand(
                    f"Ok, let's start the quiz. Please answer by sending the number of the answer "
                    f"that you think is correct. "
                ).message
            )
            hints_needed += self.ask(
                question="As the assistant, what should you do if the user begins a dialogue, but doesn't say what she wants?",
                choices=[
                    "I tell the user what task I can help her with",
                    "I ask the user how I can help",
                    "I should say that I cannot understand what she's saying",
                ],
                answer=2,
                hints=[
                    "No... To answer you should send either '1', '2', or '3' (without the quotes).",
                    "Not quite. Try again :)",
                    "Not quite. One more try...",
                ],
            )
            hints_needed += self.ask(
                question="For the assistant, what of these things is the MOST important?",
                choices=[
                    "Being helpful to the user",
                    "Following the flow chart of the current task whenever possible",
                    "Making the conversation as short as possible",
                    "Making the conversation as long as possible",
                ],
                answer=2,
                hints=[
                    "No. The length of the conversation is not as important to us as its quality. Try again.",
                    "No. The correct answer starts with 'Following the flow chart...'. Try again.",
                ],
            )
            if hints_needed == 0:
                self.mturk_agent.observe(
                    GuideCommand(
                        f"Perfect Score! Well done! You got your qualification for the task "
                        f"'AI Dialogues Stage II - Single Task Dialogues'."
                    ).message
                )
            elif hints_needed < 4:
                self.mturk_agent.observe(
                    GuideCommand(
                        f"Nicely done! You got your qualification for the task "
                        f"'AI Dialogues Stage II - Single Task Dialogues'."
                    ).message
                )
            else:
                self.mturk_agent.observe(
                    GuideCommand(
                        f"Done! You got your qualification for the task "
                        f"'AI Dialogues Stage II - Single Task Dialogues'."
                    ).message
                )
        except ConnectionError:
            self.episodeDone = True
            return
        except TutorialFailedError as e:
            self.mturk_agent.observe(
                GuideCommand(
                    f"Sorry, but the correct answer was choice {e}. Thank you for trying, though!"
                ).message
            )
            return
        self.mturk_agent.observe(GuideCommand(f"All done!").message)

        self.episodeDone = True

    def check_response(self, expected_choice: Optional[int] = None) -> bool:
        message = self.mturk_agent.act()
        if is_disconnected(message):
            raise ConnectionError()
        else:
            if message.get("text", "1").isnumeric():
                choice = int(message.get("text", "1"))
            else:
                choice = 0
            return (
                expected_choice is None
                or choice == expected_choice
            )

    def ask(
        self,
        question: Text,
        choices: List[Text],
        answer: int,
        hints: Optional[List[Text]] = None,
    ) -> int:
        question_and_choices: Text = question + "\n"
        for i, choice in enumerate(choices):
            question_and_choices += f" {i+1}: {choice}\n"
        self.mturk_agent.observe(GuideCommand(question_and_choices).message)
        hints = hints or []
        hints_given = 0
        while not self.check_response(answer) and hints_given <= len(hints):
            if hints_given == len(hints):
                raise TutorialFailedError(answer)
            self.mturk_agent.observe(GuideCommand(hints[hints_given]).message)
            hints_given += 1
        return hints_given

    def get_model_agent(self):
        return self.mturk_agent

    def get_task_agent(self):
        return self.mturk_agent

    def episode_done(self):
        return self.episodeDone
