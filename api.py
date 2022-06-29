import os
from queue import Empty

from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
import dotenv
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from marshmallow import Schema, fields

dotenv.load_dotenv()

db_user = os.environ.get('DB_USERNAME')
db_pass = os.environ.get('DB_PASSWORD')
db_hostname = os.environ.get('DB_HOSTNAME')
db_name = os.environ.get('DB_NAME')

DB_URI = 'mysql+pymysql://{db_username}:{db_password}@{db_host}/{database}'.format(db_username=db_user, db_password=db_pass, db_host=db_hostname, database=db_name)

engine = create_engine(DB_URI, echo=True)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Student(db.Model):
    __tablename__ = "student"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    cellphone = db.Column(db.String(13), unique=True, nullable=False)

    @classmethod
    def get_all(cls):
        return cls.query.all()
    
    @classmethod
    def get_by_id(cls, id):
        return cls.query.get_or_404(id)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

class StudentSchema(Schema):
    id = fields.Integer()
    name = fields.Str()
    email = fields.Str()
    age = fields.Integer()
    cellphone = fields.Str()

student_schema = StudentSchema

@app.route('/', methods = ['GET'])
def home():
    return jsonify('<p>Hello from students API!</p>'), 200

@app.route('/api', methods = ['GET'])
def api_main():
    return render_template('doc.html'), 200

@app.route('/api/students', methods=['GET'])
def get_all_students():
    students = Student.get_all()
    student_list = StudentSchema(many=True)
    response = student_list.dump(students)
    return jsonify(response), 200

@app.route('/api/students/get/<int:id>', methods = ['GET'])
def get_student(id):
    student_info = Student.get_by_id(id)
    serializer = StudentSchema()
    response = serializer.dump(student_info)
    return jsonify(response), 200

@app.route('/api/students/add', methods = ['POST'])
def add_student():
    json_data = request.get_json()
    new_student = Student(
        name= json_data.get('name'),
        email=json_data.get('email'),
        age=json_data.get('age'),
        cellphone=json_data.get('cellphone')
    )
    new_student.save()
    serializer = StudentSchema()
    data = serializer.dump(new_student)
    return jsonify(data), 201

@app.route('/api/students/modify/<int:id>', methods = ['PATCH'])
def modify_student(id):
    student = Student.get_by_id(id)
    
    student_json = request.get_json()
    stud_name = student_json.get('name'),
    stud_email = student_json.get('email'),
    stud_age = student_json.get('age'),
    stud_cellphone = student_json.get('cellphone')

    if 'name' in student_json:
        student.name = stud_name
    if 'email' in student_json:
        student.email = stud_email
    if 'age' in student_json:
        student.age = stud_age
    if 'cellphone' in student_json:
        student.cellphone = stud_cellphone
    try:
        student.save()
        serializer = StudentSchema()
        data = serializer.dump(student)
        return jsonify(data), 200
    except Exception as e:
        print(e)
        return 304 #jsonify(error="Something go wrong")

@app.route('/api/students/change/<int:id>', methods = ['PUT'])
def change_student(id):
    student = Student.get_by_id(id)
    
    student_json = request.get_json()
    stud_name = student_json.get('name'),
    stud_email = student_json.get('email'),
    stud_age = student_json.get('age'),
    stud_cellphone = student_json.get('cellphone')

    #check that get all nessesery fields 
    if 'name' in student_json and 'email' in student_json and 'age' in student_json and 'cellphone' in student_json:
        student.name = stud_name
        student.email = stud_email
        student.age = stud_age
        student.cellphone = stud_cellphone
    else:
        return jsonify(responce='You need input all data fields '+
        '{name,email,age,cellphone}')
    try:
        student.save()
        serializer = StudentSchema()
        data = serializer.dump(student)
        return jsonify(data), 200
    except Exception as e:
        print(e)
        return 304 #jsonify(error="Something go wrong")

@app.route('/api/deleteStudent/<int:id>', methods = ['DELETE'])
def delete_student(id):
    try:
        student = Student.get_by_id(id)
        student.delete()
    except Exception as e:
        print(e)
        return 304
    return jsonify(response="Student was deleted"), 200

@app.route('/api/health-check/ok', methods = ['GET'])
def health_check_ok():
    return jsonify(response="All`s OK"), 200

@app.route('/api/health-check/bad', methods = ['GET'])
def health_check_bad():
    return jsonify(response="It's just for testing, right?"), 500

    
if __name__ == '__main__':
    engine = create_engine(DB_URI, echo=True)
    if not database_exists(engine.url):
        create_database(engine.url)
    db.create_all()
    app.run(host="0.0.0.0", debug=True, port=8081)
