"""
File parsing utilities for Canon Ledger.
Supports .txt, .md, and .docx formats with zero external binary dependencies.
"""

import io
import re
import zipfile
import xml.etree.ElementTree as ET
from typing import Tuple, List

XML_NAMESPACES = {
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
}

def parse_docx(file_bytes: bytes) -> str:
    """
    Extracts text paragraphs from a .docx file without requiring external libraries.
    """
    paragraphs = []
    with zipfile.ZipFile(io.BytesIO(file_bytes)) as z:
        if 'word/document.xml' not in z.namelist():
            raise ValueError("Invalid DOCX file: word/document.xml not found")
        xml_content = z.read('word/document.xml')
        root = ET.fromstring(xml_content)
        
        # In docx, w:p represents a paragraph, w:t represents text runs
        for p in root.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
            runs = []
            for t in p.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'):
                if t.text:
                    runs.append(t.text)
            p_text = "".join(runs).strip()
            if p_text:
                paragraphs.append(p_text)
                
    return "\n\n".join(paragraphs)

def parse_manuscript_file(filename: str, file_bytes: bytes) -> Tuple[str, str]:
    """
    Parses an uploaded chapter file (TXT, MD, or DOCX).
    Returns (suggested_title, raw_text).
    """
    ext = filename.lower().split('.')[-1] if '.' in filename else ''
    
    if ext == 'docx':
        text = parse_docx(file_bytes)
    else:
        # Try UTF-8 first, fallback to latin-1 / cp1252
        try:
            text = file_bytes.decode('utf-8')
        except UnicodeDecodeError:
            try:
                text = file_bytes.decode('utf-8-sig')
            except UnicodeDecodeError:
                text = file_bytes.decode('latin-1', errors='replace')
                
    # Normalize line endings
    text = text.replace('\r\n', '\n').replace('\r', '\n').strip()
    
    # Try to extract a title from the first line or heading if present
    suggested_title = filename
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    if lines:
        first_line = lines[0]
        # Clean markdown heading markers # or Chapter
        cleaned_first = re.sub(r'^[#\s*_-]+', '', first_line).strip()
        if cleaned_first and len(cleaned_first) <= 80:
            suggested_title = cleaned_first
            
    return suggested_title, text

# Known abbreviations that do not terminate a sentence
ABBREVIATIONS = {'dr', 'mr', 'mrs', 'ms', 'capt', 'st', 'jr', 'sr', 'prof', 'col', 'gen', 'rep', 'sen'}

def split_into_sentences(text: str) -> List[dict]:
    """
    Accurately splits chapter text into numbered sentences while preserving paragraph context.
    Correctly handles:
    - Honorifics/abbreviations (Dr., Mr., etc.)
    - Dialogue quotes with attribution tags ("Stop!" he yelled.)
    """
    sentences = []
    paragraphs = text.split('\n\n')
    sentence_counter = 1
    
    for p_idx, para in enumerate(paragraphs, start=1):
        # Strip raw markdown heading syntax e.g. # Chapter 1 -> Chapter 1
        para_clean = re.sub(r'^#{1,6}\s+', '', para.strip()).strip()
        if not para_clean:
            continue
            
        # Tokenize by scanning character by character or regex with boundary validation
        pos = 0
        para_len = len(para_clean)
        sent_start = 0
        
        while pos < para_len:
            char = para_clean[pos]
            if char in '.!?':
                # Check if preceded by an abbreviation
                word_before = para_clean[sent_start:pos].split()[-1] if para_clean[sent_start:pos].split() else ""
                clean_wb = re.sub(r'[^a-zA-Z]', '', word_before).lower()
                if clean_wb in ABBREVIATIONS:
                    pos += 1
                    continue
                    
                # Peek ahead for closing quotes or parens
                next_pos = pos + 1
                while next_pos < para_len and para_clean[next_pos] in '"\'\u201d\u2019)':
                    next_pos += 1
                    
                # Peek ahead past spaces
                peek_space = next_pos
                while peek_space < para_len and para_clean[peek_space].isspace():
                    peek_space += 1
                    
                # If next non-space word starts with lowercase, it is dialogue tag (e.g. "Stop!" he yelled)
                if peek_space < para_len and para_clean[peek_space].islower():
                    # Not a sentence end yet
                    pos = peek_space
                    continue
                    
                # If peek_space is at end of para or followed by uppercase/quote/number, it's a true sentence end
                if peek_space >= para_len or para_clean[peek_space].isupper() or para_clean[peek_space] in '"\'\u201c\u20180123456789':
                    s_text = para_clean[sent_start:next_pos].strip()
                    if s_text:
                        sentences.append({
                            'sentence_num': sentence_counter,
                            'text': s_text,
                            'paragraph_num': p_idx
                        })
                        sentence_counter += 1
                    sent_start = peek_space
                    pos = peek_space
                    continue
            pos += 1
            
        # Leftover text in paragraph
        if sent_start < para_len:
            leftover = para_clean[sent_start:].strip()
            if leftover:
                sentences.append({
                    'sentence_num': sentence_counter,
                    'text': leftover,
                    'paragraph_num': p_idx
                })
                sentence_counter += 1
                
    return sentences
