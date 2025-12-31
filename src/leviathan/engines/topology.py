import numpy as np
from scipy.spatial import cKDTree
import networkx as nx

def build_structure_graph(positions, linking_length):
    """
    Converts a point cloud (Quasars) into a graph using Friends-of-Friends.
    positions: (N, 3) array of XYZ coordinates (Mpc)
    linking_length: Max distance to link two nodes (Mpc)
    
    Returns: NetworkX Graph
    """
    tree = cKDTree(positions)
    # Find all pairs within linking_length
    pairs = tree.query_pairs(r=linking_length)
    
    G = nx.Graph()
    G.add_nodes_from(range(len(positions)))
    G.add_edges_from(pairs)
    
    return G

def get_largest_structure(G):
    """
    Returns the diameter (longest path) of the largest connected component.
    """
    if nx.is_empty(G):
        return 0, 0
        
    # Get connected components (Clusters)
    components = sorted(nx.connected_components(G), key=len, reverse=True)
    largest_comp = G.subgraph(components[0])
    
    # Calculate physical diameter (Approximate via bounding box for speed, or exact graph diameter)
    # For exact graph diameter (longest shortest path), it's computationally expensive O(N^3).
    # We will use the 'Extent' metric: max distance between any two nodes in the cluster.
    return len(largest_comp), largest_comp

def measure_extent(subgraph, positions):
    """
    Measures the maximum physical distance between any two points in the cluster.
    """
    nodes = list(subgraph.nodes())
    coords = positions[nodes]
    
    # Brute force max distance (okay for small clusters, optimized for large)
    # We use the Convex Hull diameter for speed
    from scipy.spatial import ConvexHull, distance_matrix
    
    if len(coords) < 3:
        return np.max(distance_matrix(coords, coords))
        
    hull = ConvexHull(coords)
    hull_points = coords[hull.vertices]
    dists = distance_matrix(hull_points, hull_points)
    return np.max(dists)
