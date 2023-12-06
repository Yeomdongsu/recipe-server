from flask import request
from flask_restful import Resource
from mysql_connection import get_connection
from mysql.connector import Error
from utils import hash_password

class UserRegisterResource(Resource) :
    def post(self) :
        data = request.get_json()

        connection = get_connection()

        try :
            query = '''
                    insert into user
                    (username, email, password)
                    values
                    (%s, %s, %s);                    
                    '''
            
            password = hash_password(data["password"])

            record = (data["username"], data["email"], password)

            cursor = connection.cursor()
            cursor.execute(query, record)

            connection.commit()

            cursor.close()
            connection.close()

        except Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {"result" : "fail", "error" : str(e)}, 500

        return {"result" : "success"}, 200    