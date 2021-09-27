import pathlib as Path
from posixpath import join

import pandas as pd
from pba import divideIntervals ,subtractIntervals ,multiplyIntervals ,addIntervals

import matplotlib.pyplot as plt
import matplotlib as mpl

mpl

home = Path.Path(__file__).parent

default_csv_file = 'default_question_library.csv'


class Question:
    option_type = 'DEFAULT'
    default_interval = [1,1]
    dfi = default_interval
    PPV = 0.5
    def __init__(self, PLR, NLR):
        self.PLR = PLR
        self.NLR = NLR
        self.options = {1: 'yes', 0: 'no', 2: 'Dont Know'}
    
    def _inherit_PPV(self,PPV):
        self.PPV = PPV

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
        A = divideIntervals(self.dfi, self.PLR)
        B = subtractIntervals(A, self.dfi)

        C = multiplyIntervals(A,B)
        D = addIntervals(self.dfi, C)
        self.C_PPV =divideIntervals(self.dfi, D)
        
        return self.C_PPV

    def no(self):
        A = divideIntervals(self.dfi, self.PPV)

        const = divideIntervals(self.NLR, 
                                subtractIntervals(A, self.dfi))
        NPV = divideIntervals(self.dfi, addIntervals(self.dfi, const))
        self.C_PPV =subtractIntervals(self.dfi, NPV)
        
        return self.C_PPV

    def dont_know(self):
        A = divideIntervals(self.dfi, self.PPV)

        B = subtractIntervals(A, self.dfi)
        C = divideIntervals(self.dfi,self.PLR)
        D = multiplyIntervals(B,C)
        ppv_U = divideIntervals(self.dfi, addIntervals(self.dfi, D))

        const = divideIntervals(self.NPV, subtractIntervals(A, self.dfi))
        NPV = divideIntervals(self.dfi, addIntervals(self.dfi, const))
        ppv_L = subtractIntervals(self.dfi, NPV)
        ppv = ppv_L + ppv_U
        self.C_PPV =[np.min(ppv), np.max(ppv)]
        
        return self.C_PPV

    def misc_answer(self,**predAnswer):
        # first check key is in options
        # then compoute 
        return self


class Questionaire:
    default_csv_file = join(home,default_csv_file)
    _verbose = True
    def __init__(self):
        print('Initialising with the default questionaire: \n \t{}'.format(self.default_csv_file))
        self.load_questionaire_csv(self.default_csv_file)

    def load_questionaire_csv(self,csv_file):
        self.csv = pd.read_csv(csv_file, index_col=[0])

    def generate_questionaire(self):

        for i in self.csv.index:
            qid = self.csv.loc[i]['Qid']
            question = self.csv.loc[i]['Question']
            PLR = [self.csv.loc[i]['PLR0'], self.csv.loc[i]['PLR1']]
            NLR = [self.csv.loc[i]['NLR0'], self.csv.loc[i]['NLR1']]
            self._init_question(qid,question,PLR,NLR)
            if self._verbose:
                print('Question {} - {}'.format(qid,question))

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

        for i, inp in enumerate(inputs):
            qId0 = list(self.question_dict.keys())[i]
            if inp == 1:
                ppv = self.question_dict[qId0].yes()
                ans = 'yes'
            elif inp == 0:
                ppv = self.question_dict[qId0].no()
                no = 'no'
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


class ICON_ARRAY:

    out_of = 10000
    marker = 'o'
    n_rows = 50
    n_cols = out_of/n_rows
    colors = ['red', 'orange', 'gray']
    other_string = 'unaffected'
    scale = 10

    def __init__(self, **kwargs):
        classes = {}
        for key, value in kwargs.items():
            classes[key] = value

        self.classes = classes

    def plot(self, **kwargs):

        x = np.arange(int(n_cols/self.scale))
        y = np.arange(int(n_rows/self.scale))

        X, Y = np.meshgrid(x, y)
        xx = np.hstack(X)
        yy = np.hstack(Y)

        fig, ax = plt.subplots(1, 1, figsize=(n_cols/10, n_rows/10))
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
len(Q.question_dict)


IA = ICON_ARRAY(killed = 10,ill=240)
IA.scale = 5
IA.plot(s=90)




ans = np.zeros(Q.csv.index)

Q.evaluate_questionaire(ans)



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
