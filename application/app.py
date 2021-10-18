from flask import Flask, request
from flask_restful import Resource, Api
from flask_cors import CORS

app = Flask(__name__)
api = Api(app)
CORS(app)

import plotly.express as px
import pandas as pd
from math import floor
import pba
from application.engine import *

from io import StringIO


@app.route("/")
def hello():
    return "Hello World!"

class Start(Resource):
    def post(self):
        default_ = 'test_3_inputs.csv'
        
        
        Q = Questionnaire()
        Q._verbose = False
        json_data = request.get_json()
        ppv = json_data['ppv']
        print(json_data['csv'])
        if json_data['csv'] == "":
            csv = default_
        else:
            csv = StringIO(json_data['csv'])
            # csv = default_
            
        if '[' in str(ppv):
            ppv = pba.I(*[float(i) for i in ppv.replace('[','').replace(']',"").split(',')])
        else:
            ppv = float(ppv)
            
        Q.load_Questionnaire_csv(csv)
        Q.generate_Questionnaire()
        Q.prevelence = ppv
        if hasattr(Q,'inc_question_ind'):
            Q.inc_question_ind = 0
            Q._increment_PPV = ppv
        print(Q.csv)
        
        question_data = Q.get_interface_Questionnaire()
        return {'Qid': list(question_data['Qid']),
            'Qtype': list(question_data['Qtype']),
            'questions': list(question_data['question_text']),
            'header': list(question_data['header']),
            'section': list(question_data['section']),
            'dependant': list(question_data['dependant'].fillna(0)),
            'description': list(question_data['description'].fillna(""))}

class Submit(Resource):
    def post(self):
        default_ = 'test_3_inputs.csv'
        
        
        Q = Questionnaire()
        Q._verbose = False
        json_data = request.get_json()
        ppv = json_data['ppv']
        if json_data['csv'] == "":
            csv = default_
        else:
            csv = StringIO(json_data['csv'])
            #csv = default_
            
        if '[' in str(ppv):
            ppv = pba.I(*[float(i) for i in ppv.replace('[','').replace(']',"").split(',')])
        else:
            ppv = float(ppv)
            
        Q.load_Questionnaire_csv(csv)
        Q.generate_Questionnaire()
        Q.prevelence = ppv
        # json_data = request.get_json()
        answers = json_data['answers']
        Q.evaluate_Questionnaire(answers)
        return {'ppv': '[%.3f,%.3f]'%(Q.final_ppv.left,Q.final_ppv.right)}
    
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
        #!TODO: make it work for other sizes
        x = [i for i in range(10) for j in range(10)]
        y = [j for i in range(10) for j in range(10)]
        ppv = request.get_json()
        N = len(x)
        red_stop = floor(N*ppv['ppvl'])
        orange_stop = floor(N*ppv['ppvr'])


        
        red_x = x[0:red_stop]
        red_y = y[0:red_stop]
        orange_x = x[red_stop:orange_stop]
        orange_y = y[red_stop:orange_stop]    
        green_x = x[orange_stop:]
        green_y = y[orange_stop:]
        print(1)
        return {
            'red_x' : red_x,
            'red_y' : red_y,
            'orange_x' : orange_x,
            'orange_y' : orange_y,
            'green_x' : green_x,
            'green_y' : green_y,
        }     

api.add_resource(Submit, '/Submit')
api.add_resource(Start,"/Start")
api.add_resource(Plot,'/Plot')

if __name__ == '__main__':
    app.run(debug=True)