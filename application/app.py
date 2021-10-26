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
        _verbose = False
        default_ = 'test_3_inputs.csv'
        
        
        
        json_data = request.get_json()
        ppv = json_data['ppv']
        try:
            compute_option = json_data['compute_ratio']
        except:
            compute_option = 'precise'
        if _verbose: print(json_data['csv'])
        if json_data['csv'] == "":
            csv = default_
        else:
            csv = StringIO(json_data['csv'])
            # csv = default_
            
        if '[' in str(ppv):
            ppv = pba.I(*[float(i) for i in ppv.replace('[','').replace(']',"").split(',')])
        else:
            ppv = float(ppv)

        Q = Questionnaire(csv)
        Q._verbose = False
        Q.generate_Questionnaire(compute_option)
        Q.prevelence = ppv
        if hasattr(Q,'inc_question_ind'):
            Q.inc_question_ind = 0
            Q._increment_PPV = ppv
        if _verbose: print(Q.csv)
        
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
        _verbose = False
        default_ = 'test_3_inputs.csv'
        json_data = request.get_json()
        ppv = json_data['ppv']
        try:
            compute_option = json_data['compute_ratio']
        except:
            compute_option = 'precise'
        if json_data['csv'] == "":
            csv = default_
        else:
            csv = StringIO(json_data['csv'])
            # csv = default_
        
        if _verbose: print('Working Questionnaire...')
        if _verbose: print(csv)
            
        if '[' in str(ppv):
            ppv = pba.I(*[float(i) for i in ppv.replace('[','').replace(']',"").split(',')])
        else:
            ppv = float(ppv)

        Q = Questionnaire(csv)
        Q.generate_Questionnaire(compute_option)
        Q.prevelence = ppv
        # json_data = request.get_json()
        answers = json_data['answers']
        Q.evaluate_Questionnaire(answers)
        inc_ppv = ['[{:.3f},{:.3f}]'.format(i.left,i.right) for i in Q.ppv_store ]
        return {'ppv': '[%.3f,%.3f]'%(Q.final_ppv.left,Q.final_ppv.right), 'incremental_ppv':inc_ppv}
    
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

def string2interval(JSint):
    if '[' in JSint:
        Int = JSint.replace('[','').replace(']','').split(',')
        Int = [float(i) for i in Int]
    elif isinstance(JSint, float):
        Int = JSint
    return Interval(Int)

class Whatiftest(Resource):
    
    def post(self):
        json_data = request.get_json() 
        print('Sense: {}'.format(json_data['sensitivity']))
        print('Sense: {}'.format(json_data['specificity']))
        print(json_data['ppv'])
        PPV = string2interval(json_data['ppv']) #json_data['ppv'].replace('[','').replace(']','').split(',')
        print(PPV)
        #TODO make sens spec interval and float sensitive 
        
        test = Test(json_data['sensitivity'],json_data['specificity'],PPV)
        #test
        Yes, No = test.what_if()
        return {'sensitivity':json_data['sensitivity'],
                'specificity':json_data['specificity'],
                'PPV_YES':'[%.3f,%.3f]'%(Yes.left,Yes.right),
                'PPV_NO':'[%.3f,%.3f]'%(No.left,No.right)}


api.add_resource(Submit, '/Submit')
api.add_resource(Start,"/Start")
api.add_resource(Whatiftest,"/testthetest")
api.add_resource(Plot,'/Plot')

if __name__ == '__main__':
    app.run(debug=True)