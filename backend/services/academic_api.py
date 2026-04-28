import requests
import xml.etree.ElementTree as ET

def search_arxiv(query, max_results=3):
    """
    Searches ArXiv for the latest research papers related to a query.
    Returns a list of dictionaries containing title, summary, and link.
    """
    if not query:
        return []
        
    base_url = "http://export.arxiv.org/api/query?"
    # Format query for ArXiv
    formatted_query = query.replace(" ", "+")
    params = f"search_query=all:{formatted_query}&start=0&max_results={max_results}&sortBy=relevance&sortOrder=descending"
    
    try:
        response = requests.get(base_url + params, timeout=10)
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            papers = []
            # ArXiv uses Atom feed format
            namespace = {'atom': 'http://www.w3.org/2005/Atom'}
            
            for entry in root.findall('atom:entry', namespace):
                title = entry.find('atom:title', namespace).text.strip()
                summary = entry.find('atom:summary', namespace).text.strip()
                link = entry.find('atom:id', namespace).text.strip()
                
                # Clean up title and summary (remove newlines)
                title = title.replace('\n', ' ')
                summary = summary.replace('\n', ' ')
                
                papers.append({
                    "title": title,
                    "summary": summary,
                    "link": link
                })
            return papers
    except Exception as e:
        print(f"Error searching ArXiv: {e}")
        
    return []
