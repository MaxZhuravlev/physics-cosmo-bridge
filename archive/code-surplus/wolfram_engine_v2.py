"""
Wolfram Hypergraph Rewriting Engine v2
======================================

CRITICAL IMPROVEMENT over v1:
  v1 matched SINGLE hyperedges only → generates tree-like 1D structures → kappa=0
  v2 matches MULTIPLE hyperedges (real Wolfram rules) → generates 2D/3D spatial geometry

Real Wolfram rule example:
  {{1,2,3},{2,4,5}} -> {{5,6,1},{6,4,2},{4,5,3}}
  This matches TWO hyperedges sharing vertex 2.

This is essential for:
  - Ollivier-Ricci kappa != 0 (requires genuine curvature, not flat 1D)
  - Dirac with non-degenerate orientation
  - All continuum limit tests
"""

from typing import List, Tuple, Set, Dict, Optional, FrozenSet
from collections import defaultdict, deque
import itertools
import numpy as np
import networkx as nx
import time

# Type aliases
Hyperedge = Tuple[int, ...]
Hypergraph = Tuple[Hyperedge, ...]  # Immutable for hashing
Rule = Tuple[List[Hyperedge], List[Hyperedge]]  # (pattern_edges, replacement_edges)


class WolframEngineV2:
    """
    Multi-edge pattern matching hypergraph rewriting engine.

    Rules are of the form:
        (pattern_edges, replacement_edges)
    where pattern_edges is a list of hyperedges to match simultaneously,
    and replacement_edges is what replaces them.

    Variable convention: integers 1,2,3,... are pattern variables.
    In pattern: same integer means same vertex (shared structure).
    In replacement: pattern variables keep their binding, new variables get fresh IDs.
    """

    def __init__(self, rules: List[Rule]):
        self.rules = rules
        self._next_vertex = 1

    def _find_matches(self, graph: List[Hyperedge], pattern: List[Hyperedge]) -> List[Dict[int, int]]:
        """
        Find all ways to match the pattern (list of hyperedges) against the graph.
        Returns list of variable bindings: {pattern_var -> graph_vertex}
        """
        matches = []

        if len(pattern) == 1:
            # Single-edge pattern: match against each hyperedge
            p = pattern[0]
            for edge in graph:
                if len(edge) != len(p):
                    continue
                # Direct positional match (Wolfram convention: order matters)
                binding = {}
                valid = True
                for pv, gv in zip(p, edge):
                    if pv in binding:
                        if binding[pv] != gv:
                            valid = False
                            break
                    else:
                        binding[pv] = gv
                if valid:
                    matches.append(binding)
            return matches

        if len(pattern) == 2:
            # Two-edge pattern: match both edges, ensuring shared variables bind consistently
            p1, p2 = pattern
            for i, edge1 in enumerate(graph):
                if len(edge1) != len(p1):
                    continue
                # Try binding p1 to edge1
                binding1 = {}
                valid1 = True
                for pv, gv in zip(p1, edge1):
                    if pv in binding1:
                        if binding1[pv] != gv:
                            valid1 = False
                            break
                    else:
                        binding1[pv] = gv
                if not valid1:
                    continue

                # Now try to extend binding to p2 from remaining edges
                for j, edge2 in enumerate(graph):
                    if j == i:
                        continue  # Can't reuse same hyperedge
                    if len(edge2) != len(p2):
                        continue

                    binding = dict(binding1)
                    valid2 = True
                    for pv, gv in zip(p2, edge2):
                        if pv in binding:
                            if binding[pv] != gv:
                                valid2 = False
                                break
                        else:
                            binding[pv] = gv
                    if valid2:
                        matches.append(binding)
            return matches

        # General case (3+ edges): recursive
        # Match first pattern edge, then recursively match rest
        p_first = pattern[0]
        p_rest = pattern[1:]

        for i, edge in enumerate(graph):
            if len(edge) != len(p_first):
                continue
            binding = {}
            valid = True
            for pv, gv in zip(p_first, edge):
                if pv in binding:
                    if binding[pv] != gv:
                        valid = False
                        break
                else:
                    binding[pv] = gv
            if not valid:
                continue

            # Remove this edge and recurse
            remaining = graph[:i] + graph[i+1:]
            sub_matches = self._find_matches_with_binding(remaining, p_rest, binding)
            matches.extend(sub_matches)

        return matches

    def _find_matches_with_binding(self, graph: List[Hyperedge], pattern: List[Hyperedge],
                                    partial_binding: Dict[int, int]) -> List[Dict[int, int]]:
        """Find matches extending a partial binding."""
        if not pattern:
            return [dict(partial_binding)]

        p_first = pattern[0]
        p_rest = pattern[1:]
        matches = []

        for i, edge in enumerate(graph):
            if len(edge) != len(p_first):
                continue
            binding = dict(partial_binding)
            valid = True
            for pv, gv in zip(p_first, edge):
                if pv in binding:
                    if binding[pv] != gv:
                        valid = False
                        break
                else:
                    binding[pv] = gv
            if not valid:
                continue

            remaining = graph[:i] + graph[i+1:]
            sub_matches = self._find_matches_with_binding(remaining, p_rest, binding)
            matches.extend(sub_matches)

        return matches

    def _apply_rule(self, graph: List[Hyperedge], pattern: List[Hyperedge],
                    replacement: List[Hyperedge], binding: Dict[int, int],
                    next_vertex: int) -> Tuple[List[Hyperedge], int, Dict[int, int]]:
        """
        Apply rule with given binding.
        Returns: (new_graph, next_vertex_after, fresh_vertex_map)
        """
        # Identify which graph edges were matched
        used_edges = []
        remaining = list(graph)

        for p_edge in pattern:
            matched_edge = tuple(binding[v] for v in p_edge)
            # Remove first occurrence
            for i, e in enumerate(remaining):
                if e == matched_edge:
                    used_edges.append(e)
                    remaining.pop(i)
                    break

        # All pattern variables that appear in the binding
        bound_vars = set(binding.keys())

        # Build replacement edges with fresh vertices for new variables
        fresh_map = {}
        nv = next_vertex

        new_edges = []
        for r_edge in replacement:
            new_edge = []
            for v in r_edge:
                if v in binding:
                    # Known variable from pattern
                    new_edge.append(binding[v])
                else:
                    # New variable: assign fresh vertex
                    if v not in fresh_map:
                        fresh_map[v] = nv
                        nv += 1
                    new_edge.append(fresh_map[v])
            new_edges.append(tuple(new_edge))

        new_graph = remaining + new_edges
        return new_graph, nv, fresh_map

    def evolve_spatial(self, initial: List[Hyperedge], steps: int,
                       max_edges: int = 5000) -> List[Hyperedge]:
        """
        Parallel-update spatial evolution: apply ALL non-overlapping matches per step.

        This is the standard Wolfram Physics evolution for studying
        spatial geometry (curvature, dimension, etc.). Parallel updating
        is what generates genuine 2D/3D spatial structure.
        """
        graph = list(initial)
        nv = max(max(e) for e in graph) + 1

        for step in range(steps):
            if len(graph) > max_edges:
                break

            applied_any = False

            for pattern, replacement in self.rules:
                matches = self._find_matches(graph, pattern)
                if not matches:
                    continue

                # Find maximal set of non-overlapping matches
                non_overlapping = self._select_non_overlapping(graph, pattern, matches)

                if not non_overlapping:
                    continue

                # Apply all non-overlapping matches simultaneously
                # Collect edges to remove and edges to add
                edges_to_remove = []
                edges_to_add = []

                for binding in non_overlapping:
                    # Identify matched edges
                    for p_edge in pattern:
                        matched_edge = tuple(binding[v] for v in p_edge)
                        edges_to_remove.append(matched_edge)

                    # Build replacement with fresh vertices
                    fresh_map = {}
                    new_edges = []
                    for r_edge in replacement:
                        new_edge = []
                        for v in r_edge:
                            if v in binding:
                                new_edge.append(binding[v])
                            else:
                                if v not in fresh_map:
                                    fresh_map[v] = nv
                                    nv += 1
                                new_edge.append(fresh_map[v])
                        new_edges.append(tuple(new_edge))
                    edges_to_add.extend(new_edges)

                # Remove matched edges
                remaining = list(graph)
                for e in edges_to_remove:
                    for i, ge in enumerate(remaining):
                        if ge == e:
                            remaining.pop(i)
                            break

                graph = remaining + edges_to_add
                applied_any = True

            if not applied_any:
                break

        return graph

    def _select_non_overlapping(self, graph: List[Hyperedge], pattern: List[Hyperedge],
                                 matches: List[Dict[int, int]]) -> List[Dict[int, int]]:
        """
        Select maximal non-overlapping set of matches.
        Two matches overlap if they use any of the same graph edges.
        Greedy algorithm.
        """
        selected = []
        used_edges = set()

        for binding in matches:
            # Compute which graph edges this match uses
            match_edges = set()
            for p_edge in pattern:
                matched_edge = tuple(binding[v] for v in p_edge)
                match_edges.add(matched_edge)

            # Check no overlap
            if match_edges & used_edges:
                continue

            selected.append(binding)
            used_edges |= match_edges

        return selected

    def evolve_multiway(self, initial: List[Hyperedge], steps: int,
                        max_states: int = 2000) -> Dict[Tuple, Dict]:
        """
        Evolve multiway system: track ALL possible rule applications.
        Each state is a frozenset of sorted hyperedges.
        """
        def state_key(graph):
            return tuple(sorted(graph))

        states = {}
        initial_key = state_key(initial)
        states[initial_key] = {
            'depth': 0,
            'parents': set(),
            'children': set(),
            'graph': list(initial)
        }

        queue = deque([(initial_key, 0)])
        nv = max(max(e) for e in initial) + 1

        while queue and len(states) < max_states:
            current_key, depth = queue.popleft()

            if depth >= steps:
                continue

            current_graph = states[current_key]['graph']

            for pattern, replacement in self.rules:
                matches = self._find_matches(current_graph, pattern)

                for binding in matches:
                    new_graph, new_nv, _ = self._apply_rule(
                        current_graph, pattern, replacement, binding, nv
                    )
                    nv = max(nv, new_nv)

                    new_key = state_key(new_graph)

                    if new_key not in states:
                        states[new_key] = {
                            'depth': depth + 1,
                            'parents': set(),
                            'children': set(),
                            'graph': new_graph
                        }
                        queue.append((new_key, depth + 1))

                    states[current_key]['children'].add(new_key)
                    states[new_key]['parents'].add(current_key)

        return states

    def build_causal_graph(self, multiway_states: Dict) -> nx.DiGraph:
        """Build causal/multiway graph from evolution."""
        G = nx.DiGraph()
        for state_key, meta in multiway_states.items():
            G.add_node(state_key, depth=meta['depth'])
            for child in meta['children']:
                G.add_edge(state_key, child)
        return G


