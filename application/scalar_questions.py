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


from binary_questions import Question_Methods


class Node(Question_Methods):
    def __init__(self,threshold, PLR, NLR):
        super().__init__()
        self.threshold = threshold
        #self.PPV = PPV
        self.PLR = PLR 
        self.NLR = NLR

        self.left = None
        self.right = None
    
    def __repr__(self):
        return 'Threshold : {}'.format(self.threshold)

    def less_than(self,PPV):
        if self.left is None:
            return self.no(PPV)
        else:
            return self.left
    
    def more_than(self,PPV):
        if self.right is None:
            return self.yes(PPV)
        else:
            return self.right


class BTree:
    summary = 'Tree object'
    def __init__(self):
        self.root = None
        #self.PPV = PPV

    def __repr__(self):
        return self.summary

    def get_root(self):
        return self.root

    def get_question(self):
        return self.root.get_question()
    
    def add(self,threshold, PLR, NLR):
        PLR = Interval(PLR)
        NLR = Interval(NLR)
        if self.root is None:
            self.root = Node(threshold, PLR, NLR)
        else:
            self._add(threshold,self.root, PLR, NLR)

    def _add(self, threshold, node, PLR, NLR):
        if threshold < node.threshold:
            if node.left is not None:
                self._add(threshold, node.left, PLR, NLR)
            else:
                node.left = Node(threshold, PLR, NLR)
        else:
            if node.right is not None:
                self._add(threshold, node.right, PLR, NLR)
            else:
                node.right = Node(threshold, PLR, NLR)
    
    @staticmethod
    def _return_less(Node,PPV):
        return Node.less_than(PPV)

    @staticmethod
    def _return_more(Node,PPV):
        return Node.more_than(PPV)
        
    def compute_tree(self, value, PPV):
        node = self.get_root()
        while isinstance(node,Node):
            node = compute_node(node, value, PPV)
        return node
    
    
def compute_node(tmp, value, PPV):
    if hasattr(tmp,'root'):
        tmp = tmp.root 
    print('Threshold: {}'.format(tmp.threshold))
    print('Values: {}'.format(value))
    
    
    if value < tmp.threshold:
        tmp = tmp.less_than(PPV)
    else:
        tmp = tmp.more_than(PPV)
    return tmp

class Binarize:    
    def __init__(self,thresholds,PLR, NLR, question):
        self.thresholds = thresholds
        self.PLR = PLR
        self.NLR = NLR
        self.question_text = question
        try:
            self.Nt = len(thresholds)
        except:
            self.Nt = 1
        self._gen_summary()
        
    
    def generate_tree(self):
        New_Tree = BTree()
        if self.Nt == 1:
            New_Tree.add(self.thresholds,self.PLR,self.NLR)
        else:   
            for i in range(self.Nt):
                New_Tree.add(self.thresholds[i],self.PLR[i],self.NLR[i])
        New_Tree.summary = self.summary
        New_Tree.question_text = self.question_text
        self.Tree = New_Tree
    
    def get_tree(self):
        return self.Tree

    def _gen_summary(self):
        s0 = 'Binarized scalar question: {}  \n'.format(self.question_text)
        s0 +='\tNumber of thresholds : \t {}\n'.format(self.Nt)
        s0 +='\tthresholds : \n\t {}\n'.format(self.thresholds)
        s0 +='\tPLR : \n\t {}\n'.format(self.PLR)
        s0 +='\tNLR : \n\t {}\n'.format(self.NLR)
        self.summary = s0

    
        
