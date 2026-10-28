import math, random, time, os, json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(BASE_DIR, 'tsp_outputs')

# Coordinate-based, real-location benchmark for a hypothetical single-vehicle route.
# Distances are great-circle/haversine, NOT road-network distances.
places = [
    ('Depot: Chandigarh Railway Station',30.70216,76.82145,'Depot'),
    ('Sector 17 Plaza, Chandigarh',30.73000,76.78000,'Chandigarh'),
    ('National Gallery of Portraits, Chandigarh',30.74031,76.78496,'Chandigarh'),
    ('Fitness Trails, Chandigarh',30.74941,76.78557,'Chandigarh'),
    ('Government Museum Complex, Chandigarh',30.74883,76.78770,'Chandigarh'),
    ('Indian Air Force Heritage Centre, Chandigarh',30.73919,76.79096,'Chandigarh'),
    ('Leisure Valley, Chandigarh',30.75289,76.79234,'Chandigarh'),
    ('Chandigarh War Memorial',30.75861,76.79664,'Chandigarh'),
    ('Rajendra Park, Chandigarh',30.76721,76.79674,'Chandigarh'),
    ('Le Corbusier Centre, Chandigarh',30.72982,76.79954,'Chandigarh'),
    ('Capitol Complex, Chandigarh',30.75662,76.80236,'Chandigarh'),
    ('Rock Garden, Chandigarh',30.75255,76.81008,'Chandigarh'),
    ('Sukhna Lake, Chandigarh',30.74438,76.81164,'Chandigarh'),
    ('Punjab Cricket Association Stadium, Mohali',30.68988,76.73774,'Mohali'),
    ('CP67 Mall, Mohali',30.67697,76.72403,'Mohali'),
    ('Fortis Hospital, Mohali',30.69889,76.72687,'Mohali'),
    ('Gurdwara Sri Amb Sahib, Mohali',30.699075,76.732509,'Mohali'),
]
N=len(places)
coords=np.array([[p[1],p[2]] for p in places])
# Haversine matrix in km
R=6371.0088
lat=np.radians(coords[:,0]); lon=np.radians(coords[:,1])
dlat=lat[:,None]-lat[None,:]; dlon=lon[:,None]-lon[None,:]
a=np.sin(dlat/2)**2+np.cos(lat[:,None])*np.cos(lat[None,:])*np.sin(dlon/2)**2
D=2*R*np.arcsin(np.sqrt(np.clip(a,0,1)))

# Chromosome includes all customer-stop indices 1...N-1; depot fixed as 0.
n=N-1

def tour_len(ch):
    path=[0]+list(ch)+[0]
    return float(sum(D[path[i],path[i+1]] for i in range(len(path)-1)))

def pmx(p1,p2,rng):
    size=len(p1); a,b=sorted(rng.sample(range(size),2))
    child=[None]*size
    child[a:b+1]=p1[a:b+1]
    # Mapping is defined by aligned segment entries.
    for i in range(a,b+1):
        gene=p2[i]
        if gene not in child:
            pos=i
            while True:
                mapped=p1[pos]
                pos=p2.index(mapped)
                if child[pos] is None:
                    child[pos]=gene; break
    for i in range(size):
        if child[i] is None: child[i]=p2[i]
    return child

def igx_child(p1,p2,rng):
    # IGX-style distance-guided crossover following the source paper's description:
    # candidates are unvisited circular neighbours of the current city in both parents;
    # choose shortest link, falling back to nearest unvisited city when needed.
    p1=list(p1); p2=list(p2); size=len(p1)
    pos1={v:i for i,v in enumerate(p1)}; pos2={v:i for i,v in enumerate(p2)}
    current=p1[0]
    child=[current]
    used={current}
    while len(child)<size:
        cand=set()
        for p, pos in ((p1,pos1),(p2,pos2)):
            j=pos[current]
            for k in ((j-1)%size,(j+1)%size):
                if p[k] not in used: cand.add(p[k])
        if cand:
            # tie break randomly, stable behavior under a fixed seed
            min_d=min(D[current,c] for c in cand)
            best=[c for c in cand if abs(D[current,c]-min_d)<1e-10]
            nxt=rng.choice(best)
        else:
            remaining=[c for c in range(1,N) if c not in used]
            min_d=min(D[current,c] for c in remaining)
            best=[c for c in remaining if abs(D[current,c]-min_d)<1e-10]
            nxt=rng.choice(best)
        child.append(nxt); used.add(nxt); current=nxt
    return child

def crossover(p1,p2,method,rng):
    if method=='PMX': return pmx(p1,p2,rng), pmx(p2,p1,rng)
    return igx_child(p1,p2,rng), igx_child(p2,p1,rng)

