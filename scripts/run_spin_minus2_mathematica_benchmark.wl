(* Low-frequency s=-2 benchmark through Windows Mathematica/BHPT. *)

Get["F:\\EMRI\\Radial_flow\\Radial_Function.wl"];

fmt[x_] := ToString[FortranForm[N[x, 30]], CharacterEncoding -> "ASCII"];
fmtComplex[z_] := StringJoin[fmt[Re[z]], If[Im[z] >= 0, "+", ""], fmt[Im[z]], " I"];

rowFor[s_, l_, m_, a_, omega_] := Module[
    {amps, inc, ref, trans, ratio},
    amps = ComputeAmplitudesMST[s, l, m, a, omega];
    inc = amps["Incidence"];
    ref = amps["Reflection"];
    trans = amps["Transmission"];
    ratio = amps["ReflectionOverIncidence"];
    {
        ToString[s],
        fmt[a],
        ToString[l],
        ToString[m],
        fmt[omega],
        fmtComplex[trans],
        fmtComplex[inc],
        fmtComplex[ref],
        fmtComplex[ratio],
        fmt[amps["AbsReflectionOverIncidence"]],
        "MST",
        "ok"
    }
];

rows = Prepend[
    {rowFor[-2, 2, 2, 0.5, 10^-4]},
    {
        "s",
        "a",
        "l",
        "m",
        "omega",
        "transmission_amplitude",
        "incidence_amplitude",
        "reflection_amplitude",
        "reflection_over_incidence",
        "abs_reflection_over_incidence",
        "method",
        "status"
    }
];

Export[
    FileNameJoin[{Directory[], "results", "spin_minus2_mathematica_lowfreq.csv"}],
    rows,
    "CSV"
];

Print["saved=", FileNameJoin[{Directory[], "results", "spin_minus2_mathematica_lowfreq.csv"}]];
Print[TableForm[rows]];
