from flask import Flask , request, jsonify , render_template
import mysql.connector
import math
import os
import re
app = Flask(__name__)


#Backend Validation Function
def validate_user_data(email , mobile , role_id , status):

    #Email
    email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    if not email or not re.match(email_pattern, email):
        return False, "Invalid email format"
    
    #mobile
    if not mobile or not mobile.isdigit() or len(mobile) != 10:
        return False ,"Mobile must be exactly 10 digits"
    
    #role_id
    try:
        role_number = int(role_id)
        if role_number < 1 or role_number > 3:
            return False , "Role ID must be between 1 and 3"
    except:
        return False , "Role ID must be a number" 
    
    #status
    if status not in ["active" , "inactive"]:
        return False , "Invalid status"
    
    return True , None


#Database Configuration

db_config = {
    "host" : "localhost",
    "user" : "root",
    "password" : "Calculus@1801",
    "database" : "render_task2" 
}

# Function to create Database Connection 

def get_db_connection():
    connection = mysql.connector.connect(**db_config)
    return connection



@app.route("/")
def home():
    return render_template("index.html")

@app.route("/test-db")
def test_db():
    try:
        
        connection = get_db_connection()
        cursor = connection.cursor()


        cursor.execute("SELECT DATABASE();")
        record = cursor.fetchone()

        cursor.close()
        connection.close()

        return f"Connected to database: {record}"
    
    
    except Exception as e:
        return f"Error: {str(e)}"




@app.route("/api/users" , methods=["GET"])
def get_users():

    try:
        #Get Query Parameters
        page = request.args.get("page" , default=1 , type=int)
        limit = request.args.get("limit" , default=10 , type=int)
        search = request.args.get("search" , default="" ,type=str)


        offset = (page - 1)*limit


        connection = get_db_connection()
        cursor = connection.cursor()

        

        #updated search 
        search = search.strip().lower()

        if search == "active" or search == "inactive":

            # Exact status match (fixes active/inactive bug)
            count_query = """
                SELECT COUNT(*)
                FROM users
                WHERE status = %s
            """
            cursor.execute(count_query, (search,))
            total_records = cursor.fetchone()[0]

            total_pages = math.ceil(total_records / limit)

            data_query = """
                SELECT id, email, mobile, role_id, status
                FROM users
                WHERE status = %s
                LIMIT %s OFFSET %s
            """
            cursor.execute(data_query, (search, limit, offset))

        else:

            search_pattern = f"%{search}%"

            count_query = """
                SELECT COUNT(*)
                FROM users
                WHERE email LIKE %s
                OR mobile LIKE %s
                OR role_id LIKE %s
                OR status LIKE %s
            """
            cursor.execute(count_query,
                        (search_pattern, search_pattern, search_pattern, search_pattern))
            total_records = cursor.fetchone()[0]

            total_pages = math.ceil(total_records / limit)

            data_query = """
                SELECT id, email, mobile, role_id, status
                FROM users
                WHERE email LIKE %s
                OR mobile LIKE %s
                OR role_id LIKE %s
                OR status LIKE %s
                LIMIT %s OFFSET %s
            """
            cursor.execute(data_query,
                        (search_pattern, search_pattern, search_pattern, search_pattern,
                            limit, offset))

            
            
        records = cursor.fetchall()
        
        users = []

        for row in records:
            user = {
               "id" : row[0],
               "email" : row[1],
               "mobile" : row[2],
               "role_id" : row[3],
               "status" : row[4]
            }
            users.append(user)

        cursor.close()
        connection.close()

        return jsonify({
            "total_records" : total_records,
            "total_pages" : total_pages,
            "current_page" : page ,
            "data" : users
        })

    except Exception as e:
        return jsonify({"error":repr(e)})
                
 #GET single User   
@app.route("/api/users/<int:user_id>", methods=["GET"])
def get_single_user(user_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT id, email, mobile, role_id, status
            FROM users
            WHERE id = %s
        """, (user_id,))

        row = cursor.fetchone()

        cursor.close()
        connection.close()

        if not row:
            return jsonify({"error": "User not found"})

        user = {
            "id": row[0],
            "email": row[1],
            "mobile": row[2],
            "role_id": row[3],
            "status": row[4]
        }

        return jsonify(user)

    except Exception as e:
        return jsonify({"error": str(e)})
    

#Create New User
@app.route("/api/users" ,methods=["POST"]) 
def create_user():
    try:
        # Get Json Data from request body
        data = request.json


        email = data.get("email")      
        mobile = data.get("mobile")
        role_id = data.get("role_id")
        status = data.get("status") 


        is_valid , error_message = validate_user_data(email , mobile , role_id , status)
        if not is_valid:
            return jsonify({"error" : error_message}) , 400
        
        connection = get_db_connection()
        cursor = connection.cursor()

        #Insert query
        insert_query = """
                INSERT INTO users(email , mobile , role_id , status)
                VALUES (%s , %s , %s , %s)
        """

        cursor.execute(insert_query,(email, mobile , role_id ,status))

        connection.commit()

        #Get last Inserted ID
        new_user_id = cursor.lastrowid
        

        cursor.close()
        connection.close()
        
        
        return jsonify ({
            "message" : "User created successfully" ,
            "user_id" : new_user_id
        })

    except Exception as e:
        return jsonify({"error": str(e)}) , 500



#Update Existing User
@app.route("/api/users/<int:user_id>" , methods=["PUT"])
def update_user(user_id):
    try:
        data = request.json

        email = data.get("email")      
        mobile = data.get("mobile")
        role_id = data.get("role_id")
        status = data.get("status")

        is_valid , error_message = validate_user_data(email ,  mobile , role_id , status)
        if not is_valid:
            return jsonify({"error" : error_message}) ,400

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("SELECT id FROM users WHERE id = %s" ,(user_id,))
        existing_user = cursor.fetchone()

        if not existing_user:
            cursor.close()
            connection.close()
            return jsonify({"error" : "User not found"})
        
        update_query = """
        UPDATE users 
        SET email = %s,
            mobile = %s,
            role_id = %s,
            status = %s
        WHERE id = %s
        """

        cursor.execute(update_query,(email,mobile,role_id,status,user_id))


        connection.commit()

        cursor.close()
        connection.close()

        return jsonify ({"message" : "User updated successfully"})
    

    except Exception as e:
        return jsonify ({"error" : str(e)})
#Delete user from databased
@app.route("/api/users/<int:user_id>" , methods=["DELETE"])
def delete_user(user_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("SELECT id FROM users WHERE id = %s" ,(user_id,))
        existing_user = cursor.fetchone()

        if not existing_user:
            cursor.close()
            connection.close()
            return jsonify({"error" : "user not found"})
        

        delete_query = "DELETE FROM users WHERE id = %s"
        cursor.execute(delete_query,(user_id,))

        connection.commit()

        cursor.close()
        connection.close()
        


        return jsonify({"message" : "User deleted successfully"})
    

    except Exception as e:
        return jsonify({"error" :str(e)})

if __name__ == "__main__":
    app.run()
