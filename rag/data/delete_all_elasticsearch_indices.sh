#!/bin/bash

# Retrieve the list of indices
indices=$(curl -X GET "http://localhost:9200/_cat/indices?h=index" | awk '{print $1}')

# Delete each index
for index in $indices
do
  echo "Deleting index: $index"
  curl -X DELETE "http://localhost:9200/$index"
done

echo "All indices deleted."
