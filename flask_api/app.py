from flask import Flask, jsonify, request
from flask_marshmallow import Marshmallow
from marshmallow import fields, ValidationError
import mysql.connector


from mysql.connector import Error



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


if __name__ == '__main__':
    app.run(debug= True)