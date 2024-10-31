#!/bin/bash  
mkdir tmp
cd ArknightsStoryJson
set -e  
while read line  
do  
  cp $line ../tmp --parents
done <../changes.txt