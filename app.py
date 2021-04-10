from logging import debug
import logging
from flask import Flask
from flask import jsonify
from flask import request
from owlready2 import *

# Connect to ontology
path = "file://C:/Users/ndcuo/Jupyter notebooks/CareerCounselingOntology.owl"
career_onto = get_ontology(path).load()

app = Flask(__name__)

@app.route('/')
def hello():
    return "You are connecting to Career Counseling server."

@app.route('/<job_role>/career_paths')
def get_job_specific_skills(job_role=None):
    logging.info(career_onto.search(type=career_onto.JobRole))
    job_role = career_onto.search(type=career_onto.JobRole, has_name=job_role)
    career_paths = career_onto.search(of_job_role=job_role)
    response = []
    for item in career_paths:
        response.append({
            'career_id': item.has_id[0],
            'level': item.has_level[0]
        })
    return jsonify(response)

@app.route('/courses')
def get_course():
    res = []
    courses = list(career_onto.search(type=career_onto.Course))
    for i, item in enumerate(courses):
        res.append({
            'course_id': 'CS10' + str(i),
            'course_name': item.course_name[0]
        })
    return jsonify(res)

@app.route('/courses/{course_id}')
def get_course_detail(course_id):
    res = {}
    courses = list(career_onto.search(type=onto.Course))
    return res

if __name__ == '__main__':
    app.run(debug=True)