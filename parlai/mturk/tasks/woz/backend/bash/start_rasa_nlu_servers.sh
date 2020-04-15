#!/bin/bash

# Start like: /parlai/mturk/tasks/woz/backend/bash/start_rasa_nlu_servers.sh path/to//ParlAI/resources &

RESOURCES_DIR=$1

$RESOURCES_DIR/book_ride/start_nlu_server.sh $RESOURCES_DIR/book_ride &
$RESOURCES_DIR/change_ride/start_nlu_server.sh $RESOURCES_DIR/change_ride &
$RESOURCES_DIR/ride_status/start_nlu_server.sh $RESOURCES_DIR/ride_status &
$RESOURCES_DIR/search_hotel/start_nlu_server.sh $RESOURCES_DIR/search_hotel &

echo "Rasa NLU servers started!"