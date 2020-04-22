#!/bin/bash

# Start like: /parlai/mturk/tasks/woz/backend/bash/train_rasa_nlu_models.sh path/to//ParlAI/resources

RESOURCES_DIR=$1
RASA_VERSION_STRING=($(rasa --version))
RASA_VERSION=${RASA_VERSION_STRING[1]}

for DIR_NAME in "book_ride" "hotel_reserve" "hotel_search" "party_plan" "party_rsvp" "plane_reserve" "plane_search" "restaurant_reserve" "restaurant_search" "ride_change" "ride_status"; do
  echo "Training NLU model for $DIR_NAME..."
  rasa train nlu -u $RESOURCES_DIR/$DIR_NAME/nlu_training_data.md -c $RESOURCES_DIR/nlu_model_config.yml --out $RESOURCES_DIR/$DIR_NAME --fixed-model-name "rasa-v"$RASA_VERSION"_nlu-"$DIR_NAME
done

echo "Rasa NLU models retrained!"