from common import *
def generate(seed=SEED):
    r=np.random.default_rng(seed);u=r.normal(0,.65,(180,4));v=r.normal(0,.65,(120,4));rows=[]
    for user in range(180):
        for item in r.choice(120,42,replace=False):rows.append((user,item,np.clip(3+u[user]@v[item]+r.normal(0,.15),1,5)))
    return pd.DataFrame(rows,columns=['user_id','item_id','rating'])
def split(df,seed=SEED):
    r=np.random.default_rng(seed);a=[];b=[];c=[]
    for _,group in df.groupby('user_id'):
        idx=r.permutation(group.index);a.extend(idx[8:]);b.extend(idx[:4]);c.extend(idx[4:8])
    return df.loc[a],df.loc[b],df.loc[c]
def predict(model,df):
    mu,bu,bi,u,v=model;users=df.user_id.to_numpy(int);items=df.item_id.to_numpy(int)
    return np.clip(mu+bu[users]+bi[items]+np.sum(u[users]*v[items],axis=1),1,5)
def train_model(train,val,rank=4,epochs=70):
    r=np.random.default_rng(SEED);mu=float(train.rating.mean());bu=np.zeros(180);bi=np.zeros(120)
    u=r.normal(0,.15,(180,rank));v=r.normal(0,.15,(120,rank));rows=train.to_numpy();best=None;loss=float('inf');best_epoch=0
    for epoch in range(1,epochs+1):
        for user,item,rating in rows[r.permutation(len(rows))]:
            user=int(user);item=int(item);old=u[user].copy();error=rating-(mu+bu[user]+bi[item]+u[user]@v[item]);lr=.025
            bu[user]+=lr*(error-.06*bu[user]);bi[item]+=lr*(error-.06*bi[item])
            u[user]+=lr*(error*v[item]-.06*u[user]);v[item]+=lr*(error*old-.06*v[item])
        model=(mu,bu,bi,u,v);current=float(np.mean((val.rating.to_numpy()-predict(model,val))**2))
        if current<loss:loss=current;best=tuple(z.copy() if isinstance(z,np.ndarray) else z for z in model);best_epoch=epoch
    return best,best_epoch
def errors(y,p):return {'rmse':float(np.sqrt(np.mean((y-p)**2))),'mae':float(np.mean(abs(y-p)))}
def main():
    df=generate();train,val,test=split(df);data(df,'ratings.csv')
    items=pd.DataFrame({'item_id':np.arange(120),'name':[f'Product {i:03}' for i in range(120)],'category':[['Books','Music','Games','Courses'][i%4] for i in range(120)]});data(items,'items.csv')
    model,epoch=train_model(train,val);base,base_epoch=train_model(train,val,rank=0)
    m={'ratings':len(df),'train':len(train),'validation':len(val),'test':len(test),'selected_epoch':epoch,'baseline_selected_epoch':base_epoch,
       'matrix_factorization':errors(test.rating.to_numpy(),predict(model,test)),'bias_baseline':errors(test.rating.to_numpy(),predict(base,test))}
    records=[]
    for user in range(10):
        observed=pd.concat([train,val]);seen=set(observed.loc[observed.user_id==user,'item_id'])
        candidates=pd.DataFrame({'user_id':user,'item_id':[i for i in range(120) if i not in seen]});candidates['predicted_rating']=predict(model,candidates)
        records.append(candidates.nlargest(5,'predicted_rating'))
    pd.concat(records).merge(items,on='item_id').to_csv(ROOT/'reports/recommendations.csv',index=False)
    scored=test.copy();scored['prediction']=predict(model,test);scored.to_csv(ROOT/'reports/test_predictions.csv',index=False)
    report(m,'Validation selects the training epoch; test ratings are used only for evaluation. Recommendations exclude training and validation items and can include held-out test items. Rating RMSE does not measure ranking performance.',
      'Held-out rating RMSE · lower is better',['Matrix factorization','User/item bias baseline'],[m['matrix_factorization']['rmse'],m['bias_baseline']['rmse']])
if __name__=='__main__':main()
