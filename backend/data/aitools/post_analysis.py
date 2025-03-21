import re
import unidecode
from bs4 import BeautifulSoup
from rapidfuzz import process, fuzz
import ahocorasick
from structs.data import TrendStruct

def normalize_word(word: str) -> str:
    """
    Normalize words by removing accents and reducing repeated letters.

    Args:
        word (str): The word to normalize.
    
    Returns:
        str: The normalized word in lowercase.
    """
    word = unidecode.unidecode(word)  # Remove accents (e.g., résumé -> resume)
    word = re.sub(r'(\w)\1{2,}', r'\1', word)  # Reduce repeated letters (e.g., Amerikkka -> America)
    return word.lower().strip()

def build_ac_automaton(keywords: set[str]) -> ahocorasick.Automaton:
    """
    Build an Aho-Corasick automaton for efficient multi-word matching.

    Args:
        keywords (set[str]): A set of keywords to be added to the automaton.
    
    Returns:
        ahocorasick.Automaton: The built Aho-Corasick automaton for fast keyword matching.
    """
    automaton = ahocorasick.Automaton()
    
    # Iterate over each keyword and add it to the Aho-Corasick trie
    for keyword in keywords:
        automaton.add_word(keyword, keyword)  # Add keyword as both key and value for retrieval
    
    # Convert the trie into a functional Aho-Corasick automaton for fast lookup
    automaton.make_automaton()
    
    return automaton

def extract_instances(tweet_html: str) -> dict[str, list[str]]:
    """
    Extracts topics from an HTML tweet body by detecting matching words.

    Args:
        tweet_html (str): The HTML content of the tweet.
    
    Returns:
        dict[str, list[str]]: A dictionary mapping detected topics to lists of matched words.
    """
    topics = TrendStruct.load_all_with_kw()  # Load all known topics and their associated keywords

    # Parse HTML and extract text content
    soup = BeautifulSoup(tweet_html, "html.parser")
    text_content = soup.get_text(separator=" ")  # Get plain text with proper spacing

    keywords_to_topics = {}  # Mapping of normalized keywords to their respective topics
    all_keywords = set()

    # Normalize and store all keywords from topics
    for topic, keywords in topics.items():
        for keyword in keywords:
            # Normalize keyword (remove accents, repeated letters, etc.)
            normalized_keyword = normalize_word(keyword)
            # Map normalized keyword to its topic  
            keywords_to_topics[normalized_keyword] = topic  
            # Store normalized keyword in the set
            all_keywords.add(normalized_keyword)  

    # Build Aho-Corasick automaton for fast keyword searching in text
    automaton = build_ac_automaton(all_keywords)
    
    found_topics = {}  # Store detected topics and matched keywords
    
    # Iterate over the text content and find matches using Aho-Corasick automaton
    for end_index, matched_keyword in automaton.iter(text_content.lower()):
        # Find the best fuzzy match for the detected keyword
        best_match, score, _ = process.extractOne(
                                    matched_keyword,
                                    all_keywords,
                                    scorer = fuzz.token_sort_ratio)
        
        # If the match is strong (score > 85), associate it with its topic
        if best_match and score > 85:
            # Retrieve the topic associated with the matched keyword
            topic = keywords_to_topics[best_match]  
            # Store the matched keyword under the topic
            found_topics.setdefault(topic, []).append(matched_keyword)  

    return found_topics
