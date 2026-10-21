"""Translations for the web UI and API messages (English is the default language)."""
from fastapi import Request

SUPPORTED = ("en", "pt")
DEFAULT = "en"
LANG_NAMES = {"en": "English", "pt": "Português"}
COOKIE = "lang"

STRINGS = {
    "en": {
        # --- shared / navigation
        "nav_why": "Why recycle",
        "nav_colors": "Bin colors",
        "nav_dashboard": "Dashboard",
        "nav_identify": "Identify an item",
        "nav_home": "Home",
        # --- home page
        "page_title": "EcoScan – Recycle the right way",
        "hero_title": "Recycle the right way",
        "hero_text": "Find out what an object is made of and where to drop it off, using open-source AI (YOLO + CLIP).",
        "hero_cta": "Upload a photo",
        "why_title": "Why recycle?",
        "why_1_title": "🌍 Less landfill waste",
        "why_1_text": "Much of what we throw away can go back into the production chain, reducing the volume sent to landfills.",
        "why_2_title": "⚡ Saves resources",
        "why_2_text": "Recycling aluminum, for example, takes far less energy than producing it from ore.",
        "why_3_title": "🤝 Creates income",
        "why_3_text": "The recycling chain supports cooperatives and thousands of waste pickers. Sorting correctly helps them directly.",
        "steps_title": "Sort in 3 steps",
        "step_1": "<b>Clean:</b> rinse packaging, without wasting water.",
        "step_2": "<b>Separate:</b> each material in its own bin or collection point.",
        "step_3": "<b>Drop off:</b> use selective collection, a recycling center or a cooperative.",
        "colors_title": "Selective-collection bin colors",
        "identify_title": "Identify your item",
        "drop_text": "Click or drag an image here",
        "city_placeholder": "Your city (optional, improves the location search)",
        "analyze_btn": "Analyze",
        "footer": "Built with FastAPI, YOLO (Ultralytics) and CLIP. Collection rules vary by municipality: check with your local authority.",
        # --- dashboard page
        "dash_page_title": "EcoScan – Dashboard",
        "dash_title": "Dashboard",
        "dash_subtitle": "What users have identified so far. Statistics only: no photo is ever stored.",
        "bars_title": "Identified materials",
        "empty_text": "No data yet.",
        "empty_link": "Upload the first photo!",
        "quality_title": "Model quality",
        "footer_refresh": "Refreshes every 10 seconds.",
        # --- API errors
        "err_not_image": "Upload an image file (JPG, PNG, WEBP).",
        "err_too_large": "Image is larger than 10 MB.",
        "err_unreadable": "Could not read the image.",
        "err_need_material": "Provide the correct material.",
        "err_conflict": "Detection does not exist or was already rated.",
        # --- JavaScript (app.js / dashboard.js)
        "js_analyzing": "Analyzing image…",
        "js_no_object": "No object identified. Try a closer photo with good lighting.",
        "js_n_found": "{n} material type(s) identified.",
        "js_analysis_failed": "Analysis failed.",
        "js_send_failed": "Failed to send.",
        "js_annotated_alt": "Image with detected objects",
        "js_thanks": "✅ Thank you! Your answer helps improve EcoScan.",
        "js_not_sure": "I'm not sure.",
        "js_which_item": "Which of these is your item?",
        "js_other_material": "Other material…",
        "js_correct_q": "What is the correct material?",
        "js_select": "Select…",
        "js_is_right": "Is this answer right?",
        "js_yes": "👍 Yes",
        "js_no": "👎 No",
        "js_low_conf": "low confidence",
        "js_provided_by_you": "provided by you",
        "js_confidence": "confidence {n}%",
        "js_whole_image": "whole image",
        "js_recyclable": "Recyclable",
        "js_not_recyclable": "Not recyclable",
        "js_how_to": "How to prepare it:",
        "js_where": "Where to drop it off:",
        "js_map_btn": "📍 Find nearby locations on the map",
        "js_photos": ["photo analyzed", "photos analyzed"],
        "js_materials": ["material identified", "materials identified"],
        "js_accuracy": "accuracy (as rated by users)",
        "js_asked_help": "times the model asked for help",
        "js_ratings": "{answered} ratings: {correct} correct and {corrected} corrected by users.",
        "js_no_ratings": "No user ratings yet.",
        "js_mistakes": "Most common mistakes",
        "js_model_said": "The model said <b>{predicted}</b>, but it was <b>{actual}</b> ({n}×)",
    },
    "pt": {
        "nav_why": "Por que reciclar",
        "nav_colors": "Cores da coleta",
        "nav_dashboard": "Dashboard",
        "nav_identify": "Identificar objeto",
        "nav_home": "Início",
        "page_title": "EcoScan – Recicle do jeito certo",
        "hero_title": "Recicle do jeito certo",
        "hero_text": "Descubra de que material é um objeto e onde descartá-lo, usando inteligência artificial open source (YOLO + CLIP).",
        "hero_cta": "Enviar uma foto",
        "why_title": "Por que reciclar?",
        "why_1_title": "🌍 Menos lixo em aterros",
        "why_1_text": "Boa parte do que descartamos pode voltar à cadeia produtiva, reduzindo o volume enviado a aterros.",
        "why_2_title": "⚡ Economia de recursos",
        "why_2_text": "Reciclar alumínio, por exemplo, gasta muito menos energia do que produzi-lo a partir do minério.",
        "why_3_title": "🤝 Gera renda",
        "why_3_text": "A cadeia da reciclagem sustenta cooperativas e milhares de catadores. Separar corretamente ajuda diretamente.",
        "steps_title": "Como separar em 3 passos",
        "step_1": "<b>Limpe:</b> enxágue embalagens, sem desperdiçar água.",
        "step_2": "<b>Separe:</b> cada material na sua lixeira ou ponto de coleta.",
        "step_3": "<b>Entregue:</b> use a coleta seletiva, um ecoponto ou uma cooperativa.",
        "colors_title": "Cores da coleta seletiva",
        "identify_title": "Identifique seu objeto",
        "drop_text": "Clique ou arraste uma imagem aqui",
        "city_placeholder": "Sua cidade (opcional, melhora a busca de locais)",
        "analyze_btn": "Analisar",
        "footer": "Feito com FastAPI, YOLO (Ultralytics) e CLIP. As regras de coleta variam por município: confirme com a prefeitura.",
        "dash_page_title": "EcoScan – Dashboard",
        "dash_title": "Dashboard",
        "dash_subtitle": "O que os usuários já identificaram. Só estatísticas: nenhuma foto é armazenada.",
        "bars_title": "Materiais identificados",
        "empty_text": "Ainda não há dados.",
        "empty_link": "Envie a primeira foto!",
        "quality_title": "Qualidade do modelo",
        "footer_refresh": "Atualiza a cada 10 segundos.",
        "err_not_image": "Envie um arquivo de imagem (JPG, PNG, WEBP).",
        "err_too_large": "Imagem maior que 10 MB.",
        "err_unreadable": "Não foi possível ler a imagem.",
        "err_need_material": "Informe o material correto.",
        "err_conflict": "Detecção inexistente ou já avaliada.",
        "js_analyzing": "Analisando imagem…",
        "js_no_object": "Nenhum objeto identificado. Tente uma foto mais próxima e com boa iluminação.",
        "js_n_found": "{n} tipo(s) de material identificado(s).",
        "js_analysis_failed": "Falha na análise.",
        "js_send_failed": "Falha ao enviar.",
        "js_annotated_alt": "Imagem com objetos detectados",
        "js_thanks": "✅ Obrigado! Sua resposta ajuda a melhorar o EcoScan.",
        "js_not_sure": "Não tenho certeza.",
        "js_which_item": "Qual destes é o seu objeto?",
        "js_other_material": "Outro material…",
        "js_correct_q": "Qual é o material correto?",
        "js_select": "Selecione…",
        "js_is_right": "Essa resposta está certa?",
        "js_yes": "👍 Sim",
        "js_no": "👎 Não",
        "js_low_conf": "confiança baixa",
        "js_provided_by_you": "informado por você",
        "js_confidence": "confiança {n}%",
        "js_whole_image": "imagem inteira",
        "js_recyclable": "Reciclável",
        "js_not_recyclable": "Não reciclável",
        "js_how_to": "Como preparar:",
        "js_where": "Onde descartar:",
        "js_map_btn": "📍 Ver locais próximos no mapa",
        "js_photos": ["foto analisada", "fotos analisadas"],
        "js_materials": ["material identificado", "materiais identificados"],
        "js_accuracy": "de acerto (segundo os usuários)",
        "js_asked_help": "vezes em que o modelo pediu ajuda",
        "js_ratings": "{answered} avaliações: {correct} corretas e {corrected} corrigidas pelos usuários.",
        "js_no_ratings": "Ainda não há avaliações dos usuários.",
        "js_mistakes": "Erros mais comuns",
        "js_model_said": "O modelo disse <b>{predicted}</b>, mas era <b>{actual}</b> ({n}×)",
    },
}


def normalize(lang: str | None) -> str | None:
    """Return a supported language code, or None if `lang` is empty/unsupported."""
    code = (lang or "").strip().lower()[:2]
    return code if code in SUPPORTED else None


def resolve_lang(request: Request, explicit: str | None = None) -> str:
    """Priority: explicit value (form/body) > ?lang= > cookie > default (English)."""
    return (
        normalize(explicit)
        or normalize(request.query_params.get("lang"))
        or normalize(request.cookies.get(COOKIE))
        or DEFAULT
    )


def t(lang: str, key: str, **kwargs) -> str:
    text = STRINGS[lang][key]
    return text.format(**kwargs) if kwargs else text


def js_strings(lang: str) -> dict:
    """The subset of strings needed by the browser scripts."""
    return {k[3:]: v for k, v in STRINGS[lang].items() if k.startswith("js_")}
