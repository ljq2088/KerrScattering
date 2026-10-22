using LinearAlgebra, TOML
include("../src/kerr_scalar_precision.jl")
using .KerrScalarPrecision
BLAS.set_num_threads(1)
# Arguments: output a omega ell m n bits outer_order inner_order quad levin.
out=ARGS[1];ispath(out) && error("preserve existing runs")
mkpath(out)
bits=parse(Int,ARGS[7]);setprecision(bits)
a=parse(BigFloat,ARGS[2]);w=parse(BigFloat,ARGS[3]);l=parse(Int,ARGS[4]);m=parse(Int,ARGS[5]);n=parse(Int,ARGS[6])
N=parse(Int,ARGS[8]);Ni=parse(Int,ARGS[9]);q=parse(Int,ARGS[10]);L=parse(Int,ARGS[11])
started=time()
sol=solve_mode(a,w,l,m;degree=N,inner_degree=Ni,phase_step=12,angular_size=48)
println("homogeneous seconds=",time()-started," rss_mb=",Sys.maxrss()/1024^2);flush(stdout)
matching=[]
for ratio in parse.(BigFloat,["4.1","4.5","5","5.5","5.9"])
    bi,br,wr,cancel=amplitudes(sol,ratio*KerrScalarPrecision.rp(a))
    push!(matching,Dict("ratio"=>string(ratio),"bi_re"=>string(real(bi)),"bi_im"=>string(imag(bi)),"br_re"=>string(real(br)),"br_im"=>string(imag(br)),"wronskian"=>string(wr),"cancellation"=>string(cancel)))
end
res,tail=quality(sol)
result=response(sol,n;quad=q,levin_degree=L,log_min=-110,log_step=BigFloat("0.5"))
record=Dict("a"=>string(a),"omega"=>string(w),"ell"=>l,"m"=>m,"n"=>n,"bits"=>bits,"outer_order"=>N,"inner_order"=>Ni,"quad"=>q,"levin"=>L,"radial_residual"=>string(res),"coefficient_tail"=>string(tail),"angular_residual"=>string(sol.angular.residual),"matching"=>matching,"seconds"=>time()-started,"rss_mb"=>Sys.maxrss()/1024^2,"julia"=>string(VERSION))
for key in keys(result)
    value=getproperty(result,key)
    if value isa Complex
        record[string(key)*"_re"]=string(real(value));record[string(key)*"_im"]=string(imag(value))
    else
        record[string(key)]=string(value)
    end
end
open(joinpath(out,"result.toml"),"w") do io;TOML.print(io,record);end
println("RESULT chi=",result.chi," phase=",result.phase," R0=",result.R0," bound_ratio=",result.bound_ratio," residual=",res," seconds=",time()-started);flush(stdout)
