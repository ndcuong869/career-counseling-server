from flask import Flask
from flask import jsonify
from flask import request
from owlready2 import *
from career_path_finding import find_career_path_by_user
from flask_cors import CORS
from firebase_admin import credentials, firestore, initialize_app
import csv


# Connect to ontology
path = "file://C:/Users/ndcuo/Downloads/career-counseling-chatbot/career-counseling-chatbot/CareerCounselingOntology.owl"
path = "file://D:/thesis report/data/ITCareerOntology.owl"
career_onto = get_ontology(path).load()

cred = credentials.Certificate('it-career-bot-firebase-adminsdk-kyvys-870e6b3f02.json')

app = Flask(__name__)
CORS(app)

default_app = initialize_app(cred)
db = firestore.client()
auth_ref = db.collection('Authentication')
skills_ref = db.collection('JobSpecificSkill')

@app.route('/')
def hello():
    return "You are connecting to Career Counseling server."

@app.route('/api/career_paths/<occupation>')
def get_job_specific_skills(occupation):
    parameters = request.get_json()
    app.logger.debug(parameters)
    user_profile = career_onto.search(
        type=career_onto.UserProfile, has_userid=user_id)[0]
    response = []
    career_paths = find_career_path_by_user(user_profile, career_onto)
    for item in career_paths:
        response.append({
            'career_id': item.has_id[0],
            'level': item.has_level[0]
        })
    return jsonify(response)


@app.route('/api/courses')
def get_course():
    res = []
    courses = list(career_onto.search(type=career_onto.Course))
    for i, item in enumerate(courses):
        res.append({
            'course_id': 'CS10' + str(i),
            'course_name': item.course_name[0]
        })
    return jsonify(res)


@app.route('/api/courses/<course_id>')
def get_course_detail(course_id):
    res = {}
    courses = list(career_onto.search(type=career_onto.Course, has_course_id=course_id))
    res['course_id'] = courses[0].has_course_id[0]
    res['course_name'] = courses[0].has_course_name[0]
    res['duration'] = courses[0].has_course_duration[0]
    res['description'] = courses[0].has_description[0]
    res['url'] = courses[0].has_url[0]
    return res, 200

@app.route("/api/login", methods = ['POST'])
def loginHandler():
    username = request.json['username']
    password = request.json['password']
    users = auth_ref.where('username', '==', username)\
                    .where('password', '==', password)\
                    .stream()
    users = list(users)
    if len(users) <= 0:
        return jsonify({}), 401
    else:
        current_user = users[0]
        app.logger.debug(current_user.id)
        return jsonify({
            'id': current_user.id
        }), 200


@app.route("/api/skills", methods = ['GET'])
def skillHandler():
    result = []
    search_params = [
        {"type": career_onto.Technology, "text": 'Technology'},
        {"type": career_onto.TechnicalSkill, "text": 'TechnicalSkill'},
        {"type": career_onto.Knowledge, "text": 'Knowledge'}
    ]
    for param in search_params:
        skills = career_onto.search(type=param["type"])
        for item in skills:
            result.append({
                "id": item.has_skill_id[0],
                "name": item.has_skill_name[0],
                "type": param["text"]
            })

    return jsonify(result), 200
    # all_skills = [doc.to_dict() for doc in skills_ref.stream()]
    # return jsonify(all_skills), 200

@app.route("/api/skills/update", methods=['GET'])
def updateSkillHandler():
    auto_id = 1
    with open('skills.csv', 'r') as file:
        reader = csv.reader(file, delimiter = ',')
        for row in reader:
            skills_ref.document(str(auto_id)).set({
                "id": auto_id,
                "name": row[0],
                "type": row[1]
            })
            auto_id = auto_id + 1

        return {}, 200

if __name__ == '__main__':
    app.run(debug=True)
