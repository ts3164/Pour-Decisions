#!/usr/bin/env python3
import json
import random
import re
import sys
import os

from flask import Flask, redirect, url_for
from flask import render_template
from flask import Response, request, jsonify
from markupsafe import Markup

app = Flask(__name__)


user_learn_info = {
    'time_started': None,
}
user_quiz_info = {}


def load_wines():
    """
    Load wines from the JSON file.
    :return: a python dictionary mapping wine name to image, pairing list, description, and next wine.

    """
    with open('wines.json') as file:
        data = json.load(file)
    return data


def get_next_wine_id(cur_wine_id: int) -> str:
    """
    Wrap around the wine index if necessary.
    """
    if cur_wine_id >= len(wines):
        return "1"
    return str(cur_wine_id + 1)

def load_quiz():
    file_path = os.path.join(app.static_folder, 'quiz.json')
    with open(file_path) as file:
        quiz_data = json.load(file)
    return quiz_data


def get_next_quiz_id(current_id):
    # Logic to get the next quiz ID
    return str(int(current_id) + 1)


# Runs on server startup. Get the wines, then mark them all as unseen.
wines = load_wines()
quizzes = load_quiz()
for wine_id, wine_details in wines.items():
    wine_details['seen'] = False


# ROUTES
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/getwines')
def get_wines():
    return jsonify(wines)

@app.route('/mark_as_seen/<wine_id>')
def mark_as_seen(wine_id):
    wines[wine_id]['seen'] = True
    return jsonify(wines)

@app.route('/mark_as_unseen/<wine_id>')
def mark_as_unseen(wine_id):
    wines[wine_id]['seen'] = False
    return jsonify(wines)

@app.route('/learn/<wine_num>')
def learn(wine_num):
    wine_to_render = wines[wine_num]
    wine_to_render['seen'] = True

    return render_template('wine_details.html', wine=wine_to_render, next_id=get_next_wine_id(int(wine_num)),
                           prev_id=str(int(wine_num) - 1), curr_id=wine_num)

@app.route('/wines')
def all_wines():
    return render_template('all_wines.html', wines=wines)


@app.route('/quiz/<quiz_num>')
def quiz(quiz_num):
    quiz_to_render = quizzes.get(quiz_num)
    if not quiz_to_render:
        return "Quiz not found", 404
    next_id = get_next_quiz_id(quiz_num)
    return render_template('quiz.html', quiz=quiz_to_render, next_id=next_id)

@app.route('/learn/record/time', methods=["POST"])
def record_time():
    """
    Internal route that timestamps the user's learn session.
    """
    json_data = request.get_json()

    if user_learn_info['time_started'] is None and 'time_started' in json_data:
        user_learn_info['time_started'] = json_data['time_started']
    elif 'time_finished' in json_data:
        user_learn_info['time_started'] = json_data['time_finished']

    return jsonify({'redirect': url_for('all_wines'), 'time_started': user_learn_info['time_started']})


@app.route('/submit_quiz', methods=['POST'])
def submit_quiz():
    data = request.get_json()
    score = data['score']
    total_questions = data['totalQuestions']
    # Optionally save or process data here
    return jsonify({'url': url_for('quiz_results', score=score, total_questions=total_questions)})


@app.route('/results')
def quiz_results():
    score = request.args.get('score', default=0, type=int)
    total_questions = request.args.get('total_questions', default=0, type=int)
    return render_template('quiz_result.html', score=score, total_questions=total_questions)





if __name__ == '__main__':
    app.run(debug=True, port=3200)
