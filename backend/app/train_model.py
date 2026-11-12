from pathlib import Path
import json
import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

BASE = Path(__file__).resolve().parents[1]
DATA = BASE/"data"/"water_quality_demo.csv"
MODELS = BASE/"models"
FEATURES = ["ph","dissolved_oxygen","turbidity","tds","contamination"]
CLASSES = ["Excellent","Good","Poor","Unsuitable"]

def create_dataset(rows=1600, seed=42):
    rng=np.random.default_rng(seed)
    ph=rng.uniform(5,10,rows); do=rng.uniform(.2,12,rows)
    turb=rng.uniform(.1,40,rows); tds=rng.uniform(50,1800,rows)
    cont=rng.choice([0,1,2],rows,p=[.68,.22,.10])
    risk=(np.maximum(0,np.abs(ph-7.4)-.8)*8 + np.maximum(0,6-do)*8 +
          np.maximum(0,turb-5)*.8 + np.maximum(0,tds-500)*.06 + cont*17)
    y=np.where(risk<10,"Excellent",np.where(risk<25,"Good",np.where(risk<60,"Poor","Unsuitable")))
    df=pd.DataFrame({"ph":ph,"dissolved_oxygen":do,"turbidity":turb,"tds":tds,
                     "contamination":cont,"category":y,"data_origin":"synthetic_demo"})
    DATA.parent.mkdir(parents=True,exist_ok=True); df.to_csv(DATA,index=False)
    return df

def train_and_save():
    MODELS.mkdir(parents=True,exist_ok=True)
    df=pd.read_csv(DATA) if DATA.exists() else create_dataset()
    df=df.dropna(subset=FEATURES+["category"])
    X=df[FEATURES]; y=df.category
    Xtr,Xte,ytr,yte=train_test_split(X,y,test_size=.2,random_state=42,stratify=y)
    models={"Decision Tree":DecisionTreeClassifier(max_depth=8,min_samples_leaf=5,class_weight="balanced",random_state=42),
            "Random Forest":RandomForestClassifier(n_estimators=180,max_depth=10,min_samples_leaf=3,class_weight="balanced",random_state=42,n_jobs=-1)}
    metrics={"dataset":"Synthetic demonstration dataset; not laboratory data","rows":len(df),
             "train_rows":len(Xtr),"test_rows":len(Xte),"features":FEATURES,"models":{}}
    for name,model in models.items():
        model.fit(Xtr,ytr); pred=model.predict(Xte)
        metrics["models"][name]={"accuracy_percent":round(accuracy_score(yte,pred)*100,2),
            "classification_report":classification_report(yte,pred,output_dict=True,zero_division=0),
            "confusion_matrix":confusion_matrix(yte,pred,labels=CLASSES).tolist(),"class_order":CLASSES}
        joblib.dump(model,MODELS/("decision_tree.joblib" if name=="Decision Tree" else "random_forest.joblib"))
    (MODELS/"metrics.json").write_text(json.dumps(metrics,indent=2))
    return metrics

if __name__=="__main__":
    m=train_and_save()
    print({k:v["accuracy_percent"] for k,v in m["models"].items()})
