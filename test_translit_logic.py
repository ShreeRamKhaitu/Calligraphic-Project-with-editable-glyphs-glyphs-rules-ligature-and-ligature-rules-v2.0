import data_gen
import sys

# Ensure UTF-8 output for Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

def translit_to_deva(text):
    CONSONANTS = data_gen.CONSONANTS
    VOWELS = data_gen.VOWELS
    MATRAS = data_gen.MATRAS

    translit_map = {**CONSONANTS, **VOWELS}
    matra_map = MATRAS
    
    keys = sorted(translit_map.keys(), key=len, reverse=True)
    vowel_keys = sorted(VOWELS.keys(), key=len, reverse=True)
    
    converted = ""
    i = 0
    last_was_consonant = False
    
    while i < len(text):
        match = False
        if last_was_consonant:
            for vk in vowel_keys:
                if text[i:i+len(vk)] == vk:
                    converted += matra_map.get(vk, VOWELS[vk])
                    i += len(vk)
                    match = True
                    last_was_consonant = False
                    break
        
        if not match:
            for k in keys:
                if text[i:i+len(k)] == k:
                    converted += translit_map[k]
                    i += len(k)
                    match = True
                    last_was_consonant = (k in CONSONANTS and k != '*')
                    break
        
        if not match:
            converted += text[i]
            i += 1
            last_was_consonant = False
    return converted

test_cases = [
    ("nmS*kar", "नमस्कर"),
    ("nmS*kaar", "नमस्कार"),
    ("namaskar", "नमशकर"),
    ("namaaskaar", "नमाशकार"),
    ("ki", "कि"),
    ("ik", "इक"),
    ("nepaal", "नेपाल"),
    ("shree", "षरेए")
]

for inp, expected in test_cases:
    result = translit_to_deva(inp)
    print(f"Input: {inp} | Result: {result} | Expected: {expected} | {'PASS' if result == expected else 'FAIL'}")
