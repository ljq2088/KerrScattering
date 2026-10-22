module KerrScalarPrecision
using LinearAlgebra, SparseArrays
export solve_mode, amplitudes, branch_jet, response, quality, gauss, coeffs, factor_jet

# Scalar specialization of the multi-domain BigFloat/refined-LU route audited
# at ljq2088/teukolsky-radial-spectral, revision 1621eb5e379b (2026-10-21).
# M=1, exp(-i omega t+i m phi); unit horizon amplitude; normalized harmonics.
rp(a)=1+sqrt(1-a*a)
rm(a)=1-sqrt(1-a*a)
rstar(a,r)=r+2rp(a)/(rp(a)-rm(a))*log((r-rp(a))/2)-2rm(a)/(rp(a)-rm(a))*log((r-rm(a))/2)
psi(a,w,m,r)=w*rstar(a,r)-m*a/(rp(a)-rm(a))*log((r-rp(a))/(r-rm(a)))
hphase(a,m)=m*a/2+m*a/rp(a)*log((rp(a)-rm(a))/2)

function lobatto(n)
    x=cospi.(BigFloat.(0:n)/n)
    weights=BigFloat.((-1).^collect(0:n)); weights[[1,end]].*=2
    D=zeros(BigFloat,n+1,n+1)
    for i in 1:n+1,j in 1:n+1
        i!=j && (D[i,j]=weights[i]/weights[j]/(x[i]-x[j]))
    end
    for i in 1:n+1; D[i,i]=-sum(D[i,:]); end
    T=[cospi(BigFloat(k*j)/n) for k in 0:n,j in 0:n]
    T[:,[1,end]]./=2; T .*= BigFloat(2)/n; T[[1,end],:]./=2
    x,D,D*D,T
end

function derivative(c)
    n=length(c)-1; d=zeros(eltype(c),n+2)
    for k in n-1:-1:0; d[k+1]=d[k+3]+2*(k+1)*c[k+2]; end
    d[1]/=2; d[1:n]
end
function clenshaw(c,x)
    b1=zero(eltype(c)); b2=b1
    for j in length(c):-1:2; b0=c[j]+2x*b1-b2; b2,b1=b1,b0; end
    c[1]+x*b1-b2
end

function gauss(n)
    x=zeros(BigFloat,n); wt=copy(x)
    for i in 1:cld(n,2)
        t=cospi(BigFloat(4i-1)/(4n+2)); dp=zero(t)
        for _ in 1:30
            p0=one(t);p1=t
            for k in 2:n; p0,p1=p1,((2k-1)*t*p1-(k-1)*p0)/k; end
            dp=n*(t*p1-p0)/(t*t-1); step=p1/dp;t-=step
            abs(step)<8eps(BigFloat) && break
        end
        # Re-evaluate the derivative at the converged abscissa.
        p0=one(t);p1=t
        for k in 2:n; p0,p1=p1,((2k-1)*t*p1-(k-1)*p0)/k; end
        dp=n*(t*p1-p0)/(t*t-1)
        x[i]=-t;x[n+1-i]=t;wt[i]=wt[n+1-i]=2/((1-t*t)*dp*dp)
    end
    x,wt
end

function angular(l,m,c,n)
    ls=collect(abs(m):abs(m)+n)
    Q=zeros(BigFloat,n+1,n+1)
    for j in 2:n+1
        k=BigFloat(ls[j]);Q[j-1,j]=Q[j,j-1]=sqrt((k*k-m*m)/(4k*k-1))
    end
    A=(diagm(BigFloat.(ls.*(ls.+1)))-c*c*(Q*Q))[1:n,1:n]
    index=l-abs(m)+1
    if c==0
        v=zeros(BigFloat,n);v[index]=1
        return (lambda=BigFloat(l*(l+1)),v=v,ls=ls[1:n],residual=BigFloat(0))
    end
    shift=BigFloat(eigvals(Symmetric(Float64.(A)))[index])+sqrt(eps(BigFloat))
    factor=lu(A-shift*I);v=zeros(BigFloat,n);v[index]=1
    residual=BigFloat(Inf);value=shift
    for _ in 1:16
        v=factor\v;v/=norm(v);av=A*v;value=dot(v,av)
        residual=norm(av-value*v,Inf)
        residual<1000n*eps(BigFloat)*max(1,opnorm(A,Inf)) && break
    end
    residual<sqrt(eps(BigFloat)) || error("angular residual failed")
    (lambda=value+c*c-2m*c,v=v,ls=ls[1:n],residual=residual)
