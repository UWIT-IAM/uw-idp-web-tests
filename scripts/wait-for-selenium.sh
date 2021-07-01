#!/usr/bin/env bash

echo "Waiting for selenium to be ready . . ."

while [[ "$ready" != 'true' ]]
do
  status=$(curl -sq http://selenium-hub:4444/wd/hub/status)
  ready=$(echo $status | jq -s .[0].value.ready)
  sleep 1
done
