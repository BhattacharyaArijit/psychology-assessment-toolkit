def reverse_score(value, min_val, max_val):
    return max_val + min_val - value

def calculate_scores(questionnaires, responses):
    """
    Returns a dict:
    {
        "items": { QID: {"raw": val, "score": val_after_reverse}, ... },
        "totals": { questionnaire_total/subscales }
    }
    """
    def reverse_score(value, min_val, max_val):
        return max_val + min_val - value

    result = {"items": {}, "totals": {}}

    for qdata in questionnaires:
        name = qdata["name"]
        reverse_items = qdata.get("reverse_items", [])

        # numeric scale
        scale = qdata.get("scale", [1,2,3,4,5])
        numeric_scale = []
        for val in scale:
            if isinstance(val, dict):
                try:
                    numeric_scale.append(int(val["value"]))
                except:
                    continue
            else:
                try:
                    numeric_scale.append(int(val))
                except:
                    continue
        if not numeric_scale:
            numeric_scale = [1,2,3,4,5]

        min_val = min(numeric_scale)
        max_val = max(numeric_scale)

        item_values = {}
        total = 0

        for q in qdata["questions"]:
            qid = f"{name}_{q['id']}"
            raw = responses.get(qid)
            if raw in ("", None):
                continue
            try:
                val = int(raw)
            except:
                continue

            score_val = reverse_score(val, min_val, max_val) if qid in reverse_items or q['id'] in reverse_items else val
            item_values[qid] = score_val
            total += score_val

            # Store per-item
            result["items"][qid] = {"raw": val, "score": score_val}

        # Total for questionnaire
        result["totals"][f"{name}_total"] = total

        # Subscales
        if "subscales" in qdata:
            for subscale, items in qdata["subscales"].items():
                sub_total = sum(item_values.get(f"{name}_{i}", 0) for i in items)
                result["totals"][f"{name}_{subscale}"] = sub_total

    return result