end

function couplings(ang,m,n,q)
    x,wt=gauss(q);C0=BigFloat(0);C2=BigFloat(0);normal=BigFloat(0)
    for (t,weight) in zip(x,wt)
        mm=abs(m);pmm=BigFloat(1)
        for k in 1:mm; pmm*=-(2k-1)*sqrt(1-t*t);end
        values=BigFloat[pmm]
        length(ang.ls)>1 && push!(values,(2mm+1)*t*pmm)
        for l in mm+2:ang.ls[end]
            push!(values,((2l-1)*t*values[end]-(l+mm-1)*values[end-1])/(l-mm))
        end
        S=BigFloat(0)
        for j in eachindex(ang.v)
            l=ang.ls[j]
            N=sqrt(BigFloat(2l+1)/(4big(pi))*BigFloat(factorial(big(l-mm)))/BigFloat(factorial(big(l+mm))))
            S+=ang.v[j]*N*values[j]
        end
        normal+=2big(pi)*weight*S*S
        C0+=2big(pi)*weight*S^(2n+2);C2+=2big(pi)*weight*t*t*S^(2n+2)
    end
    C0,C2,abs(normal-1)
end

function factor_jet(a,w,m,r,kind)
    d=(r-rp(a))*(r-rm(a));dp=2r-2;K=(r*r+a*a)*w-m*a
    power,sgn=kind==:in ? (0,-1) : (-1,kind==:up ? 1 : -1)
    phase=psi(a,w,m,r)-(kind==:in ? hphase(a,m) : 0)
    f=r^power*exp(sgn*im*phase)
    q=power/r+sgn*im*K/d
    qp=-power/r^2+sgn*im*(2w*r*d-K*dp)/d^2
    f,q,qp
end

function coeffs(a,w,m,lam,z,kind)
    rr=rp(a)
    if z==0
        kind==:in && error("in branch excludes infinity")
        sgn=kind==:up ? 1 : -1
        return (BigFloat(0),-2sgn*im*w*rr,-lam)
    end
    r=rr/z;d=(r-rr)*(r-rm(a));K=(r*r+a*a)*w-m*a
    zr=-z*z/rr;zrr=2z^3/rr^2
    if kind==:in
        b=2r-2-2im*K;c=-2im*w*r-lam
    else
        sgn=kind==:up ? 1 : -1
        b=2r-2-2d/r+2sgn*im*K
        c=-2/r+2a*a/r^2-lam+2sgn*im*(m*a-a*a*w)/r
    end
    d*zr^2,d*zrr+b*zr,c
end

function mesh(a,w,kind,phase_step)
    rr=rp(a)
    if kind==:in
        base=sort(vcat(1 ./ parse.(BigFloat,["6","5","4","3","2","1.6","1.3","1.1","1.02","1.005"]),BigFloat(1)))
    else
        base=BigFloat[0,min(BigFloat("0.025"),w*rr/20)]
        while base[end]<BigFloat("0.25");push!(base,min(BigFloat("0.25"),base[end]*BigFloat("1.6")));end
    end
    edges=BigFloat[base[1]]
    for (lo,hi) in zip(base[1:end-1],base[2:end])
        if lo==0 || hi==1;push!(edges,hi);continue;end
        s0=rstar(a,rr/lo);s1=rstar(a,rr/hi)
        n=max(1,ceil(Int,2w*abs(s1-s0)/phase_step))
        for j in 1:n-1
            target=s0+(s1-s0)*j/n;left=lo;right=hi;z=(left+right)/2
            for _ in 1:precision(BigFloat)+20
                r=rr/z;f=rstar(a,r)-target
                abs(f)<32eps(BigFloat)*max(1,abs(target)) && break
                if f>0;left=z;else;right=z;end
                df=-(r*r+a*a)/((r-rr)*(r-rm(a)))*rr/z^2
                trial=z-f/df;z=left<trial<right ? trial : (left+right)/2
            end
            push!(edges,z)
        end
        push!(edges,hi)
    end
    edges
