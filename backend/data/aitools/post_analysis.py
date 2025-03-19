import re
import unidecode
from bs4 import BeautifulSoup
from rapidfuzz import process, fuzz
import ahocorasick
from structs.data import TrendStruct

def normalize_word(word: str) -> str:
    """Normalize words by reducing repeated letters and handling accents."""
    word = unidecode.unidecode(word)  # Remove accents (e.g., résumé -> resume)
    word = re.sub(r'(\w)\1{2,}', r'\1', word)  # Reduce repeated letters (e.g., Amerikkka -> America)
    return word.lower().strip()

def build_ac_automaton(keywords):
    """Build an Aho-Corasick automaton for efficient multi-word matching."""
    automaton = ahocorasick.Automaton()
    for keyword in keywords:
        automaton.add_word(keyword, keyword)
    automaton.make_automaton()
    return automaton

def extract_instances(tweet_html: str) -> dict[str, list[str]]:
    """Extract topics from an HTML tweet body and return detected topics with matched words."""
    topics = TrendStruct.load_all_with_kw()

    soup = BeautifulSoup(tweet_html, "html.parser")
    text_content = soup.get_text(separator=" ")  # Get plain text with proper spacing

    keywords_to_topics = {}
    all_keywords = set()

    for topic, keywords in topics.items():
        for keyword in keywords:
            normalized_keyword = normalize_word(keyword)
            keywords_to_topics[normalized_keyword] = topic
            all_keywords.add(normalized_keyword)

    # Build Aho-Corasick automaton for fast keyword search
    automaton = build_ac_automaton(all_keywords)
    
    found_topics = {}
    
    for end_index, matched_keyword in automaton.iter(text_content.lower()):
        best_match, score, _ = process.extractOne(matched_keyword, all_keywords, scorer=fuzz.token_sort_ratio)
        if best_match and score > 85:
            topic = keywords_to_topics[best_match]
            found_topics.setdefault(topic, []).append(matched_keyword)
    
    return found_topics
