def calculate_trust_label(pred_pct: float, actual_pct: float) -> str:
    # Direction Check whether both predicted and actual changes are in the same direction (both positive or both negative)
    # If both represent same direction (both positive or both negative)
    # Using a small epsilon for float comparison safety
    same_direction = (pred_pct > 0 and actual_pct > 0) or (pred_pct < 0 and actual_pct < 0)

    if not same_direction:
        # Special case: If actual is essentially 0 (flat), but we predicted movement
        if abs(actual_pct) < 0.0005: 
             return "Direction Accurate (Precision)"
        return "Direction Missed (Warning)"

    # Magnitude Check
    diff = abs(pred_pct - actual_pct)
    
    # If the difference is less than 0.15%, it is a Bullseye
    if diff < 0.0015:
        return "Direction Matched (High Trust)"
    
    # If Actual move was BIGGER than Predicted move (We were safe)
    if abs(actual_pct) > abs(pred_pct):
        return "Direction Matched (Conservative)"
        
    return "Direction Matched (Optimistic)"