import pathlib as Path
from posixpath import join

import pandas as pd
from pba import divideIntervals ,subtractIntervals ,multiplyIntervals ,addIntervals

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

    def __init__(self):
        print('Initialising with the default questionaire: \n \t{}'.format(self.default_csv_file))
        self.load_questionaire_csv(self.default_csv_file)

    def load_questionaire_csv(self,csv_file):
        self.csv = pd.read_csv(csv_file, index_col=[0])

    def generate_questionaire(self):

        for i in self.csv.index:
            qid = self.csv.iloc[i]['Qid']
            question = self.csv.iloc[i]['Question']
            PLR = [self.csv.iloc[i]['PLR0'], self.csv.iloc[i]['PLR1']]
            NLR = [self.csv.iloc[i]['NLR0'], self.csv.iloc[i]['NLR1']]
            self._init_question(qid,question,PLR,NLR)

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
            elif inp == 0:
                ppv = self.question_dict[qId0].no()
            else:
                ppv = self.question_dict[qId0].dont_know()
            
            print('i : {} \n ppv: {}'.format(i,ppv))

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

        


import numpy as np
Q = Questionaire()
Q.generate_questionaire()
    
ans = np.zeros(len(Q.question_dict))

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
