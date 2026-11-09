from common import *
def generate(n=1095,seed=SEED):
    r=np.random.default_rng(seed);t=np.arange(n)
    y=np.maximum(1,160+.055*t+25*np.sin(2*np.pi*t/7)+18*np.cos(2*np.pi*t/365.25)+r.normal(0,9,n))
    return pd.DataFrame({'date':pd.date_range('2022-01-01',periods=n),'units':y.round()})
def row(t,h):
    return [1,t/365.25,np.sin(2*np.pi*t/7),np.cos(2*np.pi*t/7),np.sin(2*np.pi*t/365.25),np.cos(2*np.pi*t/365.25),h[t-1]/200,h[t-7]/200]
def forecast(history,horizon):
    h=list(map(float,history));n=len(h);x=np.array([row(t,h) for t in range(7,n)]);y=np.array(h[7:])
    penalty=np.eye(x.shape[1]);penalty[0,0]=0;w=np.linalg.solve(x.T@x+penalty,x.T@y);out=[]
    for t in range(n,n+horizon):
        p=max(0,float(np.array(row(t,h))@w));h.append(p);out.append(p)
    return np.array(out)
def naive(history,horizon):
    h=list(history)
    for _ in range(horizon):h.append(h[-7])
    return np.array(h[-horizon:])
def errors(y,p):
    return {'mae':float(np.mean(abs(y-p))),'rmse':float(np.sqrt(np.mean((y-p)**2))),'wape':float(np.sum(abs(y-p))/np.sum(abs(y)))}
def main():
    df=generate();data(df);y=df.units.to_numpy();folds=[]
    for cutoff in [700,756,812,868,924,980]:
        actual=y[cutoff:cutoff+7]
        folds.append({'cutoff':cutoff,'model_mae':errors(actual,forecast(y[:cutoff],7))['mae'],'baseline_mae':errors(actual,naive(y[:cutoff],7))['mae']})
    cutoff=len(y)-28;p=forecast(y[:cutoff],28);base=naive(y[:cutoff],28)
    m={'rolling_backtests':folds,'final_holdout':errors(y[cutoff:],p),'seasonal_naive':errors(y[cutoff:],base)}
    pd.DataFrame({'date':df.date.iloc[cutoff:],'actual':y[cutoff:],'forecast':p,'seasonal_naive':base,'residual':y[cutoff:]-p}).to_csv(ROOT/'reports/forecasts.csv',index=False)
    report(m,'Six historical rolling backtests precede a final 28-day holdout. Both models recursively forecast without observing actual future demand.',
      'Final holdout MAE · lower is better',['Ridge seasonal model','Seasonal naive'],[m['final_holdout']['mae'],m['seasonal_naive']['mae']])
if __name__=='__main__':main()
