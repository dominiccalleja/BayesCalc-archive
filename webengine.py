from flask import Flask, request
from flask_restful import Resource, Api
from flask_cors import CORS
app = Flask(__name__)
api = Api(app)
CORS(app)

symptoms = ['headache','temperature','cough']
class Questionare(Resource):
    def post(self):
        json_data = request.get_json()
        i = json_data['i']
        
        return {'symptom': symptoms[i],'i': i+1}
    
api.add_resource(Questionare, '/Questionare')

if __name__ == '__main__':
    app.run(port = 5000, debug=False)