import math
import random

def get_data(filename):
    """
    From data file, reads, formats and saves data as a list.
    Args:
        filename: the name of a data file such as data.txt.
    Returns:
        lines: a list of formatted and relevant data items extracted from the data file.
    """  
    f = open(filename, 'r')
    lines = f.read().splitlines() # Reads, formats and saves data as a list.
    f.close()
    lines = [x.strip() for x in lines if x.strip()] #Removes empty list items.
    
    return lines

def parse_data(lines):
    """
    Seperates and organizes raw data extracted from data file.
    Args:
        lines: list of system data from get_data function.
    Returns:
        node_qty: an integer denoting quantity of nodes in the system.
        weights: list of tuples of nodes, edges and respective weights for the system.
    """
    weights = []
    for l in lines: # Iterative through list of lines saved from data file.
        if l[0] == str('c'): # Skips comments, lines with a first character 'c'.
            continue
        elif l[0] == str('p'): # Identifes 'p' line which includes qty values for nodes and weights.
            p = l.split(' ') # Formats and saves'p' line data to a list.
            node_qty = int(p[2])
        else:
            weights.append(tuple(map(int, l.split()))) # Formats and saves weights from lines list.
            
    return (node_qty, weights)

class Node(object):
    """
    Class of objects to represent the characteristics and behaviors of nodes within the system.
    """
    def __init__(self):
        """
        Initialize a Node instance, saves all parameters as attributes of the instance.
        Parameters:
            spin: the spin of the node which can be positive (+1) or negative (-1).       
            h: an integer, the field weight h applied to the node.
            Jn: a list of tuples of nodes with thier corresponding edge weights.        
        """
        self.spin = random.choice((-1,1)) # Randomly assigns spin when a node is initialized
        self.h = 0
        self.Jn = []

    def seth(self, h):
        self.h = h
    
    def geth(self):
        return self.h
    
    def setJn(self, Jn):
        self.Jn.append(Jn) # Nodes may have one or more edges so this parameter is a list.
        
    def getJn(self):
        return self.Jn
    
    def switchSpin(self):
        self.spin = -self.spin # When invoked, reverses spin of node from -1 to 1 or 1 to -1.
    
    def getSpin(self):
        return self.spin
    
    def getE(self, nodes): # Calculates energy of a node; nodes: a list of node objects.
        E=0
        for i in self.getJn():
            E += (self.geth() * self.getSpin()) + (i[1] * self.getSpin() * nodes[i[0]].getSpin()) 
        return (-E) # Returns an integer, self spin * (the sum of products of edge weight and spin for nodes connected to self .    

class Model(Node):
    """
    Class of Nodes to model the characteristics and behaviors of the system of edges and nodes.
    """
    def __init__(self, node_qty, weights): 
        """
        Initialize a Model instance, creates Nodes with their respective field and edge weights based on problem data.
        Parameters:
            nodes: a dict of Node objects.
            Js: a list of tuples, each of which indicate two nodes joined by an edge and the edge weight.
            hs: a list of tuples, each of which indicate a node and its resepctive field weight.
        Args:
            node_qty: an integer, number of nodes within model.
            weights: list of tuples of nodes, edges and respective weights for the model.
        """        
        self.nodes = {}
        self.Js = []
        self.hs = []

        for n in range(node_qty):
            self.nodes[n] = Node() # Creates the specified quantity of nodes.
        for w in weights:
            if w[0] != w[1]: # Identitfes edge weights according to problem specifcation.
                self.nodes[w[0]].setJn((w[1],w[2])) # For first node in tuple, assigns edge weight for adjacent node.
                self.nodes[w[1]].setJn((w[0],w[2])) # For adjacent node, assigns edge weight with first node in tuple.
                self.Js.append((w[0], w[1], w[2])) # This list is created to represent edge weights for the whole model.
            elif w[0] == w[1]: # Identitfes node field weights according to problem specifcation.
                self.nodes[w[0]].seth(w[2]) # Sets field weight for each node.
                self.hs.append((w[0], w[2])) # Adds to list of nodes and its weight for whole model.
            # Js Edge weights for the whole model.
            # Jn Edge weights for only the edges of a particular node.
    def getNodes(self):
        return self.nodes
    
    def getJs(self):
        return self.Js
    
    def geths(self):
        return self.hs  
 
def update(model, nodes, node_qty, T=1.0):
    """
    Updates state of system by randomly switching spin based on current energy of system.
    Args:
        model: an instance of a Model object.
        nodes: a dictionary of node objects.
        node_qty: an integer, quantity of nodes within model.
        T: a float, non zero temperature for the Boltzmann distribution probability formula.
    """
    for i in range(node_qty):
        n = random.randint(0, node_qty-1) # Randomly selects a node in the model.
        E = nodes[n].getE(nodes)
        if E > 0:
            nodes[n].switchSpin() # If energy is high, inverts node spin.
        elif E <= 0 and random.random() < math.exp(2*E/T): # If energy is low, randomly inverts node spin anyway as a function of Boltzmann distribution.
            nodes[n].switchSpin()

def modelE(model, nodes, node_qty, I, T):
    """    
    Seeks to calculate the energy of the system after a user determined number (I) updates to the model.
    Args:
        model: an instance of a Model object.
        nodes: a dictionary of node objects.
        node_qty: an integer, quantity of nodes within model.
        I: an integer, user input dictating number of updates to the model prior to determing final system energy.
        T: a float, non zero temperature for the Boltzmann distribution probability formula.
    Returns:
        mE: an integer indicating energy of the system according to the Hamiltonian specifed in the Test Introduction.
    """
    mE = 0
    for i in range(I):
        update(model, nodes, node_qty, T) # Invokes an update to the model.
    for w in model.getJs(): # Iterates over a list of tuples of nodes joined by an edge.
        mE += nodes[w[0]].getSpin() * nodes[w[1]].getSpin() * w[2] # Sums product of spins with shared edges and edge weights.
    for w in model.geths(): # Iterates over a list of tuples of nodes with resepctive field weights.
        mE += nodes[w[0]].getSpin() * w[1] # Sums product of spins and weights.
    return -mE

def modelSpin(model, nodes):
    """
    Determines and reports spin state of nodes.
    Args:
        model: an instance of a Model object.
        nodes: a dictionary of node objects.
    Returns:
        state: a list of node spins for the model, either -1 or +1.
    """
    state = []
    for e in nodes:
        state.append(nodes[e].getSpin())
    state = ['+' if x > 0 else '-' for x in state]
    return state

def main():
    """
    Requests input from the user, invokes data retrieval and parsing, invokes and saves an instance of a Model and the respective system Nodes.
    Prints formated output of modelE and modelSpin functions.
    """
    filename = str(input('Reminder: your data file must be in the same folder as your program file.\n\nPlease enter the filename (data.txt): ') or 'data.txt')
    I = int(input('Number of steps (10)? ') or '10')
    T = float(input('Temperature, a float greater than zero (1.0): ') or '1')
    node_qty, weights = parse_data(get_data(filename))
    model = Model(node_qty, weights)
    nodes = model.getNodes()
    
    print("\nOutput: \n\n", modelE(model, nodes, node_qty, I, T), "\n")
    print(*(modelSpin(model, nodes)))

main()
