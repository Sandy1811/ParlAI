#!/bin/bash

MODEL_PATH=$1

rasa run --enable-api -m $MODEL_PATH/nlu-change_ride.tar.gz -p 5006