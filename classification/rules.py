"""Broad deterministic construction classification for Opportunity Radar v0.8.0."""
import re

PROJECT_RULES = [
 ("school", r"(schule|schulzentrum|gymnasium|realschule|mittelschule|grundschule|berufsschule|campus|sporthalle)"),
 ("kindergarten", r"(kita|kindergarten|kindertageseinrichtung|kinderhaus|kinderkrippe|hort)"),
 ("hospital", r"(klinikum|krankenhaus|klinik|medizinzentrum|operationssaal|pflegezentrum)"),
 ("fire_station", r"(feuerwehrhaus|feuerwache|feuerwehrgerätehaus|rettungswache)"),
 ("residential", r"(wohnungsbau|wohngebäude|wohnanlage|wohnheim|mehrfamilienhaus|sozialwohnungen|wohnungen)"),
 ("administration", r"(rathaus|verwaltungsgebäude|landratsamt|bürgerzentrum|dienstgebäude|justizgebäude|polizei)"),
 ("industrial", r"(industriehalle|produktionshalle|gewerbehalle|lagerhalle|werkstatt|betriebsgebäude|logistikzentrum)"),
 ("sports_leisure", r"(sporthalle|turnhalle|stadion|schwimmbad|hallenbad|freibad|sportanlage|freizeitanlage)"),
 ("university_research", r"(universität|hochschule|forschungsgebäude|laborgebäude|institutsgebäude|campus)"),
 ("care_social", r"(pflegeheim|seniorenheim|altenheim|sozialzentrum|jugendzentrum|wohnheim)"),
 ("road", r"(straßenbau|fahrbahnerneuerung|bundesstraße|staatsstraße|kreisstraße|ortsstraße|verkehrsanlage)"),
 ("bridge", r"(brücke|brückenbau|überführung|unterführung|viadukt)"),
 ("rail", r"(bahnhof|bahnsteig|gleis|eisenbahn|schienen|stellwerk|bahnanlage)"),
 ("water_wastewater", r"(kläranlage|kanalbau|abwasser|wasserwerk|wasserversorgung|trinkwasser|kanalisation|regenrückhalte)"),
 ("energy", r"(photovoltaik|solar|windpark|umspannwerk|energiezentrale|wärmenetz|fernwärme|batteriespeicher)"),
 ("public_space", r"(außenanlage|freianlage|parkplatz|parkhaus|platzgestaltung|grünanlage)"),
]

TRADE_RULES = [
 ("insulation", r"(dämm|schallschutz|isolierarbeiten)"),
 ("fencing", r"(zaun|zäune|geländer)"),
 ("electrical", r"(elektro|elektrotechnik|starkstrom|schwachstrom|beleuchtung|netzwerktechnik|sicherheitsbeleuchtung)"),
 ("hvac", r"(heizung|lüftung|hls|tga|wärmepumpe|kälte|klima|gebäudetechnik)"),
 ("drywall", r"(trockenbau|gipskarton|abhangdecke|akustikdecke)"),
 ("painting", r"(maler|anstrich|beschichtung|lackier)"),
 ("flooring", r"(bodenbelag|bodenleger|parkett|estrich|fliesen|naturstein)"),
 ("roof", r"(dach|dachdecker|spengler|abdichtung|dachdeckung)"),
 ("windows_doors", r"(fenster|türen|tore|sonnenschutz|raffstore)"),
 ("facade", r"(fassade|wärmedämmverbundsystem|wdvs|vorhangfassade)"),
 ("earthworks", r"(erdarbeiten|tiefbau|baugrube|aushub|bodenarbeiten)"),
 ("structural", r"(rohbau|beton|mauerwerk|stahlbeton|zimmerer|holzbau|stahlbau)"),
 ("landscaping", r"(außenanlagen|landschaftsbau|galabau|pflaster|freianlagen)"),
 ("fire_protection", r"(brandschutz|sprinkler|brandmelde|rauchabzug)"),
 ("plumbing", r"(sanitär|trinkwasser|abwasserinstallation|rohrleitung)"),
 ("elevator", r"(aufzug|aufzugsanlage|förderanlage)"),
 ("demolition", r"(abbruch|rückbau|demontage)"),
 ("roadworks", r"(asphalt|straßenbau|fahrbahn|verkehrswegebau)"),
 ("sewer_pipe", r"(kanalbau|kanalsanierung|rohrleitungsbau|entwässerung)"),
 ("railworks", r"(gleisbau|oberbau|bahnsteig|schienen)"),
 ("solar_energy", r"(photovoltaik|solaranlage|pv-anlage|solar|batteriespeicher)"),
]

# CPV prefixes provide a second signal when notice titles are terse.
CPV_PROJECT_PREFIXES = {
 "4521":"industrial", "45211":"residential", "45212":"public_building",
 "45213":"commercial", "45214":"university_research", "45215":"care_social",
 "4522":"civil_engineering", "45221":"bridge", "4523":"infrastructure",
 "45231":"water_wastewater", "45232":"water_wastewater", "45233":"road",
 "45234":"rail", "4525":"energy",
}
CPV_TRADE_PREFIXES = {
 "4511":"demolition", "45112":"earthworks", "45233":"roadworks", "45234":"railworks",
 "45261":"roof", "45262":"structural", "4531":"electrical", "4532":"insulation",
 "4533":"hvac", "4534":"fencing", "45343":"fire_protection", "45332":"plumbing", "4535":"building_services",
 "4541":"plastering", "4542":"windows_doors", "4543":"flooring", "4544":"painting", "4545":"finishing",
}

def _cpvs(cpv):
    if cpv is None: return []
    if isinstance(cpv, (str,int)): cpv=[cpv]
    out=[]
    for x in cpv:
        if isinstance(x,dict): x=x.get("code") or x.get("value") or x.get("cpv") or ""
        s=re.sub(r"\D", "", str(x))
        if s: out.append(s)
    return out

def _prefix_lookup(codes, mapping):
    hits=[]
    for code in codes:
        best=None
        for p,v in mapping.items():
            if code.startswith(p) and (best is None or len(p)>len(best[0])): best=(p,v)
        if best: hits.append(best[1])
    return hits

def classify(text, cpv=None):
    t=(text or "").lower()
    project=next((x for x,p in PROJECT_RULES if re.search(p,t)), "")
    trades=[x for x,p in TRADE_RULES if re.search(p,t)]
    codes=_cpvs(cpv)
    if not project:
        ph=_prefix_lookup(codes, CPV_PROJECT_PREFIXES)
        project=ph[0] if ph else ""
    for x in _prefix_lookup(codes, CPV_TRADE_PREFIXES):
        if x not in trades: trades.append(x)
    return project,trades
