import re
from rapidfuzz import process

def normalize_word(word: str) -> str:
    """Normalize words by reducing repeated letters (e.g., Amerikkka -> America)"""
    return re.sub(r'(\w)\1{2,}', r'\1', word)  # Replace 3+ repeated chars with single char

def tag_post_body(topics: dict, post: str) -> tuple[list[str], str]:
    # Create a mapping of keyword to topic
    keyword_to_topic = {}
    all_keywords = []
    
    for topic, meta in topics.items():
        for keyword in meta["keywords"]:
            normalized_keyword = normalize_word(keyword.lower())  # Normalize keywords
            keyword_to_topic[normalized_keyword] = topic  # Store in lowercase for case-insensitive matching
            all_keywords.append(normalized_keyword)
    
    # Function to find the best fuzzy match
    def find_best_match(word):
        normalized_word = normalize_word(word.lower())
        result = process.extractOne(normalized_word, all_keywords, score_cutoff=75)
        if result:
            match, score, _ = result
            return match
        return None  # Return None if no good match is found
    
    # Tokenize the post into words
    words = re.findall(r'\b\w+\b', post)
    found_topics = set()
    
    # Replace words with fuzzy-matched spans
    modified_words = []
    for word in words:
        match = find_best_match(word)
        if match:
            topic = keyword_to_topic[match]
            found_topics.add(topic)
            modified_words.append(f'<span class="{topic}">{word}</span>')
        else:
            modified_words.append(word)
    
    # Reconstruct the post
    for original, modified in zip(words, modified_words):
        post = post.replace(original, modified, 1)
    
    return list(found_topics), post