import numpy as np

from math import sqrt

class Node:
    def __init__(self,threshold):
        self.threshold = threshold
    
    def checker(self, value):
        # TODO: add a maybe
        if value > self.threshold:
            return 1
        else:
            return 0


class Tree:

    def __init__(self,lower_bound, upper_bound, nb_tree=4):
        """

        nb_tree = number of nodes on tree
        """

        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.nb_tree = nb_tree
        self.nl_tree = sqrt(nb_tree)


    def add_threshold(self):
    
    def add_likelihood_ratio(self):
    
    def _generate_tree(self):
        
        for l in range(self.nl_tree):
            self.Tree = Tree()