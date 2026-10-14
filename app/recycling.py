"""Knowledge base: materials, bin colors and drop-off guidance.

Bin colors follow the color code of Brazil's CONAMA Resolution 275 (blue = paper, red = plastic,
green = glass, yellow = metal...). Adapt them to your region if needed.
"""
from urllib.parse import quote_plus

MATERIALS = {
    "plastic": {
        "name": "Plastic",
        "icon": "🧴",
        "bin_color": "Red",
        "hex": "#e53935",
        "recyclable": True,
        "how_to": "Empty it, give it a quick rinse and flatten it to save space. Caps can go along with it.",
        "drop_off": ["Red selective-collection bin", "Recycling center", "Waste-picker cooperative"],
        "search": "recycling center plastic",
    },
    "glass": {
        "name": "Glass",
        "icon": "🍾",
        "bin_color": "Green",
        "hex": "#43a047",
        "recyclable": True,
        "how_to": "Rinse it and drop it off whole. If it is broken, wrap it in newspaper and label it to prevent cuts.",
        "drop_off": ["Green selective-collection bin", "Recycling center", "Glass bring-bank"],
        "search": "glass recycling drop-off",
    },
    "metal": {
        "name": "Metal",
        "icon": "🥫",
        "bin_color": "Yellow",
        "hex": "#fbc02d",
        "recyclable": True,
        "how_to": "Wash cans and packaging and crush them when possible. Do not discard full aerosol cans.",
        "drop_off": ["Yellow selective-collection bin", "Recycling center", "Scrap metal yard"],
        "search": "scrap metal recycling",
    },
    "paper": {
        "name": "Paper / Cardboard",
        "icon": "📦",
        "bin_color": "Blue",
        "hex": "#1e88e5",
        "recyclable": True,
        "how_to": "Keep it dry and clean. Flatten boxes. Greasy or wet paper is not recyclable.",
        "drop_off": ["Blue selective-collection bin", "Recycling center", "Waste-picker cooperative"],
        "search": "paper cardboard recycling",
    },
    "electronic": {
        "name": "Electronic",
        "icon": "💻",
        "bin_color": "Orange (hazardous waste)",
        "hex": "#fb8c00",
        "recyclable": True,
        "how_to": "Never put it in regular trash: it contains heavy metals. Remove batteries first.",
        "drop_off": [
            "Take-back points (stores and manufacturers)",
            "Recycling center that accepts e-waste",
            "Municipal e-waste collection drives",
        ],
        "search": "electronic waste drop-off",
    },
    "organic": {
        "name": "Organic",
        "icon": "🍌",
        "bin_color": "Brown",
        "hex": "#6d4c41",
        "recyclable": True,
        "how_to": "It can become fertilizer through composting. Otherwise use the organic-waste bin.",
        "drop_off": ["Home or community composter", "Brown bin / organic waste collection"],
        "search": "composting drop-off",
    },
    "ceramic": {
        "name": "Ceramic / Porcelain",
        "icon": "🍽️",
        "bin_color": "Gray (non-recyclable)",
        "hex": "#757575",
        "recyclable": False,
        "how_to": "It cannot be recycled with glass (different melting point). Wrap it if broken. If it is intact, consider donating it.",
        "drop_off": ["Regular trash (non-recyclable)", "Donation, if in good condition"],
        "search": "bulky waste drop-off ceramics",
    },
}

# English descriptions (CLIP understands them best) used for zero-shot material classification.
# Several phrases per material are scored independently and their probabilities are summed.
PROMPTS = {
    "plastic": ["a plastic bottle", "a plastic container", "a plastic bag", "a plastic cup", "a plastic packaging"],
    "glass": ["a glass bottle", "a glass jar", "a drinking glass", "a piece of glass"],
    "metal": ["an aluminum can", "a metal can", "a tin can", "a metal object", "a metal fork or spoon"],
    "paper": ["paper", "a newspaper", "a cardboard box", "a sheet of paper", "a paper bag", "a book"],
    "electronic": ["an electronic device", "a laptop", "a mobile phone", "a computer keyboard", "an electronic circuit board"],
    "organic": ["fruit", "vegetables", "food waste", "a banana peel", "leftover food"],
    "ceramic": ["a ceramic plate", "a porcelain mug", "a ceramic bowl", "a clay pot"],
}
# Negative labels: help reject crops that are not waste (people, scenery...).
NEGATIVE_PROMPTS = ["a person", "an animal", "a building", "a landscape", "a car", "furniture", "a plant", "clothing"]

# COCO classes that can plausibly be waste. Only these YOLO crops are sent to CLIP;
# everything else (skateboard, people...) is ignored and falls back to whole-image analysis.
CONSIDER_COCO = {
    "bottle", "wine glass", "cup", "fork", "knife", "spoon", "bowl", "vase", "scissors", "toothbrush",
    "book", "cell phone", "laptop", "keyboard", "mouse", "remote", "tv", "microwave", "toaster", "hair drier",
    "banana", "apple", "orange", "broccoli", "carrot", "sandwich", "hot dog", "pizza", "donut", "cake",
    "handbag", "backpack", "suitcase", "umbrella", "frisbee",
}


def material_info(key: str, city: str | None = None) -> dict:
    info = dict(MATERIALS[key])
    term = info.pop("search")
    if city:
        term += f" {city}"
    info["map_url"] = "https://www.google.com/maps/search/" + quote_plus(term)
    info["key"] = key
    return info
