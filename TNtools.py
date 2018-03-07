"""
This file contains tools for the creation, manipulation und analysis of livestock trade network.
A livestock trade network has special features:
- is directed
- is temporal with respect ot the number of nodes and the number of active edges. Strictly  speaking edges are
    present for one day.
- edges may be weighted with distances, trade, volume trade frequency

"""
import pandas as pd
import networkx as nx
import collections
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import describe


def readedgelist(fnedgelist, dtypes, dates=None, nrows=None):
    """
    see also the comment in the from_edgelist method

    An edge list is the basic building block of the
    networks used as a model for animal trade between farms.

    As the name suggests, an edge list is a list of edges.
    Each line of an edge list corresponds to exactly one edge.
    Each line contains at least the names of the nodes connected
    by an edge and any other attributes of the edge.

    The list of edges is called el and the name of the file containing
    the data is called fnedgelist.

    The data of an edge list are read from cvs file (comma separated file)
    into a pandas dataframe, because here the possibilities of an extensive
    data processing exist. In addition, a pandas dataframe can be translated
    directly into a networkx graph.


    reads edgelist form csv and creates pandas dataframe
    scv file needs to have the following column header:

    S,T,VOL,"ZUGA_DATE","MELD_DATE",MELD_DELAY

    all columns except VOL and MELD_DELAY (which are of type int) are of type string

    :param fnedgelist:
    """

    if dates == None:
        return pd.read_csv(fnedgelist, sep=',',
                           dtype=dtypes,
                           nrows = nrows
                           )

    return pd.read_csv(fnedgelist, sep=',',
                       dtype=dtypes,
                       parse_dates=dates,
                       infer_datetime_format=True,
                       nrows = nrows
                       )

def process_commodity_dict(e, d, hasedge=False):
    s,t,v,c = e
    if hasedge == False:
        d[c]=v
    else:
        if c in d:
            d[c].value = d[c].value + v
        else:
            d[c] = v

    return d


def from_edgelist(el, G):
    # TODO: COMMODITY is a specific feature of this project.
    """
    Minimum information which must be included in the dataframe el include a column with eindeuteige Kennung der source nodes
    and a column with eindeutiger Kennung target nodes which must be denoted with "S" and "T" in the edgelist.
    All other information represent additional information of the contact between s and t (e.g. trade volumen, product, etc.
    Because it is not possible to design an all purpose function for all situations, the from_edgelist method has to be
    adapted and recoded according to the requirements.
    Predefined functions (networkx from_pandas_dataframe) for the transformation from an edgelist to a graph are not
    used in this situation.
    With multiple trade actions between nodes s and t, we want to produce a graph which is as simple as possible. There
    exit many rules how to handle this situation. One is to override a previous drawn edge, which is not problematic in
    cases when no more information than the source and the traget node names are available. If more information exists,
    other rules should be applied. An obvious one is to instantiate a multigraph object, which is able to handel multiple
    connections between nodes. In this implementation we stick to the single edge between nodes graph implementation
    and save additioinal information as edge attributes.
    An example: We observe 2 trade activities between nodes s and t with animals heads traded of
    5 and 6 animals respectively. Total number of head equals 11 and the frequency of trade between s and t equals 2
    in this example.
    Both pieces of information are stored as edge attributes.
    This rule can be implemented in a straight forward manner.
    If an edge is already present, we get the attributes for that edge form the pandas dataframe and update the edge
    attributes in a specific way.

    :rtype: networkx graph object G
    :param el: edgelist as a pandas dataframe object.
    :param G: type of graph generated, diGraph, Graph, etc.
    :return: a graph object
    """
    if 'TYPE' in el.columns():
        edges = list(zip(
            el['S'].values.tolist(),
            el['T'].values.tolist(),
            el['VOL'].values.tolist(),
            el['TYPE'].values.tolist()
        ))
        for e in edges:
            s,t,v,c = e
            # print('edge is', e)
            # print(s,t,v)
            if G.has_edge(s,t):
                G[s][t]['VOL'] += v
                G[s][t]['FREQ'] += 1
                G[s][t]['DOG'] = G[s][t]['DOG'] + " " + c       # DOG := Description Of Goods
                G[s][t]['COMMODITY'] = process_commodity_dict(e, G[s][t]['COMMODITY'], G.has_edge(s,t))
            else:
                commo_dict = {}
                pcd = process_commodity_dict(e, commo_dict, G.has_edge(s,t))
                # print('pcd : ', pcd)
                G.add_edge(s, t, VOL=v, FREQ = 1, DOG = c, COMMODITY = pcd)
    else:
        edges = list(zip(
            el['S'].values.tolist(),
            el['T'].values.tolist(),
            el['VOL'].values.tolist(),
        ))
        for e in edges:
            s,t,v, = e
            if G.has_edge(s,t):
                G[s][t]['VOL'] += v
                G[s][t]['FREQ'] += 1
            else:
                G.add_edge(s, t, VOL=v, FREQ = 1)

    return G


