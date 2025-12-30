# Constants for Length-Weight Relationship: W = a * L^b
# W in grams, L in cm
# Data approximates common fish found in Korean markets.

FISH_LWR_CONSTANTS = {
    "scomber japonicus": {"a": 0.005, "b": 3.15}, # Mackerel (고등어)
    "scomber scombrus": {"a": 0.005, "b": 3.15}, # Mackerel
    "paralichthys olivaceus": {"a": 0.007, "b": 3.05}, # Olive Flounder (광어/넙치)
    "pagrus major": {"a": 0.015, "b": 2.95}, # Red Seabream (참돔)
    "trichiurus lepturus": {"a": 0.0005, "b": 3.4}, # Largehead Hairtail (갈치) - very long and thin
    "engraulis japonicus": {"a": 0.006, "b": 3.0}, # Japanese Anchovy (멸치)
    "clupea pallasii": {"a": 0.009, "b": 3.1}, # Pacific Herring (청어)
    "gadus macrocephalus": {"a": 0.008, "b": 3.05}, # Pacific Cod (대구)
    "theragra chalcogramma": {"a": 0.006, "b": 3.0}, # Alaska Pollock (명태)
    "sebastes schlegelii": {"a": 0.012, "b": 3.0}, # Korean Rockfish (조피볼락/우럭)
    "konosirus punctatus": {"a": 0.01, "b": 3.0}, # Gizzard Shad (전어)
    "seriola quinqueradiata": {"a": 0.012, "b": 2.95}, # Japanese Amberjack (방어)
    "lateolabrax japonicus": {"a": 0.010, "b": 3.0}, # Japanese Seabass (농어)
}

# Fillet Yield Rates (Ratio of meat weight to total weight)
# Reference: Average yield from whole fish to skin-on/skin-off fillet
YIELD_CONSTANTS = {
    "광어": 0.48,      # Flounder (High yield)
    "넙치": 0.48,
    "우럭": 0.30,      # Rockfish (Big head)
    "조피볼락": 0.30,
    "참돔": 0.38,      # Red Sea Bream
    "연어": 0.65,      # Salmon (High yield)
    "고등어": 0.50,     # Mackerel
    "전어": 0.45,
    "농어": 0.40,
    "감성돔": 0.35,
    "돌돔": 0.35,
    "방어": 0.45,
    "숭어": 0.40,
    "오징어": 0.60,
    "낙지": 0.85,
    "문어": 0.80,
}

def get_fillet_yield(fish_name: str) -> float:
    """
    Returns the estimated fillet yield rate (0.0 - 1.0) for a given fish name.
    """
    if not fish_name:
        return 0.35
        
    term = fish_name.strip()
    # Direct match
    if term in YIELD_CONSTANTS:
        return YIELD_CONSTANTS[term]
        
    # Partial match
    for key, rate in YIELD_CONSTANTS.items():
        if key in term or term in key:
            return rate
            
    return 0.35 # Default conservative yield

DEFAULT_CONSTANTS = {"a": 0.01, "b": 3.0}

def get_fish_constants(scientific_name: str) -> dict:
    """
    Retrieves LWR constants for a given scientific name (case-insensitive).
    Returns DEFAULT_CONSTANTS if not found.
    """
    if not scientific_name:
        return DEFAULT_CONSTANTS
    
    key = scientific_name.lower().strip()
    return FISH_LWR_CONSTANTS.get(key, DEFAULT_CONSTANTS)

def calculate_weight(scientific_name: str, length_cm: float) -> float:
    """
    Calculates estimated weight in kg using W = a * L^b.
    Output is in kg (the formula uses a*L^b for grams).
    """
    constants = get_fish_constants(scientific_name)
    a = constants["a"]
    b = constants["b"]
    
    weight_grams = a * (length_cm ** b)
    return weight_grams / 1000.0
