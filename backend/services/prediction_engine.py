import datetime

def calculate_learning_decay(last_score, last_review_date):
    """
    Calculates the current mastery level based on time passed.
    Simplified Forgetting Curvec: Mastery = Score * e^(-t/S)
    """
    today = datetime.datetime.now()
    days_passed = (today - last_review_date).days
    # S - Strength of memory (Higher Score = stronger memory)
    strength = max(last_score/10,1)

    import math
    current_mastery = last_score * math.exp(-days_passed/strength)

    return round(current_mastery, 2)

def get_study_recommendation(mastery_score):
        """ Analyzes the score and provides human-like feedback."""
        if mastery_score < 30:
            return "🚨 PANIC MODE: You are forgetting fast! Review immediately."
        if mastery_score < 50:
            return "🔥 Critical: Restudy immediately!"
        if mastery_score < 75:
            return "⚠️ Warning: Memory is fading. Quick Review suggested."
        if mastery_score < 90:
            return "👍 Good! Keep it going."
        if mastery_score < 95:
            return "⚡ Excellent: Almost there!"
        if mastery_score < 98:
            return "🌟 Pro Mode: You are a master!"
        else:
            return "🏆 LEGEND: 100% Mastery!"   
