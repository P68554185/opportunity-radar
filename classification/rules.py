import re
PROJECT_RULES=[
 ("school",r"(schule|gymnasium|realschule|mittelschule|grundschule|schulzentrum|sporthalle)"),
 ("kindergarten",r"(kita|kindergarten|kindertageseinrichtung|kinderhaus|kinderkrippe|hort)"),
 ("hospital",r"(klinikum|krankenhaus|klinik)"),
 ("fire_station",r"(feuerwehrhaus|feuerwache|feuerwehrgerätehaus)"),
]
TRADE_RULES=[
 ("electrical",r"(elektro|elektrotechnik|starkstrom|schwachstrom|beleuchtung)"),
 ("hvac",r"(heizung|lüftung|sanitär|hls|tga|wärmepumpe)"),
 ("drywall",r"(trockenbau|gipskarton)"),("painting",r"(maler|anstrich|beschichtung)"),
 ("flooring",r"(bodenbelag|bodenleger|parkett|estrich)"),("roof",r"(dach|dachdecker|spengler)"),
 ("windows_doors",r"(fenster|türen|tore)"),("facade",r"(fassade|wärmedämmverbundsystem|wdvs)"),
 ("earthworks",r"(erdarbeiten|tiefbau|baugrube)"),("structural",r"(rohbau|beton|mauerwerk|stahlbeton)"),
 ("landscaping",r"(außenanlagen|landschaftsbau|galabau)"),("fire_protection",r"(brandschutz|sprinkler)")
]
def classify(text):
    t=(text or "").lower()
    project=next((x for x,p in PROJECT_RULES if re.search(p,t)),"")
    trades=[x for x,p in TRADE_RULES if re.search(p,t)]
    return project,trades
