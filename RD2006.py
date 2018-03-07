"""
This script supports ot analyse the 2006 reporting delay
"""
import TNtools as tnt
import networkx as nx
import pandas as pd
import click




def stats_with_el(el):
    print(el.head())
    r, c = el.shape
    maxvol = el["VOL"].sum()
    print("data frame created ")
    #
    # create empty diGraph
    G = nx.DiGraph()


    #
    # get the set of sorted delays
    # TODO: will be used later for complete analysis
    delays = sorted(set(el['MELD_DELAY'].values.tolist()))

    # neig = [(d, el[el["MELD_DELAY"] <= d].count()["MELD_DELAY"]/float(r)) for d in delays]

    rd = 0
    vol = 0
    noe = []
    print("trade freq and trade vol")
    with click.progressbar(delays) as bar:
        for d in bar:
            # print(d)
            # rd += el[el["MELD_DELAY"] == d].count()["VOL"]
            # print(rd)
            sel = el.ix[el["MELD_DELAY"] == d]
            rd += sel['VOL'].count()
            vol += sel['VOL'].sum()
            # print(d, el[el["MELD_DELAY"] == d].sum()["VOL"])
            # vol += el[el["MELD_DELAY"] == d].sum()["VOL"]
            # print(vol)
            noe.append((d, float(rd) / float(r), vol / float(maxvol)))

    print("save data")
    df = pd.DataFrame(data=noe, columns=['delay[days]', 'edges', 'tradevol'])
    df.to_csv("/Users/TOSS/Documents/Projects/ReportingDelay/data/edges_vs_delay.csv",
              index=False,
              sep=',')

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
    if 'TYPE' in el.columns:
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


def large_scale_structure(el, dels):
    #
    # muss noch umprogrammiert werden, um die verschiedenen großskaliegen Strukturen
    # auswaehlen zu koennen
    G = from_edgelist(el, nx.DiGraph())
    noac = nx.number_attracting_components(G)
    print("number of attractings components : ",
          noac)
    print("number of nodes : ",
          nx.number_of_nodes(G))
    #
    # in dem Funktionsausruf wird unterschieden zwischen strongly und
    # weakly connected componten, der Name ist nicht mehr passend
    # gwcc_G = len(max(nx.strongly_connected_components(G), key=len))
    # print(gwcc_G, " ", nx.number_of_nodes(G))
    # hier kommt jetzt die average shortest path length
    # aspl = nx.average_shortest_path_length(G)
    # print("average shortest path length complete graph :", aspl)
    resultslist=[]
    G = nx.DiGraph()
    with click.progressbar(dels) as delays:
        for d in delays:
            sel = el.ix[el["MELD_DELAY"] == d]
            G = from_edgelist(sel, G)
            #
            # strongly connected component
            # gwcc_Gd = (len(max(nx.strongly_connected_components(G), key=len)))
            #
            # average shortest path length
            # aspl_d = nx.average_shortest_path_length(G)
            #
            # number of attracting components
            noac_d = nx.number_attracting_components(G)
            resultslist.append((d, noac, noac_d, float(noac_d)/float(noac)))
    return resultslist


def nodeCentralities(el, dels):
    """Compute centralities for nodes"""
    G = from_edgelist(el, nx.DiGraph())
    nono = nx.number_of_nodes(G)

    G = nx.DiGraph()

    centralities = []

    print(range(5))

    #with click.progressbar(dels[:2]) as delays:
    with click.progressbar(range(4)) as delays:
        for d in delays:
            sel = el.ix[el["MELD_DELAY"] == d]
            G = from_edgelist(sel, G)
            ch = nx.harmonic_centrality(G)
            # print(sum(ch.values()) / (nx.number_of_nodes(c) * (nx.number_of_nodes(c) - 1)))
            fragmentation = 1. - (sum(ch.values()) / (nono * (nono - 1)))
            centralities.extend([d, fragmentation])

    print("ready to return")
    return centralities

    # df_central = pd.DataFrame(harmonic_c)
    # print(df_central.head())

if __name__ == "__main__":
    # A livestock trade network graph is created from an edgelist.
    # An edgelist is an comma seperated file with a header
    # The minimum elements in the edgelist are the source and the target nodes.
    # In order to set up the graph from an edgelist one hast ot specify the
    # * filename
    # * data types
    # * the variables used are dates.
    fn_edgelist = "/Users/TOSS/Documents/Projects/ReportingDelay/data/Delay2006.csv"
    dtypes = {"S": str, "T": str, "VOL": int, "ZUGA_DATE": str, "MELD_DATE": str, "MELD_DELAY": int}
    el = tnt.readedgelist(fn_edgelist, dtypes=dtypes, dates=["ZUGA_DATE", "MELD_DATE"])
    delays = sorted(set(el['MELD_DELAY'].values.tolist()))

    #stats_with_el(el)
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
    #
         # From edgelist muss immer angepasst werden
    # lss = large_scale_structure(el, delays)
    # for items in lss:
    #     print(items)

    nC = nodeCentralities(el, delays)
    print(nC)
