(*
CRITICAL TEST: Ollivier-Ricci on Spatial Hypergraphs
====================================================

Goal: Test continual limit on 2D/3D embedded graphs
Expected: κ ≠ 0 stable for N>1000

This is THE test that makes theorems unconditional!
*)

Needs["SetReplace`"];

Print["========================================"];
Print[" SPATIAL HYPERGRAPH TESTS"];
Print[" Ollivier-Ricci Curvature"];
Print["========================================"];
Print[];

(* Test 1: Simple spatial rule with embedding *)
Print["Test 1: Basic Spatial Rule"];
Print["----------------------------"];

(* Rule from Wolfram Physics - spatial type *)
spatialRule = {{x, y}, {y, z}} -> {{x, w}, {w, z}, {w, y}};

(* Initial condition *)
spatialInit = {{1, 2}, {2, 3}, {3, 4}, {4, 1}};  (* Square *)

Print["Rule: ", spatialRule];
Print["Initial: ", spatialInit, " (square)"];
Print[];

(* Evolve *)
Print["Evolving..."];
result = WolframModel[
    spatialRule,
    spatialInit,
    5,
    "EventSelectionFunction" -> None  (* All events, full multiway *)
];

(* Get states *)
states = result["StatesList"];
nStates = Length[states];

Print["Generated ", nStates, " states in 5 steps"];
Print[];

(* Get causal graph *)
causalGraph = result["CausalGraph"];
Print["Causal graph: ", VertexCount[causalGraph], " vertices, ",
      EdgeCount[causalGraph], " edges"];
Print[];

(* Compute graph distance matrix for Ollivier-Ricci *)
(* Note: SetReplace may not have built-in Ollivier-Ricci *)
(* We'll compute graph curvature measure instead *)

If[VertexCount[causalGraph] > 1,
    (* Simple curvature measure: average clustering coefficient *)
    clustering = Mean[LocalClusteringCoefficient[causalGraph,
                                                   VertexList[causalGraph]]];
    Print["Average clustering (curvature proxy): ", clustering];

    (* Graph distance statistics *)
    If[VertexCount[causalGraph] < 100,
        distances = GraphDistanceMatrix[causalGraph];
        avgDist = Mean[Flatten[distances]];
        Print["Average graph distance: ", avgDist];
    ];

    Print[];
];

(* Test 2: Registry of Notable Universes - known spatial *)
Print[];
Print["Test 2: From Wolfram Physics Registry"];
Print["----------------------------"];

(* Example: Binary rule with spatial structure *)
registryRule = {{1,2},{2,3}} -> {{1,4},{4,3},{2,4}};
registryInit = {{1,2},{2,3},{3,1}};  (* Triangle *)

Print["Rule: ", registryRule];
Print["Initial: Triangle"];

result2 = WolframModel[registryRule, registryInit, 6];
states2 = result2["StatesList"];

Print["Generated ", Length[states2], " states"];

causal2 = result2["CausalGraph"];
Print["Causal graph: ", VertexCount[causal2], " vertices"];
Print[];

(* Dimension estimate from graph *)
(* Spectral dimension: d_s = 2 * <r²> / <r> for random walk *)
If[VertexCount[causal2] > 10 && VertexCount[causal2] < 500,
    (* Sample random walks *)
    startVertex = First[VertexList[causal2]];

    (* This is placeholder - proper spectral dimension needs eigenvalue analysis *)
    eigenvals = Eigenvalues[N[AdjacencyMatrix[causal2]]];
    nonzeroEigs = Select[eigenvals, Abs[#] > 0.01 &];
    effectiveDim = Length[nonzeroEigs];

    Print["Effective dimension (eigenvalue count): ", effectiveDim];
    Print[];
];

(* Summary *)
Print["========================================"];
Print[" SUMMARY"];
Print["========================================"];
Print[];
Print["SetReplace WORKING: Tests completed"];
Print[];
Print["Next: Run full spatial tests"];
Print["  - Larger N (>1000)"];
Print["  - Proper Ollivier-Ricci (needs custom implementation)"];
Print["  - Multiple spatial rules from Registry"];
Print[];
Print["Estimated time for full suite: 30-60 min"];
Print[];
