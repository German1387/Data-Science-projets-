from common import *
import math
def generate(n=1200,seed=SEED):
    r=np.random.default_rng(seed);group=r.choice(4,n,p=[.3,.25,.25,.2]);centers=np.array([[10,18,1100],[25,6,280],[120,2,90],[8,5,850]])
    values=centers[group]*np.exp(r.normal(0,.3,(n,3)))
    return pd.DataFrame({'customer_id':np.arange(n),'recency_days':np.maximum(1,values[:,0].round()),'orders_90d':np.maximum(1,values[:,1].round()),'spend_90d':values[:,2].round(2)})
def assign(x,centers):return np.argmin(((x[:,None]-centers[None,:])**2).sum(2),axis=1)
def kmeans(x,k,seed=SEED,n_init=8):
    r=np.random.default_rng(seed);best=None;loss=float('inf')
    for _ in range(n_init):
        centers=x[r.choice(len(x),k,replace=False)].copy()
        for _ in range(150):
            labels=assign(x,centers);updated=np.array([x[labels==j].mean(0) if np.any(labels==j) else x[r.integers(len(x))] for j in range(k)])
            if np.max(abs(updated-centers))<1e-6:centers=updated;break
            centers=updated
        labels=assign(x,centers);inertia=float(np.sum((x-centers[labels])**2))
        if inertia<loss:loss=inertia;best=(centers.copy(),labels.copy(),inertia)
    return best
def silhouette(x,labels):
    distances=np.sqrt(((x[:,None]-x[None,:])**2).sum(2));values=[]
    for i in range(len(x)):
        own=labels==labels[i];count=int(own.sum())
        if count==1:values.append(0.);continue
        a=distances[i,own].sum()/(count-1);b=min(distances[i,labels==j].mean() for j in np.unique(labels) if j!=labels[i]);values.append(float((b-a)/max(a,b)) if max(a,b)>0 else 0.)
    return float(np.mean(values))
def adjusted_rand(a,b):
    _,a=np.unique(a,return_inverse=True);_,b=np.unique(b,return_inverse=True);table=np.zeros((a.max()+1,b.max()+1),dtype=int);np.add.at(table,(a,b),1)
    pairs=lambda z:np.sum(z*(z-1)/2)
    observed=pairs(table);left=pairs(table.sum(1));right=pairs(table.sum(0));total=math.comb(len(a),2);expected=left*right/total;denominator=(left+right)/2-expected
    return float((observed-expected)/denominator) if denominator else 1.
def main():
    df=generate();data(df);features=['recency_days','orders_90d','spend_90d'];logged=np.log1p(df[features].to_numpy());x=(logged-logged.mean(0))/logged.std(0)
    r=np.random.default_rng(SEED);sample=r.choice(len(x),400,replace=False);models={};candidates=[]
    for k in range(2,7):
        centers,labels,inertia=kmeans(x,k);models[k]=(centers,labels);candidates.append({'k':k,'silhouette':silhouette(x[sample],labels[sample]),'inertia':inertia})
    best=max(candidates,key=lambda c:c['silhouette']);k=best['k'];centers,labels=models[k];stability=[]
    for i in range(8):
        boot=r.choice(len(x),len(x));bc,_,_=kmeans(x[boot],k,seed=100+i,n_init=4);stability.append(adjusted_rand(labels,assign(x,bc)))
    m={'selected_k':k,'candidates':candidates,'bootstrap_ari':stability,'mean_bootstrap_ari':float(np.mean(stability)),'cluster_sizes':{str(j):int(np.sum(labels==j)) for j in range(k)}}
    df['cluster']=labels;df.to_csv(ROOT/'reports/assignments.csv',index=False);profiles=df.groupby('cluster')[features].median();profiles['customers']=df.groupby('cluster').size();profiles.to_csv(ROOT/'reports/cluster_profiles.csv')
    report(m,'Assess both separation and resampling stability. Cluster identifiers are arbitrary; use the original-unit median profiles to interpret their behavior before proposing campaigns.',
      'Sampled silhouette by cluster count',[f"k = {c['k']}" for c in candidates],[c['silhouette'] for c in candidates])
if __name__=='__main__':main()
