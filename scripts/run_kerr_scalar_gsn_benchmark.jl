using Pkg

const GSN_PROJECT = "/home/ljq/code/GSN/GeneralizedSasakiNakamura.jl"
Pkg.activate(GSN_PROJECT; io=devnull)

using GeneralizedSasakiNakamura
using Printf

function fmt_complex(z)
    return @sprintf("%.16e%+.16eim", real(z), imag(z))
end

function is_usable_amplitude(z)
    return isfinite(real(z)) && isfinite(imag(z)) && abs(z) > 0.0
end

function rsout_for(omega)
    return max(GeneralizedSasakiNakamura._DEFAULT_rsout, 20 / abs(omega))
end

function solve_rin(s, l, m, a, omega, rsin, rsout, horizon_order, infinity_order, method)
    return Teukolsky_radial(
        s, l, m, a, omega, IN,
        rsin,
        rsout;
        horizon_expansion_order=horizon_order,
        infinity_expansion_order=infinity_order,
        method=method,
    )
end

function main()
    cases = [
        # Schwarzschild and non-superradiant reference points.
        (0, 0, 0.0, 0.01),
        (0, 0, 0.0, 0.1),
        (0, 0, 0.0, 0.5),
        (1, 0, 0.0, 0.1),
        (1, 0, 0.0, 0.5),
        (0, 0, 0.5, 0.1),
        (1, 0, 0.5, 0.1),
        (2, 0, 0.5, 0.1),
        (2, 0, 0.5, 0.5),

        # Moderate-spin Kerr modes, including both sides of m Omega_H.
        (1, 1, 0.5, 0.05),
        (1, 1, 0.5, 0.1),
        (1, 1, 0.5, 0.2),
        (2, 1, 0.5, 0.05),
        (2, 1, 0.5, 0.1),
        (2, 1, 0.5, 0.3),
        (2, 1, 0.5, 0.8),
        (2, 2, 0.5, 0.01),
        (2, 2, 0.5, 0.05),
        (2, 2, 0.5, 0.1),
        (2, 2, 0.5, 0.24),
        (2, 2, 0.5, 0.25),
        (2, 2, 0.5, 0.26),
        (2, 2, 0.5, 0.275),
        (2, 2, 0.5, 0.3),
        (2, 2, 0.5, 0.6),
        (2, 2, 0.5, 1.0),

        # High-spin Kerr modes near the stronger superradiant window.
        (2, 2, 0.9, 0.02),
        (2, 2, 0.9, 0.05),
        (2, 2, 0.9, 0.2),
        (2, 2, 0.9, 0.5),
        (2, 2, 0.9, 0.58),
        (2, 2, 0.9, 0.62),
        (2, 2, 0.9, 0.65),
        (2, 2, 0.9, 0.9),
        (3, 2, 0.9, 0.05),
        (3, 2, 0.9, 0.2),
        (3, 2, 0.9, 0.6),
    ]

    mkpath("results")
    out = joinpath("results", "kerr_scalar_gsn_benchmark.csv")
    open(out, "w") do io
        println(io, "s,l,m,a,omega,rsin,rsout,horizon_order,infinity_order,method,lambda,transmission_amplitude,incidence_amplitude,reflection_amplitude,normalization,status")
        for (l, m, a, omega) in cases
            s = 0
            rsin = GeneralizedSasakiNakamura._DEFAULT_rsin
            rsout = rsout_for(omega)
            horizon_order = 30
            infinity_order = 40
            Rin = nothing
            method_used = ""
            status = "failed: no method attempted"
            try
                for method in ["Riccati", "linear"]
                    try
                        trial = solve_rin(
                            s, l, m, a, omega, rsin, rsout,
                            horizon_order, infinity_order, method,
                        )
                        Rin = trial
                        method_used = method
                        if is_usable_amplitude(trial.incidence_amplitude) && is_usable_amplitude(trial.reflection_amplitude)
                            status = "ok"
                            break
                        end
                        status = "failed: nonfinite-or-zero amplitude from GSN"
                    catch err
                        status = "failed: $(err)"
                    end
                end

                if Rin === nothing
                    println(io, join([s, l, m, a, omega, rsin, rsout, horizon_order, infinity_order, method_used, "NaN", "NaN", "NaN", "NaN", "NaN", status], ","))
                    println("failed: s=0 l=", l, " m=", m, " a=", a, " omega=", omega, " status=", status)
                    continue
                end

                println(io, join([
                    s,
                    l,
                    m,
                    a,
                    omega,
                    rsin,
                    rsout,
                    horizon_order,
                    infinity_order,
                    method_used,
                    Rin.mode.lambda,
                    fmt_complex(Rin.transmission_amplitude),
                    fmt_complex(Rin.incidence_amplitude),
                    fmt_complex(Rin.reflection_amplitude),
                    Rin.normalization_convention,
                    status,
                ], ","))

                println("s=0 l=", l, " m=", m, " a=", a, " omega=", omega)
                println("  lambda=", Rin.mode.lambda)
                println("  transmission=", Rin.transmission_amplitude)
                println("  incidence=", Rin.incidence_amplitude)
                println("  reflection=", Rin.reflection_amplitude)
                println("  normalization=", Rin.normalization_convention)
                println("  rsout=", rsout)
                println("  status=", status)
            catch err
                println(io, join([s, l, m, a, omega, rsin, rsout, horizon_order, infinity_order, method_used, "NaN", "NaN", "NaN", "NaN", "NaN", "failed: $(err)"], ","))
                println("failed: s=0 l=", l, " m=", m, " a=", a, " omega=", omega, " err=", err)
            end
        end
    end
    println("saved=", out)
end

main()
