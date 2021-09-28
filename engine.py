import pathlib as Path
from posixpath import join

import pandas as pd
import time
#from pba import divideIntervals ,subtractIntervals ,multiplyIntervals ,addIntervals

from pba import Interval

import matplotlib.pyplot as plt
import matplotlib as mpl



try: 
    home = Path.Path(__file__).parent
except:
    home = Path.Path('__file__').parent

default_csv_file = 'default_question_library.csv'


class Question:
    option_type = 'DEFAULT'
    
    dfi = Interval([1, 1]) #default_interval
    PPV = Interval(0.01)

    def __init__(self, PLR, NLR):
        self.PLR = Interval(PLR)
        self.NLR = Interval(NLR)
        self.options = {1: 'yes', 0: 'no', 2: 'Dont Know'}
    
    def _inherit_PPV(self,PPV):
        self.PPV = Interval(PPV)

    def _add_question(self, question):
        self.question_text = question

    def get_question(self):
        return self.question_text

    def _add_options(self,*predValue):
        self.option_type = 'misc'
        self.options = {}
        for k, v in predValue:
            self.options[k] = v 

        #### These answers are still a bloody mess. Need to split them up into more sensible methods too! 
            # Might even be an idea to stick them in their own class!!! 

    def yes(self):
        self.C_PPV = compute_ppv(self.PLR, self.PPV)
        return self.C_PPV

    def no(self):
        self.C_PPV = compute_npv(self.NLR, self.PPV)
        return self.C_PPV

    def dont_know(self):
        UB = compute_ppv(self.PLR, self.PPV)
        LB = compute_npv(self.NLR, self.PPV)
        self.C_PPV = Interval([LB.left, UB.right])
        return self.C_PPV

    def misc_answer(self,**predAnswer):
        # first check key is in options
        # then compoute 
        return self


class Questionaire:
    default_csv_file = join(home,default_csv_file)
    _verbose = True
    PPV = prevelence = 0.5

    def __init__(self):
        print('Initialising with the default questionaire: \n \t{}'.format(self.default_csv_file))
        self.load_questionaire_csv(self.default_csv_file)

    def load_questionaire_csv(self,csv_file):
        if csv_file.split('.')[-1] == 'csv':
            self.csv = pd.read_csv(csv_file, index_col=[0])
        elif csv_file.split('.')[-1] == 'xlsx' or csv_file.split()[-1] == 'xls':
            self.csv = pd.read_csv(csv_file, index_col=[0])

    def generate_questionaire(self):

        for i in self.csv.index:
            qid = self.csv.loc[i]['Qid']
            question = self.csv.loc[i]['Question']
            PLR = [self.csv.loc[i]['PLR0'], self.csv.loc[i]['PLR1']]
            NLR = [self.csv.loc[i]['NLR0'], self.csv.loc[i]['NLR1']]
            self._init_question(i,question,PLR,NLR)
            if self._verbose:
                print('Question {} - {} [{}]'.format(i,question, qid))

    def get_N_questions(self):
        return len(self.csv.index)
    
    def get_final_question_id(self):
        return self.csv.iloc[self.get_N_questions()]['Qid']

    def _init_question(self, qId, question, PLR, NLR):
        if not hasattr(self,'question_dict'):
            print('Generating new questionaire')
            self.question_dict = {}
        
        self.question_dict[qId] = Question(PLR,NLR)
        self.question_dict[qId]._add_question(question)

    def evaluate_questionaire(self, inputs):
        
        self.question_dict[0].PPV = Interval(self.prevelence)

        for i, inp in enumerate(inputs):
            qId0 = list(self.question_dict.keys())[i]
            if inp:
                ppv = self.question_dict[qId0].yes()
                ans = 'yes'
            elif not inp:
                ppv = self.question_dict[qId0].no()
                ans = 'no'
            else:
                ppv = self.question_dict[qId0].dont_know()
                ans = 'dont know'
            
            if self._verbose:
                print('Q : {} \n\tAns : {}  \n\t ppv: {}'.format(
                    self.question_dict[qId0].get_question(), ans, ppv))

            if i == self.get_N_questions()-1:
                self.final_ppv = ppv
                return self.final_ppv
            
            qId1 = list(self.question_dict.keys())[i+1]
            self.question_dict[qId1]._inherit_PPV(ppv)
            

    def get_final_ppv(self):
        if not hasattr(self, 'final_ppv'):
            print(
                'Error: You have not computed the PPV. Pass answers to self.evaluate_questionaire(inputs)')
        else:
            return self.final_ppv

def compute_ppv(LR,PPV):
    C_PPV = 1/(1+(1/PPV-1)/LR)
    return C_PPV