end

function refined_solve(A,rhs)
    length(rhs)<=24000 || error("matrix size guard")
    Sys.maxrss()<1_500_000_000 || error("memory guard")
    rn=zeros(BigFloat,length(rhs));cn=copy(rn)
    for j in 1:length(rhs),k in nzrange(A,j);rn[A.rowval[k]]+=abs2(A.nzval[k]);end
    rn.=sqrt.(rn)
    for j in 1:length(rhs),k in nzrange(A,j)
        A.nzval[k]/=rn[A.rowval[k]];cn[j]+=abs2(A.nzval[k])
    end
    cn.=sqrt.(cn)
    for j in 1:length(rhs),k in nzrange(A,j);A.nzval[k]/=cn[j];end
    b=rhs./rn;factor=lu(ComplexF64.(A));u=Complex{BigFloat}.(factor\ComplexF64.(b))
    matnorm=opnorm(A,Inf);err=BigFloat(Inf)
    for iteration in 0:40
        defect=b-A*u;err=norm(defect,Inf)/(matnorm*norm(u,Inf)+norm(b,Inf))
        err<=10000eps(BigFloat) && return u./cn,err,iteration
        u .+= Complex{BigFloat}.(factor\ComplexF64.(defect))
    end
    error("iterative refinement did not converge: $err")
end

function solve_branch(a,w,m,lam,kind,n,phase_step)
    edges=mesh(a,w,kind,phase_step);cells=length(edges)-1;sz=n+1
    x,D,D2,T=lobatto(n);rows=Int[];cols=Int[];vals=Complex{BigFloat}[]
    add(i,j,v)=(push!(rows,i);push!(cols,j);push!(vals,v))
    for cell in 1:cells
        half=(edges[cell+1]-edges[cell])/2;mid=(edges[cell+1]+edges[cell])/2
        for i in 2:n
            a2,a1,a0=coeffs(a,w,m,lam,mid+half*x[i],kind)
            row=(cell-1)*(n-1)+i-1
            for j in 1:sz
                add(row,(cell-1)*sz+j,a2*D2[i,j]/half^2+a1*D[i,j]/half+(i==j ? a0 : 0))
            end
        end
    end
    offset=cells*(n-1);rhs=zeros(Complex{BigFloat},cells*sz)
    sc,si=kind==:in ? (cells,1) : (1,sz)
    add(offset+1,(sc-1)*sz+si,1)
    for j in 1:sz;add(offset+2,(sc-1)*sz+j,D[si,j]*2/(edges[sc+1]-edges[sc]));end
    endpoint=kind==:in ? BigFloat(1) : BigFloat(0)
    _,b,c=coeffs(a,w,m,lam,endpoint,kind)
    rhs[offset+1]=1;rhs[offset+2]=-c/b
    for cell in 1:cells-1
        add(offset+2cell+1,(cell-1)*sz+1,1);add(offset+2cell+1,(cell+1)*sz,-1)
        for j in 1:sz
            add(offset+2cell+2,(cell-1)*sz+j,D[1,j]*2/(edges[cell+1]-edges[cell]))
            add(offset+2cell+2,cell*sz+j,-D[end,j]*2/(edges[cell+2]-edges[cell+1]))
        end
    end
    A=sparse(rows,cols,vals,cells*sz,cells*sz)
    u,backward,iterations=refined_solve(A,rhs);co=T*reshape(u,sz,cells)
    (kind=kind,edges=edges,co=co,d1=mapslices(derivative,co,dims=1),
     d2=mapslices(c->derivative(derivative(c)),co,dims=1),backward=backward,iterations=iterations)
end

function envelope(b,z,der=0)
    cell=clamp(searchsortedlast(b.edges,z),1,length(b.edges)-1)
    lo,hi=b.edges[cell:cell+1];x=(2z-lo-hi)/(hi-lo)
    co=der==0 ? b.co : der==1 ? b.d1 : b.d2
    clenshaw(view(co,:,cell),x)*(2/(hi-lo))^der
end

