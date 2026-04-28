import urllib.parse

def get_youtube_recommendations(topics):
    """
    Generates educational YouTube search links for the given topics.
    """
    recommendations = []
    
    # Priority channels for high-quality education
    educational_suffixes = [
        "educational explanation",
        "crash course",
        "khan academy",
        "ted-ed"
    ]
    
    for topic in topics[:5]: # Top 5 topics
        query = f"{topic} educational explanation"
        encoded_query = urllib.parse.quote(query)
        url = f"https://www.youtube.com/results?search_query={encoded_query}"
        
        recommendations.append({
            "topic": topic,
            "url": url,
            "display_name": f"Learn about {topic.capitalize()} on YouTube"
        })
        
    return recommendations
