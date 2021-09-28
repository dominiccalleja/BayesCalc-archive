import sys
from engine import Questionaire as Questionaire

Q = Questionaire()
Q.prevelence = 0.01
Q.load_questionaire_csv('test_3_inputs.csv')
Q.generate_questionaire()
Q.evaluate_questionaire(inputs = [int(i) for i in list(sys.argv[1])])

if len(sys.argv)>=2:
    Q.what_if_test(float(sys.argv[2]), float(sys.argv[3]))