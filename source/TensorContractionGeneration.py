# -*- coding: utf-8 -*-
"""TensorContraction.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1n8SNsKp283B1e5Kh-6WjmQEMgjeGBcZ0
"""
import networkx as nx
grid = [["H", "H", "S", "-", "-"], ["CNOT", "*", "-", "-", "-"], ["-", "CNOT", "*", "-", "-"],
        ["CNOT", "*", "CCX", "*", "*"], ["CCX", "*", "*", "S", "-"], ["S", "-", "-", "-", "-"]]
grid = [["H", "H", "H", "H"], ["CX", "*", "X(1/2)", "T"], ["X(1/2)", "CX", "*", "Y(1/2)"], ["T", "X(1/2)", "CX", "*"], ["CX", "-", "-", "*"], ["H", "H", "H", "H"]]
# ["CX", "*", "-", "-"], ["-", "CX", "*", "-"], 
#        ["-", "-", "CX", "*"],
#grid = [["CX", "-", "-", "*"]]
# grid[col][row]

# LL(1) Grammar to parse grid implemented using recursive descent
# S(n, m) := B(n, m)
# B(n, m) := idS B(n, m-1) | idC B(n, m - 1) | * B(n, m-1)
    #        W(n-1, m, 0)  | W(n-1, m, k)    | W(n-1, m, -1)
# W(n, m, k) := idS          | *              | idC(k1)
#               W(n, m-1, k) | W(n, m-1, k-1) | W(n, m-1, k1)

idS = {"H", "S", "T", "X(1/2)", "Y(1/2)", "-"}
idC = {"CNOT": 1, "CCX": 2, "CX": 1}
idI = {"CX": 1}
parsingFlag = False

class Node:
     def __init__(self,data):
          self.data = data
          self.parent = None
          self.left = None
          self.middle = None
          self.right = None
          self.associations = None
     def __repr__(self):
          return repr(self.data)
     def add_left(self,node):
         self.left = node
         if node is not None:
             node.parent = self
     def add_middle(self,node):
         self.middle = node
         if node is not None:
             node.parent = self
     def add_right(self,node):
         self.right = node
         if node is not None:
             node.parent = self
     def add_associations(self,associations):
         self.associations = associations
     def get_associations(self):
         return self.associations
     def get_left(self):
        return self.left
     def get_middle(self):
        return self.middle
     def get_right(self):
        return self.right
     def get_parent(self):
        return self.parent
     def get_data(self):
        return self.data
        
class Multigate:
    def __init__(self):
        self.actorTypes = ["Control", "Actor"]
        self.actorMatrix = {"Control": [[1,0], [0,1]], "Actor": [[0,1],[1,0]]}
        self.qubitAssociation = []
    def getMatrix(qubit, actor):
        return self.actorMatrix[(self.qubitAssociation[qubit])]
    def addQubit(qubit, actor):
        self.qubitAssociation[qubit] = actor
        
def W(grid, n, m, k, associations):
  rootNode = Node("W("+str(n)+","+str(m)+","+str(k)+")")
  global idS, idC, parsingFlag
  if(n == len(grid) or m == len(grid[0])):
    if(k < 0 or k > 0):
      print("Parse Error...")
      parsingFlag = True
    return rootNode, associations
    
  leftNode = Node((grid[n][m], m))
  middleNode = Node(("NotReal", -1))
  if(grid[n][m] == "-"):
    middleNode, associationsNew = W(grid, n, m+1, k, associations)
    leftNode.add_associations(associationsNew)
    rootNode.add_left(leftNode)
    rootNode.add_middle(middleNode)
    return rootNode, associations
  if(grid[n][m] in idS):
    leftNode.add_associations({m: "Actor"})
    middleNode, _ = W(grid, n, m+1, k, {m: "Actor"})
  else:
    if(grid[n][m] in idC):
      if(k == 0):
        middleNode, futureAssociations = W(grid, n, m+1, k+idC[grid[n][m]], dict({}))
        totalAssociations = {m: "Actor"}
        if(futureAssociations != None):
            totalAssociations.update(futureAssociations)
        leftNode.add_associations(totalAssociations)
      else:
        middleNode, futureAssociations = W(grid, n, m+1, k+idC[grid[n][m]], associations)
        totalAssociations = {m: "Actor"}
        if(futureAssociations != None):
            totalAssociations.update(futureAssociations)
        leftNode.add_associations(totalAssociations)
    else:
      if(grid[n][m] == "*"):
        if(k != 0):
            totalAssociations = associations
            totalAssociations[m] = "Control"
        else:
            totalAssociations = {m: "Control"}
        middleNode, futureAssociations = W(grid, n, m+1, k + -1, totalAssociations)
        if(futureAssociations != None):
            totalAssociations.update(futureAssociations)
        leftNode.add_associations(totalAssociations)
      else:
        print("Parse Error...")
        parsingFlag = True
        return rootNode, associations
  rootNode.add_left(leftNode)
  rootNode.add_middle(middleNode)
  return rootNode, associations
  
