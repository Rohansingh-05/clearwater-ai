"""Demonstration WQI only: the PPT does not specify an official formula or weights."""
WEIGHTS = {"pH": .15, "Dissolved oxygen": .25, "Turbidity": .25, "TDS": .25, "Contamination indicator": .10}

def clamp(x):
    return max(0.0, min(100.0, float(x)))

def category(score):
    if score >= 90: return "Excellent"
    if score >= 70: return "Good"
    if score >= 50: return "Poor"
    return "Unsuitable"

def calculate_wqi(s):
    ph = 100 if 6.5 <= s["ph"] <= 8.5 else clamp(100 - (6.5-s["ph"])*35 if s["ph"] < 6.5 else 100-(s["ph"]-8.5)*35)
    scores = {
        "pH": round(ph, 2),
        "Dissolved oxygen": round(clamp(s["dissolved_oxygen"]/8*100), 2),
        "Turbidity": round(clamp(100-s["turbidity"]*4), 2),
        "TDS": round(clamp(100-s["tds"]/15), 2),
        "Contamination indicator": {0:100.0, 1:50.0, 2:0.0}[s["contamination"]]
    }
    contributions = {k: round(scores[k]*v, 2) for k,v in WEIGHTS.items()}
    total = round(sum(contributions.values()), 2)
    return {"score":total, "category":category(total), "parameter_scores":scores,
            "weights":WEIGHTS, "weighted_contributions":contributions,
            "method_note":"Demonstration weighted-score method; not an official WHO/CPCB WQI formula."}
