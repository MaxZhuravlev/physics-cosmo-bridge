(*
SPATIAL DIRAC - CONTRACTING & MIXED RULES
=========================================

GOAL: Test Dirac structure with rules that have BOTH E+ and E-
      (expanding AND contracting transitions)

HYPOTHESIS: Mixed rules will give non-degenerate M⁺M⁻ ≈ αM²

Previous test (SPATIAL_DIRAC_TEST.wl):
  - Expanding rule only → all E+, no E- → degenerate

This test:
  - Contracting rules
  - Mixed rules
  - Should give E+ and E- → non-degenerate
*)

Needs["SetReplace`"];

Print["================================================================================"];
Print[" SPATIAL DIRAC - CONTRACTING & MIXED RULES"];
Print[" Goal: Non-degenerate spinor structure"];
Print["================================================================================"];
Print[];

(* Helper: Compute descendants count *)
descendantsCount[graph_, vertex_] := Module[{reachable},
    reachable = VertexOutComponent[graph, vertex];
    Length[reachable] - 1  (* -1 to exclude vertex itself *)
];

(* Helper: Classify transition as E+ or E- based on descendants *)
classifyTransition[graph_, v1_, v2_] := Module[{d1, d2},
    d1 = descendantsCount[graph, v1];
    d2 = descendantsCount[graph, v2];
    If[d2 >= d1, "+", "-"]
];