function branch_jet(sol,b,r)
    z=rp(sol.a)/r;u=envelope(b,z);uz=envelope(b,z,1);uzz=envelope(b,z,2)
    f,q,qp=factor_jet(sol.a,sol.w,sol.m,r,b.kind)
    zr=-z*z/rp(sol.a);zrr=2z^3/rp(sol.a)^2
    (f*u,f*(q*u+zr*uz),f*((q*q+qp)*u+(2q*zr+zrr)*uz+zr*zr*uzz))
end

function amplitudes(sol,r)
    i=branch_jet(sol,sol.inner,r);d=branch_jet(sol,sol.down,r);u=branch_jet(sol,sol.up,r)
    det=d[1]*u[2]-d[2]*u[1]
    bi=(i[1]*u[2]-i[2]*u[1])/det;br=(d[1]*i[2]-d[2]*i[1])/det
    delta=(r-rp(sol.a))*(r-rm(sol.a))
    cancellation=(abs(d[1]*i[2])+abs(d[2]*i[1]))/max(abs(d[1]*i[2]-d[2]*i[1]),eps(BigFloat))
    bi,br,abs(delta*det/(2im*sol.w)-1),cancellation
end

function solve_mode(a,w,l,m;degree=40,inner_degree=degree,phase_step=12,angular_size=48)
    0<=a<1 && w>0 && l>=abs(m) || error("unsupported parameters")
    ang=angular(l,m,a*w,angular_size)
    inner=solve_branch(a,w,m,ang.lambda,:in,inner_degree,phase_step)
    down=solve_branch(a,w,m,ang.lambda,:down,degree,phase_step)
    up=solve_branch(a,w,m,ang.lambda,:up,degree,phase_step)
    (a=a,w=w,l=l,m=m,lam=ang.lambda,angular=ang,inner=inner,down=down,up=up)
end

function quality(sol)
    residual=BigFloat(0);tail=BigFloat(0)
    for b in (sol.inner,sol.down,sol.up)
        tail=max(tail,maximum(abs.(b.co[end-5:end,:]))/maximum(abs.(b.co)))
        for cell in 1:length(b.edges)-1, j in 1:3
            z=b.edges[cell]+(b.edges[cell+1]-b.edges[cell])*BigFloat(j)/4
            r=rp(sol.a)/z;R,Rr,Rrr=branch_jet(sol,b,r)
            delta=(r-rp(sol.a))*(r-rm(sol.a));K=(r*r+sol.a^2)*sol.w-sol.m*sol.a
            terms=(delta*Rrr,(2r-2)*Rr,(K*K/delta-sol.lam)*R)
            residual=max(residual,abs(sum(terms))/sum(abs.(terms)))
        end
    end
    residual,tail
end

function levin(sol,edges,j,fun,degree)
    if j==0
        gx,gw=gauss(degree);answer=zero(Complex{BigFloat})
        for (lo,hi) in zip(edges[1:end-1],edges[2:end]), k in eachindex(gx)
            z=(lo+hi)/2+(hi-lo)*gx[k]/2;answer+=(hi-lo)*gw[k]/2*fun(z)
        end
        return answer
    end
    x,D,_,_=lobatto(degree);sz=degree+1;cells=length(edges)-1
    rows=Int[];cols=Int[];vals=Complex{BigFloat}[];rhs=zeros(Complex{BigFloat},cells*sz)
    add(i,k,v)=(push!(rows,i);push!(cols,k);push!(vals,v))
    for cell in 1:cells
        half=(edges[cell+1]-edges[cell])/2;mid=(edges[cell+1]+edges[cell])/2
        for i in 1:degree
            z=mid+half*x[i];rr=rp(sol.a)
            ds=rr^2-2rr*z+sol.a^2*z*z;hs=rr^2+sol.a^2*z*z
            phi=-2j*im*rr*(sol.w*hs-sol.m*sol.a*z*z)/ds
            row=(cell-1)*degree+i;rhs[row]=z*z*fun(z)
            for k in 1:sz;add(row,(cell-1)*sz+k,z*z*D[i,k]/half+(i==k ? phi : 0));end
        end
    end
    offset=cells*degree;add(offset+1,sz,1)
    for cell in 1:cells-1
        add(offset+cell+1,(cell-1)*sz+1,1);add(offset+cell+1,(cell+1)*sz,-1)
    end
    v,_,_=refined_solve(sparse(rows,cols,vals,cells*sz,cells*sz),rhs)
    v[(cells-1)*sz+1]*exp(2j*im*psi(sol.a,sol.w,sol.m,rp(sol.a)/edges[end]))
