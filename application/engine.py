import pathlib as Path
from posixpath import join
import sys

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

sys.path.append(str(home))
from binary_questions import *
from scalar_questions import *
default_csv_file = str(home.parent)+'/input_files/default_questionnaire.csv'

class Test(Question):

    def __init__(self, sensitivity, specificity, PPV):
        super().__init__(sensitivity=sensitivity, specificity=specificity)
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
        return [if_positive, if_negative]


class Questionnaire(Test):
    
    prevelence = 0.5
    def __init__(self, csv_file):
        self._verbose = False
        if self._verbose: print('Initialising the Questionnaire: \n \t{}'.format(csv_file))
        self.load_Questionnaire_csv(csv_file)

    def load_Questionnaire_csv(self,csv_file):
        self.csv = pd.read_csv(csv_file)

    def generate_Questionnaire(self, compute_option = 'robust',midpoint = .5):
        self._check_existing_questions()
        self.compute_option = compute_option
        self.__new_method_generate_Questionnaire()

    def get_LR(self, LRs, compute_option):
        # Returns relevant LR interval for the chosen copmpute_option
        Compute_options = ['robust','precise', 'left', 'right', 'midpoint']
        if not compute_option in Compute_options:
            print('ERROR: compute_option must be {}'.format(Compute_options))
        else:
            if compute_option == Compute_options[0]:
                # Robust: return PLR0-PLR1 & NLR0-NLR1 intervals
                return [
                    Interval(LRs['PLR0'], LRs['PLR1']), 
                    Interval(LRs['NLR0'], LRs['NLR1'])
                    ]
            elif compute_option == Compute_options[1]:
                # PRecise: return PLR0-PLR1 & NLR0-NLR1 intervals
                return [
                    Interval(LRs['PLR'], LRs['PLR']), 
                    Interval(LRs['NLR'], LRs['NLR'])
                    ]
            elif compute_option == Compute_options[2]:
                # Robust: return PLR0-PLR1 & NLR0-NLR1 intervals
                return [
                    Interval(LRs['PLR0'], LRs['PLR0']), 
                    Interval(LRs['NLR0'], LRs['NLR0'])
                    ]
            elif compute_option == Compute_options[3]:
                # Robust: return PLR0-PLR1 & NLR0-NLR1 intervals
                return [
                    Interval(LRs['PLR1'], LRs['PLR1']), 
                    Interval(LRs['NLR1'], LRs['NLR1'])
                    ]
            elif compute_option == Compute_options[4]:
                # Robust: return PLR0-PLR1 & NLR0-NLR1 intervals
                return [
                    Interval(Interval(LRs['PLR0'], LRs['PLR1']).midpoint()), 
                    Interval(Interval(LRs['NLR0'], LRs['NLR1']).midpoint()) 
                    ]

    def __new_method_generate_Questionnaire(self):
        Qtype = self.csv.Qtype.values
        header = 'Diagnostic Questionnaire'
        section = 0
        c = 0 
        for i in self.csv.index:
            #qid = c#self.csv.loc[i]['Qid']
            qid = self.csv.loc[i]['Qid']
            qdep = self.csv.loc[i]['Dependant']
            qdescription = self.csv.loc[i]['Description']
            if self._verbose: print(self.csv.loc[i]['Question'])
            if Qtype[i] == 'H':
                header = self.csv.loc[i]['Question']
                section +=1

            elif Qtype[i] == 'S':
                Squestion = self.csv.loc[i]['Question']
                j = i +1
                c = 0 
                PLRs = []
                NLRs = []
                thresholds = []
                while Qtype[j] == 'SA' :
                    
                    qPLR, qNLR = self.get_LR(self.csv.loc[j]['PLR0':'NLR'], self.compute_option)
                    if j == self.csv.index[-1]:
                        break
                    PLRs.append(qPLR)
                    if c ==0 :
                        NLRs.append(qNLR)
                    else:
                        NLRs.append(qPLR)

                    thresholds.append(float(re.findall(r'\d+',self.csv.loc[j]['Question'])[0])) ### Need to seperate the carrat
                    if self._verbose: print(thresholds)
                    j+=1
                    c +=1
                if not j == self.csv.index[-1]:
                    self._init_scalar_question(qid, Squestion, thresholds, PLRs, NLRs, header,section, qdep,qdescription )
                    

            elif Qtype[i] == 'SA':
                continue
            
            elif Qtype[i] == 'B':
                qPLR, qNLR = self.get_LR(self.csv.loc[i]['PLR0':'NLR'], self.compute_option)
                question = self.csv.loc[i]['Question']
                self._init_binary_question(qid,question,qPLR,qNLR, header,section, qdep,qdescription )
                c += 1

    def get_N_questions(self):
        return len(self.csv.index)
    
    def get_final_question_id(self):
        return self.csv.iloc[self.get_N_questions()]['Qid']

    def _check_existing_questions(self):
        if not hasattr(self,'question_dict'):
            if self._verbose: print('Generating new Questionnaire')
            self.question_dict = {}

    #TODO: Tidy up this fucking mess! 

    def _init_binary_question(self, qId, question, PLR, NLR, header, section, qdep,qdescription):
        self.question_dict[qId] = Question(PLR,NLR)
        self.question_dict[qId]._add_question(question)
        self.question_dict[qId].Qid = qId
        self.question_dict[qId].Qtype = 'B'
        self.question_dict[qId].header = header
        self.question_dict[qId].section = section
        self.question_dict[qId].dependant = qdep
        self.question_dict[qId].description = qdescription


    def _init_scalar_question(self,qId_0, question, thresholds, PLRs, NLRs, header, section, qdep,qdescription):
        scalar_question = Binarize(thresholds, PLRs, NLRs, question)
        scalar_question.generate_tree()

        self.question_dict[qId_0] = scalar_question.get_tree()
        if self._verbose: print(question)
        self.question_dict[qId_0].root._add_question(question) #
        self.question_dict[qId_0].Qid = qId_0
        self.question_dict[qId_0].Qtype = 'S'
        self.question_dict[qId_0].header = header
        self.question_dict[qId_0].section = section
        self.question_dict[qId_0].dependant = qdep
        self.question_dict[qId_0].description = qdescription

    def evaluate_Questionnaire(self, inputs):
        ppv_store = [self.prevelence]
        PPV = Interval(self.prevelence)

        for i, inp in enumerate(inputs):
            qId0 = list(self.question_dict.keys())[i]
            qtype = self.question_dict[qId0].Qtype
            #if qtype == 'S':
            #    inp = float(re.findall(r'\d+',inp)[0])6

            PPV = self.answer_question(qId0, inp, qtype, PPV)
            ppv_store.append(PPV)
            if self._verbose:
                print('Q : {} \n\tAns : {}  \n\t ppv: {}'.format(
                    self.question_dict[qId0].get_question(), inp, PPV))
        self.final_ppv = PPV
        self.ppv_store = ppv_store

    def answer_question(self,QID, answer, Qtype, PPV):
        if Qtype == 'S':
            if answer != -1:
                ppv = self.question_dict[QID].compute_tree(answer,PPV)
                ans = 'Scaler'
            else:
                ppv = PPV
        else:
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
                'Error: You have not computed the PPV. Pass answers to self.evaluate_Questionnaire(inputs)')
        else:
            return self.final_ppv

    def get_natural_frequency(self, denominator = 1000):
        return denominator * self.final_ppv

    def what_if_test(self,sense, spec):
        super().__init__(sense, spec,self.final_ppv)
        YES, NO = self.what_if()
        return YES, NO


    def _get_question_property(self,prop):
        return [getattr(self.question_dict[i],prop) for i in list(self.question_dict.keys())]

    def get_interface_Questionnaire(self,*property_list):
        if not property_list:
            property_list = ['Qid','section','header','question_text','Qtype','dependant','description']
        JAVA = pd.DataFrame()
        for label in property_list:
            JAVA[label] = self._get_question_property(label)
        return JAVA

    def __repr__(self):
        if hasattr(self,'question_dict'):
            return 'Questionnaire class with {} questions'.format(len(self.question_dict))
            #[self.question_dict[i] for i in self.question_dict]
        else:
            return 'Evaluate generate_Questionnaire'



