"""
masterdata.py -- Normalisation et traduction unifiee du masterdata.

Centralise :
  1. Dictionnaire de traduction ARABE -> FRANCAIS (indicateurs, unites, domaines)
  2. Standardisation des unites (POURCENTAGE -> %, Base100 -> INDICE, etc.)
  3. Enrichissement du domaine_code via INDICATOR_CODES
  4. Correction des codes indicateurs catch-all (INDICATEUR.HCP.GENERIQUE)
  5. Filtrage des sources non-economiques (concours, emplois, etc.)
"""

from __future__ import annotations

import re

import polars as pl

# ---------------------------------------------------------------------------
# 1. TRADUCTION ARABE -> FRANCAIS
#    Source : scan complet de 431 fichiers data/raw/economie/
#    Appliquee aux date_label et aux code_indicateur avant pipeline.
# ---------------------------------------------------------------------------
_ARABIC_TO_FR: dict[str, str] = {
    # === Titres de domains ===
    "المؤشرات الإجتماعية": "Indicateurs sociaux",
    "المؤشرات القطاعية": "Indicateurs sectoriels",
    "المؤشرات الماكرو اقتصادية": "Indicateurs macroeconomiques",
    # === Démographie ===
    "الديمغرافيا": "Demographie",
    "الساكنة": "Population",
    "معدل التمدن": "Taux d'urbanisation",
    "معدل الأنوثة": "Taux de feminite",
    "معدل الخصوبة": "Taux de fecondite",
    "المعدل الخام للولادات": "Taux brut de natalite",
    "المعدل الخام للوفيات": "Taux brut de mortalite",
    "عدد الأسر": "Nombre de menages",
    "متوسط عدد أفراد الأسر": "Taille moyenne des menages",
    # === Agriculture ===
    "الفلاحة والصيد البحري": "Agriculture et peche",
    "الفلاحة": "Agriculture",
    "الحبوب": "Cereales",
    "القمح الصلب": "Ble dur",
    "القمح الطري": "Ble tendre",
    "الشعير": "Orge",
    "الذرة": "Mais",
    "القطنيات": "Coton",
    "عباد الشمس": "Tournesol",
    "الفول السوداني": "Arachide",
    "المزروعات السكرية": "Cultures sucrieres",
    "الشمندر": "Betterave",
    "قصب السكر": "Canne a sucre",
    "الخضراوات الموسمية": "Legumes de saison",
    "الطماطم": "Tomate",
    "البطاطس": "Pomme de terre",
    "تربية الماشية": "Elevage",
    "عدد رؤوس الماشية": "Nombre de tetes de betail",
    "البقر": "Bovins",
    "الغنم": "Ovins",
    "الماعز": "Caprins",
    "الذبائح المراقبة": "Abattage controle",
    # === Peche ===
    "الصيد البحري": "Peche maritime",
    "أسطول الصيد البحري": "Flottille de peche",
    "الصيد الساحلي": "Peche cotiere",
    "الصيد في أعالي البحار": "Peche hauturiere",
    # === Mines ===
    "المعادن": "Mines",
    "إنتاج واستعمال الفوسفاط": "Production et utilisation des phosphates",
    "المعادن الحديدية": "Minerais de fer",
    # === Energie ===
    "الطاقـــة والماء": "Energie et eau",
    "نشاط قطاع الطاقة": "Activite du secteur energetique",
    "الكهرباء من أصل مائي": "Electricite hydraulique",
    "الكهرباء من أصل ريحي": "Electricite eolienne",
    "الكهرباء من أصل شمسي": "Electricite solaire",
    "النفط الخام و الغاز الطبيعي": "Petrole brut et gaz naturel",
    "الفحم الحجري": "Charbon",
    "المنتجات النفطية": "Produits petroliers",
    "الغاز الطبيعي": "Gaz naturel",
    "العجز الطاقي": "Deficit energetique",
    "معدل ملء السدود": "Taux de remplissage des barrages",
    "سد الوحدة": "Barrage Al Wahda",
    "سد المسيرة": "Barrage Al Massira",
    "سد بين الويدان": "Barrage Bin El Ouidane",
    "سد ادريس الأول": "Barrage Idriss Ier",
    # === Industrie ===
    "الصناعات التحويلية": "Industries de transformation",
    "الصناعة الغذائية والتبغ": "Industrie agroalimentaire et tabac",
    "الصناعة النسيجية والجلدية": "Industrie textile et cuir",
    "الصناعة الكيماوية": "Industrie chimique",
    "صناعة وسائل النقل": "Industrie des transports",
    "تكرير البترول": "Raffinage du petrole",
    "القيمة المضافة": "Valeur ajoutee",
    "الرقم الإستدلالي للإنتاج الصناعي": "Indice de production industrielle",
    "نشاط صناعة السكر": "Activite de l'industrie suciere",
    "نشاط المطاحن الصناعية": "Activite des meuneries industrielles",
    "نشاط الصناعة الزيتية": "Activite de l'huilerie",
    "نشاط صناعة الحليب": "Activite de l'industrie laitiere",
    "البناء والأشغال العمومية": "Batiment et travaux publics",
    "نشاط صناعة الإسمنت": "Activite de l'industrie cimentiere",
    "إنطلاق الأشغال بالوحدات السكنية": "Mise en chantier des logements",
    # === Transports ===
    "النقـــــل": "Transports",
    "شبكة الطرق المعبدée": "Reseau routier pave",
    "عدد السيارات المتنقلة": "Nombre de vehicules en circulation",
    "رواج السيارات": "Flux de vehicules",
    "الرواج الطرق": "Trafic routier",
    "نقل المسافرين": "Transport de voyageurs",
    "النقل السككي": "Transport ferroviaire",
    "النقل الجوي": "Transport aerien",
    "نقل البضائع": "Transport de marchandises",
    "عدد حوادث السير": "Nombre d'accidents de la route",
    "عدد الضحايا": "Nombre de victimes",
    "القتلى": "Tues",
    # === Tourisme ===
    "السياحـــة": "Tourisme",
    "الطاقة الإيوائية للفنادق": "Capacite d'accueil hoteliere",
    "نسبة التوافد على الفنادق": "Taux d'occupation des hotels",
    "الليالي السياحية في الفنادق المصنفة": "Nuitnees touristiques hotels classes",
    "المداخيل السياحية": "Recettes touristiques",
    "فرنسا": "France",
    "إسبانيا": "Espagne",
    "ألمانيا": "Allemagne",
    "إيطاليا": "Italie",
    "الولايات المتحدة الأمريكية": "Etats-Unis",
    # === Telecom ===
    "المواصلات السلكية واللاسلكية": "Telecommunications",
    "المنخرطين في الهاتف المحمول": "Abonnes telephone mobile",
    "الهاتف المحمول": "Telephone mobile",
    "الهاتف الثابت": "Telephone fixe",
    "المنخرطين في الأنترنيت": "Abonnes Internet",
    # === Assurance ===
    "التأمينات": "Assurances",
    "رقم معاملات شركات التأمين": "CA compagnies d'assurance",
    # === Comptes nationaux ===
    "الناتج الداخلي الخام": "PIB",
    "变动 الناتج الداخلي الخام بالأسعار التابثة": "Variation du PIB en prix constants",
    "القيم المضافة بالأسعار التابثة": "VA en prix constants",
    "نسبة نمو الناتج الداخلي الخام": "Taux de croissance du PIB",
    "الناتج الداخلي الخام بالأسعار الجارية": "PIB prix courants",
    "الناتج الداخلي الخام دون احتساب الفلاحة": "PIB hors agriculture",
    "القطاع الأول": "Premier secteur",
    "القطاع الثاني": "Deuxieme secteur",
    "القطاع الثالث": "Troisieme secteur",
    "الصادرات": "Exportations",
    "الواردات من السلع والخدمات": "Importations biens et services",
    "الإستهلاك النهائي الداخلي": "Consommation finale interieure",
    "التكوين الخام للرأسمال الثابت": "FBCF",
    "变动 المخزونات": "Variation des stocks",
    "الدخل القومي الخام": "RNB",
    "الإدخال القومي الخام": "Epargne nationale brute",
    # === Budget / Finances publiques ===
    "بيان الميزانيات الملحقة": "Etat des budgets annexes",
    "الــــــمــــداخـــــيـــل": "Recettes",
    "الــنــــفـــــقـــــات": "Depenses",
    "المجموع": "Total",
    "الميزانية": "Budget",
    "المداخيل": "Recettes",
    "النفقات": "Depenses",
    "نفقات تسديد الديون": "Depenses service de la dette",
    "امدادات": "Subventions",
    "المجموع العام": "Total general",
    "الفائض الحقيقي الخام": "Excedent brut",
    "الفائض الحقيقي الصافي": "Excedent net",
    "الضرائب والرسوم": "Impots et taxes",
    # === Emploi / Concours ===
    "التوظيف": "Recrutement",
    "المنصب": "Poste",
    "المباراة": "Concours",
    "وزارة الداخلية": "Ministere de l'Interieur",
    "وزارة الاقتصاد والمالية": "Ministere de l'Economie et des Finances",
    "المندوبية السامية للتخطيط": "HCP",
    "المكتب الوطني للكهرباء": "ONEE",
    "المكتب الوطني للمياه الصالحة للشرب": "ONEP",
    "السنة": "Annee",
    "التخصص": "Specialite",
    "عميد": "Doyen",
    "مدير": "Directeur",
    "أستاذ": "Professeur",
    "تقني": "Technicien",
    "طبيب": "Medecin",
    "محاسب": "Comptable",
    "سائقين": "Chauffeurs",
    "حارس": "Gardien",
    "مفتش": "Inspecteur",
    "منسق": "Coordinateur",
    "خبير": "Expert",
    "خبراء": "Experts",
    "المبادرة الوطنية للتنمية البشرية": "INDH",
    # === Unites ===
    "بمليون درهم": "En millions de DH",
    "بملايين الدراهم": "En millions de DH",
    "ألف طن": "Millier de tonnes",
    "بألف طن": "En milliers de tonnes",
    "بالألف": "En milliers",
    "مم": "mm",
    "كم": "km",
    "بمليون كم": "En millions de km",
    "بمليون كيلواط": "En millions de kWh",
    "بمليون متر مكعب": "En millions de m3",
    "بمليون لتر": "En millions de litres",
    "قنطار في الهكتار": "q/ha",
    "درهم للكلغ": "DH/kg",
    "درهم للطن": "DH/t",
    "النسبة المئوية": "%",
    "变动": "Variation",
    "النسبة": "Ratio",
    "معدل": "Taux",
}

