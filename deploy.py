#!/usr/bin/env python

import json
import os
import subprocess
import datetime
import shutil
from dateutil.parser import parse

def main():
    today = datetime.date.today()
    today_prefix = today.strftime("%Y%m%d")

    frotend_repo_path = '/Users/fuma/code/newsclouds-gatsby'

    # Create the cloud
    subprocess.check_call(["python", "dailycloud.py"])

    # Move clouds dir
    shutil.move(today_prefix, os.path.join('dailyclouds', today_prefix))

    # Create the clouds json
    clouds = []
    for entry in os.listdir('dailyclouds'):
        if entry.startswith('.'):
            continue

        clouds.append({
            'name': entry,
            'date': parse(entry).strftime('%Y-%m-%d'),
            'image': '/dailyclouds/%s/%s.image.png' % (entry, entry, ),
            'txt': None,
        })

    # Pull repo
    subprocess.check_call(["git", "pull", "origin", "master"], cwd=frotend_repo_path)

    # Copy clouds json
    shutil.rmtree(os.path.join(frotend_repo_path, 'static', 'dailyclouds'), ignore_errors=True)
    shutil.copytree('dailyclouds', os.path.join(frotend_repo_path, 'static', 'dailyclouds'))

    # Write clouds file
    with open(os.path.join(frotend_repo_path, 'data', 'clouds.json'), "w") as outfile:
        json.dump(clouds, outfile)

    # Deploy to 2 world
    # subprocess.check_call(["yarn", "deploy"], cwd=frotend_repo_path)
    subprocess.check_call(["npm", "run", "deploy"], cwd=frotend_repo_path)


if __name__ == '__main__':
    main()