if __name__ == '__main__':
    import numpy as np


    print(7*'#' +'TESTING GCA APP' + 7*'#')
    
    Q = Questionnaire(str(home.parent)+'\input_files\\default_questionnaire_clean.csv')
    Q._verbose = True
    Q.prevelence = .25
    #Q.load_Questionnaire_csv('/Users/dominiccalleja/GCA_App/GCA_engine/input_files/Vinnette_tests.csv')
    #Q.load_Questionnaire_csv('/Users/dominiccalleja/GCA_App/GCA_engine/input_files/Vinnette_tests.csv')
    #str(home.parent)+'/input_files/vanessa_modded.csv')
    Q.generate_Questionnaire(compute_option='midpoint')
    CSV = Q.get_interface_Questionnaire()

    #Q.compute_with_precise()

    Answers = np.ones(34)
    Answers[0] = 90
    Answers[23] = 1
    Answers[24] = 1 
    Answers[32] = 30
    # Answers[35] = 50

    Q.evaluate_Questionnaire(Answers)
    Q.final_ppv




    patients = pd.read_excel(str(home.parent)+'\input_files\Vinnette_tests_1.xlsx')

    P0 = patients['PATIENT1']
    P0.values
    Q.evaluate_Questionnaire(P0.values[:-1])
    Q.final_ppv