def mutate(ch,rng,rate=0.20):
    ch=ch.copy()
    if rng.random()<rate:
        i,j=sorted(rng.sample(range(len(ch)),2))
        if rng.random()<0.5:
            ch[i],ch[j]=ch[j],ch[i]
        else:
            ch[i:j+1]=reversed(ch[i:j+1])
    return ch

def run_ga(method,seed,pop_size=100,generations=500,cross_rate=0.9,mutation_rate=0.20):
    rng=random.Random(seed)
    pop=[]
    base=list(range(1,N))
    for _ in range(pop_size):
        q=base.copy(); rng.shuffle(q); pop.append(q)
    best_ch=None; best_fit=float('inf'); history=[]
    t0=time.perf_counter()
    for gen in range(generations):
        fits=[tour_len(x) for x in pop]
        idx=int(np.argmin(fits))
        if fits[idx]<best_fit:
            best_fit=fits[idx]; best_ch=pop[idx].copy()
        history.append(best_fit)
        # tournament selection, same for both methods
        elite_idx=np.argsort(fits)[:2]
        newpop=[pop[int(i)].copy() for i in elite_idx]
        while len(newpop)<pop_size:
            def select():
                cand=[rng.randrange(pop_size) for _ in range(3)]
                win=min(cand,key=lambda k:fits[k]); return pop[win]
            p1=select().copy(); p2=select().copy()
            if rng.random()<cross_rate:
                c1,c2=crossover(p1,p2,method,rng)
            else:
                c1,c2=p1,p2
            newpop.append(mutate(c1,rng,mutation_rate))
            if len(newpop)<pop_size: newpop.append(mutate(c2,rng,mutation_rate))
        pop=newpop
    # last gen best in pop
    fits=[tour_len(x) for x in pop]
    idx=int(np.argmin(fits))
    if fits[idx]<best_fit: best_fit=fits[idx]; best_ch=pop[idx].copy()
    elapsed=time.perf_counter()-t0
    return {'method':method,'seed':seed,'best_km':best_fit,'runtime_s':elapsed,'route':[0]+best_ch+[0],'history':history}

# Held-Karp exact optimum with depot fixed, bitmask DP over non-depot nodes.
def held_karp():
    m=N-1
    # dp[mask, j] = shortest path from depot through mask ending at j (j is 0..m-1 mapping to place j+1)
    dp=np.full((1<<m,m), np.inf, dtype=np.float64)
    parent=np.full((1<<m,m), -1, dtype=np.int16)
    for j in range(m): dp[1<<j,j]=D[0,j+1]
    for mask in range(1<<m):
        # skip masks with no meaningful states
        remmask=mask
        while remmask:
            bit=remmask & -remmask; j=bit.bit_length()-1; remmask-=bit
            prevmask=mask ^ (1<<j)
            if prevmask==0: continue
            # vectorized over predecessor nodes
            kbits=prevmask
            best=np.inf; bestk=-1
            while kbits:
                kb=kbits & -kbits; k=kb.bit_length()-1; kbits-=kb
                val=dp[prevmask,k]+D[k+1,j+1]
                if val<best: best=val; bestk=k
            dp[mask,j]=best; parent[mask,j]=bestk
    full=(1<<m)-1
    best=np.inf; end=-1
    for j in range(m):
        val=dp[full,j]+D[j+1,0]
        if val<best: best=val; end=j
    path=[]; mask=full; j=end
    while j>=0:
        path.append(j+1)
        pj=int(parent[mask,j]); mask ^= (1<<j)
        if mask==0: break
        j=pj
    path.reverse()
    return float(best),[0]+path+[0]

