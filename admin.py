
__author__ = "Dominic Calleja"
__copyright__ = "Copyright 2020"
__credits__ = "Nick Gray, Alex Wimbush"
__license__ = "RESTRICTED"
__version__ = "0.1"
__date__ = '01/4/2020'
__maintainer__ = "Dominic Calleja"
__email__ = "d.calleja@liverpool.ac.uk"
__status__ = "Draft"

__verbose__ = True

t= ['\t+===================================+\n']
t.append('\t|              RoBaeCalc            |\n')
t.append('\t|   Bayesian Diagnostic Calculator  |\n')
t.append('\t|   Credit: '+__credits__+' |\n')
t.append('\t|             Version: '+__version__ + 9*' '+' |\n')
t.append('\t|                                   |\n')
t.append('\t|'+__copyright__+' (c) ' + __author__+' |\n')
t.append('\t+====================================+\n')

description = 'A software libary for the robust coputation of desease \nlikelihood given patient histories and any sequential \ndiagnositic algorithm'


def copyR(logfile):
    """Print copyright information to file."""
    outputf=open(logfile, 'a')
    outputf.write('+'+'='*77+'+ \n')
    for tt in t[1:-1]:
        outputf.write(tt)
    outputf.write('+'+'='*77+'+'+ '\n')
    outputf.write('\n')
    outputf.close()
    return


if __verbose__==True:
    print(*t)
    print(description)


class Clinician:
    _verbose_=True
    patients = {}
    _details_ = {}
    _logstring_ = []

    def __init__(self, *name):
        if name:
            self.add_clinician_details(name=name[0])

    def add_clinician_details(**kwargs):

        for Key, Value in kwargs:
            setattr(self._details_,Key) = Value

    def get_clinician_details(self):
        deets = ''
        for Key, Value in self._details_:
            d = '{} \t: {}\n'.format(Key,Value)
            deets = deets+d
        return deets

    def add_patient(self,patient):
        if self._verbose_:
            print('Adding patient {} to clinician {}'.format())
        self.patients[patient.uid] = patient        

    # def __repr__(self):
    #     return
    
    def get_patient_list(self):
        patient_list = []
        for Key, Value in self.patients:
            patient_list.append(Value.name)
        return patient_list
    
    def get_patient_uids(self):
        patient_list = []
        for Key, Value in self.patients:
            patient_list.append(Key)
        return patient_list


class Patient:
    def __init__(self, **information):
        if information:
            self._add_patient_data(information)

    def _add_patient_data(self, **information):
        for key, value in information:
            setattr(self, key) = value

    def get_patient_info(self,type_info):
        return getattr(self,type_info)
        
    def _add_clinician(self,*clinician, clinician_uid=None):
        if isinstance(clincian(),Clinician):
            self.clincian_name = clinician.name 
            self.clinician_id = clinician.id
        else: 
            assert clinician_uid not None
            self.clincian_name = clinician[0]
            self.clinician_id = clinician.id
    
    def get_clinician(self):
        return '{} (UID: {})'.format(self.clincian_name, self.clinician_id)

    def __repr__(self):
        return

    def add_questionaire_answers(self,questionaire, answers):
        # iterate through questions. Giving answers 
        output_string = ''
        QIDS = list(questionaire.question_dict.keys())
        for i, ans in enumerate(answers):
            if ans == -1:
                break
            Qid = QIDS[i]
            Qno = questionaire.question_dict[Qid].question_number
            Qest = questionaire.question_dict[Qid].question_text
            
            q_string = '[{}] - {} \t ans: {}\n'.format(Qno,Qest,ans)
            output_string = output_string + q_string
        self.question_string = output_string
    
    def get_questionaire_answers(self)
        return self.question_string

    def generate_output_file(self):
    


def timestamp_format(t0, t1):
    t_delta = t1-t0

    if t_delta/60 < 1:
        time = '{:.3f} (sec)'.format(t_delta)
    elif t_delta/60 > 1 and t_delta/60/60 < 1:
        time = '{:.3f} (min)'.format(t_delta/60)
    else:
        time = '{:.3f} (hrs)'.format(t_delta/60/60)

    return time
        
    