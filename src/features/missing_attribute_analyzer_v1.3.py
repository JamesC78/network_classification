# Searches a CSV file and finds missing attributes
# Written by Charles Morris
# dictMax, dictMin, dictAverage taken from code by Casey Primozic
import csv
import os
import networkx as nx
import threading
import queue
import time
import igraph as ig #i don't know if there is a commonly used short name for it so I made this up
from scoop import futures

#num_worker_threads = 20  # Adjust to desired number of threads  (number of cores minus 1)
#C:\Users\kschmit1\Documents\GitHub\network_classification\src\features



queueAtt = []  # A list that contains a list of graphs and number corresponding to a calculation in doCalculation
incompleteGraphs = dict()  # used to store incomplete graph names and attribute numbers
completeGraphs = []  # used to store complete graphs

#network_path = 'C:/Users/Owner/Downloads/network_repository_graphs' #designate the location of the network path to walk (or can I add a way to do it from the current location by default?)
#the path above is from James' laptop
network_path = 'E://VERUM/synthetic_graphs' #This is Adriana's flash drive

infile = open('/Users/kschmit1/Documents/GitHub/network_classification/src/data/synthetic_test.csv')

reader = csv.reader(infile)
mydict = dict((rows[0], rows[1:]) for rows in reader)
header = mydict['Graph']
infile.close()

completeRow = True
#lock = threading.Lock()

#print('incomplete graphs: ', incompleteGraphs)

# searches a list (incompleteGraphs) for a string(graph name) and the numbers that follow(attributes to calculate)
def queueCal(g):
#    graph_name = None
#    calculation = None
#    nowComplete = False
    for i in g.keys():
        if i not in ['Graph']:
            tmplst=list([i])
            tmplst.extend(g[i])
            queueAtt.append(tmplst)
        
#        if isinstance(i, str):
#            graph_name = i
#        elif isinstance(i, int):
#            calculation = i
#            # print "I am going to run calculation " + header[i] + " on " + str(graph_name)
#            queueAtt.append([graph_name, i])
#            global completeGraphs
#            nowComplete = True
#            for j in mydict[graph_name]:
#                if j is "":
#                    nowComplete = False
#        if nowComplete is True:
#            completeGraphs.append(graph_name)
#            for k in mydict[graph_name]:
#                completeGraphs.append(k)
#            writer.writerow(completeGraphs)
#            completeGraphs = []
#            nowComplete = False


# Takes a list from queueAtt and runs the correct calculation on the correct graph
def doCalculation(g):
    list_of_attributes = list(mydict[g[0]])
    #list_of_attributes.extend([None]*14)
    for root, dirs, files in os.walk(network_path):
        for names in files:
            if names.split(".")[0] == g[0]:
                graph = nx.read_edgelist(root + "/" + g[0] + ".csv") #decided to use read edgelist for the synthetic graphs
                i_graph = ig.Graph()
                i_graph = i_graph.Read_Edgelist(root + "/" + g[0] + ".csv") #also using .csv to read synthetic graph files
                while len(g) > 1:
                    calcindx=g.pop()
                    
                    print("Calculating " + header[calcindx] + " for " + g[0])
                    if calcindx is 0:
                        list_of_attributes[calcindx] = "none"
                    if calcindx is 1:
                        list_of_attributes[calcindx] = nx.number_of_nodes(graph)
                    elif calcindx is 2:
                        list_of_attributes[calcindx] = nx.number_of_edges(graph)
                    elif calcindx is 3:
                        list_of_attributes[calcindx] = nx.density(graph)
                    elif calcindx is 4:
                        newDict = dict(nx.degree(graph))
                        list_of_attributes[calcindx] = dictMax(newDict)
                    elif calcindx is 5:
                        newDict = dict(nx.degree(graph))
                        list_of_attributes[calcindx] = dictMin(newDict)
                    elif calcindx is 6:
                        newDict = dict(nx.degree(graph))
                        list_of_attributes[calcindx] = dictAverage(newDict) #this returns a decimal, while the network repository calculation rounds down
                    elif calcindx is 7:
                        list_of_attributes[calcindx] = nx.degree_assortativity_coefficient(graph)
                    elif calcindx is 8:
                        newDict = dict(nx.triangles(graph))
                        list_of_attributes[calcindx] = dictTotal(newDict)
                    elif calcindx is 9:
                        newDict = dict(nx.triangles(graph))
                        list_of_attributes[calcindx] = dictAverage(newDict) #this returns a decimal, while the network repository calculation rounds down
                    elif calcindx is 10:
                        newDict = dict(nx.triangles(graph))
                        list_of_attributes[calcindx] = dictMax(newDict)
                    elif calcindx is 11:
                        list_of_attributes[calcindx] = nx.average_clustering(graph)
                    elif calcindx is 12:  # Frac Closed Triangles = Global CC
                        list_of_attributes[calcindx] = nx.transitivity(graph)
                    elif calcindx is 13:  #creates a new graph that is the max k-core, and then takes the min degree of that core, aka k
                        new_graph = graph.copy()
                        new_graph.remove_edges_from(new_graph.selfloop_edges()) # nx.k_core can't operate on a graph with self-loops - this might alter the max k-core
                        k_core = nx.k_core(new_graph)
                        newDict = dict(nx.degree(k_core))
                        list_of_attributes[calcindx] = dictMin(newDict) + 1 # there are different ways of representing k-core number, NetRep. adds 1
                    elif calcindx is 14:  # max clique (max_clique doesnt exsist? and graph_clique_number returned different than in CSV file)
                        #list_of_attributes[calcindx] = nx.graph_clique_number(graph) #ryan and nesreen said that the clique number is the same thing as max clique
                        list_of_attributes[calcindx] =i_graph.clique_number()  #ignores directionality of edges (fine for synthetic graphs)
                    #elif calcindx is 15:  # Cant find Chromatic number in nx, will have to calculate upper bound?
                    #    list_of_attributes[calcindx] = 'na'
                    #elif calcindx is 15:
                    #    #find number of connected components
                    #    list_of_attributes[calcindx] = nx.number_connected_components(graph)
                    else:
                        list_of_attributes[calcindx] = 'missing'
    
    lst_return = []
    lst_return.append(g[0])
    lst_return.extend(list_of_attributes)
    return lst_return


