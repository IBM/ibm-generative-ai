#!/bin/bash

files_to_remove="$(poe test --type integration | grep -o "Can't overwrite existing cassette ([^)]*)" | sed "s/.*('\(.*\)').*/\1/p" | sort | uniq)"

if [ -z "$files_to_remove" ]; then
  echo "No casettes to rewrite"
  exit 0
fi

echo "Files to remove:"
for file in $files_to_remove; do
  echo $file
done;

read -rp "Proceed? (y/N) " response
response=$(echo "$response" | tr '[:upper:]' '[:lower:]')

if [[ "$response" == "y" ]]; then
  rm -f $files_to_remove
  poe test --type integration -- --record-mode once
else
  exit 1
fi
