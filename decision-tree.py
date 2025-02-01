import networkx as nx
import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional, Set
import graphviz

@dataclass
class Config:
    contract_rent: float = 70.0
    premium: float = 0.15
    total_space: float = 100000.0
    more_vertex: int = 2
    no_more_vertex: int = 3
    print_debug: bool = False

config = Config()

class DecisionTree:
    def __init__(self):
        self.g = nx.DiGraph()
        self.setup_graph()
        
    def setup_graph(self):
        edges = [
            (1,2), (1,3),
            (2,4), (2,5), (2,6),
            (3,7), (3,8), (3,9),
            (4,10), (4,11), (4,12),
            (5,13), (5,14), (5,15),
            (6,16), (6,17), (6,18),
            (7,19), (7,20), (7,21),
            (8,22), (8,23), (8,24),
            (9,25), (9,26), (9,27)
        ]
        self.g.add_edges_from(edges)
        
        edge_probs = {
            (1,2): 1.0, (1,3): 1.0,
            (2,4): 0.4, (2,5): 0.5, (2,6): 0.1,
            (4,10): 0.6, (4,11): 0.3, (4,12): 0.1,
            (5,13): 0.4, (5,14): 0.5, (5,15): 0.1,
            (6,16): 0.2, (6,17): 0.6, (6,18): 0.2
        }
        nx.set_edge_attributes(self.g, edge_probs, 'probability')
        
        self._copy_probabilities(4, 7)
        self._copy_probabilities(5, 8)
        self._copy_probabilities(6, 9)
        self._copy_probabilities(2, 3)

        vertex_labels = {
            2: "Take +10%", 3: "Take +0%",
            4: "M+", 5: "M0", 6: "M-", 
            7: "M+", 8: "M0", 9: "M-"
        }
        
        for i in [10,13,16,19,22,25]:
            vertex_labels[i] = "D+"
        for i in [11,14,17,20,23,26]:
            vertex_labels[i] = "D0"
        for i in [12,15,18,21,24,27]:
            vertex_labels[i] = "D-"
            
        nx.set_node_attributes(self.g, vertex_labels, 'label')
        
        vertex_weights = {
            2: 0.1, 3: 0.0,  # Action vertices
            4: 0.1, 5: 0.0, 6: -0.05,  # Market change vertices
            7: 0.1, 8: 0.0, 9: -0.05   # Market change vertices
        }
        
        for i in [10,13,16,19,22,25]:
            vertex_weights[i] = 0.1  # D+
        for i in [11,14,17,20,23,26]:
            vertex_weights[i] = 0.0  # D0
        for i in [12,15,18,21,24,27]:
            vertex_weights[i] = -0.05  # D-
            
        nx.set_node_attributes(self.g, vertex_weights, 'weight')

    def _copy_probabilities(self, source: int, dest: int) -> None:
        source_edges = list(self.g.out_edges(source))
        dest_edges = list(self.g.out_edges(dest))
        
        for (_, s_target), (_, d_target) in zip(source_edges, dest_edges):
            prob = self.g[source][s_target].get('probability', 0)
            self.g[dest][d_target]['probability'] = prob

    def get_terminal_vertices(self, start_vertex: Optional[int] = None) -> List[int]:
        if start_vertex is None:
            return [v for v in self.g.nodes() if self.g.out_degree(v) == 0]
        else:
            descendants = list(nx.descendants(self.g, start_vertex))
            return [v for v in descendants if self.g.out_degree(v) == 0]

    def get_vertex_probability(self, vertex: int) -> float:
        if vertex == 1:
            return 1.0
            
        path = nx.shortest_path(self.g, 1, vertex)
        prob = 1.0
        
        for i in range(len(path)-1):
            edge_prob = self.g[path[i]][path[i+1]].get('probability', 0)
            prob *= edge_prob
            
        return prob

    def calculate_cost(self, vertex: int) -> float:
        if vertex not in self.get_terminal_vertices():
            raise ValueError(f"Vertex {vertex} is not a terminal vertex")
            
        path = nx.shortest_path(self.g, 1, vertex)
        
        demand_delta = self.g.nodes[vertex]['weight']
        market_vertex = path[-2]
        market_delta = self.g.nodes[market_vertex]['weight']
        action_vertex = path[1]
        uptake = self.g.nodes[action_vertex]['weight']
        
        have = config.total_space * (1 + uptake)
        need = config.total_space * (1 + demand_delta)
        
        if have < need:
            bandaid_space = need - have
            cost = bandaid_space * config.contract_rent * (1 + market_delta) * (1 + config.premium)
        else:
            excess_space = have - need
            cost = excess_space * config.contract_rent
            
        return cost

    def analyze_decision_choices(self):
        print("\nDecision Analysis:\n")
        
        more_terminals = self.get_terminal_vertices(config.more_vertex)
        more_ev = 0
        print("Choice: Take More Space (Vertex 2)")
        print("Terminal | Probability | Cost ($) | Expected Value ($)")
        print("-" * 50)
        for v in sorted(more_terminals):
            prob = self.get_vertex_probability(v)
            cost = self.calculate_cost(v)
            ev = prob * cost
            more_ev += ev
            print(f"{v:8d} | {prob:10.3f} | {cost:9,.2f} | {ev:16,.2f}")
        print(f"Total Expected Value for More Space: ${more_ev:,.2f}\n")

        no_more_terminals = self.get_terminal_vertices(config.no_more_vertex)
        no_more_ev = 0
        print("Choice: Take No More Space (Vertex 3)")
        print("Terminal | Probability | Cost ($) | Expected Value ($)")
        print("-" * 50)
        for v in sorted(no_more_terminals):
            prob = self.get_vertex_probability(v)
            cost = self.calculate_cost(v)
            ev = prob * cost
            no_more_ev += ev
            print(f"{v:8d} | {prob:10.3f} | {cost:9,.2f} | {ev:16,.2f}")
        print(f"Total Expected Value for No More Space: ${no_more_ev:,.2f}\n")

        if more_ev < no_more_ev:
            print(f"Optimal choice: Take More Space (saves ${no_more_ev - more_ev:,.2f})")
        else:
            print(f"Optimal choice: Take No More Space (saves ${more_ev - no_more_ev:,.2f})")

        return more_ev, no_more_ev

    def calculate_evpi(self):
        more_ev, no_more_ev = self.analyze_decision_choices()
        best_decision_ev = min(more_ev, no_more_ev)
        
        ev_perfect = 0
        more_vertices = sorted(self.get_terminal_vertices(config.more_vertex))
        no_more_vertices = sorted(self.get_terminal_vertices(config.no_more_vertex))
        
        print("\nEVPI Analysis:")
        print("\nState-by-state comparison:")
        print("State | More Space EV | No More EV | Best EV")
        print("-" * 50)
        
        for v_more, v_no_more in zip(more_vertices, no_more_vertices):
            ev_more = self.get_vertex_probability(v_more) * self.calculate_cost(v_more)
            ev_no_more = self.get_vertex_probability(v_no_more) * self.calculate_cost(v_no_more)
            best_ev = min(ev_more, ev_no_more)
            ev_perfect += best_ev
            print(f"{v_more:5d} | ${ev_more:11,.2f} | ${ev_no_more:9,.2f} | ${best_ev:7,.2f}")
        
        print(f"\nBest decision EV without perfect information: ${best_decision_ev:,.2f}")
        print(f"Expected value with perfect information: ${ev_perfect:,.2f}")
        evpi = best_decision_ev - ev_perfect
        print(f"Value of perfect information: ${evpi:,.2f}")
        
        return evpi

    def visualize(self, filename='decision_tree'):
        dot = graphviz.Digraph(comment='Space Decision Tree')
        dot.attr(rankdir='LR')  # Left to right layout
        
        # Node styles
        dot.attr('node', shape='box')
        
        # Add nodes with labels and weights
        for node in self.g.nodes():
            label = self.g.nodes[node].get('label', '')
            weight = self.g.nodes[node].get('weight', '')
            
            # Format node label
            if node == 1:
                node_label = 'Start'
            elif label in ['Take +10%', 'Take +0%']:
                node_label = f'{label}'
            else:
                node_label = f'Node {node}\n{label}\n{weight:+.0%}' if weight != '' else f'Node {node}\n{label}'
            
            # Different styles for different node types
            if node == 1:
                dot.node(str(node), node_label, shape='circle')
            elif node in [2, 3]:  # Decision nodes
                dot.node(str(node), node_label, shape='diamond')
            elif self.g.out_degree(node) == 0:  # Terminal nodes
                # Calculate cost for terminal nodes
                cost = self.calculate_cost(node) if self.g.out_degree(node) == 0 else 0
                prob = self.get_vertex_probability(node)
                node_label += f'\nCost: ${cost:,.0f}\nProb: {prob:.3f}'
                dot.node(str(node), node_label, shape='box')
            else:
                dot.node(str(node), node_label, shape='oval')

        # Add edges with probabilities
        for edge in self.g.edges():
            prob = self.g[edge[0]][edge[1]].get('probability', '')
            if prob != '':
                dot.edge(str(edge[0]), str(edge[1]), label=f'{prob:.2f}')
            else:
                dot.edge(str(edge[0]), str(edge[1]))

        # Save the visualization
        dot.render(filename, view=True, format='png')
        return dot

if __name__ == "__main__":
    tree = DecisionTree()
    more_ev, no_more_ev = tree.analyze_decision_choices()
    evpi = tree.calculate_evpi()
    tree.visualize()