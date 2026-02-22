from flask import Flask , request, jsonify , render_template
import mysql.connector
import math
import os
app = Flask(__name__)


#Database Configuration


db_config = {
    "host": os.environ.get("DB_HOST"),
    "user": os.environ.get("DB_USER"),
    "password": os.environ.get("DB_PASSWORD"),
    "database": os.environ.get("DB_NAME"),
    "port": int(os.environ.get("DB_PORT"))
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

        search_pattern = f"%{search}%"


         
        #Count Query (with search)
        count_query = """
            SELECT COUNT(*)
            FROM users
            WHERE email LIKE %s
            OR mobile LIKE %s
            OR role_id LIKE %s
            OR status LIKE %s
        """
        cursor.execute(count_query,(search_pattern,search_pattern,search_pattern,search_pattern))
        total_records = cursor.fetchone()[0]

        total_pages = math.ceil(total_records/limit)

        #Fetch Paginated Users
        data_query = """
            SELECT id , email , mobile , role_id , status
            FROM users
            WHERE email LIKE %s
            OR MOBILE LIKE %s
            OR role_id LIKE %s
            OR status LIKE %s
            LIMIT %s OFFSET %s
                    
        """
        cursor.execute(data_query ,
                       (search_pattern,search_pattern,search_pattern,search_pattern,
                        limit , offset))

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


        if not email or not mobile:
            return jsonify({"error" : "Email and Mobile are recquired"})
        
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