# ---------------------------------------------------------------------------
# 2. STANDARDISATION DES UNITES
#    Normalise toutes les variantes de notation d'unites vers un code unique.
# ---------------------------------------------------------------------------
_UNIT_NORMALIZE: dict[str, str] = {
    "POURCENTAGE": "%",
    "Indice": "INDICE",
    "Base100": "INDICE",
    "En millions de dhs": "MAD",
    "milliers": "MILLIERS",
    "Mois_import": "MOIS_IMPORT",
    "?": "?",
}

# ---------------------------------------------------------------------------
# 3. ENRICHISSEMENT DOMAINES
#    Mappe les domaine_code "?" vers la valeur correcte via INDICATOR_CODES.
#    Fait dans pipeline, pas ici (depend de INDICATOR_CODES importe).
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# 4. CORRECTION INDICATEURS CATCH-ALL
#    Certains fichiers HCP ne sont pas discriminables par nom de fichier.
#    On utilise le nom de sheet pour affiner.
# ---------------------------------------------------------------------------
_HCP_SHEET_TO_INDICATOR: dict[str, str] = {
    "i_1.1": "PIB.TRIM.VOL",
    "i_1.2": "PIB.ANNUEL.VOL",
    "i_1.3": "PIB.CROISSANCE",
    "i_1.4": "VAB.AGRICULTURE",
    "i_1.5": "VAB.INDUSTRIE",
    "i_1.6": "VAB.SERVICES",
    "i_1.7": "CHOMAGE.TAUX",
    "i_1.8": "CHOMAGE.TAUX.URBAIN",
    "i_1.9": "CHOMAGE.TAUX.RURAL",
    "i_1.10": "EMPLOI.VOLUME",
    "i_1.11": "IPC.GLISSEMENT",
    "i_1.12": "IPC.MENSUEL",
    "i_1.13": "TAUX.DIRECTEUR",
    "i_1.14": "CREDIT.ECONOMIE",
    "i_1.15": "M3",
    "i_1.16": "RESERVES.CHANGE",
    "i_1.17": "EXPORTATIONS",
    "i_1.18": "IMPORTATIONS",
    "i_1.19": "BALANCE.COMMERCIALE",
    "i_1.20": "DETTE.PUBLIQUE",
    "i_1.21": "EMPLOI.VOLUME",
    "i_1.22": "RECETTES",
    "i_1.23": "DEPENSES",
    "i_1.24": "INVESTISSEMENT.PUBLIC",
    "i_1.25": "DEFICIT.BUDGET",
    "i_1.26": "IDE.FLUX",
    "i_1.27": "IDE.STOCK",
    "i_1.28": "CHANGE.USD",
    "i_1.29": "CHANGE.EUR",
}

