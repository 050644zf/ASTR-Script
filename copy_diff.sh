#!/bin/bash  
set -e  
while read line  
do  
  mkdir -p tmp/$line && cp ArknightsStoryJson/$line tmp/$line
done <changes.txt