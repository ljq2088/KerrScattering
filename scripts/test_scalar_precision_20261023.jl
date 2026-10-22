using Test, LinearAlgebra
include("../src/kerr_scalar_precision.jl")
using .KerrScalarPrecision
BLAS.set_num_threads(1)
setprecision(256)
@testset "scalar exact transformation and angular normalization" begin
    for a in parse.(BigFloat,["0","0.5","0.9"]), w in parse.(BigFloat,["0.00001","0.1","10"]), m in (0,2), kind in (:in,:up,:down), ratio in ("1.01","4","20")
        r=KerrScalarPrecision.rp(a)*parse(BigFloat,ratio);z=KerrScalarPrecision.rp(a)/r
        lam=BigFloat(7)/3;u=1+z+im*z*z;uz=1+2im*z;uzz=2im
        f,q,qp=factor_jet(a,w,m,r,kind);zr=-z*z/KerrScalarPrecision.rp(a);zrr=2z^3/KerrScalarPrecision.rp(a)^2
        R=f*u;Rr=f*(q*u+zr*uz);Rrr=f*((q*q+qp)*u+(2q*zr+zrr)*uz+zr*zr*uzz)
        delta=(r-KerrScalarPrecision.rp(a))*(r-KerrScalarPrecision.rm(a));K=(r*r+a*a)*w-m*a
        original=delta*Rrr+(2r-2)*Rr+(K*K/delta-lam)*R
        A2,A1,A0=coeffs(a,w,m,lam,z,kind);peeled=f*(A2*uzz+A1*uz+A0*u)
        @test abs(original-peeled)/max(abs(original),abs(peeled),one(w))<big"1e-65"
    end
    for l in 0:2,n in 1:3
        ang=KerrScalarPrecision.angular(l,0,BigFloat(0),32)
        C0,C2,err=KerrScalarPrecision.couplings(ang,0,n,64)
        @test err<big"1e-65"
        @test C0>0 && C2>0
        l==0 && @test abs(C0-(4big(pi))^(-n))<big"1e-65"
    end
    x,w=gauss(48)
    @test abs(sum(w)-2)<big"1e-65"
    @test abs(sum(w.*x.^30)-BigFloat(2)/31)<big"1e-65"
end
@testset "Levin auxiliary integral and horizon phase" begin
    a=big"0.5";w=big"0.1";m=0;rr=KerrScalarPrecision.rp(a)
    sol=(a=a,w=w,m=m)
    edges=parse.(BigFloat,["0","0.01","0.05","0.1"])
    for j in (-2,-1,1,2)
        function f(z)
            ds=rr^2-2rr*z+a*a*z*z;hs=rr^2+a*a*z*z
            2z-2j*im*rr*(w*hs-m*a*z*z)/ds
        end
        exact=edges[end]^2*exp(2j*im*KerrScalarPrecision.psi(a,w,m,rr/edges[end]))
        value=KerrScalarPrecision.levin(sol,edges,j,f,32)
        @test abs(value/exact-1)<big"1e-60"
    end
    value=KerrScalarPrecision.levin(sol,edges,0,z->z^4,24)
    @test abs(value-edges[end]^5/5)<big"1e-65"
    for m in (0,2)
        r=rr+big"1e-30";p=w-m*a/(2rr)
        factor=first(factor_jet(a,w,m,r,:in))
        @test abs(factor/exp(-im*p*KerrScalarPrecision.rstar(a,r))-1)<big"1e-27"
    end
end
