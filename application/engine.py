import pathlib as Path
from posixpath import join
import re

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

from application.binary_questions import *
from application.scalar_questions import *


class Test(Question_Methods):

    def __init__(self, sensitivity, specificity, PPV):
        super().__init__(sensitivity=sensitivity, specificity=sensitivity)
        self._PPV_pretest = PPV
    
    def what_if(self):

        if_positive = self.yes(self._PPV_pretest)
        if_negative = self.no(self._PPV_pretest)

        test_string = []
        test_string.append('Should you administer a test?')
        test_string.append( 'This patients has a current PPV of {}'.format(self._PPV_pretest))
        test_string.append('\n\t A positive test would give the patient a PPV of {}'.format(if_positive))
        test_string.append('\n\t A negative test would give the patient a PPV of {}'.format(if_negative))
    
        print(*test_string)


class Questionaire(Test):
    default_csv_file = str(home.parent)+'/test_3_inputs.csv'
    _verbose = True
    prevelence = 0.5
    def __init__(self):
        print('Initialising with the default questionaire: \n \t{}'.format(self.default_csv_file))
        self.load_questionaire_csv(self.default_csv_file)

    def load_questionaire_csv(self,csv_file):
        self.csv = pd.read_csv(csv_file)
        # if csv_file.split('.')[-1] == 'csv':
        #     self.csv = pd.read_csv(csv_file, index_col=None)
        # elif csv_file.split('.')[-1] == 'xlsx' or csv_file.split()[-1] == 'xls':
        #     self.csv = pd.read_csv(csv_file, index_col=None)

    def generate_questionaire(self):
        self._check_existing_questions()
        ### Remove this once we are all using the up to dat csv format
        if [i for i in self.csv.columns if i == 'Qtype']:
            self.__new_method_generate_questionaire()
        else:
            self.__deprecated_generate_questionaire()

        #if self._verbose:
        #    print('Question {} - {} [{}]'.format(i,question, qid))

    ## Activate subsiquent with an option in generate questionaire! 
    def compute_with_midpoint(self):
        return 'TODO impliment to change the .csv to the midpoint'
    
    def compute_with_endpoint(self, right=True):
        return 'TODO impliment to change the .csv to the endpoint'

    def compute_with_mean(self):
        return 'TODO impliment to change the .csv to the PLR/NLR variables'

    def __new_method_generate_questionaire(self):
        Qtype = self.csv.Qtype.values
        for i in self.csv.index:
            qid = self.csv.loc[i]['Qid']
            if Qtype[i] == 'H':
                header = self.csv.loc[i]['Question']

            elif Qtype[i] == 'S':
                Squestion = self.csv.loc[i]['Question']
                j = i +1
                PLRs = []
                NLRs = []
                thresholds = []
                while Qtype[j] == 'SA':
                    PLRs.append([self.csv.loc[j]['PLR0'], self.csv.loc[j]['PLR1']])
                    NLRs.append([self.csv.loc[j]['NLR0'], self.csv.loc[j]['NLR1']])
                    thresholds.append(float(re.findall(r'\d+',self.csv.loc[j]['Question'])[0])) ### Need to seperate the carrat
                    j+=1
                self._init_scalar_question(i, Squestion, thresholds, PLRs, NLRs)

            elif Qtype[i] == 'Sa':
                break
            
            elif Qtype[i] == 'B':
                question = self.csv.loc[i]['Question']
                PLR = [self.csv.loc[i]['PLR0'], self.csv.loc[i]['PLR1']]
                NLR = [self.csv.loc[i]['NLR0'], self.csv.loc[i]['NLR1']]
                self._init_binary_question(i,question,PLR,NLR)   

    def __deprecated_generate_questionaire(self):
        for i in self.csv.index:
            qid = self.csv.loc[i]['Qid']
            question = self.csv.loc[i]['Question']
            PLR = [self.csv.loc[i]['PLR0'], self.csv.loc[i]['PLR1']]
            NLR = [self.csv.loc[i]['NLR0'], self.csv.loc[i]['NLR1']]
            self._init_binary_question(i,question,PLR,NLR)      

    def get_N_questions(self):
        return len(self.csv.index)
    
    def get_final_question_id(self):
        return self.csv.iloc[self.get_N_questions()]['Qid']

    def _check_existing_questions(self):
        if not hasattr(self,'question_dict'):
            print('Generating new questionaire')
            self.question_dict = {}

    def _init_binary_question(self, qId, question, PLR, NLR):
        self.question_dict[qId] = Question(PLR,NLR)
        self.question_dict[qId]._add_question(question)

    def _init_scalar_question(self,qId_0, question, thresholds, PLRs, NLRs):
        scalar_question = Binarize(thresholds, PLRs, NLRs)
        scalar_question.generate_tree()

        self.question_dict[qId_0] = scalar_question.get_tree()
        self.question_dict[qId_0].root._add_question(question) #

    def evaluate_questionaire(self, inputs):
        
        PPV = Interval(self.prevelence)

        for i, inp in enumerate(inputs):
            qId0 = list(self.question_dict.keys())[i]
            PPV = self.answer_question(qId0,inp,PPV)
            if self._verbose:
                print('Q : {} \n\tAns : {}  \n\t ppv: {}'.format(
                    self.question_dict[qId0].get_question(), inp, PPV))
        self.final_ppv = PPV

    def answer_question(self,QID, answer, PPV):
        if answer == 1:
            ppv = self.question_dict[QID].yes(PPV)
            ans = 'yes'
        elif answer == 0:
            ppv = self.question_dict[QID].no(PPV)
            ans = 'no'
        elif answer == 2:
            ppv = self.question_dict[QID].dont_know(PPV)
            ans = 'dont know'
        else: #question skipped
            ppv = PPV
        return ppv

    def answer_next_question(self,answer): 
        if not hasattr(self,'inc_question_ind'):
            self.inc_question_ind = 0
            self._increment_PPV = self.prevelence

        QId = list(self.question_dict.keys())[self.inc_question_ind]
        self._increment_PPV = self.answer_question(QId, answer, self._increment_PPV)
        
        if self.inc_question_ind == len(list(self.question_dict.keys()))-1:
            self.final_ppv = self._increment_PPV    
        self.inc_question_ind +=1

    def get_next_symptom(self):
        if not hasattr(self,'inc_question_ind'):
            quest = 0
        else:
            quest =self.inc_question_ind
        if quest == len(self.question_dict.keys()):
            return "__END__"
        QId = list(self.question_dict.keys())[quest]
        return self.question_dict[QId].question_text

    def get_final_ppv(self):
        if not hasattr(self, 'final_ppv'):
            print(
                'Error: You have not computed the PPV. Pass answers to self.evaluate_questionaire(inputs)')
        else:
            return self.final_ppv

    def get_natural_frequency(self, denominator = 1000):
        return denominator * self.final_ppv

    def what_if_test(self,sense, spec):
        super().__init__(sense, spec,self.final_ppv)
        self.what_if()




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

