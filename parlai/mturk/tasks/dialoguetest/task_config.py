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
task_config[
    'hit_description'
] = "You recently started a new job in Berlin and need to find an apartment to live in. " \
    "For now, you stay in a hotel, but that is expensive, so you'll want to find something soon. " \
    "A friend of yours recommended the virtual assistant that you are about to talk to now. " \
    "Maybe it can help you find something you like?"


"""One or more words or phrases that describe the HIT, separated by commas.
On MTurk website, these words are used in searches to find HITs.
"""
task_config['hit_keywords'] = 'chat,dialog'


"""A detailed task description that will be shown on the HIT task preview page
and on the left side of the chat page. Supports HTML formatting.
"""
task_config[
    'task_description'
] = '''
<div id="intro">
You recently started a new job in Berlin and need to find an apartment to live in. 
For now, you stay in a hotel, but that is expensive, so you'll want to find something soon. 
A friend of yours recommended the virtual assistant that you are about to talk to now. 
Maybe it can help you find something you like?<br><br>
</div>

<div id="ask_accept">
If you are ready, please click "Accept HIT" to start this task.<br>
</div>

<div id="input"></div>
<div float="right">
  <button class="btn btn-primary" style="width: 120px; font-size: 16px; float: left; margin-left: 10px; padding: 0px;" id="kb_button">KB Query</button>
</div>

<script type="text/javascript">

var num_messages = 0;
var numberOfItemTypes;

$("button#kb_button").hide();

function enable_button(button, enable) {
    if (enable) {
      button.removeClass('disabled');
      button.prop("disabled", false);
    } else {
      button.addClass("disabled");
      button.prop("disabled", true);
    }
}

function makeInput(info, agent_id) {
  $('#ask_accept').html("You are the " + agent_id);
  if (agent_id.startsWith("Wizard")) {
    $("button#kb_button").show();
    enable_button($("button#kb_button"), false);
  }
}

(function() {
    // Override handle_new_message function
    handle_new_message = function() {
        var new_message_id = arguments[0];
        var message = arguments[1];
        var agent_id = message.id;
        var text = message.text;
        var info = message.info;
        var was_this_agent = (agent_id == cur_agent_id);

        if (displayed_messages.indexOf(new_message_id) !== -1) {
            // This message has already been seen and put up into the chat
            log(new_message_id + ' was a repeat message', 1);
            return;
        }

        log('New message, ' + new_message_id + ' from agent ' + agent_id, 1);
        displayed_messages.push(new_message_id);

        if (message.info) {
            makeInput(message.info, agent_id);
        } else if (text.startsWith('<query>')) {
            message.id = (was_this_agent ? "YOU" : agent_id);
            // add_message_to_conversation(was_this_agent ? "YOU" : "THEM", text, was_this_agent);
            add_message_to_conversation(was_this_agent ? "YOU" : agent_id, text, was_this_agent);
        } else {
            num_messages++;
            if (num_messages >= 2) {
                enable_button($("button#kb_button"), !was_this_agent);
            }

            message.id = (was_this_agent ? "YOU" : agent_id);
            add_message_to_conversation(was_this_agent ? "YOU" : agent_id, text, was_this_agent);
        }
    };
})();


function send_query(selection) {
      new_message_id = uuidv4();
      send_packet(
        TYPE_MESSAGE,
        {
          text: selection,
          id: cur_agent_id,
          message_id: new_message_id,
          episode_done: false
        },
        true,
        true,
        function(msg) {
        }
      );
}


$("button#kb_button").on('click', function () {
  send_query('<query> some question');
});

</script>
'''
