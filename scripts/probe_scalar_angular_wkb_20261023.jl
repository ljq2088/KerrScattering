using LinearAlgebra, TOML
include("../src/kerr_scalar_precision.jl")
using .KerrScalarPrecision
BLAS.set_num_threads(1);setprecision(384)
out=ARGS[1];ispath(out) && error("preserve existing output")
rows=[];a=BigFloat("0.5");rr=KerrScalarPrecision.rp(a)
integrals=BigFloat[atan(a/rr)/a]
for n in 2:4
    push!(integrals,(2n-3)*integrals[end]/(2(n-1)*a*a)-rr/(2(n-1)*a*a*(rr*rr+a*a)^(n-1)))
end
for w in BigFloat.([1,2,3,5,10,20,50,100]),n in 1:3
    size=w<=20 ? 48 : 96
    ang=KerrScalarPrecision.angular(0,0,a*w,size)
    C0,C2,normal=KerrScalarPrecision.couplings(ang,0,n,2size)
    refined=KerrScalarPrecision.angular(0,0,a*w,size+16)
    D0,D2,normal_refined=KerrScalarPrecision.couplings(refined,0,n,2(size+16))
    asym=(a*w)^n/((2big(pi))^n*(n+1))
    leading=a^n/((2big(pi))^n*2(n+1))*integrals[n]*w^(n-1)
    finite=(C0*integrals[n]+a*a*(C2-C0)*integrals[n+1])/(2w)
    push!(rows,Dict("omega"=>string(w),"n"=>n,"C0"=>string(C0),"C2"=>string(C2),"angular_ratio"=>string(C0/asym),"phase_leading"=>string(leading),"phase_finite_angular_wkb"=>string(finite),"angular_norm_error"=>string(max(normal,normal_refined)),"angular_size"=>size,"angular_refinement_change"=>string(max(abs(D0/C0-1),abs(D2/C2-1)))))
end
open(out,"w") do io;TOML.print(io,Dict("rows"=>rows));end