# ---------------------------------------------------------------------------
# 5. MOTS-CLES NON-ECONOMIQUES (a exclure du pipeline economie)
#    Ces fichiers contiennent des concours, emplois, experts -- pas des
#    indicateurs economiques.
# ---------------------------------------------------------------------------
_NON_ECONOMIC_KEYWORDS = frozenset({
    "concours", "examens", "emplois_superieurs", "experts",
    "annuaire", "agences_de_voyages", "guides_touristiques",
    "honoraires", "immobilier", "sdata",
})

# ---------------------------------------------------------------------------
# Lookup tables pre-buildies (resolues au chargement du module)
# ---------------------------------------------------------------------------
try:
    from .parsers.base import INDICATOR_CODES
except ImportError:
    INDICATOR_CODES = {}

_DOMAIN_LOOKUP: dict[str, str] = {
    code: meta.get("domaine", "?") for code, meta in INDICATOR_CODES.items()
}
_UNIT_LOOKUP: dict[str, str] = {
    code: meta.get("unite", "?") for code, meta in INDICATOR_CODES.items()
}


# ---------------------------------------------------------------------------
# Helpers pour map_elements (fonctions top-level, pas de lazy import)
# ---------------------------------------------------------------------------
def _translate_element(val: str) -> str:
    if not val:
        return val
    return _ARABIC_TO_FR.get(str(val).strip(), str(val))