def compute_npv(LR,NPV):
    C_PPV = 1 / (1 + (LR/((1/NPV)-1)))
    return C_PPV


class ICON_ARRAY:

    out_of = 10000
    marker = 'o'
    n_rows = 50
    colors = ['red', 'orange', 'gray']
    other_string = 'unaffected'
    scale = 10
    n_cols = out_of/n_rows
    def __init__(self, **kwargs):
        classes = {}
        for key, value in kwargs.items():
            classes[key] = value

        self.classes = classes

    def plot(self, **kwargs):

        x = np.arange(int(self.n_cols/self.scale))
        y = np.arange(int(self.n_rows/self.scale))

        X, Y = np.meshgrid(x, y)
        xx = np.hstack(X)
        yy = np.hstack(Y)

        fig, ax = plt.subplots(1, 1, figsize=(self.n_cols/10, self.n_rows/10))
        missing = []
        i = 0
        v0 = 0
        labels = []
        for key, value in self.classes.items():
            value = int(value/self.scale)
            ax.scatter(xx[v0:v0+value], yy[v0:v0+value],
                       marker='o', c=self.colors[i], label=key, **kwargs)
            missing.append(value)
            labels.append(key)
            v0 = v0+value
            i = i+1

        ax.scatter(xx[v0:], yy[v0:], marker='o',
                   c=self.colors[i], label=self.other_string, **kwargs)
        ax.axes.xaxis.set_ticks([])
        ax.axes.yaxis.set_ticks([])
        ax.legend(labels, loc="lower center",
                  bbox_to_anchor=(0.1, -0.2), fontsize=15)
        fig.subplots_adjust(bottom=0.1)
        plt.show()








import numpy as np
Q = Questionaire()
Q.generate_questionaire()
len(Q.csv.index.values)
len(Q.question_dict.keys())

ans = np.ones(len(Q.csv.index))
Q.evaluate_questionaire(ans)


IA = ICON_ARRAY(killed = 10,ill=240)
IA.scale = 5
IA.plot(s=90)




"""
Testing with reduced questions
"""
csv_test = '/Users/dominiccalleja/GCA_App/test_3_inputs.csv'
Qtest = Questionaire()
Qtest.load_questionaire_csv( csv_test)
Qtest.generate_questionaire()


ans = np.ones(len(Qtest.csv.index))
all_true = Qtest.evaluate_questionaire(ans)

ans = np.zero(len(Qtest.csv.index))
all_false = Qtest.evaluate_questionaire(ans)





def computePrevelanceModel(gen, ag):

        from pba import linear_interpolate as li

        male_age_prev = {'Age': [50, 60, 70, 80, 90],
                        'Prevelance_Lower': [46/100000, 46/100000, 90/100000, 275/100000, 600/100000],
                        'Prevelance_Upper': [156/100000, 160/100000, 170/100000, 450/100000, 700/100000]}

        female_age_prev = {'Age': [50, 60, 70, 80, 90],
                        'Prevelance_Lower': [46/100000, 46/100000, 250/100000, 1000/100000, 1700/100000],
                           'Prevelance_Upper': [156/100000, 160/100000, 300/100000, 1200/100000, 1900/100000]}

        if (gen == 'male' and ag < 50):
            prev = [0.001, 0.001]

        elif (gen == 'male' and ag <= 90):
            prev_lower = li(male_age_prev['Age'],
                            male_age_prev['Prevelance_Lower'], ag)
            prev_upper = li(male_age_prev['Age'],
                            male_age_prev['Prevelance_Upper'], ag)
            prev = [prev_lower, prev_upper]

        elif (gen == 'male' and ag > 90):
            prev_lower = li(male_age_prev['Age'],
                            male_age_prev['Prevelance_Lower'], 90)
            prev_upper = li(male_age_prev['Age'],
                            male_age_prev['Prevelance_Upper'], 90)
            prev = [prev_lower, prev_upper]

        if (gen == 'female' and ag <= 50):
            prev = [0.001, 0.001]

        elif (gen == 'female' and ag <= 90):
            prev_lower = li(
                female_age_prev['Age'], female_age_prev['Prevelance_Lower'], ag)
            prev_upper = li(
                female_age_prev['Age'], female_age_prev['Prevelance_Upper'], ag)
            prev = [prev_lower, prev_upper]

        elif (gen == 'female' and ag > 90):
            prev_lower = li(
                female_age_prev['Age'], female_age_prev['Prevelance_Lower'], 90)
            prev_upper = li(
                female_age_prev['Age'], female_age_prev['Prevelance_Upper'], 90)
            prev = [prev_lower, prev_upper]

        return prev
    # compute prevelance from gender and age
    vprev1 = computePrevelanceModel(gender, age)
