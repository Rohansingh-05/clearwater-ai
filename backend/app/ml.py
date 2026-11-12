from pathlib import Path
import joblib
import pandas as pd
from .train_model import FEATURES, MODELS, train_and_save

def get_models():
    if not (MODELS/"random_forest.joblib").exists() or not (MODELS/"decision_tree.joblib").exists():
        train_and_save()
    return {"Decision Tree":joblib.load(MODELS/"decision_tree.joblib"),
            "Random Forest":joblib.load(MODELS/"random_forest.joblib")}

def predict(sample):
    row=pd.DataFrame([[sample[k] for k in FEATURES]],columns=FEATURES)
    results={}
    for name,model in get_models().items():
        probs=model.predict_proba(row)[0]; labels=list(model.classes_); i=int(probs.argmax())
        results[name]={"category":str(labels[i]),"confidence":round(float(probs[i])*100,2),
                       "probabilities":{str(k):round(float(v)*100,2) for k,v in zip(labels,probs)}}
    return {"primary_model":"Random Forest","primary":results["Random Forest"],"models":results,
            "note":"Confidence is a model probability estimate, not a measure of water safety."}
