from flask import (
    Flask, render_template, redirect, url_for,
    request, send_from_directory
)
import datetime
import subprocess
import os
import time
import shutil

app = Flask(__name__)

STOCK_REPO_PATH = "/Users/fuma/code/newsclouds-stock"

@app.route("/")
def index():
    today = datetime.date.today()
    cloud = today.strftime("%Y%m%d")

    # Read News
    news_file = "./%s/%s.txt" % (cloud, cloud)
    try:
        with open(news_file, 'r') as f:
            news = f.read()
    except FileNotFoundError:
        news = ''

    # Read Frequencies
    freq_file = "./%s/%s.freq.txt" % (cloud, cloud)
    try:
        with open(freq_file, 'r') as f:
            freq = f.read()
    except FileNotFoundError:
        freq = ''

    # Read Config
    config_file = "./%s/%s.config.json" % (cloud, cloud)
    try:
        with open(config_file, 'r') as f:
            config = f.read()
    except FileNotFoundError:
        config = ''

    # Image
    image_file = "./%s/%s.png" % (cloud, cloud)
    t = int(time.time())
    image_url =  "/dailyclouds/%s/%s.png?t=%s" % (cloud, cloud, t)
    image_exist = os.path.isfile(image_file)

    return render_template("dailycloud.html", cloud=cloud, news=news,
                           freq=freq, config=config, image_url=image_url,
                           image_exist=image_exist)

@app.route("/", methods=['POST'])
def make_cloud():
    today = datetime.date.today()
    cloud = today.strftime("%Y%m%d")

    if os.path.isdir(cloud):
        # Write Frequencies
        freq_file = "./%s/%s.freq.txt" % (cloud, cloud)
        with open(freq_file, "w") as outfile:
            outfile.write(request.form['freq'])

        # Read Config
        config_file = "./%s/%s.config.json" % (cloud, cloud)
        with open(config_file, "w") as outfile:
            outfile.write(request.form['config'])

    subprocess.check_call(["python", "dailycloud.py"])

    return redirect(url_for("index"))

@app.route("/dailyclouds/<path:path>")
def static_dailyclouds(path):
    return send_from_directory('', path)

@app.route("/clean-all", methods=['POST'])
def clean_all():
    today = datetime.date.today()
    cloud = today.strftime("%Y%m%d")

    shutil.rmtree(cloud, ignore_errors=True)

    subprocess.check_call(["python", "dailycloud.py"])

    return redirect(url_for("index"))

@app.route("/clean-config", methods=['POST'])
def clean_config():
    today = datetime.date.today()
    cloud = today.strftime("%Y%m%d")

    config_file = "./%s/%s.config.json" % (cloud, cloud)
    os.remove(config_file)

    subprocess.check_call(["python", "dailycloud.py"])

    return redirect(url_for("index"))

@app.route("/clean-freq", methods=['POST'])
def clean_freq():
    today = datetime.date.today()
    cloud = today.strftime("%Y%m%d")

    freq_file = "./%s/%s.freq.txt" % (cloud, cloud)
    os.remove(freq_file)

    subprocess.check_call(["python", "dailycloud.py"])

    return redirect(url_for("index"))

@app.route("/deploy", methods=['POST'])
def deploy():
    today = datetime.date.today()
    cloud = today.strftime("%Y%m%d")

    if os.path.isdir(cloud):
        # Copy generated cloud
        shutil.copytree(cloud, os.path.join(STOCK_REPO_PATH, cloud))

        # Commmit new cloud
        origWD = os.getcwd()
        os.chdir(STOCK_REPO_PATH)
        subprocess.check_call(["git", "add", cloud])
        subprocess.check_call(["git", "commit", "-m", cloud])
        subprocess.check_call(["git", "push", "origin", "master"])
        os.chdir(origWD)

    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
