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
