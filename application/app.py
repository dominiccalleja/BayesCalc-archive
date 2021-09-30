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

default_ = StringIO('''Qid,Question,dependant,PLR0,PLR1,NLR0,NLR1
1000,Headache,,5.2,5.2,0.7,0.7
1001,Headache worse in morning?,1000,7.5,7.5,0.4,0.4
2000,Temperature,,5.4,5.4,1.3,1.3
3000,Cough,,0.6,0.6,1.3,1.3
3001,Dry Cough,3000,0.6,0.6,2,2
''')


Q = Questionaire()
Q._verbose = False
# Q.generate_questionaire()
    
# class Questions(Resource):
#     def post(self):
#         json_data = request.get_json()
#         i = json_data['i']
        
#         return {'symptom': symptoms[i],'i': i+1}

@app.route("/")
def hello():
    return "Hello World!"

class Start(Resource):
    def post(self):
        json_data = request.get_json()
        ppv = json_data['ppv']
        if json_data['csv'] == "":
            csv = default_
        else:
            csv = StringIO(json_data['csv'])
        
        if '[' in str(ppv):
            ppv = pba.I(*[float(i) for i in ppv.replace('[','').replace(']',"").split(',')])
        else:
            ppv = float(ppv)
            
        Q.load_questionaire_csv(csv)
        Q.generate_questionaire()
        Q.prevelence = ppv
        if hasattr(Q,'inc_question_ind'):
            Q.inc_question_ind = 0
            Q._increment_PPV = ppv

        return {
            'Qid': list(Q.csv['Qid']),
            'questions': list(Q.csv['Question']),
            'dependant': list(Q.csv['Dependant'].fillna(0))
            }

class Submit(Resource):
    def post(self):
        json_data = request.get_json()
        answers = json_data['answers']
        Q.evaluate_questionaire(answers)
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

        N = len(x)
        red_stop = floor(N*Q.final_ppv.left)
        orange_stop = floor(N*Q.final_ppv.right)
        
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

class Print_pdf(Resource):
    def post():
        return {}
    
api.add_resource(Submit, '/Submit')
api.add_resource(Start,"/Start")
api.add_resource(Plot,'/Plot')
api.add_resource(Print_pdf,'/Print_pdf')

if __name__ == '__main__':
    app.run(debug=True)