def hypergraph_to_graph(hypergraph: List[Hyperedge]) -> nx.Graph:
    """
    Convert hypergraph to ordinary graph for geometric analysis.
    Each hyperedge (a,b,c) creates edges a-b, b-c, a-c.
    This is the SPATIAL graph whose geometry we measure.
    """
    G = nx.Graph()
    for edge in hypergraph:
        for i in range(len(edge)):
            for j in range(i+1, len(edge)):
                G.add_edge(edge[i], edge[j])
    return G


# =============================================================================
# Registry of Notable Wolfram Universes
# These are REAL multi-edge rules that generate 2D/3D spatial geometry
# =============================================================================

WOLFRAM_RULES_V2 = {
    # Rule 30 analog: simple but generates complex structure
    "rule_simple_growth": {
        "rules": [
            ([( 1, 2, 3)], [(1, 4, 5), (4, 2, 5), (5, 3, 4)])
        ],
        "initial": [(0, 0), (0, 0), (0, 0)],  # Will be replaced below
        "description": "Simple single-edge growth rule"
    },

    # THE KEY RULE: {{1,2,3},{2,4,5}} -> {{5,6,1},{6,4,2},{4,5,3}}
    # This is Wolfram's original rule that generates 3D-like spatial structure
    "wolfram_original": {
        "rules": [
            ([(1, 2, 3), (2, 4, 5)], [(5, 6, 1), (6, 4, 2), (4, 5, 3)])
        ],
        "initial": [(1, 2, 3), (2, 4, 5)],
        "description": "Wolfram original: 2-edge pattern, generates 3D-like geometry"
    },

    # {{1,2},{1,3}} -> {{1,4},{4,2},{4,3}}
    # Known to generate 2D spatial structure
    "rule_2d_binary": {
        "rules": [
            ([(1, 2), (1, 3)], [(1, 4), (4, 2), (4, 3)])
        ],
        "initial": [(1, 2), (1, 3), (1, 4)],
        "description": "Binary 2-edge rule, generates 2D geometry"
    },

    # {{1,2},{1,3},{1,4}} -> {{5,2},{5,3},{5,4},{1,5}}
    # Star expansion
    "rule_star_expansion": {
        "rules": [
            ([(1, 2), (1, 3), (1, 4)], [(5, 2), (5, 3), (5, 4), (1, 5)])
        ],
        "initial": [(1, 2), (1, 3), (1, 4)],
        "description": "Star expansion: 3-edge pattern → 4 edges"
    },

    # {{1,2},{3,2}} -> {{1,4},{4,3},{4,2}}
    # Simple 2-edge binary rule
    "rule_simple_2edge": {
        "rules": [
            ([(1, 2), (3, 2)], [(1, 4), (4, 3), (4, 2)])
        ],
        "initial": [(1, 2), (2, 3), (3, 1)],
        "description": "Simple 2-edge binary, triangle seed"
    },

    # {{1,2},{1,3}} -> {{4,2},{4,3},{1,4},{4,1}}
    # Bidirectional expansion (richer geometry)
    "rule_bidir": {
        "rules": [
            ([(1, 2), (1, 3)], [(4, 2), (4, 3), (1, 4), (4, 1)])
        ],
        "initial": [(1, 2), (1, 3), (2, 3)],
        "description": "Bidirectional expansion from 2-edge pattern"
    },
}