if __name__ == '__main__':
    import numpy as np


    print(7*'#' +'TESTING GCA APP' + 7*'#')
    
    Q = Questionaire()
    Q._verbose = False
    Q.load_questionaire_csv(str(home.parent)+'/testing_questionaire_mackie.csv')

    Q.generate_questionaire()
    Q.question_dict[0].compute_tree(6,.99)

    # Q.prevelence = 0.1
    # print(list(Q.csv['dependant']))

    # # Using the Btree
    # Tree = BTree()  # Pass PPV
    # Tree.add(10,[.9,.99],.8) # Pass Threshold, PPV, NPV 
    # Tree.add(20,.6,.2)# Pass Threshold, PPV, NPV

    # T = Tree.get_tree()


    # Tree.compute_tree(5000,.6)


    # BB = Binarize([0,1,2],[Interval(.5,.99),Interval(.4),Interval(.2)],[.1,.2,.3])
    # BB.generate_tree()
    # Tree = BB.get_tree()
    # root = Tree.get_root()
    # root._add_question('Testing')

    # root.get_question()


    # Tree.compute_tree(1,.99)

#     Q = Questionaire()
#     Q._verbose = False
#     Q.generate_questionaire()
#     len(Q.csv.index.values)
#     len(Q.question_dict.keys())


