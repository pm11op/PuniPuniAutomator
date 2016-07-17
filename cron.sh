#!/bin/bash
source /Users/masaru/.bashrc
date +"%Y%m%d %H:%M:%S" >> /var/log/puni.log 
/usr/local/bin/python /Users/masaru/Projects/punipuni/src/battle.py
