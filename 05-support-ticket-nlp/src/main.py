from common import *
import re
from collections import Counter
PHRASES={
'billing':['invoice shows a duplicate charge','refund for the payment is missing','subscription billing amount is wrong','payment charged twice on my invoice','refund this incorrect subscription charge','billing invoice payment needs a refund'],
'account':['password reset for my account failed','login access to my profile is blocked','change the email for my account','cannot login after password change','account profile email access is lost','reset login password for account access'],
'technical':['app crashes with a server error','software freezes after the latest update','dashboard bug makes the screen blank','server error crashes my dashboard','software update has a screen bug','app freezes with a technical error'],
'delivery':['package tracking says shipment is late','shipping address on my order is wrong','courier delivery has not arrived','late shipment package needs tracking','order delivery went to wrong address','courier shipping tracking shows no package']}
def tokens(text):return re.findall(r'[a-z]{2,}',text.lower())
def generate(seed=SEED):
    r=np.random.default_rng(seed);rows=[]
    for label,phrases in PHRASES.items():
        for family,phrase in enumerate(phrases):
            split='train' if family<4 else ('validation' if family==4 else 'test')
            for _ in range(70):
                prefix=r.choice(['please help','hello support','urgent request','can someone check']);suffix=r.choice(['since yesterday','today','for the second time','please investigate']);noise=r.choice(['','account','order','payment','app'])
                mixed=bool(r.random()<.30)
                secondary=str(r.choice([c for c in PHRASES if c!=label]))
                extra=(' also '+PHRASES[secondary][family]) if mixed else ''
                rows.append((f'{prefix} primary request {phrase}{extra} {suffix} {noise} reference {r.integers(10000,99999)}',label,f'{label}-{family}',split,mixed))
    return pd.DataFrame(rows,columns=['text','label','family','split','mixed_intent'])
def vectorize(texts,vocab):
    x=np.zeros((len(texts),len(vocab)))
    for i,text in enumerate(texts):
        for token,count in Counter(tokens(text)).items():
            if token in vocab:x[i,vocab[token]]=count
    return x
def fit(texts,labels):
    vocab={t:i for i,t in enumerate(sorted(set(t for text in texts for t in tokens(text))))};classes=sorted(set(labels));x=vectorize(texts,vocab)
    counts=np.array([x[np.array(labels)==c].sum(0)+1 for c in classes]);likelihood=np.log(counts/counts.sum(1,keepdims=True))
    prior=np.log(np.array([sum(np.array(labels)==c) for c in classes])/len(labels));return vocab,classes,likelihood,prior
def probabilities(model,texts):
    vocab,classes,likelihood,prior=model;scores=vectorize(texts,vocab)@likelihood.T+prior;scores-=scores.max(1,keepdims=True);p=np.exp(scores);return p/p.sum(1,keepdims=True)
def metrics(y,pred,classes):
    matrix=np.array([[sum((y==a)&(pred==b)) for b in classes] for a in classes]);f1=[]
    for i in range(len(classes)):
        tp=matrix[i,i];f1.append(float(2*tp/max(matrix[i].sum()+matrix[:,i].sum(),1)))
    return {'accuracy':float(np.mean(y==pred)),'macro_f1':float(np.mean(f1)),'class_order':classes,'confusion_matrix':matrix.tolist()}
def main():
    df=generate();data(df);train=df[df.split=='train'];val=df[df.split=='validation'];test=df[df.split=='test']
    model=fit(train.text.tolist(),train.label.tolist());classes=np.array(model[1]);vp=probabilities(model,val.text.tolist());vpred=classes[vp.argmax(1)];vy=val.label.to_numpy();eligible=[]
    for threshold in np.linspace(.25,.999,100):
        keep=vp.max(1)>=threshold
        if keep.mean()>=.25 and np.mean(vpred[keep]==vy[keep])>=.9:eligible.append(float(threshold))
    threshold=min(eligible) if eligible else 1.01;p=probabilities(model,test.text.tolist());pred=classes[p.argmax(1)];y=test.label.to_numpy();keep=p.max(1)>=threshold
    m={'model':metrics(y,pred,model[1]),'majority_baseline':metrics(y,np.full(len(y),train.label.mode()[0]),model[1]),
       'validation_selected_threshold':threshold,'test_routing_coverage':float(keep.mean()),'test_accepted_accuracy':float(np.mean(pred[keep]==y[keep])) if keep.any() else None,
       'mixed_intent_test_accuracy':float(np.mean(pred[test.mixed_intent.to_numpy()]==y[test.mixed_intent.to_numpy()])),
       'single_intent_test_accuracy':float(np.mean(pred[~test.mixed_intent.to_numpy()]==y[~test.mixed_intent.to_numpy()])),
       'vocabulary_size':len(model[0]),'split_sizes':{'train':len(train),'validation':len(val),'test':len(test)}}
    result=test.copy();result['prediction']=pred;result['confidence']=p.max(1);result['auto_route']=keep;result.to_csv(ROOT/'reports/test_predictions.csv',index=False)
    vocab=list(model[0]);rows=[]
    for i,label in enumerate(model[1]):
        importance=model[2][i]-np.mean(np.delete(model[2],i,axis=0),axis=0)
        for j in np.argsort(importance)[-10:][::-1]:rows.append((label,vocab[j],importance[j]))
    pd.DataFrame(rows,columns=['class','token','log_likelihood_contrast']).to_csv(ROOT/'reports/influential_tokens.csv',index=False)
    report(m,'Full phrase families are reserved for validation and test. Inspect confusion, accepted coverage and the stated language limitations before considering automated routing.',
      'Test macro F1',['Naive Bayes','Majority baseline'],[m['model']['macro_f1'],m['majority_baseline']['macro_f1']])
if __name__=='__main__':main()