# Fix initial for rule_simple_growth: use a proper trinary seed
WOLFRAM_RULES_V2["rule_simple_growth"]["initial"] = [(1, 2, 3)]


def test_engine_v2():
    """Basic functionality test"""
    print("=" * 70)
    print("WolframEngineV2 - Basic Tests")
    print("=" * 70)

    for name, spec in WOLFRAM_RULES_V2.items():
        print(f"\n[{name}] {spec['description']}")

        engine = WolframEngineV2(spec['rules'])

        # Spatial evolution (deterministic)
        t0 = time.time()
        spatial = engine.evolve_spatial(spec['initial'], steps=50, max_edges=1000)
        t1 = time.time()

        # Convert to graph
        G = hypergraph_to_graph(spatial)

        print(f"  Spatial: {len(spatial)} hyperedges, {G.number_of_nodes()} vertices, "
              f"{G.number_of_edges()} edges ({t1-t0:.2f}s)")

        if G.number_of_nodes() > 3:
            # Basic geometry
            if nx.is_connected(G):
                diameter = nx.diameter(G)
                avg_degree = np.mean([d for _, d in G.degree()])
                print(f"  Connected: YES, diameter={diameter}, avg_degree={avg_degree:.1f}")
            else:
                components = list(nx.connected_components(G))
                largest = max(components, key=len)
                print(f"  Connected: NO, {len(components)} components, "
                      f"largest={len(largest)} vertices")

        # Multiway evolution (small scale for test)
        t0 = time.time()
        multiway = engine.evolve_multiway(spec['initial'], steps=4, max_states=200)
        t1 = time.time()

        print(f"  Multiway: {len(multiway)} states ({t1-t0:.2f}s)")

    print("\n[OK] All rules functional")


if __name__ == "__main__":
    test_engine_v2()
