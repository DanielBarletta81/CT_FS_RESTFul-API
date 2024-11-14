from flask import Flask, jsonify, request
from flask_marshmallow import Marshmallow
from marshmallow import fields, ValidationError
import mysql.connector


from mysql.connector import Error

#Task 1

app = Flask(__name__)
ma = Marshmallow(app)

class MemberSchema(ma.Schema):
    id = fields.String(required=True)
    name = fields.String(required=True)
    age = fields.String(required=True)

    class Meta:
        fields = ("id", "name", "age")

member_schema = MemberSchema()
members_schema = MemberSchema(many=True)


def get_db_connection():

    db_name = "Gym_Members"
    user = "root"
    password = "Babinz2023!"
    host = "localhost"

    try:
      conn = mysql.connector.connect(
         database = db_name,
         user = user,
         password = password,
         host = host
      )
      print("Successful connection to MySQL database.")
      return conn
    
    except Error as e:
      print(f'An exception occurred{e}')
      return None



#Task 2 Setting up API endpoints for Members

@app.route('/', methods =['GET'])

def home():
    return "Welcome to the Fitness Center DB!!"

@app.route('/members', methods=['GET'])

def get_members():
   try:
     conn = get_db_connection()
     if conn is None:
        return jsonify({"error": "Database connection failed."}), 500
     cursor = conn.cursor(dictionary=True)

     query = 'SELECT * FROM Members'

     cursor.execute(query)

     members = cursor.fetchall()

     return members_schema.jsonify(members)


   except Error as e:
     print(f'Error: {e}')
     return jsonify({"error": "Internal Server Error."}), 500
   
   finally:
     if conn and conn.is_connected():
        cursor.close()
        conn.close()


@app.route('/members', methods=['POST'])
def add_a_member():
   try:
     member_data = member_schema.load(request.json)
   except ValidationError as e:
     print(f'Validation Error: {e}')
     return jsonify(e.messages), 400

   try:
     conn = get_db_connection()
     if conn is None:
        return jsonify({"error": "Database connection failed."}), 500
     cursor = conn.cursor(dictionary=True)

     new_member = (member_data["id"], member_data["name"], member_data["age"])
     query = 'INSERT INTO Members(id, name, age) VALUES (%s, %s, %s)'

     cursor.execute(query, new_member)

     conn.commit()     

     return jsonify({"message": "New member added successfully"}), 201

   except Error as e:
     print(f'Error: {e}')
     return jsonify({"error": "Internal Server Error."}), 500
   
   finally:
     if conn and conn.is_connected():
        cursor.close()
        conn.close()

@app.route('/members/<int:id>', methods=['PUT'])
def update_member(id):
   try:
     # use member_schema(singular) to retrieve member by Id
     member_data = member_schema.load(request.json)
     #catch errors in input during update
   except ValidationError as e:
     print(f'Validation Error: {e}')
     return jsonify(e.messages), 400

   try: # try to connect to db
     conn = get_db_connection()
     if conn is None:
        return jsonify({"error": "Database connection failed."}), 500
     #set up cursor
     cursor = conn.cursor(dictionary=True)
# set variable to hold member info for update
     updated_member = (member_data['id'], member_data['name'], member_data['age'], id)
     query = "UPDATE Members SET id = %s, name= %s, age= %s WHERE id= %s"

     cursor.execute(query, updated_member)

     conn.commit()     

     return jsonify({"message": "Member updated successfully"}), 201

   except Error as e:
     print(f'Error: {e}')
     return jsonify({"error": "Internal Server Error."}), 500
   
   finally:
     if conn and conn.is_connected():
        cursor.close()
        conn.close()

@app.route('/members/<int:id>', methods=['DELETE'])
def delete_member(id):
   
   try:
     conn = get_db_connection()
     if conn is None:
        return jsonify({"error": "Database connection failed."}), 500
     cursor = conn.cursor(dictionary=True)

     member_to_delete = (id,)
      
     cursor.execute("SELECT * FROM Members WHERE id = %s", member_to_delete )
     member = cursor.fetchone()
     if not member:
        return jsonify({"error": "Member not found"}), 404

     query = "DELETE FROM Members  WHERE id= %s"

     cursor.execute(query, member_to_delete)

     conn.commit()     

     return jsonify({"message": "Member deleted successfully"}), 201

   except Error as e:
     print(f'Error: {e}')
     return jsonify({"error": "Internal Server Error."}), 500
   
   finally:
     if conn and conn.is_connected():
        cursor.close()
        conn.close()

