#!/bin/bash  
mkdir tmp
cd ArknightsStoryJson
set -e  
while read line  
do  
  echo $line
  cp $line ../tmp --parents
done <../changes.txt