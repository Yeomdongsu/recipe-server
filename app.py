from flask import Flask
from flask_jwt_extended import JWTManager
from flask_restful import Api
from resources.recipe import RecipeListResource, RecipePublishResource, RecipeResource
from resources.user import UserRegisterResource
from config import Config

# flask 프레임워크를 이용한 Restful API 서버 개발

app = Flask(__name__)

# 환경변수 세팅
app.config.from_object(Config)
# JWT 매니저를 초기화
JWTManager(app)

api = Api(app)

# API를 구분해서 실행시키는 것은 HTTP method와 url의 조합이다.

# 리소스(API코드)와 경로를 연결한다.
api.add_resource(RecipeListResource, "/recipes")
api.add_resource(RecipeResource, "/recipes/<int:recipe_id>") # <타입:변수명>
api.add_resource(RecipePublishResource, "/recipes/<int:recipe_id>/publish")
api.add_resource(UserRegisterResource, "/user/register")

if __name__ == "__main__" :
    app.run()