class SessionSchema(ma.Schema):
    session_id = fields.Integer(required=True)
    member_id = fields.Integer(required=True)
    session_date = fields.Date(required=True)
    session_time = fields.String(required=True)
    activity = fields.String()
    

    
     
  #  FOREIGN KEY (member_id) REFERENCES Members(id)
    class Meta:
        fields = ("session_id", "member_id", "session_date", "session_time", "activity")

session_schema = SessionSchema()
sessions_schema = SessionSchema(many=True)

# Task 3 Setting up routes to manage workout sessions
# 
#     
@app.route('/sessions', methods=['GET'])

def get_sessions():
   try:
     conn = get_db_connection()
     if conn is None:
        return jsonify({"Error": "Database connection failed."}), 500
     cursor = conn.cursor(dictionary=True)

     query = 'SELECT * FROM WorkoutSessions'

     cursor.execute(query)

     sessions = cursor.fetchall()

     return sessions_schema.jsonify(sessions)


   except Error as e:
     print(f'Error: {e}')
     return jsonify({"error": "Internal Server Error."}), 500
   
   finally:
     if conn and conn.is_connected():
        cursor.close()
        conn.close()


@app.route('/sessions', methods=['POST'])
def add_a_session():
   try:
     session_data = session_schema.load(request.json)
   except ValidationError as e:
     print(f'Validation Error: {e}')
     return jsonify(e.messages), 400

   try:
     conn = get_db_connection()
     if conn is None:
        return jsonify({"error": "Database connection failed."}), 500
     cursor = conn.cursor(dictionary=True)
# 
     new_session = (session_data["session_id"], session_data["member_id"], session_data["session_date"] , session_data["session_time"], session_data["activity"])
     query = 'INSERT INTO WorkoutSessions(id, name, age) VALUES (%s, %s, %s, %s, %s)'

     cursor.execute(query, new_session)

     conn.commit()     

     return jsonify({"message": "New workout session added successfully"}), 201

   except Error as e:
     print(f'Error: {e}')
     return jsonify({"error": "Internal Server Error."}), 500
   
   finally:
     if conn and conn.is_connected():
        cursor.close()
        conn.close()

@app.route('/sessions/<int:session_id>', methods=['PUT'])
def update_session(session_id):
   try:
     # use member_schema(singular) to retrieve member by Id
     session_data = session_schema.load(request.json)
     #catch errors in input during update
   except ValidationError as e:
     print(f'Validation Error: {e}')
     return jsonify(e.messages), 400

   try: # try to connect to db
     conn = get_db_connection()
     if conn is None:
        return jsonify({"error": "Database connection failed."}), 500
     #set up cursor
     cursor = conn.cursor(dictionary=True)
# set variable to hold session info for update
     updated_session = (session_data["session_id"], session_data["member_id"], session_data["session_date"] , session_data["session_time"], session_data["activity"], session_id)
     query = 'UPDATE WorkoutSessions SET session_id = %s, member_id = %s, session_date = %s, session_time = %s, activity = %s WHERE session_id= %s'

     cursor.execute(query, updated_session)

     conn.commit()     

     return jsonify({"message": "Workout session updated successfully"}), 201

   except Error as e:
     print(f'Error: {e}')
     return jsonify({"error": "Internal Server Error."}), 500
   
   finally:
     if conn and conn.is_connected():
        cursor.close()
        conn.close()

@app.route('/sessions/<int:id>', methods=['DELETE'])
def delete_session(session_id):
   
   try:
     conn = get_db_connection()
     if conn is None:
        return jsonify({"error": "Database connection failed."}), 500
     cursor = conn.cursor(dictionary=True)

     session_to_delete = (session_id,)
     query = 'SELECT * FROM sessions WHERE session_id = %s'
      
     cursor.execute(query, session_to_delete)
     session = cursor.fetchone()
     if not session:
        return jsonify({"error": "Session not found"}), 404

     delete_query = "DELETE FROM WorkoutSessions WHERE session_id= %s"

     cursor.execute(delete_query, session_to_delete)

     conn.commit()     

     return jsonify({"message": "Session deleted successfully"}), 201

   except Error as e:
     print(f'Error: {e}')
     return jsonify({"error": "Internal Server Error."}), 500
   
   finally:
     if conn and conn.is_connected():
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug= True)