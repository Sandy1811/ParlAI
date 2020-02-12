#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

task_config = {}

"""A short and descriptive title about the kind of task the HIT contains.
On the Amazon Mechanical Turk web site, the HIT title appears in search results,
and everywhere the HIT is mentioned.
"""
task_config['hit_title'] = 'Negotiate a deal with another user!'


"""A description includes detailed information about the kind of task the HIT contains.
On the Amazon Mechanical Turk web site, the HIT description appears in the expanded
view of search results, and in the HIT and assignment screens.
"""
task_config['hit_description'] = (
    'You will have a conversation with another user to agree how to divide some objects'
    'between you. Negotiate hard to get a deal worth as many points as possible!'
)


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
<div id="preview">
You will have a conversation with another user to agree how to divide some objects between you. Negotiate hard to
get a deal worth as many points as possible<br><br>

If you are ready, please click "Accept HIT" to start this task.
</div>

<div id="input"></div>
<div float="right">
  <button class="btn btn-primary" style="width: 120px; font-size: 16px; float: left; margin-left: 10px; padding: 0px;" id="id_no_deal_button">Done</button>
  <button class="btn btn-primary" style="width: 120px; font-size: 16px; float: left; margin-left: 10px; padding: 0px;" id="id_send_deal_button">Query KB</button>
</div>

<script type="text/javascript">

var values = [0, 0, 0];
var counts = [0, 0, 0];

var num_messages = 0;
var numberOfItemTypes;

var your_selection = "";
var their_selection = "";

var image_path = "https://github.com/facebookresearch/end-to-end-negotiator/raw/master/src/images/";
var image_names = ["book", "hat", "ball"];

$("button#id_send_deal_button").hide();
$("button#id_no_deal_button").hide();

function enable_button(button, enable) {
    if (enable) {
      button.removeClass('disabled');
      button.prop("disabled", false);
    } else {
      button.addClass("disabled");
      button.prop("disabled", true);
    }
}

function makeInput(info) {
  $('#preview').html("");
  $("button#id_send_deal_button").show();
  enable_button($("button#id_send_deal_button"), false);
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
            makeInput(info);
        } else if (text.startsWith('<query>')) {
            message.id = (was_this_agent ? "YOU:" : "THEM:");
            var agent_id = message.id;
            add_message_to_conversation(was_this_agent ? "YOU" : "THEM", text, was_this_agent);
        } else {
            num_messages++;
            if (num_messages >= 2) {
                enable_button($("button#id_send_deal_button"), !was_this_agent);
            }

            if (num_messages >= 10) {
                $("button#id_no_deal_button").show();
                enable_button($("button#id_no_deal_button"), !was_this_agent);
            }

            message.id = (was_this_agent ? "YOU:" : "THEM:");
            var agent_id = message.id;
            add_message_to_conversation(was_this_agent ? "YOU" : "THEM", text, was_this_agent);
        }
    };
})();

function completion_message(your_selection, their_selection) {
    if (your_selection == "" || their_selection == "") {
        // Haven't both entered deal
        return ;
    }

    var your_counts = your_selection.match(/\d+/g);
    var their_counts = their_selection.match(/\d+/g);
    var agree = true;
    var all_zero = true;
    var score = 0;

    for (var i=0; i<counts.length; i++) {
        var your_count = parseInt(your_counts[2 * i + 1]);
        var their_count = parseInt(their_counts[2 * i + 1]);

        all_zero = all_zero && your_count == 0;
        all_zero = all_zero && their_count == 0;
        agree = agree && ((your_count + their_count) == counts[i]);
        score += your_count * values[i];
    }

    if (!agree) {
        score = 0;
    }

    var msg = "";
    msg += "<br><h1> Your score: " + score + "/10</h1>";

    if (all_zero) {
        msg += "Please try to reach agreements with your partner in future.";
    } else if (!agree) {
        msg += "You and your partner entered <b>different deals</b>. " +
                "Please try to carefully agree deals in future, or your work may be rejected.";
    } else if (score < 5) {
        msg += "Please <b>negotiate harder</b> in future to get good deals or your work may be rejected.";
    } else if (score < 7 && num_messages < 4) {
        msg += "Please <b>negotiate harder</b> in future to get good deals or your work may be rejected.";
    } else if (score == 9 || score == 10) {
        msg += "You got a <b>great deal</b>, keep up the good work!";
    } else {
        msg += "Thanks for successfully agreeing a deal.";
    }

    $('#input').html(msg);

}


function send_deal(selection) {
      // Disable the send button
      // enable_button($("button#id_no_deal_button"), false);
      // enable_button($("button#id_send_msg_button"), false);
      // enable_button($("button#id_send_deal_button"), false);

      new_message_id = uuidv4();
      // your_selection = selection;
      // completion_message(your_selection, their_selection);
      // if (!their_selection) {
      //   $('#response-type-text-input').html("Waiting for your partner to enter the deal...");
      // }

      // Send a packet
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

$("button#id_send_deal_button").on('click', function () {
  send_deal('<query> some question');
});

$("button#id_no_deal_button").on('click', function () {
  send_deal("<query> another question");
});

</script>
'''
