using Pkg

const GSN_PROJECT = "/home/ljq/code/GSN/GeneralizedSasakiNakamura.jl"
Pkg.activate(GSN_PROJECT; io=devnull)

using GeneralizedSasakiNakamura
using Printf

function fmt_complex(z)
    return @sprintf("%.16e%+.16eim", real(z), imag(z))
end

function main()
    cases = [
        (0, 0, 0.5, 0.1),
        (1, 1, 0.5, 0.1),
        (2, 1, 0.5, 0.3),
        (2, 2, 0.5, 0.1),
        (2, 2, 0.5, 0.01),
        (2, 2, 0.5, 1.0),
    ]

    mkpath("results")
    out = joinpath("results", "kerr_scalar_gsn_benchmark.csv")
    open(out, "w") do io
        println(io, "s,l,m,a,omega,lambda,transmission_amplitude,incidence_amplitude,reflection_amplitude,normalization,status")
        for (l, m, a, omega) in cases
            s = 0
            try
                Rin = Teukolsky_radial(
                    s, l, m, a, omega, IN,
                    GeneralizedSasakiNakamura._DEFAULT_rsin,
                    GeneralizedSasakiNakamura._DEFAULT_rsout;
                    horizon_expansion_order=30,
                    infinity_expansion_order=40,
                    method="Riccati",
                )
                println(io, join([
                    s,
                    l,
                    m,
                    a,
                    omega,
                    Rin.mode.lambda,
                    fmt_complex(Rin.transmission_amplitude),
                    fmt_complex(Rin.incidence_amplitude),
                    fmt_complex(Rin.reflection_amplitude),
                    Rin.normalization_convention,
                    "ok",
                ], ","))

                println("s=0 l=", l, " m=", m, " a=", a, " omega=", omega)
                println("  lambda=", Rin.mode.lambda)
                println("  transmission=", Rin.transmission_amplitude)
                println("  incidence=", Rin.incidence_amplitude)
                println("  reflection=", Rin.reflection_amplitude)
                println("  normalization=", Rin.normalization_convention)
            catch err
                println(io, join([s, l, m, a, omega, "NaN", "NaN", "NaN", "NaN", "NaN", "failed: $(err)"], ","))
                rethrow()
            end
        end
    end
    println("saved=", out)
end

main()
