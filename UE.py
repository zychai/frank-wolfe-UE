import pandas as pd
import numpy as np
import networkx as nx
from scipy.optimize import minimize_scalar


def BPR(FFT, flow, capacity, alpha=0.15, beta=4.0):
    # FTT: indicates the fastest passage time
    # flow: indicates the traffic flow of a section
    # capacity: indicates the road capacity
    # alpha and beta, which are arguments to the BPR function, take default values here
    return FFT * (1 + alpha * (flow / capacity) ** beta)


def all_none_initialize(G, od_df):
    # This is the actual allocation, allocated as all and nothing on the zero flow graph to get flow_real
    # This function is only used once for initialization
    for _, od_data in od_df.iterrows():
        source = od_data["o"]
        target = od_data["d"]
        demand = od_data["demand"]
        # Calculate the shortest path
        shortest_path = nx.shortest_path(G, source=source, target=target, weight="weight")
        # Update the traffic on the path
        for i in range(len(shortest_path) - 1):
            u = shortest_path[i]
            v = shortest_path[i + 1]
            G[u][v]['flow_real'] += demand
    # After initializing the flow, update the impedance
    for _, _, data in G.edges(data=True):
        data['weight'] = BPR(data['FFT'], data['flow_real'], data['Capacity'])


def all_none_temp(G, od_df):
    # This is a virtual assignment used to get f_temp
    nx.set_edge_attributes(G, 0, 'flow_temp')
    for _, od_data in od_df.iterrows():
        # Every update has to read OD, try to optimize this later
        source = od_data["o"]
        target = od_data["d"]
        demand = od_data["demand"]
        # Calculate the shortest path
        shortest_path = nx.shortest_path(G, source=source, target=target, weight="weight")
        # Update the traffic on the path
        for i in range(len(shortest_path) - 1):
            u = shortest_path[i]
            v = shortest_path[i + 1]
            G[u][v]['flow_temp'] += demand


def get_descent(G):
    # Get descent direction
    for _, _, data in G.edges(data=True):
        data['descent'] = data['flow_temp'] - data['flow_real']


def objective_function(temp_step, G):
    s, alpha, beta = 0, 0.15, 4.0
    for _, _, data in G.edges(data=True):
        x = data['flow_real'] + temp_step * data['descent']
        s += data["FFT"] * (x + alpha * data["Capacity"] / (beta + 1) * (x / data["Capacity"]) ** (beta + 1))
    return s


def update_flow_real(G):
    # This function actually adjusts the flow, adjusts flow_real, and updates the weight
    best_step = get_best_step(G)  # Get the optimal step size
    for _, _, data in G.edges(data=True):
        # Adjust the flow rate and update the blockage
        data['flow_real'] += best_step * data["descent"]
        data['weight'] = BPR(data['FFT'], data['flow_real'], data['Capacity'])


def get_best_step(G, tolerance=1e-4):
    result = minimize_scalar(objective_function, args=(G,), bounds=(0, 1), method='bounded', tol=tolerance)
    return result.x


def build_network(Link_path):
    # Read the edge data
    links_df = pd.read_csv(Link_path)
    G = nx.from_pandas_edgelist(links_df, source='O', target='D', edge_attr=['FFT', 'Capacity'],
                                create_using=nx.DiGraph())
    nx.set_edge_attributes(G, 0, 'flow_temp')
    nx.set_edge_attributes(G, 0, 'flow_real')
    nx.set_edge_attributes(G, 0, 'descent')
    nx.set_edge_attributes(G, nx.get_edge_attributes(G, "FFT"), 'weight')
    return G


def main():
    G = build_network("Link.csv")  # Build a road network
    od_df = pd.read_csv("OD.csv")  # Get OD requirements
    all_none_initialize(G, od_df)  # Initialize the network flow
    print("Initial flow", list(nx.get_edge_attributes(G, 'flow_real').values()))

    epoch = 0  # Record the number of iterations
    err, max_err = 1, 1e-4  # Respectively represents the initial value and the maximum allowable error
    f_list_old = np.array(list(nx.get_edge_attributes(G, 'flow_real').values()))
    while err > max_err:
        epoch += 1
        all_none_temp(G, od_df)  # All and none allocation, get flow_temp
        get_descent(G)  # Calculate the gradient, i.e. flow_temp-flow_real
        update_flow_real(
            G)  # First one-dimensional search to obtain the optimal step size, and then adjust the traffic, update the road resistance

        # Calculate and update the error err
        f_list_new = np.array(
            list(nx.get_edge_attributes(G, 'flow_real').values()))  # This variable is the new network traffic list
        d = np.sum((f_list_new - f_list_old) ** 2)
        err = np.sqrt(d) / np.sum(f_list_old)
        f_list_old = f_list_new

    print("User balanced traffic", list(nx.get_edge_attributes(G, 'flow_real').values()))
    print("Number of iterations", epoch)
    # Export network balancing traffic
    df = nx.to_pandas_edgelist(G)
    df = df[["source", "target", "flow_real"]].sort_values(by=["source", "target"])
    df.to_csv("Network equalization result.csv", index=False)


if __name__ == '__main__':
    main()
