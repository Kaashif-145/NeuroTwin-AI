import random

def generate_study_structure(topics, level):
    """
    Generates a structured 7-day study roadmap based on identified topics and difficulty level.
    """
    days = {
        "Day 1-2: Foundations": [],
        "Day 3-5: Deep Dive": [],
        "Day 6-7: Expert Practice & Review": []
    }
    
    if not topics:
        topics = ["Core Concepts", "Theoretical Framework", "Practical Applications", "Case Studies"]

    shuffled_topics = list(topics)
    random.shuffle(shuffled_topics)
    
    # Split topics across the days
    num_topics = len(shuffled_topics)
    
    # Foundation
    days["Day 1-2: Foundations"] = shuffled_topics[:max(1, num_topics // 3)]
    
    # Deep Dive
    days["Day 3-5: Deep Dive"] = shuffled_topics[max(1, num_topics // 3):max(2, (2 * num_topics) // 3)]
    
    # Expert Review
    days["Day 6-7: Expert Practice & Review"] = shuffled_topics[max(2, (2 * num_topics) // 3):]
    
    # Add structured advice
    guide = [
        f"Target Complexity: {level}",
        "Focus on defining all key terms during the Foundation phase.",
        "Attempt the 10-mark descriptive questions during the Deep Dive phase.",
        "Take the 15-mark Expert Mastery Quiz on Day 7 to finalize your preparation."
    ]
    
    return {
        "roadmap": days,
        "advice": guide
    }
