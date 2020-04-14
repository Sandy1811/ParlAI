#!/bin/bash

for PORT_NR in 5005 5006 5007 5008; do
  PID=$(lsof -i :$PORT_NR | awk 'NR > 1 {print $2}')
  kill -9 $PID
done

echo "Rasa NLU servers stopped!"