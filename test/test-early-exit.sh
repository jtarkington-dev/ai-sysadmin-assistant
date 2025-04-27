#!/bin/bash


step_count=5

for i in $(seq 1 "$step_count"); do
  echo "Starting step $i..."
  if [ $((RANDOM % 3)) -eq 0 ]; then
    echo "Step $i failed!"
    exit 1 
  fi
  echo "Step $i completed."
done

echo "All steps completed successfully."