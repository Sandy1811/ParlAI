#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

task_config = {}

"""A short and descriptive title about the kind of task the HIT contains.
On the Amazon Mechanical Turk web site, the HIT title appears in search results,
and everywhere the HIT is mentioned.
"""
task_config['hit_title'] = 'Find a new apartment by chatting to a virtual assistant.'


"""A description includes detailed information about the kind of task the HIT contains.
On the Amazon Mechanical Turk web site, the HIT description appears in the expanded
view of search results, and in the HIT and assignment screens.
"""
task_config['hit_description'] = (
    "You recently started a new job in Berlin and need to find an apartment to live in. "
    "For now, you stay in a hotel, but that is expensive, so you'll want to find something soon. "
    "A friend of yours recommended the virtual assistant that you are about to talk to now. "
    "Maybe it can help you find something you like?"
)


"""One or more words or phrases that describe the HIT, separated by commas.
On MTurk website, these words are used in searches to find HITs.
"""
task_config['hit_keywords'] = 'chat,dialog'


"""A detailed task description that will be shown on the HIT task preview page
and on the left side of the chat page. Supports HTML formatting.
"""
with open("front_end.html", "r", encoding="utf-8") as file:
    task_config['task_description'] = file.read()
