import pathlib as Path
from posixpath import join

import pandas as pd
import time

from pba import Interval, sometimes, always

import matplotlib.pyplot as plt
import matplotlib as mpl

from io import StringIO

try: 
    home = Path.Path(__file__).parent
except:
    home = Path.Path('__file__').parent

# default_csv_file = StringIO('''Qid,Question,dependant,PLR0,PLR1,NLR0,NLR1
# 1000,Headache,,5.2,5.2,0.7,0.7
# 1001,Headache worse in morning?,1000,7.5,7.5,0.4,0.4
# 2000,Temperature,,5.4,5.4,1.3,1.3
# 3000,Cough,,0.6,0.6,1.3,1.3
# 3001,Dry Cough,3000,0.6,0.6,2,2
# ''')

class Question_Methods:

    def _add_question(self, question, question_number = ''):
        self.question_text = question
        self.question_number = question_number

    def get_question(self):
        return self.question_text

    def _add_options(self,*predValue):
        self.option_type = 'misc'
        self.options = {}
        for k, v in predValue:
            self.options[k] = v 

        #### These answers are still a bloody mess. Need to split them up into more sensible methods too! 
            # Might even be an idea to stick them in their own class!!! 

    def yes(self,PPV):
        self.C_PPV = compute_ppv(self.PLR, PPV)
        return self.C_PPV

    def no(self,PPV):
        #C_PPV = compute_ppv(self.NLR, self.PPV)
        C_PPV = compute_npv(self.NLR, PPV)
        self.C_PPV = 1 - C_PPV
        #self.
        return self.C_PPV

    def dont_know(self,PPV):
        UB = compute_ppv(self.PLR, PPV)
        LB = compute_npv(self.NLR, PPV)
        self.C_PPV = Interval([LB.left, UB.right])
        return self.C_PPV

    def misc_answer(self,**predAnswer):
        # first check key is in options
        # then compoute 
        return print('TO DO')

    def _add_section_header(self,header):
        self.header = header
    
    def get_section_header(self):
        if hasattr(self,'header'):
            return header
        else:
            return 'Diagnosis Questions'

    def __repr__(self):
        return 'Question {}:  {} \n\t +ve LR {} \n\t -ve LR {}'.format(self.question_text,self.question_number, self.PLR,self.NLR)


class Question(Question_Methods):
    option_type = 'DEFAULT'
    
    dfi = Interval([1, 1]) #default_interval
    #use_sensitivity_specificity = False

    def __init__(self, PLR=None, NLR=None, sensitivity=None, specificity=None):

        #TODO fix the error handling for the weird combos of different stats
        if PLR is not None:
            assert NLR is not None
            assert sensitivity is None and specificity is None
        else:
            assert sensitivity is not None and specificity is not None
            if specificity == 1:
                specificity = .9999999
                            
            PLR = sensitivity/(1-specificity)
            NLR = (1-sensitivity)/specificity
        
        self.PLR = Interval(PLR)
        self.NLR = Interval(NLR)

        self.options = {1: 'yes', 0: 'no', 2: 'Dont Know'}
        super().__init__()