#     print('\n\n All True')
#     ans = np.ones(len(Q.csv.index))
#     all_true = Q.evaluate_questionaire(ans)
#     Q.what_if_test(.9,.9)


#     print('\n\n All False')
#     time.sleep(10)
#     ans = np.zeros(len(Q.csv.index))
#     all_true = Q.evaluate_questionaire(ans)
#     Q.what_if_test(.9,.9)



#     print('\n\nAll dont know')
#     time.sleep(10)
#     ans = np.ones(len(Q.csv.index))*2
#     all_maybe = Q.evaluate_questionaire(ans)
#     Q.what_if_test(.9,.9)

#     print('\n\nRandom')
#     time.sleep(10)
#     ans = np.random.randint(0,2,len(Q.csv.index))
#     all_random = Q.evaluate_questionaire(ans)
#     Q.what_if_test(.9,.9)



#     csv_test = '/Users/dominiccalleja/GCA_App/test_3_inputs.csv'
#     Qtest = Questionaire()
#     Qtest.prevelence = 0.01
#     Qtest.load_questionaire_csv( csv_test)
#     Qtest.generate_questionaire()


#     ans = [0,1,0]#np.ones(len(Qtest.csv.index))
#     all_true = Qtest.evaluate_questionaire(ans)

#     Qtest.what_if_test(.9,.9)
    
    



#     # IA = ICON_ARRAY(killed = 10,ill=240)
#     # IA.scale = 5
#     # IA.plot(s=90)




# """
# Testing with reduced questions
# """



# # ans = np.zeros(len(Qtest.csv.index))
# # all_false = Qtest.evaluate_questionaire(ans)





# # def computePrevelanceModel(gen, ag):

# #         from pba import linear_interpolate as li

# #         male_age_prev = {'Age': [50, 60, 70, 80, 90],
# #                         'Prevelance_Lower': [46/100000, 46/100000, 90/100000, 275/100000, 600/100000],
# #                         'Prevelance_Upper': [156/100000, 160/100000, 170/100000, 450/100000, 700/100000]}

# #         female_age_prev = {'Age': [50, 60, 70, 80, 90],
# #                         'Prevelance_Lower': [46/100000, 46/100000, 250/100000, 1000/100000, 1700/100000],
# #                            'Prevelance_Upper': [156/100000, 160/100000, 300/100000, 1200/100000, 1900/100000]}

# #         if (gen == 'male' and ag < 50):
# #             prev = [0.001, 0.001]

# #         elif (gen == 'male' and ag <= 90):
# #             prev_lower = li(male_age_prev['Age'],
# #                             male_age_prev['Prevelance_Lower'], ag)
# #             prev_upper = li(male_age_prev['Age'],
# #                             male_age_prev['Prevelance_Upper'], ag)
# #             prev = [prev_lower, prev_upper]

# #         elif (gen == 'male' and ag > 90):
# #             prev_lower = li(male_age_prev['Age'],
# #                             male_age_prev['Prevelance_Lower'], 90)
# #             prev_upper = li(male_age_prev['Age'],
# #                             male_age_prev['Prevelance_Upper'], 90)
# #             prev = [prev_lower, prev_upper]

# #         if (gen == 'female' and ag <= 50):
# #             prev = [0.001, 0.001]

# #         elif (gen == 'female' and ag <= 90):
# #             prev_lower = li(
# #                 female_age_prev['Age'], female_age_prev['Prevelance_Lower'], ag)
# #             prev_upper = li(
# #                 female_age_prev['Age'], female_age_prev['Prevelance_Upper'], ag)
# #             prev = [prev_lower, prev_upper]

# #         elif (gen == 'female' and ag > 90):
# #             prev_lower = li(
# #                 female_age_prev['Age'], female_age_prev['Prevelance_Lower'], 90)
# #             prev_upper = li(
# #                 female_age_prev['Age'], female_age_prev['Prevelance_Upper'], 90)
# #             prev = [prev_lower, prev_upper]

# #         return prev
# #     # compute prevelance from gender and age
# #     vprev1 = computePrevelanceModel(gender, age)