def B(grid, n, m):
  global idS, idC, parsingFlag
  rootNode = Node("B("+str(n)+","+str(m)+")")
  if(n == len(grid) or m == len(grid[0])):
    return rootNode
  leftNode = Node((grid[n][m], m))
  if(grid[n][m] in idS):
    middleNode, _ = W(grid, n, m+1, 0, dict({}))
    leftNode.add_associations({m: "Actor"})
    rightNode = B(grid, n+1, m)
  else:
    if(grid[n][m] in idC):
      middleNode, associations = W(grid, n, m+1, idC[grid[n][m]], {m: "Actor"})
      leftNode.add_associations(associations)
      rightNode = B(grid, n+1, m)
    else:
      if(grid[n][m] == "*"):
        middleNode, associations = W(grid, n, m+1, -1, {m: "Control"})
        leftNode.add_associations(associations)
        rightNode = B(grid, n+1, m)
      else:
        print("Parse Error...")
        parsingFlag = True
        return rootNode
  rootNode.add_left(leftNode)
  rootNode.add_middle(middleNode)
  rootNode.add_right(rightNode)
  return rootNode 
  
def generateParseTree(grid, n, m):
  rootMain = Node("S("+str(n)+","+str(m)+")")
  rootParse = B(grid, n, m)
  rootMain.add_middle(rootParse)
  if(not parsingFlag):
    print("Valid quantum circuit...")
    return rootMain
  return None

def printTree(root, level=0):
    print("  " * (2*level), root, "Associations: ", root.get_associations(), type(root.get_data()))
    if(root.get_left() != None):
        printTree(root.get_left(), level + 1)
    if(root.get_middle() != None):
        printTree(root.get_middle(), level + 1)
    if(root.get_right() != None):
        printTree(root.get_right(), level + 1)
    
def parse(grid):
    parseTree = generateParseTree(grid, 0, 0)
    return parseTree

def extractLayer(node, partialArray):
  if(node == None):
    return []
  layerRemaining = []
  if(node.get_left() != None and node.get_left().get_data()[0] != '-' and node.get_left().get_data()[0] != '*'):
    layerRemaining = [(node.get_left(), node.get_left().get_associations())]
  if(node.get_middle() != None):
    layerRemaining2 = extractLayer(node.get_middle(), [])
    layerRemaining = layerRemaining + layerRemaining2
  array = partialArray + layerRemaining
  return array

def getComputation(root, layers):
    if(root.get_right() != None):
        layers.append(extractLayer(root, []))
        layer = getComputation(root.get_right(), layers)
    return layers

def getComputationLayers(tree):
  return getComputation(tree.get_middle(), [])

def generateTensorNetworkGraph(computationLayers, qubit):
  import networkx as nx
  G = nx.Graph()
  qubitAssociations = {-1: "None"}
  for i in range(qubit):
    G.add_node("S(" + str(i+1) + ")")
    qubitAssociations[i] = "S(" + str(i+1) + ")"
  index = 0
  for layer in computationLayers:
    index = index + 1
    qubitsUsed = {-10}
    for transformation in layer:
      (operations, associations) = transformation
      (operation, qubit) = operations.get_data()
      if(len(associations) == 1):
        node = "L(" + operation + "," + str(qubit) + "," + str(index) + ")"
        G.add_node(node)
        G.add_edge(qubitAssociations[qubit], node)
        qubitAssociations[qubit] = node
        qubitsUsed.add(qubit)
      else:
        if(operation in idI and len(associations) > 1):
          for key1, value1 in associations.items():
            for key2, value2 in associations.items():
              if(key1 != key2):
                G.add_edge(qubitAssociations[key1], qubitAssociations[key2])
            qubitsUsed.add(key1)
          qubitsUsed.add(qubit)
        else:
          if(len(associations) > 1):
            oldOnes = []
            for key1, value1 in associations.items():
              oldOnes.append(qubitAssociations[key1])
            for key, value in associations.items():
              node = "L(" + operation + "," + str(key+1) + "," + str(index) + ")"
              G.add_node(node)
              qubitAssociations[key] = node
              qubitsUsed.add(key)
            qubitsUsed.add(qubit)
            for key1, value1 in associations.items():
              for key2, value2 in associations.items():
                if(key1 != key2):
                  G.add_edge(qubitAssociations[key1], qubitAssociations[key2])
            for key1 in oldOnes:
              for key2, values2 in associations.items():
                if(key1 != key2):
                  G.add_edge(qubitAssociations[key2], key1)
            for key1 in oldOnes:
              for key2 in oldOnes:
                if(key1 != key2):
                  G.add_edge(key2, key1)
    for i in range(qubit):
      if(i not in qubitsUsed):
        G.add_edge(qubitAssociations[i], qubitAssociations[i])
  return G

def drawTensorNetworkGraph(G):
  pos = nx.spring_layout(G)
  nx.draw(G, with_labels=True)
