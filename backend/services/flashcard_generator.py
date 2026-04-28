import re
import random

def generate_flashcards(text, num_cards=15):
    """
    Generates facts for flashcards from the text.
    Uses a heuristic approach to find 'Fact: Explanation' patterns.
    """
    # Simple strategy: Identify key sentences and turn them into Front/Back pairs
    sentences = re.split(r'(?<=[.!?]) +', text)
    
    # Filter for interesting sentences (length 15-30 words)
    candidates = [s for s in sentences if 15 < len(s.split()) < 35]
    random.shuffle(candidates)
    
    flashcards = []
    for sentence in candidates[:num_cards]:
        # Split sentence into two halves for front/back
        words = sentence.split()
        pivot = len(words) // 2
        
        front = " ".join(words[:pivot]) + "..."
        back = "..." + " ".join(words[pivot:])
        
        flashcards.append({
            "front": front,
            "back": back,
            "original": sentence
        })
        
    return flashcards