# Returns true or false after checking to see if a queued graph has been completed
def isComplete(graph):
    for item in mydict[graph]:
        if item is '':
            return False
    return True


# Dedicated to writing only completed queued graphs
def newWriter(graph):
    newCompleteGraphs = []
    with open(out_path, 'a') as outfile:
        writer = csv.writer(outfile)
        newCompleteGraphs.append(graph)
        for keys in mydict[graph]:
            newCompleteGraphs.append(keys)
        writer.writerow(newCompleteGraphs)


# Analysis Functions
def dictAverage(inDict):
    sum = 0
    for key in inDict:
        sum += inDict[key]
    if sum != 0:
        return sum / float(len(inDict))
    else:
        return 0


def dictMax(inDict):
    maxNum = 0
    if len(inDict) == 0:
        return 0
    for key in inDict:
        if maxNum < inDict[key]:
            maxNum = inDict[key]
    return maxNum


def dictMin(inDict):
    minNum = "null"
    if len(inDict) == 0:
        return 0
    for key in inDict:
        if minNum == "null":
            minNum = inDict[key]
        if minNum > inDict[key]:
            minNum = inDict[key]
    return minNum


def dictTotal(inDict):
    totalNum = 0
    if len(inDict) == 0:
        return 0
    for key in inDict:
        totalNum += inDict[key]
    return totalNum

# Multithreading part of code
#def worker():
#    while True:
#        item = q.get()
#        if item is None:
#            break
#        doCalculation(item)
#        if isComplete(item[0]) is True:
#            lock.acquire()
#            try:
#                newWriter(item[0])
#            finally:
#                lock.release()
#        q.task_done()


if __name__ == '__main__':

    #out_path = '/Users/kschmit1/Documents/GitHub/network_classification/src/features/synthetic_features_paralleldata.csv'  # designate your own output path
    out_path=r"C:\Users\kschmit1\Google Drive\Research and Grants\Research\Networks\summer 2017\synthetic_features_test.csv"
    

    
    with open(out_path, 'w', newline= '') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(['Graph']+ header)



    # searches each key for missing data, if not missing data, it writes the complete row to the csv file.  If missing data, it add graph name and attributes missing to incomplete graphs
    for keys in mydict:
        array = mydict[keys]  # may not be needed
        completeRow = True  # used to reset completeRow condition true for each iteration
        incompleteGraphs[keys]=[]
        for i in range(len(array)):
            if array[i] is '':
                # print "The graph " + keys+ " is missing an the attribute " + header[i]
                completeRow = False
                incompleteGraphs[keys].append(i)
                #incompleteGraphs.append(i)
        if (completeRow is True) and (keys not in 'Graph'):
            print(keys)
            completeGraphs.append(keys)
            for j in array:
                completeGraphs.append(j)
            with open(out_path, 'a', newline= '') as outfile:
                writer = csv.writer(outfile)
                writer.writerow(completeGraphs)
                completeGraphs = []
    
    outfile.close()
    
    #print(incompleteGraphs)
    
    queueCal(incompleteGraphs)  # generates list of graph and attributes needed to run
    
    #print(queueAtt)
    
    tmp = list(futures.map(doCalculation, queueAtt))
    
    #print(mydict)
    print(tmp)
    
    with open(out_path, 'a') as outfile:
        writer = csv.writer(outfile)
        for row in tmp:
            writer.writerow(row)
    
    
#    q = queue.Queue(0)
#    threads = []
#    for m in range(num_worker_threads):
#        t = threading.Thread(target=worker)
#        t.start()
#        threads.append(t)
#        time.sleep(.1)
#    
#    for item in queueAtt:
#        q.put(item)
#    
#    q.join()
#    
#    for i in range(num_worker_threads):
#        q.put(None)
#    for t in threads:
#        t.join()