if __name__=='__main__':
    os.makedirs(OUT_DIR, exist_ok=True)
    print('locations',N,'stops',n,flush=True)
    t0=time.perf_counter(); opt, opt_route=held_karp(); print('exact',opt,'seconds',time.perf_counter()-t0,flush=True)
    # fixed location table
    pd.DataFrame([{'id':i,'location':p[0],'latitude':p[1],'longitude':p[2],'role':p[3]} for i,p in enumerate(places)]).to_csv(os.path.join(OUT_DIR, 'location_data.csv'),index=False)
    pd.DataFrame(D,columns=[p[0] for p in places],index=[p[0] for p in places]).to_csv(os.path.join(OUT_DIR, 'distance_matrix_km.csv'))
    results=[]; histories={}
    for method in ('PMX','IGX'):
        for seed in range(30):
            res=run_ga(method,seed=1000+seed,pop_size=60,generations=250)
            results.append({k:v for k,v in res.items() if k not in ('route','history')})
            histories[(method,seed)]=res['history']
            if seed in (0,9,19,29): print(method,seed,round(res['best_km'],3),round(res['runtime_s'],3),flush=True)
    df=pd.DataFrame(results)
    df['optimal_km']=opt
    df['gap_pct']=(df['best_km']-opt)/opt*100
    df.to_csv(os.path.join(OUT_DIR, 'run_results.csv'),index=False)
    # best routes and average histories
    bestres={}
    for method in ('PMX','IGX'):
        sub=df[df.method==method]
        br=sub.loc[sub.best_km.idxmin()]
        seed=int(br.seed)
        r=run_ga(method,seed=seed,pop_size=60,generations=250)
        # use rerun same seed for matching best route
        bestres[method]={'seed':seed,'distance_km':r['best_km'],'runtime_s':r['runtime_s'],'route':r['route']}
    with open(os.path.join(OUT_DIR, 'summary.json'),'w') as f:
        json.dump({'exact_optimum_km':opt,'exact_route':opt_route,'best_routes':bestres,'n_locations':N,'generations':250,'population':60,'runs_per_method':30},f,indent=2)
    # chart 1 best, mean, sd
    fig,ax=plt.subplots(figsize=(7.2,4.4))
    means=df.groupby('method').best_km.mean(); stds=df.groupby('method').best_km.std()
    ax.bar(means.index,means.values,yerr=stds.values,capsize=5)
    ax.axhline(opt,linestyle='--',label=f'Exact optimum ({opt:.2f} km)')
    ax.set_ylabel('Best route distance per run (km)'); ax.set_title('PMX vs IGX: Route Distance Across 30 Runs'); ax.legend(); ax.grid(axis='y',alpha=.25)
    fig.tight_layout(); fig.savefig(os.path.join(OUT_DIR, 'fig1_route_distance.png'),dpi=220); plt.close(fig)
    # chart 2 runtime
    fig,ax=plt.subplots(figsize=(7.2,4.4))
    groups=[df[df.method==m].runtime_s.values for m in ('PMX','IGX')]
    ax.boxplot(groups,tick_labels=['PMX','IGX'],showmeans=True)
    ax.set_ylabel('Runtime per GA run (seconds)'); ax.set_title('Computational Cost by Crossover Operator'); ax.grid(axis='y',alpha=.25)
    fig.tight_layout(); fig.savefig(os.path.join(OUT_DIR, 'fig2_runtime.png'),dpi=220); plt.close(fig)
    # chart 3 convergence averaged across seeds
    fig,ax=plt.subplots(figsize=(7.2,4.4))
    for method in ('PMX','IGX'):
        arr=np.array([histories[(method,s)] for s in range(30)])
        ax.plot(np.mean(arr,axis=0),label=method)
    ax.axhline(opt,linestyle='--',color='black',label='Exact optimum')
    ax.set_xlabel('Generation'); ax.set_ylabel('Best-so-far distance (km)'); ax.set_title('Mean Convergence Across 30 Independent Runs'); ax.legend(); ax.grid(alpha=.25)
    fig.tight_layout(); fig.savefig(os.path.join(OUT_DIR, 'fig3_convergence.png'),dpi=220); plt.close(fig)
    # map-like route plot (coord scatter with arrows) for best route of each crossover
    for method in ('PMX','IGX'):
        route=bestres[method]['route']
        fig,ax=plt.subplots(figsize=(7.5,5.4))
        for i,p in enumerate(places):
            ax.scatter(p[2],p[1],s=30 if i else 75,marker='s' if i==0 else 'o')
            ax.annotate(str(i)+': '+p[0].split(',')[0].replace('Depot: ','')[:22],(p[2],p[1]),xytext=(3,3),textcoords='offset points',fontsize=7)
        for a,b in zip(route[:-1],route[1:]):
            ax.annotate('',xy=(places[b][2],places[b][1]),xytext=(places[a][2],places[a][1]),arrowprops=dict(arrowstyle='->',lw=0.8,alpha=.55))
        ax.set_xlabel('Longitude'); ax.set_ylabel('Latitude'); ax.set_title(f'{method} Best Route (Geographic-distance proxy; not road routing)'); ax.grid(alpha=.2)
        fig.tight_layout(); fig.savefig(os.path.join(OUT_DIR, f'route_{method.lower()}.png'),dpi=220); plt.close(fig)
    # print stats
    print('\nSUMMARY',flush=True)
    for method in ('PMX','IGX'):
        s=df[df.method==method]
        print(method,'mean',s.best_km.mean(),'sd',s.best_km.std(),'median',s.best_km.median(),'min',s.best_km.min(),'max',s.best_km.max(),'runtime mean',s.runtime_s.mean(),'gap mean',s.gap_pct.mean(),flush=True)
    print('outputs saved',flush=True)
