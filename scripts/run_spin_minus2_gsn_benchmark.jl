using Pkg

const GSN_PROJECT = "/home/ljq/code/GSN/GeneralizedSasakiNakamura.jl"
Pkg.activate(GSN_PROJECT; io=devnull)

using GeneralizedSasakiNakamura
using Printf

function fmt_complex(z)
    return @sprintf("%.16e%+.16eim", real(z), imag(z))
end

function main()
    s = -2
    l = 2
    m = 2
    a = 0.5
    omegas = [10.0, 0.1]

    mkpath("results")
    out = joinpath("results", "spin_minus2_gsn_highfreq.csv")
    open(out, "w") do io
        println(io, "s,a,l,m,omega,lambda,transmission_amplitude,incidence_amplitude,reflection_amplitude,normalization,status")
        for omega in omegas
            try
                Rin = Teukolsky_radial(
                    s, l, m, a, omega, IN,
                    GeneralizedSasakiNakamura._DEFAULT_rsin,
                    GeneralizedSasakiNakamura._DEFAULT_rsout;
                    horizon_expansion_order=20,
                    infinity_expansion_order=30,
                    method="Riccati",
                )
                println(io, join([
                    s,
                    a,
                    l,
                    m,
                    omega,
                    Rin.mode.lambda,
                    fmt_complex(Rin.transmission_amplitude),
                    fmt_complex(Rin.incidence_amplitude),
                    fmt_complex(Rin.reflection_amplitude),
                    Rin.normalization_convention,
                    "ok",
                ], ","))

                println("omega=", omega)
                println("  lambda=", Rin.mode.lambda)
                println("  transmission=", Rin.transmission_amplitude)
                println("  incidence=", Rin.incidence_amplitude)
                println("  reflection=", Rin.reflection_amplitude)
                println("  normalization=", Rin.normalization_convention)
            catch err
                println(io, join([s, a, l, m, omega, "NaN", "NaN", "NaN", "NaN", "NaN", "failed: $(err)"], ","))
                rethrow()
            end
        end
    end
    println("saved=", out)
end

main()
