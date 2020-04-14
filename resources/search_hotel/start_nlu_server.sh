#!/bin/bash

MODEL_PATH=$1

rasa run --enable-api -m $MODEL_PATH/nlu-search_hotel.tar.gz -p 5008