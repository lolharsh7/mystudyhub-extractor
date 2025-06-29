
from flask import Flask, jsonify, render_template, request
import requests
from bs4 import BeautifulSoup
import urllib.parse
import os

app = Flask(__name__)

BASE_URL = "https://www.mystudyhub.site/RWA/"
headers = {
    "User-Agent": "Mozilla/5.0"
}


def get_subjects(batch_id):
    url = f"{BASE_URL}details.php?id={batch_id}"
    resp = requests.get(url, headers=headers)
    soup = BeautifulSoup(resp.text, 'html.parser')
    subjects = []
    for a in soup.find_all('a', href=True):
        if "topics.php?courseid=" in a['href']:
            parts = urllib.parse.parse_qs(urllib.parse.urlparse(a['href']).query)
            subjects.append({
                "subject_name": a.text.strip(),
                "subject_id": parts['subjectid'][0]
            })
    return subjects


def get_topics(batch_id, subject_id):
    url = f"{BASE_URL}topics.php?courseid={batch_id}&subjectid={subject_id}"
    resp = requests.get(url, headers=headers)
    soup = BeautifulSoup(resp.text, 'html.parser')
    topics = []
    for a in soup.find_all('a', href=True):
        if "concepts.php?courseid=" in a['href']:
            parts = urllib.parse.parse_qs(urllib.parse.urlparse(a['href']).query)
            topics.append({
                "topic_name": a.text.strip(),
                "topic_id": parts['topicid'][0]
            })
    return topics


def get_classes(batch_id, subject_id, topic_id):
    url = f"{BASE_URL}contents.php?courseid={batch_id}&subjectid={subject_id}&topicid={topic_id}&conceptid=1"
    resp = requests.get(url, headers=headers)
    soup = BeautifulSoup(resp.text, 'html.parser')
    classes = []
    for a in soup.find_all('a', href=True):
        if "watch.php?courseid=" in a['href'] and "id=" in a['href']:
            parts = urllib.parse.parse_qs(urllib.parse.urlparse(a['href']).query)
            classes.append({
                "class_name": a.text.strip(),
                "class_id": parts['id'][0]
            })
    return classes


def get_video_links(batch_id, class_id):
    url = f"{BASE_URL}watch.php?courseid={batch_id}&id={class_id}"
    resp = requests.get(url, headers=headers)
    soup = BeautifulSoup(resp.text, 'html.parser')
    links = []
    for a in soup.find_all('a', href=True):
        if "watch.php?url=" in a['href']:
            parsed = urllib.parse.parse_qs(urllib.parse.urlparse(a['href']).query)
            stream_url = urllib.parse.unquote(parsed['url'][0])
            links.append({
                "quality": a.text.strip(),
                "link": stream_url
            })
    return links


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/batch/<batch_id>')
def batch_data(batch_id):
    subjects = get_subjects(batch_id)
    return jsonify(subjects)


@app.route('/topics')
def topics():
    batch_id = request.args.get("batch_id")
    subject_id = request.args.get("subject_id")
    topics = get_topics(batch_id, subject_id)
    return jsonify(topics)


@app.route('/classes')
def classes():
    batch_id = request.args.get("batch_id")
    subject_id = request.args.get("subject_id")
    topic_id = request.args.get("topic_id")
    classes = get_classes(batch_id, subject_id, topic_id)
    return jsonify(classes)


@app.route('/videos')
def videos():
    batch_id = request.args.get("batch_id")
    class_id = request.args.get("class_id")
    links = get_video_links(batch_id, class_id)
    return jsonify(links)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
