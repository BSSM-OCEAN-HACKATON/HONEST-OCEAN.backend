from typing import List, Dict
from sqlalchemy.orm import Session
from app.models import MerchantRecord
import math

def calculate_best_path(points: List[int], db: Session) -> List[int]:
    """
    Calculates the best path using Prim's Algorithm (MST) -> DFS (Preorder Traversal).
    This provides a 2-approximation for the TSP.
    """
    if not points or len(points) < 2:
        return points

    # 1. Fetch Coordinates
    records = db.query(MerchantRecord).filter(MerchantRecord.id.in_(points)).all()
    coords = {r.id: (r.latitude, r.longitude) for r in records}
    
    # Filter points that exist in DB to avoid errors
    valid_points = [p for p in points if p in coords]
    if len(valid_points) < 2:
        return valid_points

    # 2. Prim's Algorithm for MST
    # We use a dense graph implementation O(V^2)
    mst_adj = {p: [] for p in valid_points}
    
    # Start with the first point in the list as the root
    start_node = valid_points[0]
    visited = set()
    
    # min_dist stores current shortest distance from standard tree to node
    # key: node_id, value: (distance, parent_node_id)
    min_dist = {p: (float('inf'), None) for p in valid_points}
    min_dist[start_node] = (0, None)
    
    # Loop until all nodes are visited
    while len(visited) < len(valid_points):
        # Extract Min: Find unvisited node with smallest distance
        current_node = None
        current_min_d = float('inf')
        
        for p in valid_points:
            if p not in visited:
                d, parent = min_dist[p]
                if d < current_min_d:
                    current_min_d = d
                    current_node = p
        
        if current_node is None:
            break # Should not happen in connected graph
            
        visited.add(current_node)
        parent_node = min_dist[current_node][1]
        
        # Add edge to MST
        if parent_node is not None:
             mst_adj[parent_node].append(current_node)
             mst_adj[current_node].append(parent_node)
        
        # Update distances to neighbors
        cur_lat, cur_lon = coords[current_node]
        
        for neighbor in valid_points:
            if neighbor not in visited:
                n_lat, n_lon = coords[neighbor]
                # Simple Euclidean Distance
                dist = math.sqrt((cur_lat - n_lat)**2 + (cur_lon - n_lon)**2)
                
                if dist < min_dist[neighbor][0]:
                    min_dist[neighbor] = (dist, current_node)

    # 3. Preorder Traversal (DFS) to generate path
    final_path = []
    visited_dfs = set()
    
    def dfs(u):
        visited_dfs.add(u)
        final_path.append(u)
        # Visit children
        for v in mst_adj[u]:
            if v not in visited_dfs:
                dfs(v)
                
    dfs(start_node)
    
    return final_path
