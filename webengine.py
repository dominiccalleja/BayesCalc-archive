from flask import Flask, request
from flask_restful import Resource, Api
from flask_cors import CORS
app = Flask(__name__)
api = Api(app)
CORS(app)

from engine import *
Q = Questionaire()
Q._verbose = False
Q.generate_questionaire()
    
# class Questions(Resource):
#     def post(self):
#         json_data = request.get_json()
#         i = json_data['i']
        
#         return {'symptom': symptoms[i],'i': i+1}
class GetFirstSymptom(Resource):
    def post(self):
        print(Q.get_next_symptom())
        return {'symptom': Q.get_next_symptom()}
    
class Yes(Resource):
    def post(self):
        json_data = request.get_json()
        # ppv = json_data['ppv']
        Q.answer_next_question(1)
        return {
            'ppv': str(Q._increment_PPV),
            'symptom': Q.get_next_symptom()
        }
        
class No(Resource):
    def post(self):
        json_data = request.get_json()
        # ppv = json_data['ppv']
        Q.answer_next_question(1)
        return {
            'ppv': str(Q._increment_PPV),
            'symptom': Q.get_next_symptom()
        }
        
class Dunno(Resource):
    def post(self):
        json_data = request.get_json()
        # ppv = json_data['ppv']
        Q.answer_next_question(1)
        return {
            'ppv': str(Q._increment_PPV),
            'symptom': Q.get_next_symptom()
        }
        

api.add_resource(Yes, '/Yes')
api.add_resource(No, '/No')
api.add_resource(Dunno, '/Dunno')

api.add_resource(GetFirstSymptom,"/GetFirstSymptom")

if __name__ == '__main__':
    app.run(port = 5000, debug=False)