end

function response(sol,n;quad=48,levin_degree=48,log_min=-100,log_step=1,match_ratio=5)
    rr=rp(sol.a);rmatch=BigFloat(match_ratio)*rr;bi,br,_,_=amplitudes(sol,rmatch)
    q=br/bi;normflux=(sol.w-sol.m*sol.a/(2rr))*2rr/sol.w
    C0,C2,angular_norm=couplings(sol.angular,sol.m,n,max(64,2length(sol.angular.v)))
    gx,gw=gauss(quad);gap=rr-rm(sol.a);tmax=log((rmatch-rr)/gap)
    nc=ceil(Int,(tmax-log_min)/log_step);jd=BigFloat(0);jo=zero(Complex{BigFloat})
    for cell in 1:nc
        lo=BigFloat(log_min)+(tmax-log_min)*(cell-1)/nc;hi=BigFloat(log_min)+(tmax-log_min)*cell/nc
        for k in eachindex(gx)
            t=(lo+hi)/2+(hi-lo)*gx[k]/2;distance=gap*exp(t);r=rr+distance
            rin=branch_jet(sol,sol.inner,r)[1]
            up=(bi*conj(rin)-conj(br)*rin)/normflux
            weight=(hi-lo)*gw[k]/2*distance*(r*r*C0+sol.a^2*C2)*abs2(rin/bi)^n
            jd+=weight*abs2(up);jo+=weight*up*up
        end
    end
    cutoff=gap*exp(BigFloat(log_min));r=rr+cutoff
    ph=exp(2im*(sol.w-sol.m*sol.a/(2rr))*rstar(sol.a,r))
    y=4rr*(sol.w-sol.m*sol.a/(2rr))/gap
    ip=cutoff*ph/(1+im*y);imn=conj(ip)
    pref=(rr*rr*C0+sol.a^2*C2)/abs2(bi)^n/normflux^2
    jd+=pref*((abs2(bi)+abs2(br))*cutoff-2real(bi*br*ip))
    jo+=pref*(bi*bi*ip-2bi*conj(br)*cutoff+conj(br)^2*imn)
    polynomial=Dict(0=>one(q))
    for _ in 1:n
        next=Dict{Int,Complex{BigFloat}}()
        for (k,v) in polynomial,(j,c) in ((-1,conj(q)),(0,1+abs2(q)),(1,q))
            next[k+j]=get(next,k+j,zero(q))+v*c
        end
        polynomial=next
    end
    zm=rr/rmatch;edges=vcat(filter(z->z<zm,sol.up.edges),zm)
    for (k,c) in polynomial
        function f(z,shift)
            u=envelope(sol.up,z);d=envelope(sol.down,z)
            radial=C0*rr^(1-2n)*z^(2n-2)+sol.a^2*C2*rr^(-2n-1)*z^(2n)
            radial*u^(n+1+k+shift)*d^(n+1-k-shift)
        end
        jd+=real(c*levin(sol,edges,k,z->f(z,0),levin_degree))
        jo+=c*levin(sol,edges,k+1,z->f(z,1),levin_degree)
    end
    rho=im*(jd+q*jo)/(2sol.w);chi=2real(rho);phase=imag(rho)
    T0=normflux/abs2(bi);R0=abs2(q);T1=T0*chi
    R1=2real(conj(q)*im*(conj(jo)+2q*jd+q*q*jo)/(2sol.w))
    bound=R0<1 ? 2phase*sqrt(R0/(1-R0)) : BigFloat(NaN)
    (bi=bi,br=br,T0=T0,R0=R0,chi=chi,phase=phase,T1=T1,R1=R1,
     jd=jd,jo=jo,bound=bound,bound_ratio=abs(chi)/bound,angular_norm=angular_norm)
end
end
