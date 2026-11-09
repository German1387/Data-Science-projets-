from common import *

def generate(n=5000,seed=SEED):
    r=np.random.default_rng(seed)
    tenure=r.integers(1,73,n);fee=r.uniform(20,120,n);calls=r.poisson(1.3,n);usage=np.maximum(0,r.normal(24,12,n))
    p=sigmoid(-1.3-.025*tenure+.012*(fee-60)+.52*calls-.035*(usage-20))
    return pd.DataFrame(dict(customer_id=np.arange(n),tenure_months=tenure,monthly_fee=fee,support_calls=calls,usage_hours=usage,churn=r.binomial(1,p)))

def cost(y,p,t):
    # Assumed contact cost $8; missed cancellation cost $60. No causal claim.
    return float(np.mean(8*(p>=t)+60*((p<t)&(y==1))))

def main():
    df=generate();data(df);order=np.random.default_rng(SEED).permutation(len(df));tr,va,te=np.split(order,[3000,4000])
    features=['tenure_months','monthly_fee','support_calls','usage_hours'];raw=df[features].to_numpy();y=df.churn.to_numpy()
    mean=raw[tr].mean(0);scale=raw[tr].std(0);x=np.c_[np.ones(len(df)),(raw-mean)/scale]
    w=logistic(x[tr],y[tr]);p=sigmoid(x@w)
    threshold=float(min(np.linspace(.02,.98,97),key=lambda t:cost(y[va],p[va],t)))
    m={'split_sizes':{'train':len(tr),'validation':len(va),'test':len(te)},'validation_selected_threshold':threshold,
       'model':classification(y[te],p[te],threshold),'baseline':classification(y[te],np.full(len(te),y[tr].mean())),
       'test_cost_per_account':cost(y[te],p[te],threshold),'contact_none_cost':float(60*y[te].mean()),'contact_all_cost':8.0}
    scored=df.iloc[te].copy();scored['risk']=p[te];scored['contact']=p[te]>=threshold
    scored.to_csv(ROOT/'reports/test_predictions.csv',index=False)
    pd.DataFrame({'feature':['intercept']+features,'coefficient':w}).to_csv(ROOT/'reports/coefficients.csv',index=False)
    report(m,'The threshold uses validation labels only. Compare discrimination, Brier score and the assumed decision costs; none of these measures demonstrates retention impact.',
      'Test ROC AUC',['Logistic regression','Constant baseline'],[m['model']['roc_auc'],m['baseline']['roc_auc']])
if __name__=='__main__': main()
