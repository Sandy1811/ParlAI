#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

task_config = {}

"""A short and descriptive title about the kind of task the HIT contains.
On the Amazon Mechanical Turk web site, the HIT title appears in search results,
and everywhere the HIT is mentioned.
"""
task_config['hit_title'] = "Chat as an AI assistant or user"


"""A description includes detailed information about the kind of task the HIT contains.
On the Amazon Mechanical Turk web site, the HIT description appears in the expanded
view of search results, and in the HIT and assignment screens.
"""
task_config['hit_description'] = (
    "Play an AI assistant or a user that interacts with it to find a ride in the city. Before you attempt this task for the first time as AI assistant, you should watch the introductory tutorial: https://bit.ly/2UgkAQ6 . "
)


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

intro_test = """In this task you will take one of two roles: You could be a 'user' who wants to find and book a car ride or, alternatively, you could take the role of a 'virtual assistant' that helps the user achieve this goal. The first time you do this task as the assistant, you have to watch and understand a tutorial video: https://bit.ly/2UgkAQ6 . \n\nNote: In this task it is important that you follow instructions precisely. In particular, in the assistant's role you will not be paid if you don't follow the flow chart whenever possible. """

task_config['task_description'] = intro_test
task_config['chat_title'] = "Chat"
