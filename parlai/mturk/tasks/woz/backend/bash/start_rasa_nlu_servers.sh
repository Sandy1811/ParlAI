#!/bin/bash

# Start like: /parlai/mturk/tasks/woz/backend/bash/start_rasa_nlu_servers.sh path/to//ParlAI/resources &

RESOURCES_DIR=$1

$RESOURCES_DIR/book_ride/start_nlu_server.sh $RESOURCES_DIR/book_ride
$RESOURCES_DIR/ride_change/start_nlu_server.sh $RESOURCES_DIR/ride_change
$RESOURCES_DIR/ride_status/start_nlu_server.sh $RESOURCES_DIR/ride_status
$RESOURCES_DIR/hotel_search/start_nlu_server.sh $RESOURCES_DIR/hotel_search
$RESOURCES_DIR/hotel_reserve/start_nlu_server.sh $RESOURCES_DIR/hotel_reserve
$RESOURCES_DIR/plane_reserve/start_nlu_server.sh $RESOURCES_DIR/plane_reserve
$RESOURCES_DIR/apartment_search/start_nlu_server.sh $RESOURCES_DIR/apartment_search
$RESOURCES_DIR/book_apartment_viewing/start_nlu_server.sh $RESOURCES_DIR/book_apartment_viewing
$RESOURCES_DIR/book_doctor_appointment/start_nlu_server.sh $RESOURCES_DIR/book_doctor_appointment
$RESOURCES_DIR/followup_doctor_appointment/start_nlu_server.sh $RESOURCES_DIR/followup_doctor_appointment
$RESOURCES_DIR/spaceship_access_codes/start_nlu_server.sh $RESOURCES_DIR/spaceship_access_codes
$RESOURCES_DIR/spaceship_life_support/start_nlu_server.sh $RESOURCES_DIR/spaceship_life_support

echo "Rasa NLU servers started!"