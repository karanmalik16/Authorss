"""
REA (Reverse Engineering Anything) Forensic Verification Helper.
Integrates REA static analysis and entropy verification into Canon Ledger.
"""

import math
from typing import Dict, Any

def calculate_shannon_entropy(data: bytes) -> float:
    """
    Computes Shannon byte entropy in bits per byte (0.0 to 8.0).
    Natural English text typically falls between 4.0 and 4.8.
    Encrypted/compressed files approach 8.0. Repetitive data approaches 0.0.
    """
    if not data:
        return 0.0
    freq = {}
    for b in data:
        freq[b] = freq.get(b, 0) + 1
    total = len(data)
    entropy = -sum((count / total) * math.log2(count / total) for count in freq.values())
    return round(entropy, 4)

def verify_manuscript_integrity(raw_text: str) -> Dict[str, Any]:
    """
    Evaluates manuscript text naturalness and integrity using Shannon entropy.
    Matches REA's inspect_byte_entropy standard.
    """
    data = raw_text.encode('utf-8')
    entropy = calculate_shannon_entropy(data)
    
    # Classify text nature
    is_natural_prose = 3.5 <= entropy <= 5.2
    
    return {
        'byte_length': len(data),
        'shannon_entropy': entropy,
        'is_natural_prose': is_natural_prose,
        'classification': 'Natural Prose Manuscript' if is_natural_prose else 'Anomalous / Encrypted / Machine Pattern'
    }
