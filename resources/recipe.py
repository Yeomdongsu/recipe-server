from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from mysql_connection import get_connection
from mysql.connector import Error

# resources 폴더 안에 만드는 파일에는 API를 만들기 위한 클래스를 작성한다.
# API를 만들기 위해서는 flask_restful 라이브러리의 Resource 클래스를 상속해야한다.

class RecipeListResource(Resource) :

    # http Method와 동일한 함수명으로 오버라이딩!

    # jwt 토큰이 헤더에 필수로 있어야 한다는 뜻
    # 토큰이 없으면 이 API는 실행이 안된다.
    @jwt_required()
    def post(self) :
        
        # 1. 클라이언트가 보내준 데이터가 있으면 그 데이터를 먼저 받아준다.
        data = request.get_json()

        # 1-1. 헤더에 JWT 토큰이 있으면 토큰정보도 받아준다.
        # 토큰에서, 토큰 만들때 사용한 데이터를 복호화 해서 가져다 준다.
        user_id = get_jwt_identity()
        
        # 2. 받아온 레시피 데이터를 DB에 저장해야 한다.
        try :
            # 2-1 db에 연결하는 코드
            connection = get_connection()

            # 2-2 쿼리문 만들기 - insert 쿼리만들기
            query = '''insert into recipe
                        (user_id, name, description, num_of_servings, cook_time, directions)
                        values
                        (%s, %s, %s, %s, %s, %s);
                    '''
            
            # 2-3 위의 쿼리에 매칭되는 변수를 처리해 준다.
            # 단 라이브러리 특성상 튜플로 만들어야 한다.
            record = (user_id, data["name"], data["description"], data["num_of_servings"],
                      data["cook_time"], data["directions"])
            
            # 2-4 커서를 가져온다.
            cursor = connection.cursor()

            # 2-5 위의 쿼리문을 커서로 실행한다.
            cursor.execute(query, record)

            # 2-6 커밋해줘야 DB에 완전히 반영된다.
            connection.commit()

            # 2-7 자원해제
            cursor.close()
            connection.close()

        except Error as e :
            print(e)
            cursor.close()
            connection.close()

            # 유저한테 알려줘야 한다.
            return {"result" : "fail", "error" : str(e)}, 500

        # 3. DB에 잘 저장됐으면 클라이언트에게 응답해준다.
        # 보내줄 정보(json)와 http 상태코드를 return한다.

        return {"result" : "success"}, 200

    def get(self) :

        # 1. 클라이언트로부터 데이터를 받아온다.
        # 없음

        # 2. db에 저장된 데이터를 가져온다
        try :
            connection = get_connection()
            
            query = '''
                    select * 
                    from recipe;
                    '''
            
            # 중요!! Select문에서 cursor를 만들 때 
            # 클라이언트에게 json 형식으로 보내줘야 하기 때문에
            # cursor() 함수의 인자 dictionary = True로 해준다.
            # 하지 않으면 리스트와 튜플의 형식으로 받아 온다.
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute(query)

            result_list = cursor.fetchall()

            # datetime은 파이썬에서 사용하는 데이터타입이므로 json 형식이 아니다
            # json은 문자열, 숫자만 가능하므로 datetime을 문자열로 바꿔줘야 한다 

            i = 0
            for row in result_list :
                result_list[i]["created_at"] = row["created_at"].isoformat()
                result_list[i]["updated_at"] = row["updated_at"].isoformat()
                i = i+1
            
            cursor.close()
            connection.close()

        except Error as e :
            print(e)
            cursor.close()
            connection.close()

            # # 유저한테 알려줘야 한다.
            return {"result" : "fail", "error" : str(e)}, 500
        
        return {"result" : "success", "items" : result_list, "count" : len(result_list)}, 200
    
class RecipeResource(Resource) :
    # Path(경로)에 숫자나 문자가 바뀌면서 처리되는 경우에는
    # 해당 변수를 파라미터에 꼭 써줘야 한다.

    # GET, DELETE 메소드는 Body에 데이터를 전달하지 않는다.
    def get(self, recipe_id) :

        # 1. 클라이언트로부터 데이터를 받아온다.
        # 이미 경로에 들어있는 recipe_id 변수에 레시피 아이디를 받아왔다.

        # 2. db에서 레시피 아이디에 해당하는 레시피 1개를 받아온다.
        try :
            connection = get_connection()

            query = '''
                    select * 
                    from recipe
                    where id = %s;
                    '''
            
            record = (recipe_id, )

            cursor = connection.cursor(dictionary=True)

            cursor.execute(query, record)

            # fetchall() 함수는 항상 결과를 리스트로 리턴한다
            result_list = cursor.fetchall()
            
            i = 0
            for row in result_list :
                result_list[i]["created_at"] = row["created_at"].isoformat()
                result_list[i]["updated_at"] = row["updated_at"].isoformat()
                i = i+1

            cursor.close()
            connection.close()

        except Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {"result" : "fail", "error" : str(e)}, 500

        # result_list에 데이터가 있는 경우와 없는 경우를 체크하여 보낸다.
        if len(result_list) == 0 :
            return {"result" : "fail", "message" : "해당 데이터가 없습니다."}, 400
        else :
            return {"result" : "success", "item" : result_list}, 200
        
    @jwt_required()    
    def put(self, recipe_id) : 
        
        # 1. 클라이언트로부터 데이터를 받아온다.
        data = request.get_json()

        user_id = get_jwt_identity()
        print(recipe_id, user_id)
        try :
            connection = get_connection()

            query = '''
                    update recipe
                    set name = %s, description = %s, num_of_servings = %s, cook_time = %s, directions = %s 
                    where id = %s and user_id = %s; 
                    '''

            record = (data["name"], data["description"], data["num_of_servings"],
                      data["cook_time"], data["directions"], recipe_id, user_id)
            
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
    
    @jwt_required()
    def delete(self, recipe_id) :

        user_id = get_jwt_identity()
        print(recipe_id, user_id)
        
        try : 
            connection = get_connection()

            query = '''
                    delete from recipe
                    where id = %s and user_id = %s;
                    '''

            record = (recipe_id, user_id)

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
    
class RecipePublishResource(Resource) :
    
    def put(self, recipe_id) :

        try :
            connection = get_connection()

            query = '''
                    update recipe
                    set is_publish = 1
                    where id = %s;
                    '''
            
            record = (recipe_id, )

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
    
    def delete(self, recipe_id) :

        try :
            connection = get_connection()

            query = '''
                    update recipe
                    set is_publish = 0
                    where id = %s;
                    '''
            
            record = (recipe_id, )

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
    
class RecipeMeResource(Resource) :

    @jwt_required()
    def get(self) :
        
        user_id = get_jwt_identity()

        try :     
            connection = get_connection()

            query = '''
                    select * 
                    from recipe
                    where user_id = %s;
                    '''
            record = (user_id, )

            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)

            myList = cursor.fetchall()

            i = 0
            for row in myList :
                myList[i]["created_at"] = row["created_at"].isoformat()
                myList[i]["updated_at"] = row["updated_at"].isoformat()
                i = i+1

            cursor.close()
            connection.close()

        except Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {"result" : "fail", "error" : str(e)}, 500

        if len(myList) == 0 :
            return {"error" : "작성한 레시피가 없습니다."}, 400

        return {"result" : "success", "items" : myList, "count" : len(myList)}, 200