from common import *
import math
def generate(n=6000,seed=SEED):
    r=np.random.default_rng(seed);t=r.binomial(1,.5,n);pre=r.gamma(2,15,n)
    revenue=np.maximum(0,8+.65*pre+r.normal(0,12,n)+2*t)
    return pd.DataFrame(dict(user_id=np.arange(n),treatment=t,pre_spend=pre,revenue=revenue))
def cuped(y,x):
    theta=float(np.cov(y,x,ddof=1)[0,1]/np.var(x,ddof=1)) if np.var(x)>0 else 0.
    return y-theta*(x-x.mean()),theta
def allocation_pvalue(k,n):
    lo=min(k,n-k)
    logs=np.array([math.lgamma(n+1)-math.lgamma(i+1)-math.lgamma(n-i+1)-n*math.log(2) for i in range(lo+1)])
    top=logs.max();return min(1.,float(2*np.exp(top)*np.exp(logs-top).sum()))
def main():
    df=generate();data(df);r=np.random.default_rng(SEED);y=df.revenue.to_numpy();x=df.pre_spend.to_numpy();t=df.treatment.to_numpy().astype(bool)
    adj,theta=cuped(y,x);raw=float(y[t].mean()-y[~t].mean());effect=float(adj[t].mean()-adj[~t].mean())
    a=np.flatnonzero(t);b=np.flatnonzero(~t);raw_draws=[];adj_draws=[]
    for _ in range(2000):
        ia=r.choice(a,len(a));ib=r.choice(b,len(b));idx=np.r_[ia,ib];adjusted,_=cuped(y[idx],x[idx])
        raw_draws.append(float(y[ia].mean()-y[ib].mean()));adj_draws.append(float(adjusted[:len(a)].mean()-adjusted[len(a):].mean()))
    extreme=0
    for _ in range(2000):
        perm=r.permutation(y);extreme+=abs(perm[t].mean()-perm[~t].mean())>=abs(raw)
    m={'n_users':len(df),'treatment_users':int(t.sum()),'sample_ratio_exact_p':allocation_pvalue(int(t.sum()),len(t)),
       'raw_revenue_effect':raw,'raw_95pct_ci':np.quantile(raw_draws,[.025,.975]).tolist(),
       'cuped_revenue_effect':effect,'cuped_95pct_ci':np.quantile(adj_draws,[.025,.975]).tolist(),
       'cuped_theta':theta,'bootstrap_variance_reduction':float(1-np.var(adj_draws)/np.var(raw_draws)),
       'raw_permutation_p':(extreme+1)/2001,'simulation_latent_additive_effect':2.0}
    pd.DataFrame({'raw_effect':raw_draws,'cuped_effect':adj_draws}).to_csv(ROOT/'reports/bootstrap.csv',index=False)
    report(m,'Interpret effect sizes with their confidence intervals. Clipping revenue at zero means the population effect differs slightly from the latent additive effect of 2. This is a simulated experiment, with no real rollout recommendation.',
      'Revenue effect per assigned user',['Raw estimate','CUPED estimate'],[raw,effect])
if __name__=='__main__':main()
