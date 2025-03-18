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

def tag_post_body(tweet_html: str):
    """Tag keywords in an HTML tweet body and return detected topics."""
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
    
    found_topics = set()
    
    def replace_keywords(text):
        """Replace keywords in text using Aho-Corasick & fuzzy matching."""
        matches = []
        for end_index, matched_keyword in automaton.iter(text.lower()):
            start_index = end_index - len(matched_keyword) + 1
            matches.append((start_index, end_index, matched_keyword))

        # Sort matches to prevent overlapping replacements
        matches.sort(key=lambda x: x[0])
        
        result_text = []
        last_end = 0

        for start, end, matched_keyword in matches:
            result = process.extractOne(matched_keyword, all_keywords, scorer=fuzz.token_sort_ratio)

            if result:  # Ensure a valid match exists
                best_match, score, _ = result
                if score > 85:
                    topic = keywords_to_topics[best_match]
                    found_topics.add(topic)
                    result_text.append(f'<span class="{topic}">{text[start:end+1]}</span>')
                else:
                    result_text.append(text[start:end+1])  # No match, keep original
            else:
                result_text.append(text[start:end+1])  # No match, keep original

            last_end = end + 1

        # Append remaining text
        result_text.append(text[last_end:])
        return "".join(result_text)

    # Modify only text nodes
    for element in soup.find_all(text=True, recursive=True):
        if element.parent.name not in ['script', 'style', 'a', 'img']:  # Skip unwanted elements
            new_text = replace_keywords(element)
            element.replace_with(BeautifulSoup(new_text, "html.parser"))

    return list(found_topics), str(soup)
