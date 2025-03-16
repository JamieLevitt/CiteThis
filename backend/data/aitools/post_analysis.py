import re
from bs4 import BeautifulSoup
from rapidfuzz import process, fuzz

from structs.data import TrendStruct

def normalize_word(word: str) -> str:
    """Normalize words by reducing repeated letters (e.g., Amerikkka -> America)"""
    return re.sub(r'(\w)\1{2,}', r'\1', word)  # Replace 3+ repeated chars with single char


def tag_post_body(tweet_html:str):
    topics = TrendStruct.load_all_with_kw()

    soup = BeautifulSoup(tweet_html, "html.parser")
    text_elements = soup.find_all(text=True, recursive=True)
    
    keywords_to_topics = {}
    for topic, keywords in topics.items():
        for keyword in keywords:
            keywords_to_topics[keyword.lower()] = topic
    
    found_topics = set()
    
    def replace_keyword(match):
        word = match.group()
        result = process.extractOne(word, keywords_to_topics.keys(), scorer=fuzz.partial_ratio)
        
        if result:
            best_match, score = result[0], result[1]
            if score > 85:  # Threshold for fuzzy matching
                topic = keywords_to_topics[best_match]
                found_topics.add(topic)
                return f'<span class="highlight">{word}</span>'
        return word
    
    for element in text_elements:
        if element.parent.name not in ['script', 'style', 'a', 'img']:  # Avoid altering links & scripts
            new_text = re.sub(r'\b\w+\b', replace_keyword, element)
            element.replace_with(BeautifulSoup(new_text, "html.parser"))
    
    return list(found_topics), str(soup)
