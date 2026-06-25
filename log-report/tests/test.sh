#!/bin/bash
# pytest + pytest-json-ctrf are baked into the environment image (environment/Dockerfile),
# so nothing is installed here at verify time.

mkdir -p /logs/verifier

# Run the suite and emit a CTRF report alongside the raw output.
pytest /tests/test_outputs.py -rA --ctrf /logs/verifier/ctrf.json

# Harbor reads the reward from /logs/verifier/reward.txt (1 = pass, 0 = fail).
if [ $? -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi
