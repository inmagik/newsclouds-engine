#!/bin/bash
source ./env/bin/activate
python deploy.py /srv/newsclouds-gatsby > deploy_cloud.log 2>&1
