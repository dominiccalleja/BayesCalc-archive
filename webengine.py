from flask import Flask, request
from flask_restful import Resource, Api
from flask_cors import CORS
app = Flask(__name__)
api = Api(app)
CORS(app)

import plotly.express as px
import pandas as pd

from engine import *
Q = Questionaire()
Q._verbose = False
# Q.generate_questionaire()
    
# class Questions(Resource):
#     def post(self):
#         json_data = request.get_json()
#         i = json_data['i']
        
#         return {'symptom': symptoms[i],'i': i+1}

class Start(Resource):
    def post(self):
        json_data = request.get_json()
        ppv = float(json_data['ppv'])
        Q.load_questionaire_csv('test_3_inputs.csv')
        Q.generate_questionaire()
        Q.prevelence = ppv
        if hasattr(Q,'inc_question_ind'):
            Q.inc_question_ind = 0
            Q._increment_PPV = ppv

        return {'symptom': Q.get_next_symptom()}
    
class Yes(Resource):
    def post(self):

        Q.answer_next_question(True)
        return {
            'ppv': str(Q._increment_PPV),
            'symptom': Q.get_next_symptom()
        }
        
class No(Resource):
    def post(self):

        Q.answer_next_question(False)
        return {
            'ppv': str(Q._increment_PPV),
            'symptom': Q.get_next_symptom()
        }
        
class Dunno(Resource):
    def post(self):

        Q.answer_next_question(2)
        return {
            'ppv': str(Q._increment_PPV),
            'symptom': Q.get_next_symptom()
        }
        
def print_fact_array(ppv: Interval):
    #!TODO: make it work for other sizes
    x = [i for i in range(10) for j in range(10)]
    y = [j for i in range(10) for j in range(10)]

    N = len(x)
    col = []
    for i in range(N):
        if i/N < ppv.left:
            col.append('sick')
        elif i/N < ppv.right:
            col.append('dunno')
        else:
            col.append('well')
    

    fig = px.scatter(pd.DataFrame({'x':x,'y':y,'col':col}), x='x',y='y',color = 'col')
    fig.update_traces(marker=dict(size=12))
    return fig.to_html(full_html=False)
    
class Plot(Resource):
    def post(self):

        return {
            'plot': print_fact_array(Q._increment_PPV)
        }     

api.add_resource(Yes, '/Yes')
api.add_resource(No, '/No')
api.add_resource(Dunno, '/Dunno')
api.add_resource(Start,"/Start")
api.add_resource(Plot,'/Plot')
if __name__ == '__main__':
    app.run(host="0.0.0.0")