def get_nat_freq(numer,denom = 1000):
    A = numer*denom
    B = denom - A    
    return ['positive : {} of {}'.format(A,denom),'negative : {} of {}'.format(B,denom)]

    P0 = patients['PATIENT4']
    P0.values
    Q.evaluate_Questionnaire(P0.values[:-1])
    Q.final_ppv
    Q.what_if_test(.77,.96)
    NF_P = get_nat_freq(.76,denom=860) 
    NF_N = get_nat_freq(.03,denom=140) 
    print('Pos Test NF: \n{}'.format(NF_P))
    print('Neg Test NF: \n{}'.format(NF_N))

    Q.final_ppv = Interval(.16)
    Q.what_if_test(.77,.96)


    P0 = patients['PATIENT3']
    P0.values
    Q.evaluate_Questionnaire(P0.values[:-1])
    Q.final_ppv


    Q.get_natural_frequency()

    P0 = patients['PATIENT4']
    P0.values
    Q.evaluate_Questionnaire(P0.values[:-1])
    Q.final_ppv
    Q.what_if_test(.77,.96)

    Q.final_ppv = Interval(.04,.76)
    Q.what_if_test(.77,1)

    Q.final_ppv = Interval(.47)
    Q.what_if_test(.77,1)


    T = Test(.77,.96,.14)    

    Q.what_if_test(.77,.96,.14)

    for ans in P0:
        Q.answer_next_question(ans)



    Qid = list(Q.question_dict)[0]

    Q.question_dict[Qid].get_question()
    Q.question_dict[Qid].header
    Q.question_dict[Qid].section
    Q.question_dict[Qid].Qtype
    Q.question_dict[Qid].Qdependant

    Qid = list(Q.question_dict)[3]
    Q.question_dict[Qid].get_question()
    Q.question_dict[Qid].header
    Q.question_dict[Qid].section
    Q.question_dict[Qid].Qtype
    Q.question_dict[Qid].Qdependant
    


    #Q.question_dict[0].Qtype
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

#     Q = Questionnaire()
#     Q._verbose = False
#     Q.generate_Questionnaire()
#     len(Q.csv.index.values)
#     len(Q.question_dict.keys())


#     print('\n\n All True')
#     ans = np.ones(len(Q.csv.index))
#     all_true = Q.evaluate_Questionnaire(ans)
#     Q.what_if_test(.9,.9)


#     print('\n\n All False')
#     time.sleep(10)
#     ans = np.zeros(len(Q.csv.index))
#     all_true = Q.evaluate_Questionnaire(ans)
#     Q.what_if_test(.9,.9)



#     print('\n\nAll dont know')
#     time.sleep(10)
#     ans = np.ones(len(Q.csv.index))*2
#     all_maybe = Q.evaluate_Questionnaire(ans)
#     Q.what_if_test(.9,.9)

#     print('\n\nRandom')
#     time.sleep(10)
#     ans = np.random.randint(0,2,len(Q.csv.index))
#     all_random = Q.evaluate_Questionnaire(ans)
#     Q.what_if_test(.9,.9)



#     csv_test = '/Users/dominiccalleja/GCA_App/test_3_inputs.csv'
#     Qtest = Questionnaire()
#     Qtest.prevelence = 0.01
#     Qtest.load_Questionnaire_csv( csv_test)
#     Qtest.generate_Questionnaire()


#     ans = [0,1,0]#np.ones(len(Qtest.csv.index))
#     all_true = Qtest.evaluate_Questionnaire(ans)

#     Qtest.what_if_test(.9,.9)
    
    



#     # IA = ICON_ARRAY(killed = 10,ill=240)
#     # IA.scale = 5
#     # IA.plot(s=90)




# """
# Testing with reduced questions
# """



# # ans = np.zeros(len(Qtest.csv.index))
# # all_false = Qtest.evaluate_Questionnaire(ans)





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
