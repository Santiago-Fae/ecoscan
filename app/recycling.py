"""Knowledge base: materials, bin colors and drop-off guidance (English and Portuguese).

Bin colors follow the color code of Brazil's CONAMA Resolution 275 (blue = paper, red = plastic,
green = glass, yellow = metal...). Adapt them to your region if needed.
"""
from urllib.parse import quote_plus

# Language-independent data (key, icon, color, recyclable) plus one text block per language.
MATERIALS = {
    "plastic": {
        "icon": "🧴", "hex": "#e53935", "recyclable": True,
        "text": {
            "en": {
                "name": "Plastic",
                "bin_color": "Red",
                "how_to": "Empty it, give it a quick rinse and flatten it to save space. Caps can go along with it.",
                "drop_off": ["Red selective-collection bin", "Recycling center", "Waste-picker cooperative"],
                "search": "recycling center plastic",
            },
            "pt": {
                "name": "Plástico",
                "bin_color": "Vermelho",
                "how_to": "Esvazie, enxágue rapidamente e amasse para ocupar menos espaço. Tampas podem ir junto.",
                "drop_off": ["Lixeira vermelha da coleta seletiva", "Ecoponto", "Cooperativa de catadores"],
                "search": "ecoponto reciclagem plástico",
            },
        },
    },
    "glass": {
        "icon": "🍾", "hex": "#43a047", "recyclable": True,
        "text": {
            "en": {
                "name": "Glass",
                "bin_color": "Green",
                "how_to": "Rinse it and drop it off whole. If it is broken, wrap it in newspaper and label it to prevent cuts.",
                "drop_off": ["Green selective-collection bin", "Recycling center", "Glass bring-bank"],
                "search": "glass recycling drop-off",
            },
            "pt": {
                "name": "Vidro",
                "bin_color": "Verde",
                "how_to": "Enxágue e descarte inteiro. Se estiver quebrado, embrulhe em jornal e identifique para evitar cortes.",
                "drop_off": ["Lixeira verde da coleta seletiva", "Ecoponto", "Pontos de entrega de vidro (PEV)"],
                "search": "ecoponto reciclagem vidro",
            },
        },
    },
    "metal": {
        "icon": "🥫", "hex": "#fbc02d", "recyclable": True,
        "text": {
            "en": {
                "name": "Metal",
                "bin_color": "Yellow",
                "how_to": "Wash cans and packaging and crush them when possible. Do not discard full aerosol cans.",
                "drop_off": ["Yellow selective-collection bin", "Recycling center", "Scrap metal yard"],
                "search": "scrap metal recycling",
            },
            "pt": {
                "name": "Metal",
                "bin_color": "Amarelo",
                "how_to": "Lave latas e embalagens e amasse quando possível. Evite descartar aerossóis cheios.",
                "drop_off": ["Lixeira amarela da coleta seletiva", "Ecoponto", "Ferro-velho / sucata"],
                "search": "ferro velho sucata reciclagem metal",
            },
        },
    },
    "paper": {
        "icon": "📦", "hex": "#1e88e5", "recyclable": True,
        "text": {
            "en": {
                "name": "Paper / Cardboard",
                "bin_color": "Blue",
                "how_to": "Keep it dry and clean. Flatten boxes. Greasy or wet paper is not recyclable.",
                "drop_off": ["Blue selective-collection bin", "Recycling center", "Waste-picker cooperative"],
                "search": "paper cardboard recycling",
            },
            "pt": {
                "name": "Papel / Papelão",
                "bin_color": "Azul",
                "how_to": "Mantenha seco e limpo. Desmonte as caixas. Papel engordurado ou molhado não é reciclável.",
                "drop_off": ["Lixeira azul da coleta seletiva", "Ecoponto", "Cooperativa de catadores"],
                "search": "ecoponto reciclagem papel papelão",
            },
        },
    },
    "electronic": {
        "icon": "💻", "hex": "#fb8c00", "recyclable": True,
        "text": {
            "en": {
                "name": "Electronic",
                "bin_color": "Orange (hazardous waste)",
                "how_to": "Never put it in regular trash: it contains heavy metals. Remove batteries first.",
                "drop_off": [
                    "Take-back points (stores and manufacturers)",
                    "Recycling center that accepts e-waste",
                    "Municipal e-waste collection drives",
                ],
                "search": "electronic waste drop-off",
            },
            "pt": {
                "name": "Eletrônico",
                "bin_color": "Laranja (resíduo perigoso)",
                "how_to": "Não jogue no lixo comum: contém metais pesados. Retire pilhas e baterias antes.",
                "drop_off": [
                    "Pontos de logística reversa (lojas e fabricantes)",
                    "Ecoponto com coleta de eletrônicos",
                    "Campanhas municipais de lixo eletrônico",
                ],
                "search": "descarte lixo eletrônico ponto de coleta",
            },
        },
    },
    "organic": {
        "icon": "🍌", "hex": "#6d4c41", "recyclable": True,
        "text": {
            "en": {
                "name": "Organic",
                "bin_color": "Brown",
                "how_to": "It can become fertilizer through composting. Otherwise use the organic-waste bin.",
                "drop_off": ["Home or community composter", "Brown bin / organic waste collection"],
                "search": "composting drop-off",
            },
            "pt": {
                "name": "Orgânico",
                "bin_color": "Marrom",
                "how_to": "Pode virar adubo por compostagem. Na coleta comum, use a lixeira de orgânicos.",
                "drop_off": ["Composteira doméstica ou comunitária", "Lixeira marrom / coleta de orgânicos"],
                "search": "compostagem ponto de coleta orgânico",
            },
        },
    },
    "ceramic": {
        "icon": "🍽️", "hex": "#757575", "recyclable": False,
        "text": {
            "en": {
                "name": "Ceramic / Porcelain",
                "bin_color": "Gray (non-recyclable)",
                "how_to": "It cannot be recycled with glass (different melting point). Wrap it if broken. If it is intact, consider donating it.",
                "drop_off": ["Regular trash (non-recyclable)", "Donation, if in good condition"],
                "search": "bulky waste drop-off ceramics",
            },
            "pt": {
                "name": "Cerâmica / Porcelana",
                "bin_color": "Cinza (rejeito)",
                "how_to": "Não é reciclável junto com vidro (outro ponto de fusão). Embrulhe se estiver quebrado. Se estiver inteiro, considere doar.",
                "drop_off": ["Lixo comum (rejeito)", "Doação, se estiver em bom estado"],
                "search": "ecoponto entulho descarte cerâmica",
            },
        },
    },
}

# English descriptions (CLIP understands them best) used for zero-shot material classification.
# Several phrases per material are scored independently and their probabilities are summed.
# These are internal model prompts and are NOT translated.
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


def _flatten(key: str, lang: str) -> dict:
    data = MATERIALS[key]
    text = data["text"][lang]
    return {
        "key": key,
        "icon": data["icon"],
        "hex": data["hex"],
        "recyclable": data["recyclable"],
        "name": text["name"],
        "bin_color": text["bin_color"],
        "how_to": text["how_to"],
        "drop_off": text["drop_off"],
    }


def material_info(key: str, city: str | None = None, lang: str = "en") -> dict:
    """Full material description in `lang`, with a map search link (optionally for `city`)."""
    info = _flatten(key, lang)
    term = MATERIALS[key]["text"][lang]["search"]
    if city:
        term += f" {city}"
    info["map_url"] = "https://www.google.com/maps/search/" + quote_plus(term)
    return info


def localized_materials(lang: str = "en") -> dict:
    """All materials in `lang` (without map links), e.g. for the bin-color legend."""
    return {key: _flatten(key, lang) for key in MATERIALS}
