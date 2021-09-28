import sys
from engine import *

Q = Questionaire()
Q.generate_questionaire()
Q.evaluate_questionaire(sys.argv)