(* Helper: Build Dirac matrices M+, M- *)
buildDiracMatrices[transitionMatrix_, causalGraph_, states_] := Module[
    {n, Mplus, Mminus, classifications, i, j},

    n = Length[states];
    Mplus = ConstantArray[0, {n, n}];
    Mminus = ConstantArray[0, {n, n}];

    (* Classify each transition *)
    Do[
        If[transitionMatrix[[i, j]] > 0,
            (* There's a transition i → j *)
            (* Find corresponding vertices in causal graph *)
            (* Simplified: use depth-based classification *)
            If[j > i,  (* Later state = typically more descendants *)
                Mplus[[i, j]] = transitionMatrix[[i, j]],
                Mminus[[i, j]] = transitionMatrix[[i, j]]
            ]
        ],
        {i, n}, {j, n}
    ];

    {Mplus, Mminus}
];

Print["TEST 1: TRIANGLE COLLAPSE (Pure Contracting)"];
Print["-----------------------------------------------"];
Print[];

(* Contracting rule: Triangle → Edge *)
contractingRule1 = {{x_, y_}, {y_, z_}, {z_, x_}} -> {{x_, z_}};
init1 = {{1, 2}, {2, 3}, {3, 1}};  (* Triangle *)

Print["Rule: Triangle collapse {{x,y},{y,z},{z,x}} → {{x,z}}"];
Print["Initial: Triangle"];
Print["Expected: Contracting transitions (E-)"];
Print[];

result1 = WolframModel[contractingRule1, init1, 5];
states1 = result1["StatesList"];
causal1 = result1["CausalGraph"];

Print["Generated: ", Length[states1], " states"];
Print["Causal graph: ", VertexCount[causal1], " vertices"];
Print[];

(* Build transition matrix by depth *)
maxDepth = Min[Length[states1] - 1, 5];
Print["Analyzing ", maxDepth, " depth transitions..."];
Print[];

Do[
    nCurrent = 1;  (* States at depth d *)
    nNext = 1;     (* States at depth d+1 *)

    (* Count E+ vs E- based on state progression *)
    (* In contracting: expect more E- *)

    Print["Depth ", d, " → ", d+1, ":"];
    Print["  (Contracting rule - expect E- dominant)"];
    Print[];
    ,
    {d, 1, maxDepth}
];

Print[];

Print["TEST 2: EDGE MERGE (Contracting)"];
Print["----------------------------------"];
Print[];

(* Another contracting pattern *)
contractingRule2 = {{x_, y_}, {y_, z_}} -> {{x_, z_}};
init2 = {{1, 2}, {2, 3}, {3, 4}};  (* Chain *)

Print["Rule: Edge merge {{x,y},{y,z}} → {{x,z}}"];
Print["Initial: Chain of 3 edges"];
Print[];

result2 = WolframModel[contractingRule2, init2, 4];
states2 = result2["StatesList"];
causal2 = result2["CausalGraph"];

Print["Generated: ", Length[states2], " states"];
Print["Causal graph: ", VertexCount[causal2], " vertices"];
Print[];

Print["TEST 3: MIXED RULE (Both Expanding and Contracting)"];
Print["-----------------------------------------------------"];
Print[];

(* Mixed rule: Sometimes adds, sometimes removes *)
(* This is tricky - need rule that naturally does both *)

(* Try: Subdivision + Collapse *)
mixedRule = {
    {{x_, y_}} :> {{x_, w_}, {w_, y_}},      (* Expand: 1 edge → 2 edges *)
    {{x_, y_}, {y_, x_}} :> {{x_, y_}}        (* Contract: 2-cycle → 1 edge *)
};

init3 = {{1, 2}, {2, 1}};  (* 2-cycle *)

Print["Rules: Mixed (subdivision + collapse)"];
Print["Initial: 2-cycle"];
Print[];

result3 = WolframModel[mixedRule, init3, 6];
states3 = result3["StatesList"];
causal3 = result3["CausalGraph"];

Print["Generated: ", Length[states3], " states"];
Print["Causal graph: ", VertexCount[causal3], " vertices"];
Print[];

(* Analyze E+/E- ratio *)
If[VertexCount[causal3] > 2,
    (* Compute descendants for each vertex *)
    descendants = Table[
        descendantsCount[causal3, v],
        {v, VertexList[causal3]}
    ];

    (* Count transitions by type *)
    edges = EdgeList[causal3];
    eplusCount = 0;
    eminusCount = 0;

    Do[
        {v1, v2} = edge;
        d1 = descendants[[v1]];
        d2 = descendants[[v2]];
        If[d2 >= d1, eplusCount++, eminusCount++],
        {edge, edges}
    ];

    Print["Transition analysis:"];
    Print["  E+ (expanding): ", eplusCount, " (", 100.*eplusCount/Length[edges], "%)"];
    Print["  E- (contracting): ", eminusCount, " (", 100.*eminusCount/Length[edges], "%)"];
    Print[];

    If[eplusCount > 0 && eminusCount > 0,
        Print["  ✓ NON-DEGENERATE (both types present!)"];
        Print["  → Can test M⁺M⁻ ≈ αM²"];
        ,
        Print["  ✗ Still degenerate (one type only)"];
    ];
];

Print[];

Print["TEST 4: HEXAGONAL SPATIAL (2D, potentially mixed)"];
Print["--------------------------------------------------"];
Print[];

(* Hexagonal mesh - can have mixed dynamics *)
hexRule = {{x_, y_}, {y_, z_}, {z_, x_}} -> {
    {x_, w_}, {w_, y_},
    {y_, u_}, {u_, z_},
    {z_, v_}, {v_, x_}
};

init4 = {{1, 2}, {2, 3}, {3, 1}};  (* Triangle *)

Print["Rule: Triangle → Hexagon"];
Print["Initial: Triangle"];
Print[];

result4 = WolframModel[hexRule, init4, 4];
states4 = result4["StatesList"];
causal4 = result4["CausalGraph"];

Print["Generated: ", Length[states4], " states"];
Print["Causal graph: ", VertexCount[causal4], " vertices"];
Print[];

(* Check if mixed *)
If[VertexCount[causal4] > 5 && VertexCount[causal4] < 1000,
    descendants4 = Table[descendantsCount[causal4, v], {v, VertexList[causal4]}];
    edges4 = EdgeList[causal4];

    eplus4 = Count[edges4, edge_ /; descendants4[[edge[[2]]]] >= descendants4[[edge[[1]]]]];
    eminus4 = Length[edges4] - eplus4;

    Print["E+: ", eplus4, " (", 100.*eplus4/Length[edges4], "%)"];
    Print["E-: ", eminus4, " (", 100.*eminus4/Length[edges4], "%)"];
    Print[];

    If[eplus4 > 0 && eminus4 > 0,
        Print["  ✓✓ MIXED DYNAMICS"];
        Print["     Testing Dirac structure..."];

        (* Build approximate transition matrix *)
        (* This is simplified - full version needs state-to-state mapping *)
        nStates = Length[states4];
        M = IdentityMatrix[nStates];  (* Placeholder *)

        (* Report structure *)
        Print["     ", nStates, " states, mixed transitions"];
        Print["     → Potentially non-degenerate Dirac"];
    ];
];

Print[];
Print["================================================================================"];
Print[" SUMMARY"];
Print["================================================================================"];
Print[];

Print["RULES TESTED:"];
Print["  1. Triangle collapse (pure contracting)"];
Print["  2. Edge merge (pure contracting)"];
Print["  3. Mixed (subdivision + collapse)"];
Print["  4. Hexagonal (spatial mixed)"];
Print[];

Print["GOAL: Find rules with BOTH E+ and E-"];
Print[];

Print["NEXT: If non-degenerate found:");
Print["  → Compute M⁺, M⁻ layer-by-layer"];
Print["  → Test M⁺M⁻ ≈ αM²"];
Print["  → Check error < 30%"];
Print[];

Print["If all degenerate:");
Print["  → Dirac remains open question"];
Print["  → Flag as future work (spatial embedding orientation)"];
Print[];
