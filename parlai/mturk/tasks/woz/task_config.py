#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

WIZARD_TUTORIAL_URL = "https://youtu.be/USrWF1ZyNWw"

task_config = {}

"""A short and descriptive title about the kind of task the HIT contains.
On the Amazon Mechanical Turk web site, the HIT title appears in search results,
and everywhere the HIT is mentioned.
"""
task_config['hit_title'] = "[Prototype] Chat as an AI assistant or user"


"""A description includes detailed information about the kind of task the HIT contains.
On the Amazon Mechanical Turk web site, the HIT description appears in the expanded
view of search results, and in the HIT and assignment screens.
"""


"""One or more words or phrases that describe the HIT, separated by commas.
On MTurk website, these words are used in searches to find HITs.
"""
task_config['hit_keywords'] = 'chat, dialogue'


"""A detailed task description that will be shown on the HIT task preview page
and on the left side of the chat page. Supports HTML formatting.
"""
# with open("front_end.html", "r", encoding="utf-8") as file:
#     task_config['task_description'] = file.read()
task_config['frontend_version'] = 1

intro_test = f"""In this task you will take one of two roles: You could be a 'user' who wants to achieve some goal, 
or, alternatively, you could take the role of an 'AI assistant' that helps the user achieve his/her goal. The 
first time you do this task as the assistant, you have to watch and understand a tutorial video: {WIZARD_TUTORIAL_URL} . 
\n\nNote: In this task it is important that you follow instructions 
precisely. In particular, in the assistant's role you will not be paid if you don't follow the flow chart whenever 
possible. """

task_config['task_description'] = intro_test
task_config['hit_description'] = intro_test
task_config['chat_title'] = "Chat"
