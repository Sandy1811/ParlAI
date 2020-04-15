#!/bin/bash

MODEL_PATH=$1

rasa run --enable-api -m $MODEL_PATH/nlu-ride_status.tar.gz -p 5007