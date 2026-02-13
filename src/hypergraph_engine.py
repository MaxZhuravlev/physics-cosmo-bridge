"""
Optimized Hypergraph Rewriting Engine
For testing Wolfram Physics predictions on real hypergraphs
"""

from typing import List, Tuple, Set, Dict, Optional
from collections import defaultdict, deque
import itertools
import numpy as np
import networkx as nx

# Type aliases
Hyperedge = Tuple[int, ...]
Hypergraph = List[Hyperedge]
Rule = Tuple[Hyperedge, List[Hyperedge]]


class HypergraphEngine:
    """Efficient hypergraph rewriting with multiway evolution"""

    def __init__(self, rules: List[Rule]):
        self.rules = rules
        self.max_vertex = 0

    def apply_rule(self, graph: Hypergraph, rule: Rule, match: Dict[int, int]) -> Hypergraph:
        """Apply rule at a specific match, returning new graph"""
        pattern, replacement = rule

        # Remove matched hyperedge
        new_graph = [e for e in graph if e != tuple(match.get(v, v) for v in pattern)]

        # Add replacement hyperedges with fresh vertices
        fresh_vertex = max(max(e) for e in graph) + 1 if graph else 1
        fresh_map = {}

        for edge in replacement:
            new_edge = []
            for v in edge:
                if v in match:
                    # Vertex from pattern - use matched value
                    new_edge.append(match[v])
                else:
                    # New vertex - assign fresh ID
                    if v not in fresh_map:
                        fresh_map[v] = fresh_vertex
                        fresh_vertex += 1
                    new_edge.append(fresh_map[v])
            new_graph.append(tuple(new_edge))

        return new_graph

    def find_matches(self, graph: Hypergraph, pattern: Hyperedge) -> List[Dict[int, int]]:
        """Find all matches of pattern in graph"""
        matches = []

        for edge in graph:
            if len(edge) != len(pattern):
                continue

            # Try to match this edge to pattern
            # For now: simple case - pattern must match exact structure
            for perm in itertools.permutations(edge):
                match = dict(zip(pattern, perm))
                # Verify match is consistent (one-to-one)
                if len(set(match.values())) == len(match):
                    matches.append(match)
                    break  # One match per edge is enough

        return matches

    def evolve_multiway(self, initial: Hypergraph, steps: int,
                        max_states: int = 1000) -> Dict[Tuple[Hyperedge, ...], Dict]:
        """
        Evolve multiway system, tracking all possible histories
        Returns: {state: {'depth': int, 'parents': set, 'children': set}}
        """
        states = {}  # state -> metadata
        queue = deque([(tuple(sorted(initial)), 0)])  # (state, depth)
        states[tuple(sorted(initial))] = {'depth': 0, 'parents': set(), 'children': set()}

        while queue and len(states) < max_states:
            state_tuple, depth = queue.popleft()

            if depth >= steps:
                continue

            state = list(state_tuple)

            # Apply all rules at all matches
            for rule in self.rules:
                pattern, _ = rule
                matches = self.find_matches(state, pattern)

                for match in matches:
                    new_graph = self.apply_rule(state, rule, match)
                    new_state = tuple(sorted(new_graph))

                    # Add edge in multiway graph
                    if new_state not in states:
                        states[new_state] = {'depth': depth + 1, 'parents': set(), 'children': set()}
                        queue.append((new_state, depth + 1))

                    states[state_tuple]['children'].add(new_state)
                    states[new_state]['parents'].add(state_tuple)

        return states

    def compute_causal_graph(self, multiway_states: Dict) -> nx.DiGraph:
        """Build causal graph from multiway evolution"""
        G = nx.DiGraph()

        for state, meta in multiway_states.items():
            G.add_node(state, depth=meta['depth'])
            for child in meta['children']:
                G.add_edge(state, child)

        return G


def test_engine():
    """Test on simple Wolfram rule"""
    # Rule: {{1,2,3},{2,4,5}} -> {{5,6,1},{6,4,2},{4,5,3}}
    rule = (
        (1, 2, 3),
        [(5, 6, 1), (6, 4, 2), (4, 5, 3)]
    )

    engine = HypergraphEngine([rule])
    initial = [(1, 2, 3), (2, 4, 5)]

    states = engine.evolve_multiway(initial, steps=3, max_states=100)
    print(f"Generated {len(states)} states in 3 steps")

    # Check causal invariance
    causal_graph = engine.compute_causal_graph(states)
    print(f"Causal graph: {causal_graph.number_of_nodes()} nodes, {causal_graph.number_of_edges()} edges")

    return states


if __name__ == "__main__":
    test_engine()
