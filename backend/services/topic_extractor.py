from sklearn.feature_extraction.text import TfidfVectorizer
from backend.services.text_cleaner import clean_ocr_garbage

def extract_topics(text):
    # Clean text first to remove OCR garbage
    text = clean_ocr_garbage(text)
    
    # Blacklist of words that should never be topics (OCR artifacts, metadata)
    blacklist = {
        'picture', 'intentionally', 'omitted', 'image', 'photo', 'figure', 'fig',
        'noise', 'filter', 'start', 'end', 'text', 'source', 'pdf', 'docx', 
        'content', 'analyzed', 'specialized', 'concept', 'omitted_image', 'images'
    }
    
    vectorizer = TfidfVectorizer(stop_words='english', min_df=1)
    
    try:
        matrix = vectorizer.fit_transform([text])
        words = vectorizer.get_feature_names_out()
        scores = matrix.toarray()[0]
        
        word_scores = list(zip(words, scores))
        sorted_words = sorted(word_scores, key=lambda x: x[1], reverse=True)
        
        # Filter out blacklisted words and numeric garbage
        top_words = []
        for word, score in sorted_words:
            word_lower = word.lower()
            if word_lower not in blacklist and len(word) > 2 and not word.isdigit():
                top_words.append(word.capitalize())
            if len(top_words) >= 12:
                break
                
        return top_words
    except:
        return ["Study Material", "Academic Document"]