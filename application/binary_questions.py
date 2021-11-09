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
        C_PPV = compute_npv(self.NLR, PPV)
        self.C_PPV = 1 - C_PPV
        return self.C_PPV

    def dont_know(self,PPV):
        UB = compute_ppv(self.PLR, PPV)
        LB = 1 - compute_npv(self.NLR, PPV)
        self.C_PPV = Interval([min(LB.left,UB.left), max(LB.right,UB.right)])
        return self.C_PPV

    def misc_answer(self,**predAnswer):
        # first check key is in options
        # then compoute 
        return print('TO DO')

    def _add_section_header(self,header):
        self.header = header
    
    def get_section_header(self):
        if hasattr(self,'header'):
            return self.header
        else:
            return 'Diagnosis Questions'

    def __repr__(self):
        return 'Binary question : {} \n\t +ve LR {} \n\t -ve LR {}'.format(self.question_text,self.PLR,self.NLR)


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



def compute_ppv(LR,PPV):
    C_PPV = 1/(1+(1/PPV-1)/LR)
    return C_PPV


def compute_npv(LR,NPV):
    C_PPV = 1 / (1 + (LR/((1/NPV)-1)))
    return C_PPV

def PPV(sens, spec, prev):
    if any([isinstance(p, Interval) for p in [sens, spec, prev]]):
        A = Interval(sens*prev)
        B = Interval((1-spec)*(1-prev))
        L = A.left/(A.left+B.right)
        U = A.right/(A.right+B.left)
        return Interval(L, U)
    else:
        return (sens*prev)/(sens*prev+(1-spec)*(1-prev))

def NPV(sens, spec, prev):
    if any([isinstance(p, Interval) for p in [sens, spec, prev]]):
        A = Interval((1-sens)*prev)
        B = Interval(spec*(1-prev))
        L = B.left/(B.left+A.right)
        U = B.right/(A.left+B.right)
        return Interval(L, U)
    else:
        return spec*(1-prev)/(((1-sens)*prev)+spec*(1-prev))

def LRtoSensSpec(PLR, NLR):
    specfunc = lambda LP, LN: (1-LP)/(LN-LP)
    if any([isinstance(P, Interval) for P in [PLR, NLR]]):
        PLR, NLR = Interval(PLR), Interval(NLR)
        L = specfunc(PLR.left, NLR.right)
        R = specfunc(PLR.right, NLR.left)
        spec = Interval(L, R)
        sens = Interval(PLR.left*(1-spec.left), PLR.right*(1-spec.right))
    else:
        spec = specfunc(PLR,  NLR)
        sens = PLR*(1-spec)
    return sens, spec
    
def Accuracy(sens, spec, prev):
    Accfunc = lambda s, t, p: s*p+p*(1-t)
    if any([isinstance(P, Interval) for P in [sens, spec, prev]]):
        R = Accfunc(sens.right, spec.right, prev.left)
        L = Accfunc(sens.left, spec.left, prev.right)
        Acc = Interval(L, R)
    else:
        Acc = Accfunc(sens, spec, prev)
    return Acc

def Inaccuracy(sens, spec, prev):
    return 1-Accuracy(sens, spec, prev)

def NND(sens, spec, prev):
    return 1/Accuracy(sens, spec, prev)

def NNM(sens, spec, prev):
    return 1/Inaccuracy(sens, spec, prev)