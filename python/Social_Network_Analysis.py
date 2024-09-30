import networkx as nx
import matplotlib.pyplot as plt

# Create a directed graph
G = nx.DiGraph()

# Add nodes (people)
people = ['Alice', 'Bob', 'Charlie', 'David', 'Eve', 'Frank']
G.add_nodes_from(people)

# Add edges (relationships)
edges = [('Alice', 'Bob'), ('Alice', 'Charlie'), ('Bob', 'David'),
         ('Charlie', 'David'), ('David', 'Eve'), ('Eve', 'Frank'),
         ('Frank', 'Alice'), ('Bob', 'Frank')]
G.add_edges_from(edges)

# Draw the graph
plt.figure(figsize=(8, 6))
nx.draw(G, with_labels=True, node_color='lightblue', node_size=2000, font_size=10, font_color='black', arrows=True)
plt.title('Simple Social Network')
plt.show()