def frequence_of_attribute(G, att="FREQ"):
    return collections.Counter(att_to_list(G, att))


def stats_of_attribute(G, att="FREQ"):
    return describe(att_to_list(G, att))


def att_to_list(G, att="FREQ"):
    return [a.get(att) for _, _,a in G.edges(data=True)]

def node_to_list(G, node='S'):
    if node is 'S':
        return [s for s, _ in G.edges()]
    else:
        return [t for _, t in G.edges()]

# Function to count words in a string.
def word_count(string):
    tokens = string.split()
    n_tokens = len(tokens)
    return n_tokens


def pivot_att(G):
    # TODO: Pivot, Attribute nach Funktionsparamters
    vol = att_to_list(G, att="VOL")
    freq = att_to_list(G, att="FREQ")
    como = att_to_list(G, att='COMMODITY')
    source = node_to_list(G)
    target = node_to_list(G, node='T')
    data= {'S':source, 'T':target, 'vol':vol, 'freq':freq, 'como': como}
    ldf = pd.DataFrame(data)
    table = pd.pivot_table(ldf, values='vol', index=['freq'], columns = ['como'], aggfunc = np.median)
    # print(pd.crosstab(ldf['S'], ldf['como'], margins=True))
    print(table)




if __name__ == "__main__":
    # A livestock trade network graph is created from an edgelist.
    # An edgelist is an comma seperated file with a header
    # The minimum elements in the edgelist are the source and the target nodes.
    # In order to set up the graph from an edgelist one hast ot specify the
    # * filename
    # * data types
    # * the variables used are dates.
    fn_edgelist = "/Users/TOSS/Documents/Projects/ReportingDelay/data/Delay2006.csv"
    dtypes = {"S": str, "T": str, "TYPE":str, "VOL": int, "log10VOL":float}
    el = readedgelist(fn_edgelist, dtypes=dtypes, dates=None, )
    #
    # readedgelist returns a pandas data frame which can be used for data manupulation and for creation of a
    # network graph
    #

    # TODO: wenn zeitliche Abhaengigkeiten umgesetzt werden muessen, dann hat das in der edgelist zu erfolgen.

    # print(el.dtypes)
    # print(el.head())
    # print(el['S'].value_counts())
    # print(el['T'].value_counts())
    #
    # Generate graph from edgelist
    # method from_edgelist muss immer angepasst werden, um auf die individuelle Datensituation eingehen zu können.
    #
    # from_edgelist(el, nx.DiGraph())
    # el ist der dataframe, der alle Informationen in der Edgelist enthält.
    # nx.Digraph() ist der zurückgegebene Typ des Graphen
    # .
    G = from_edgelist(el, nx.DiGraph())     # From edgelist muss immer angepasst werden
    print("Number of edges           :", nx.number_of_edges(G))
    print("Frequency of trade Volume : ", frequence_of_attribute(G, "VOL"))
    # print("Frequency of Commodity    : ", frequence_of_attribute(G, "COMMODITY"))
    print("Stats of trade volume     : ", stats_of_attribute(G, "VOL"))
    # print(G.edges(data=True))
    # pivot_att(G)
    #
    # outdegree of node
    print(G.in_degree())
    print(G.out_degree())
    print(G.degree)
    # Kanten ausgeben
    for e in G.edges(data=True):
       print('Edge :', e)

    print(att_to_list(G, att="DOG"))
    #
    # Hier haben wir ein directory von allen ausgehenden Kanten von 208... mit den zugehoerigen Informationen
    print(G['208000000000000'])
    print(nx.degree_assortativity_coefficient(G, x='out', y='in'))
    # TODO: Change node name by degree
    # if you want to change all the keys:
    # d = {'x':1, 'y':2, 'z':3}
    # d1 = {'x':'a', 'y':'b', 'z':'c'}
    # In [10]: dict((d1[key], value) for (key, value) in d.items())
    # Out[10]: {'a': 1, 'b': 2, 'c': 3}
    print(nx.average_neighbor_degree(G, target='in'))
    print(nx.k_nearest_neighbors(G, target='in'))
    # data = att_to_list(G, att="VOL")
    # sns.set_style('whitegrid')
    # sns.distplot(np.log10(np.array(data)), rug=True)
    # plt.show()

    # for e in G.edges(data=True):
    #     s,t,att = e
    #     if att.get("FREQ") > 1:
    #         print(e)