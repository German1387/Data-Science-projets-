from pathlib import Path
import json
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
SEED=42
def data(df,name='data.csv'):
    df.to_csv(ROOT/'data'/name,index=False)
def sigmoid(x): return 1/(1+np.exp(-np.clip(x,-35,35)))
def logistic(x,y,steps=1800):
    w=np.zeros(x.shape[1])
    for _ in range(steps):
        penalty=.01*w;penalty[0]=0
        w-=.15*(x.T@(sigmoid(x@w)-y)/len(y)+penalty)
    return w
def classification(y,p,t=.5):
    y=np.asarray(y);p=np.asarray(p);pred=p>=t
    tp=int(np.sum(pred&(y==1)));fp=int(np.sum(pred&(y==0)))
    fn=int(np.sum(~pred&(y==1)));tn=int(np.sum(~pred&(y==0)))
    pos=p[y==1];neg=p[y==0]
    return {'roc_auc':float(np.mean((pos[:,None]>neg)+.5*(pos[:,None]==neg))),
      'precision':tp/max(tp+fp,1),'recall':tp/max(tp+fn,1),'accuracy':(tp+tn)/len(y),
      'brier_score':float(np.mean((p-y)**2)),'confusion_matrix':dict(tp=tp,fp=fp,fn=fn,tn=tn)}
def report(metrics,text,title,labels,values):
    import html
    out=ROOT/'reports'
    (out/'metrics.json').write_text(json.dumps(metrics,indent=2,allow_nan=False)+'\n')
    (out/'report.md').write_text('# Results\n\n'+text+'\n\n![Results](results.svg)\n\n```json\n'+json.dumps(metrics,indent=2)+'\n```\n')
    height=160+54*len(labels);mx=max(abs(float(v)) for v in values) or 1
    svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="850" height="{height}" role="img" aria-label="{html.escape(title)}">',
      '<rect width="100%" height="100%" fill="#f4f7fc"/>',
      f'<text x="32" y="43" font-family="sans-serif" font-size="23" fill="#132541">{html.escape(title)}</text>',
      '<text x="32" y="72" font-family="sans-serif" font-size="12" fill="#53627b">SYNTHETIC DATA · REPRODUCIBLE RUN · SEED 42</text>']
    for i,(label,value) in enumerate(zip(labels,values)):
        y=100+54*i;length=440*abs(float(value))/mx
        svg += [f'<text x="32" y="{y+20}" font-family="sans-serif" font-size="14">{html.escape(str(label))}</text>',
          f'<rect x="270" y="{y}" width="{length:.1f}" height="28" rx="4" fill="#2967d7"/>',
          f'<text x="{280+length:.1f}" y="{y+20}" font-family="sans-serif" font-size="13">{float(value):.3f}</text>']
    (out/'results.svg').write_text('\n'.join(svg+['</svg>']))
    print(json.dumps(metrics,indent=2))
