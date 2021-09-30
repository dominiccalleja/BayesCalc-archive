



class Patient:
    def __init__(self, **information):
        if information:
            self._add_patient_data(information)

    def _add_patient_data(self, information):
        


    def __repr__(self):
        return

    def _add_questionaire_answers(self,questionaire):

        


class Clinician:

    _verbose_=True
    patients = {}
    _logstring_ = []
    def __init__(self, name):

    
    def add_patient(self,patient):
        if self._verbose_:
            print('Adding patient {} to clinician {}'.format())
        self.patients[patient.uid] = patient
        