def _normalize_unit_element(val: str) -> str:
    if not val:
        return "?"
    return _UNIT_NORMALIZE.get(str(val).strip(), str(val).strip())


def _lookup_domain_element(code: str) -> str:
    return _DOMAIN_LOOKUP.get(code, "?")


def _fix_catchall_element(row: dict) -> str:
    fs = row.get("fichier_source", "")
    code = row.get("code_indicateur", "")
    if code != "INDICATEUR.HCP.GENERIQUE":
        return code
    fn = fs.lower().replace("\\", "/")
    for prefix, indicator in _HCP_SHEET_TO_INDICATOR.items():
        if prefix in fn:
            return indicator
    return code


def _is_non_economic_element(val: str) -> bool:
    fn = str(val).lower()
    return any(kw in fn for kw in _NON_ECONOMIC_KEYWORDS)


# ---------------------------------------------------------------------------
# FONCTIONS PUBLIQUES
# ---------------------------------------------------------------------------

def translate_arabic(text: str) -> str:
    """Traduit un texte arabe -> francais via le dictionnaire."""
    if not text:
        return text
    return _ARABIC_TO_FR.get(text.strip(), text)


def normalize_unit(unit: str) -> str:
    """Normalise un label d'unite vers le code standard."""
    if not unit:
        return "?"
    return _UNIT_NORMALIZE.get(unit.strip(), unit.strip())


def is_non_economic(filename: str) -> bool:
    """Detecte si un fichier n'est PAS un fichier economique."""
    fn = filename.lower()
    return any(kw in fn for kw in _NON_ECONOMIC_KEYWORDS)


def fix_indicator_from_filename(filename: str, code: str) -> str:
    """Corrige le code indicateur en fonction du nom de fichier/sheet."""
    if code != "INDICATEUR.HCP.GENERIQUE":
        return code
    fn = filename.lower().replace("\\", "/")
    for prefix, indicator in _HCP_SHEET_TO_INDICATOR.items():
        if prefix in fn:
            return indicator
    return code


def apply_masterdata_normalization(df: pl.DataFrame) -> pl.DataFrame:
    """
    Applique toutes les normalisations de masterdata au DataFrame fact.
    Appele dans pipeline Phase 3.

    Operations :
      1. Traduction arabe -> francais dans date_label
      2. Normalisation des unites
      3. Enrichissement domaine_code via code_indicateur
      4. Correction des codes catch-all
      5. Suppression des lignes non-economiques
    """
    if df.is_empty():
        return df

    # 1. Traduire les date_label arabes
    df = df.with_columns(
        pl.col("date_label").map_elements(
            _translate_element, return_dtype=pl.Utf8
        ).alias("date_label")
    )

    # 2. Normaliser les unites
    df = df.with_columns(
        pl.col("unite").map_elements(
            _normalize_unit_element, return_dtype=pl.Utf8
        ).alias("unite")
    )

    # 3. Enrichir domaine_code depuis INDICATOR_CODES
    df = df.with_columns(
        pl.col("code_indicateur").map_elements(
            _lookup_domain_element, return_dtype=pl.Utf8
        ).alias("_domain_from_code")
    )
    df = df.with_columns(
        pl.when(pl.col("domaine_code").eq("?"))
        .then(pl.col("_domain_from_code"))
        .otherwise(pl.col("domaine_code"))
        .alias("domaine_code")
    ).drop("_domain_from_code")

    # 4. Corriger les indicateurs catch-all
    df = df.with_columns(
        pl.struct(["fichier_source", "code_indicateur"]).map_elements(
            _fix_catchall_element, return_dtype=pl.Utf8
        ).alias("code_indicateur")
    )

    # 5. Filtrer les fichiers non-economiques
    df = df.filter(
        ~pl.col("fichier_source").map_elements(
            _is_non_economic_element, return_dtype=pl.Boolean
        )
    )

    return df
