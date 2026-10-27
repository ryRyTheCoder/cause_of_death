"""Cause-of-death cleaning rules for the Nashville City Cemetery ledger (Question 1).

The clerks wrote causes by hand for 130 years, so one disease can appear under dozens of
spellings ("Cholrea", "Cholera", "Colera"...). Cleaning happens in three readable steps:

1. ``normalize``     lowercase, turn punctuation into spaces, collapse spacing.
2. ``SPELLING``      fix whole words, one clerk spelling at a time ("cholrea" -> "cholera"),
   then ``PHRASES``   fix multi-word abbreviations ("inf of bowls" -> "inflammation of bowels").
3. ``RULES``         ordered (category, pattern) pairs. The category whose pattern matches
                     earliest in the text wins; ties go to the rule listed first, so specific
                     rules ("cholera infantum") sit above general ones ("cholera").

Anything no rule matches keeps its spelling-corrected text in Title Case, so nothing is
forced into a group it doesn't belong to; those rows are listed for review in the notebook.

Grouping principles (the assignment's: group types of one disease, never diseases that only
share a symptom):
  * merge spellings and synonyms of one disease (consumption = phthisis = tuberculosis);
  * group sites of one condition (cancer of breast / stomach / womb -> Cancer;
    heart disease / heart attack / heart failure -> Heart Disease);
  * keep apart diseases that share a word: scarlet / yellow / typhoid / bilious fever;
    cholera / cholera morbus / cholera infantum; smallpox / chicken pox;
    yellow jaundice / yellow fever;
  * historical terms with no single modern meaning (hives, phthisic, cold, brain fever,
    complication) keep their own label instead of a guessed modern diagnosis.
"""
import re

UNKNOWN = 'Unknown'


def normalize(text):
    """Lowercase, '&' -> 'and', punctuation -> space, single spaces."""
    t = str(text).lower().replace('&', ' and ')
    t = re.sub(r"[^a-z0-9' ]+", ' ', t)
    t = t.replace("'", '')
    return re.sub(r'\s+', ' ', t).strip()


# Multi-word fixes, applied in order between two passes of the word-by-word SPELLING fixes.
PHRASES = [
    # cholera infantum / morbus written as one fused or abbreviated word
    (r'\bcol(re|ry|rey)?mo?r?bus\b', 'cholera morbus'),
    (r'\bcholorafobus\b', 'cholera morbus'),
    (r'\b(cholrea|cholera|cholra|choler|cholea|colera|colney|cholney|colrey|cholrey|colry|corey|cho|chol)\s+(inf\w*|inph\w*)\b', 'cholera infantum'),
    (r'\b(cholrea|cholera|cholra|choler|cholre|colera|chalera|colney|colrey|colry)\s+(mo\w*)\b', 'cholera morbus'),
    # "inf / infl / inft / inflamation ..." meaning inflammation (only when an organ follows,
    # because "inf" and "inft" also abbreviate "infant")
    (r'\b(inf|infl|inft|infla|inflam|inflama?tion|inflmation|inflma|inflmn|inflmtn|infimation|infermation|imphermation|'
     r'inphemation|inphermation|infalamtion|inlfamation|infln|influn|inftn|inflm)\s+'
     r'(?=(of\s+)?(the\s+)?(bowel|bowl|howel|brain|bran|brian|brane|lung|stomach|stoamch|liver|kidney|throat|heart|hart|bladder|'
     r'breast|womb|head|nable|b\b))', 'inflammation '),
    (r'\binflamatory\s+(r|rheu|rheumatism|rhumatism|rhematism)\b', 'inflammatory rheumatism'),
    (r'\b(s|scarlet|scarlot|scarlett|scalot|scaret|sarlett)\s+(fever|feever|feaver|feve)\b', 'scarlet fever'),
    (r'\b(t|ty|typh|typhoid|typhoyd|tyfoid|typoid|typhard|tyfosld)\s+(fever|feever|feaver)\b', 'typhoid fever'),
    (r'\b(int|intermitent|intermittent|intmitan|intesuit)\s+(fever|feever)\b', 'intermittent fever'),
    (r'\b(con|cong|congs|conj|congestic|congestine|conjestic|conjestc|conjestiv|conjetive|congestion|congeston|conges|congestive|dum)\s+(chill|chil|chills|chils)\b', 'congestive chill'),
    (r'\b(cong|conj|congestic|congestine|conjestic|conges|congestion|conjestive)\s+(fever|feever)\b', 'congestive fever'),
    (r'\b(b|bil|bilis|billious|biliouse|belions|belous|belious|biulious)\s+(fever|feever|diarrh\w*|diar\w*|cholic|colic)\b', r'bilious \2'),
    (r'\b(sum|sumer|summer|sun|sermoner)\s+(com\w*|cpl\w*)\b', 'summer complaint'),
    (r'\b(ch|chr|chro|chron|chronic|chonic|cronic|cronick)\s+(?=d)', 'chronic '),
    (r'\b(gen|genl|genral)\s+(?=de|di)', 'general '),
    (r'\b(dis|diseas|dissease|deseas|desease|diaease|diasease|diasese|dease|deease)\s+(?=(of\s+)?(the\s+)?(heart|hart|lung|liver|bowel|bowl|brain|head|kidney|womb|woumb|spine|bladder|breast|glands))', 'disease '),
    (r'\b(aff|aft)\s+(?=of)', 'affection '),
    (r'\bstill\s+born\w*|\bstil\s+born\w*|\bstill\s+bor[dn]\b|\bstil\s+burth\b|\bsill\s*born\b|\bstilborn\b|\bstillborn\b|\bstill\s+borned\b', 'stillborn'),
    (r'\bt\s+b\b', 'tuberculosis'),
    (r'\bg\s+s\s+wound\b', 'gunshot wound'),
    (r'\bgun\s+shot\b', 'gunshot'),
    (r'\bsmall?\s+pox\b|\bsamlpox\b|\bsmal?pox\b', 'smallpox'),
    (r'\b(chicken|chicane)\s+pox\b', 'chickenpox'),
    (r'\block\s*(jaw|goy)\b', 'lockjaw'),
    (r'\bla\s*grippe\b|\blagridge\b|\bgrippe\b', 'influenza'),
    (r'\b(r\s*r|rail\s*r(oa|o)de?|railroad)\b', 'railroad'),
    (r'\b(brain)brain\b', r'\1'), (r'\b(rheumatism)rheumatism\b', r'\1'), (r'\bliverof the liver\b', 'liver'),
]

# Whole-word clerk spellings found in this ledger -> standard spelling.
SPELLING = {
    # cholera
    'cholrea': 'cholera', 'cholra': 'cholera', 'cholorea': 'cholera', 'cholre': 'cholera', 'colera': 'cholera',
    'chalera': 'cholera', 'cholea': 'cholera',
    # measles, mumps
    'measels': 'measles', 'measeles': 'measles', 'meales': 'measles', 'mealeses': 'measles', 'mealses': 'measles',
    'measals': 'measles', 'measelis': 'measles', 'measleas': 'measles', 'measlels': 'measles', 'measlles': 'measles',
    'measls': 'measles', 'miasles': 'measles', 'massles': 'measles',
    # tuberculosis
    'consumpion': 'consumption', 'consumpiton': 'consumption', 'consumpon': 'consumption', 'consumpsan': 'consumption',
    'consumptoin': 'consumption', 'consuption': 'consumption', 'consusption': 'consumption', 'conumption': 'consumption',
    'conusmption': 'consumption', 'coinsumption': 'consumption', 'comsumption': 'consumption', 'consption': 'consumption',
    'consumson': 'consumption', 'sonsumption': 'consumption',
    # pneumonia
    'pneumonie': 'pneumonia', 'pneuminia': 'pneumonia', 'numonia': 'pneumonia', 'pnemonia': 'pneumonia',
    'pnenmonia': 'pneumonia', 'penumonia': 'pneumonia', 'pneamonia': 'pneumonia', 'pnenmonie': 'pneumonia',
    'pnennonia': 'pneumonia', 'pnenumonia': 'pneumonia', 'pneuamonie': 'pneumonia', 'pneumona': 'pneumonia',
    'pneumoniae': 'pneumonia', 'pneunmonia': 'pneumonia', 'pneunonia': 'pneumonia', 'pneunonie': 'pneumonia',
    'pnuemonia': 'pneumonia', 'pnuemonie': 'pneumonia', 'pnumonia': 'pneumonia', 'peumonia': 'pneumonia',
    'peunomonia': 'pneumonia', 'pheumonie': 'pneumonia', 'pennumonea': 'pneumonia', 'penunmony': 'pneumonia',
    'neuomonia': 'pneumonia', 'numenia': 'pneumonia', 'pneumon': 'pneumonia', 'pneumoni': 'pneumonia',
    'pneumomia': 'pneumonia', 'pneumnie': 'pneumonia', 'pneu': 'pneumonia', 'pnenmonie': 'pneumonia',
    # diarrhea, dysentery
    'diarrhaea': 'diarrhea', 'diarherea': 'diarrhea', 'diarhoera': 'diarrhea', 'diarrhoea': 'diarrhea', 'diareah': 'diarrhea',
    'diarhea': 'diarrhea', 'diarhaea': 'diarrhea', 'diarhoea': 'diarrhea', 'diarhoerea': 'diarrhea', 'dearhaera': 'diarrhea',
    'dearhea': 'diarrhea', 'dearheora': 'diarrhea', 'dearherea': 'diarrhea', 'dearhoora': 'diarrhea', 'dearhorea': 'diarrhea',
    'diarah': 'diarrhea', 'diarhaera': 'diarrhea', 'diarhaerea': 'diarrhea', 'diarheara': 'diarrhea', 'diarheare': 'diarrhea',
    'diarheerea': 'diarrhea', 'diarheora': 'diarrhea', 'diarhera': 'diarrhea', 'diarhoe': 'diarrhea', 'diarhoorea': 'diarrhea',
    'diarhorea': 'diarrhea', 'diarhoura': 'diarrhea', 'diarraheoa': 'diarrhea', 'diarrhara': 'diarrhea',
    'diarrheara': 'diarrhea', 'diarrhoera': 'diarrhea', 'direarh': 'diarrhea', 'direire': 'diarrhea', 'drarhea': 'diarrhea',
    'draieah': 'diarrhea', 'dyarah': 'diarrhea', 'dearrheo': 'diarrhea', 'diaroah': 'diarrhea', 'diaroh': 'diarrhea',
    'diarr': 'diarrhea', 'diarrh': 'diarrhea', 'dearha': 'diarrhea', 'direar': 'diarrhea', 'diar': 'diarrhea',
    'diarrhrea': 'diarrhea', 'diarhee': 'diarrhea', 'diarhoee': 'diarrhea', 'dearheo': 'diarrhea', 'dearrhen': 'diarrhea',
    'deaseah': 'diarrhea', 'diarhoorea': 'diarrhea',
    'dysentary': 'dysentery', 'disentery': 'dysentery', 'disentary': 'dysentery', 'dyentery': 'dysentery',
    'dysenteary': 'dysentery', 'dysentey': 'dysentery', 'dysentry': 'dysentery', 'dysinley': 'dysentery',
    'dysintery': 'dysentery', 'ducntery': 'dysentery', 'dysenter': 'dysentery', 'flucks': 'flux',
    # diphtheria, croup, whooping cough
    'diptheria': 'diphtheria', 'diphtherie': 'diphtheria', 'dyptheria': 'diphtheria', 'diphthera': 'diphtheria',
    'dipheria': 'diphtheria', 'diphhuria': 'diphtheria', 'dipthari': 'diphtheria', 'diptharis': 'diphtheria',
    'dipthera': 'diphtheria', 'diptherie': 'diphtheria', 'dipthier': 'diphtheria', 'dipthra': 'diphtheria',
    'dipthrie': 'diphtheria', 'diuptheria': 'diphtheria', 'dyphery': 'diphtheria', 'dyptherea': 'diphtheria',
    'dyptherie': 'diphtheria', 'dytheria': 'diphtheria', 'dytpheria': 'diphtheria', 'diftheris': 'diphtheria',
    'diphehirie': 'diphtheria', 'dypartia': 'diphtheria', 'diph': 'diphtheria',
    'croop': 'croup', 'croope': 'croup', 'croupe': 'croup', 'crope': 'croup', 'crupe': 'croup',
    'hooping': 'whooping', 'whoping': 'whooping', 'hoping': 'whooping', 'coff': 'cough', 'coof': 'cough',
    # fevers
    'feever': 'fever', 'feaver': 'fever', 'feve': 'fever', 'scarlot': 'scarlet', 'scarlett': 'scarlet', 'scalot': 'scarlet',
    'scaret': 'scarlet', 'sarlett': 'scarlet', 'typhoyd': 'typhoid', 'tyfoid': 'typhoid', 'typoid': 'typhoid',
    'typhard': 'typhoid', 'tyfosld': 'typhoid', 'billious': 'bilious', 'biliouse': 'bilious', 'bilis': 'bilious',
    'belious': 'bilious', 'belions': 'bilious', 'belous': 'bilious', 'conjestive': 'congestive', 'conjestion': 'congestion',
    'conjeston': 'congestion', 'congeston': 'congestion', 'conestion': 'congestion', 'conjestive': 'congestive',
    'intermitent': 'intermittent', 'maleria': 'malaria', 'spatted': 'spotted', 'barin': 'brain', 'braine': 'brain',
    'brane': 'brain', 'brian': 'brain', 'brains': 'brain', 'bran': 'brain',
    # organs
    'hart': 'heart', 'bowls': 'bowels', 'bowles': 'bowels', 'bowell': 'bowels', 'howels': 'bowels', 'bowel': 'bowels',
    'stomache': 'stomach', 'stoamche': 'stomach', 'stoamch': 'stomach', 'lung': 'lungs', 'lunges': 'lungs',
    'longs': 'lungs', 'lougs': 'lungs', 'lugs': 'lungs', 'woumb': 'womb', 'wond': 'womb', 'brest': 'breast',
    # other diseases
    'dropsey': 'dropsy', 'dopsey': 'dropsy', 'dopsy': 'dropsy', 'drosy': 'dropsy', 'dropsin': 'dropsy',
    'teethin': 'teething', 'teathing': 'teething', 'teethink': 'teething', 'wormes': 'worms',
    'appoplexy': 'apoplexy', 'aperplexy': 'apoplexy', 'apoplaxy': 'apoplexy', 'apopley': 'apoplexy', 'apoplxey': 'apoplexy',
    'apoplxy': 'apoplexy', 'apopexy': 'apoplexy', 'aoplexy': 'apoplexy', 'apipoplexy': 'apoplexy', 'aplexy': 'apoplexy',
    'aplexion': 'apoplexy', 'appelxy': 'apoplexy', 'apperplexy': 'apoplexy', 'applexy': 'apoplexy', 'apploxey': 'apoplexy',
    'apploxy': 'apoplexy', 'appoloxy': 'apoplexy', 'appoplesy': 'apoplexy', 'appoplexcy': 'apoplexy', 'spoplexy': 'apoplexy',
    'sppoplexy': 'apoplexy', 'apoplepsy': 'apoplexy', 'apolepsy': 'apoplexy',
    'pluracy': 'pleurisy', 'pleurisey': 'pleurisy', 'pleuricy': 'pleurisy', 'plurasy': 'pleurisy', 'pleurisa': 'pleurisy',
    'pluralisis': 'pleurisy', 'plurallis': 'pleurisy', 'plurallisis': 'pleurisy', 'plurilis': 'pleurisy',
    'scroffula': 'scrofula', 'scrofalow': 'scrofula', 'scroffalo': 'scrofula', 'scafalow': 'scrofula', 'scaffolow': 'scrofula',
    'schofflow': 'scrofula', 'scofalow': 'scrofula', 'scoffolo': 'scrofula', 'scraffalow': 'scrofula',
    'scraffellow': 'scrofula', 'scrafflow': 'scrofula', 'scrawfulow': 'scrofula', 'scrofalaw': 'scrofula',
    'scrofales': 'scrofula', 'scroffala': 'scrofula', 'scroffalow': 'scrofula', 'scroffellow': 'scrofula',
    'scroffola': 'scrofula', 'scroffolo': 'scrofula', 'scroffow': 'scrofula', 'scroffulo': 'scrofula', 'scrofloo': 'scrofula',
    'scrofolow': 'scrofula', 'scrofulo': 'scrofula', 'scrophulosis': 'scrofula',
    'spasom': 'spasms', 'spasoms': 'spasms', 'spasams': 'spasms', 'spasm': 'spasms', 'spamasm': 'spasms',
    'drownded': 'drowned', 'drownd': 'drowned', 'drown': 'drowned',
    'janders': 'jaundice', 'jandice': 'jaundice', 'jondice': 'jaundice', 'ganders': 'jaundice',
    'yallow': 'yellow', 'yalow': 'yellow', 'yollow': 'yellow', 'yalaw': 'yellow', 'yallaw': 'yellow',
    'thrash': 'thrush', 'poisan': 'poison', 'poisen': 'poison', 'poisand': 'poisoned', 'poisend': 'poisoned', 'possen': 'poison',
    'rhumatism': 'rheumatism', 'rhematism': 'rheumatism', 'rhumitism': 'rheumatism', 'rhumtism': 'rheumatism',
    'rheamatism': 'rheumatism', 'rhumsitism': 'rheumatism', 'rhumantism': 'rheumatism',
    'inflamation': 'inflammation', 'inflmation': 'inflammation', 'erysiplas': 'erysipelas',
    'paralisis': 'paralysis', 'parolisis': 'paralysis', 'paralasis': 'paralysis', 'peralysis': 'paralysis',
    'meningetis': 'meningitis', 'menegitis': 'meningitis', 'menengetis': 'meningitis', 'mennigitis': 'meningitis',
    'menigites': 'meningitis', 'menigetes': 'meningitis', 'menintitis': 'meningitis', 'menningitis': 'meningitis',
    'mingitis': 'meningitis', 'minigitis': 'meningitis', 'miningitis': 'meningitis', 'mnegitis': 'meningitis',
    'memingities': 'meningitis', 'menegetus': 'meningitis', 'mentigetis': 'meningitis', 'mininggetes': 'meningitis',
    'minegetius': 'meningitis', 'mengitis': 'meningitis',
    'influensa': 'influenza', 'influensar': 'influenza', 'influenzer': 'influenza', 'influenzid': 'influenza',
    'influenzy': 'influenza', 'infleunza': 'influenza',
    'unknowm': 'unknown', 'knwon': 'known', 'unnone': 'unknown', 'unnow': 'unknown', 'unnon': 'unknown',
    'accident': 'accident', 'acident': 'accident', 'acedent': 'accident', 'acidente': 'accident', 'acedente': 'accident',
    'accidently': 'accidentally', 'accidentaly': 'accidentally', 'accedently': 'accidentally',
    'pulmonrary': 'pulmonary', 'infjury': 'injury', 'vaccinaition': 'vaccination', 'enteretis': 'enteritis',
    'eryriplas': 'erysipelas', 'essapipelas': 'erysipelas', 'heemorage': 'hemorrhage', 'dieas': 'disease', 'hear': 'heart',
    'locomortor': 'locomotor', 'locomoton': 'locomotor', 'atexia': 'ataxia', 'exahustion': 'exhaustion', 'pelegra': 'pellagra',
    'pneuralgie': 'neuralgia', 'pneusalgy': 'neuralgia', 'parailis': 'paralysis', 'paryalsis': 'paralysis', 'shingls': 'shingles',
    'vistas': 'vitus', 'murdrd': 'murdered', 'uterstiaty': 'interstitial', 'neshretis': 'nephritis',
    'hermerage': 'hemorrhage', 'hermorage': 'hemorrhage',
}

# Ordered rules: (Cause of Death Updated, pattern searched in the cleaned text).
RULES = [
    # --- not a cause: blank, unknown, or a note about the person / undertaker / place ---
    (UNKNOWN, r'^$|^unknown$|^not known$|^no known$|^not stated$|^n a$|^m a$|^death unknown$|^deth unknown$|'
              r'^unknown dis\w*$|^dis unknown$|^unknown disease$|^disease$|^his disease$|^infant$|^child$|^maple$|^short$|'
              r'^born\b|^borned\b|^daughter of|undertaker|^finley dorris|^removed from|^brought from|^died below$|^died in (louisville|virginia|gen hospital|st thomas)|'
              r'^died at |^cremated$|^nashville tn$|^physcian out abs$|^age \d+|^unknown perhaps'),
    # --- birth and infancy ---
    ('Stillborn', r'\bstillborn'),
    ('Premature Birth', r'\bprem\w*|\bpreamture\b|\buntiml\w* burth\b|\bpre birth\b'),
    # --- cholera family: three different diseases ---
    ('Cholera Infantum (summer complaint)', r'\bcholera infantum\b|\bsummer complaint\b|\binfantile diarrhea\b'),
    ('Cholera Morbus', r'\bcholera morbus\b'),
    ('Cholera', r'\bcholera\b'),
    # --- named fevers (kept apart) ---
    ('Scarlet Fever', r'\bscarlet fever\b|\bscarlatina\b'),
    ('Yellow Fever', r'\byellow fever\b'),
    ('Pneumonia', r'\btyphoid pneumonia\b|\bt pneumonia\b|\btyph pneumonia\b'),
    ('Typhoid Fever', r'\btyphoid\b|\btyphus abdominalis\b'),
    ('Malaria (intermittent fever, chills and fever)', r'(?<!typhas )\bmalaria\w*|\bintermittent fever\b|\bchills? and fever\b|\bchills fever\b|\bmal fever\b'),
    ('Congestive Chill or Fever', r'\bcongestive (chill\w*|chil\w*|fever)\b'),
    ('Bilious Fever', r'\bbilious fever\b|^bilious$'),
    ('Spotted Fever', r'\bspotted fever\b'),
    ('Childbirth (incl. childbed fever)', r'\bchild ?be(d|de|ad)\b|\bchid bed\b|\bchildbed\b|\bchild ?birth\b|\bchid birth\b|\bchild barth\b|'
                                         r'\bpu?erperal\b|\bpurperal\b|\bperperal\b|\bdied in child bed\b'),
    ('Brain Fever / Inflammation', r'\bbrain fever\b|\bbrain feve\b|\binflammation (of )?(the )?brain\b|\bcongestion (of )?(the )?brain\b|'
                                   r'\b(con|cong|cang|conj|congest)\s+(of\s+)?(the\s+)?brain\b'),
    ('Softening of the Brain', r'\bsoft\w* (of )?brain\b|\bcerebral softening\b'),
    ('Brain or Head Disease (unspecified)', r'\bbrain (affected|efected|trouble)\b|\bdisease (of )?(the )?brain\b|\bdiseased brain\b|\baffection (of )?(the )?brain\b|'
                                            r'\baffection brain\b|\binfection of brain\b|\beffection of the brain\b|'
                                            r'\binflammation (of )?(the )?head\b|\baffection of (the )?head\b|\bdisease (of )?(the )?head\b|\bof the head\b|^head$'),
    # --- tuberculosis and related ---
    ('Tuberculosis (consumption)', r'\b(bowels? )?consumption\b|\btub\w*culo?\w*|\btubucul\w*|\btubuc\w*|\btuburk\w*|\bturtuclas\b|\bturburculous\b|\btuberc\w*|'
                                   r'\btuberosis\b|\btuberlosis\b|\btubeculas\b|\bphthisis\b|\bphithisis\b|\bphihisis\b|\bphthissis\b|'
                                   r'\bpulmonalis\b|\bpulmonary tub\w*|\bpulmarnory tub\w*|\bpulminary tub\w*|\btuberlicis\b|\btuburcolis\b|\bacute phthis\b|\baali phthis\b|\bphetis palmonbis\b|\btb\b|\bbercular\b'),
    ('Phthisic (asthma or tuberculosis)', r'\bphthisi?c\w*|\bphithisic\b|\bphthesic\b|\bphthipic\b|\bphthiric\b|\bphthie\b|\bphthrie\b|'
                                          r'\bphthsic\b|\bphthisie\b|\bplithisic\b|\bphythisic\b|\bphysh?asic\b|\bphlhic\b|\btisic\b'),
    ('Scrofula', r'\bscrofula\b|\bkings evill?\b'),
    ('White Swelling', r'\bwhi(te|le) swel\w*|\bwhite wellen\b'),
    # --- respiratory ---
    ('Pneumonia', r'\bpneumonia\b|\bbron\w*\s+pneumonia\b|\blungs? fever\b|\binflammation (of )?(the )?lungs\b|\bpleuro\b'),
    ('Bronchitis', r'\bbronch\w*|\bbronk\w*|\bbron\b|\bbrochitis\b|\bbra[i]?n chitis\b|\bbroncitis\b|\bbroncitus\b'),
    ('Pleurisy', r'\bpleurisy\b'),
    ('Influenza (la grippe)', r'\binfluenza\b'),
    ('Asthma', r'\basthma\b|\bastma\b|\basma\b|\basmen\b|\basmer\b|\basshmis\b'),
    ('Diphtheria', r'\bdiphtheria\b|\bdyp\b'),
    ('Croup', r'\bcroup\b|\bmembran\w*'),
    ('Whooping Cough', r'\bwhooping cough\b|\bpertussis\b'),
    ('Sore Throat / Quinsy', r'\bso(re|ar|r)\s+thr\w*|\bsore throt\b|\bthroat trouble\b|\bulcer\w* (in |of )?(the )?throat\b|\bquin\w*|\bquenzy\b|'
                             r'\btonsil\w*|\binflammation (of )?(the )?throat\b|\baffection of the throat\b|\bulcrated sore throat\b'),
    ('Lung Disease (other)', r'\b(disease|affection|aff)\s+(of\s+)?(the\s+)?lungs\b|\bcongestion\s+(of\s+)?(the\s+)?lungs\b|\b(cang|cong|conj)\s+(of\s+)?lungs\b|'
                             r'\bdisease lungs\b|\bdiseased lungs\b|\blungs? (disease|dis|trouble|effectation|diseased)\b|^lungs$|^of the lungs$|'
                             r'\bpulmonary\b|\bpul odema\b|\bacute adema of lungs\b|\baffectat lungs\b|\ba\w*lectas\w*|\belelectases\b|'
                             r'\b(hem\w*|hm\w*|him\w*|hum\w*|bleeding|bled to death)\s+(at\s+|of\s+)?(the\s+)?lungs\b|\bhemorhage of l\b|\bhemorage of l\b|'
                             r'\bparalysis lungs\b|\ba\w*ss\w* of lungs\b|\bbronchall\b|\bdied suddenly by bleeding lungs\b'),
    ('Cold', r'^cold$|^colde$|^colod$|^died from cold$'),
    # --- common infectious diseases of childhood ---
    ('Measles', r'\bmeasles\b'),
    ('Smallpox', r'\bsmallpox\b|\bvariola\b'),
    ('Chicken Pox', r'\bchickenpox\b'),
    ('Mumps', r'\bmumps\b'),
    ('Teething', r'\bteething\b|\bdentition\b'),
    ('Worms', r'\bworms?\b'),
    ('Thrush', r'\bthrush\b|\baph\w*th\w*|\bepthea\b'),
    ('Hives', r'\bhives\b'),
    ('Marasmus', r'\bm[ao]r?r?asm\w*|\bmararmus\b|\bmarusmus\b|\bharasmus\b|\brasmus\b|\bmaiafrmus\b|\bmerrasmus\b|\bmarasmas\b'),
    ('Convulsions (spasms, fits)', r'\bconvul\w*|\bconfuls\w*|\bconvuis\w*|\bspasms\b|\bfits?\b|\bfitts?\b|\bcramps?$|\beclamp\w*'),
    ('Erysipelas', r'\b(e|a|ai|ay|es|ey|er)[a-z]{0,4}(s|c|z)[iey]{0,2}(p|f)[a-z]*(l|ll)[a-z]*s\b|\berysip\w*|\besiples\b|\bersiples\b|\bensiplus\b|'
                   r'\bdricipplis\b|\beruplias\b|\bertspidas\b|\bemasipelas\b|\barasiphlus\b|\bainsyplus\b|\baysiplas\b|\berecepulus\b'),
    # --- digestive ---
    ('Dysentery (flux)', r'\bdysentery\b|\bflux\b'),
    ('Diarrhea', r'\bdiarrhea\b|\bbilious diarrhea\b'),
    ('Bowel Inflammation / Disease', r'\binflammation (of )?(the )?bowels\b|\b(cong|congestion|conj|con|cons)\s+(of\s+)?(the\s+)?bowels\b|'
                                     r'\bcongestive bowels\b|\b(entero|enter|entera|entre|entiow|enters)\s*(colit\w*|culitis|coletis)\b|\benter\w*itis\b|'
                                     r'\bgastro (enteritis|entenitis|entintis|interitis)\b|\bcolit\w*|\bcoletis\b|\bulcerat\w* (of )?(the )?bowels\b|'
                                     r'\bdisease (of )?(the )?bowels\b|\bbowels? (trouble|complt|complaint)\b|\bderangement of the bowels\b|'
                                     r'\baffection of bowels\b|^bowels$|^of bowels$|\balong bowels\b|\babcess of the bowels\b|'
                                     r'\bhem\w* (of )?(the )?bowels?\b|\bintestinal of bowels\b|\bcongestion stomach bowels\b'),
    ('Intestinal Obstruction / Hernia', r'\bobstruct\w*|\bobstraction\b|\block bowels\b|\bstrang\w* (of )?the bowels\b|\bhernia\b|\brupture$|\binternal opaction\b'),
    ('Appendicitis / Peritonitis', r'\bappend\w*|\bapprendicitis\b|\bperiton\w*|\bperatonites\b|\bpeatonitus\b|\bperetositis\b|\bacute peritenits\b'),
    ('Stomach Disease (dyspepsia, gastritis)', r'\bulc\w* (of |in )?(the )?stomach\b|\bstomach\b|\bgastri\w*|\bdysp\w*|\bdisp\w*|\bindig\w*|\bindijestion\b|\bindideton\b|\bacat digestion\b'),
    ('Colic', r'\bcolic\b|\bcholic\w*|\bcollic\w*|\bcollc\b|\bcolick\b|\bcramp colic\b'),
    ('Liver Disease', r'\b(abs?c?ess?|abcese|absess|abeess)\s+(of|on)\s+(the\s+)?liver\b|\bliver\b|\blive complt\b|\bhepatitis\b|\bcinhosis\b|\bcirrhosis\b'),
    ('Jaundice', r'\bjaundice\b'),
    # --- heart, circulation, stroke ---
    ('Heart Disease', r'\bheart\b|\bcardi\w*|\bangina\w*|\b\w*gina pectoris\b|\baggina pectrio\b|\bangia pectas\b|\baugina redos\b|\bcoronary\b|\bcaranary\b|'
                      r'\bcarnory\b|\bmitral\b|\bmatril regurgitation\b|\bpericard\w*|\bmyo?card\w*|\bmyacard\w*|\bmy\w*card\w*|\bmicorditis\b|\bmyscarditis\b|'
                      r'\bmyorerntes\b|\bvalouv heart\b|\bendocrist\b|\bpalpa\w* (at|of) the heart\b|\bpattaron heart\b|\bheart attack\b|'
                      r'^of heart$|^of the heart$|\bacragea heart\b|\bcarary acardeson\b|\bchoronis myocadis\b|\bchroci myecarditis\b|\bmycalits\b'),
    ('Apoplexy (stroke)', r'\bapoplex\w*|\bapoplect\w*|\bapopl\w*|\baperplect\w*|\bappelet\w*|\bappl?ex\w*|\bappoleptick\b|\bapoleptic\b|\bnervious apoplexy\b|'
                          r'\bstroke\b|\bcere?b\w*\s+(hem\w*|thromb\w*)|\bdied suddenly apoplexy\b|\b(cebral|cerbral|cerbbual|ceuberal|canebral|cebril)\s+\w+|\bcenbrar\b'),
    ('Paralysis', r'\bpara?l\w*|\bpary?l\w*|\bparol\w*|\bpalse?y\b|\bhemiplegia\b|\bemplegia\b|\bpariletick\b|\bparletick\b|\bparilisik\b|'
                  r'\bparititick\b|\bporolisis\b|\bpralaysis\b|\bperalysis\b|\bparralisis\b|\bparenclymdey\b|\bbuldor paralysis\b'),
    ('Vascular Disease (arteriosclerosis, aneurysm, embolism)', r'\barteri\w*|\barteris\w*|\barterio\b|\bartero\b|\baneurism\b|\banuerism\b|\bannurism\b|\baneurysm\b|\baneariz\b|\bembol\w*|\beubolisine\b'),
    ('Hydrocephalus (dropsy of the brain)', r'\bdropsy\s+(of|in|on)\s+(the\s+)?(brain|head)\b|\bbrain brain dropsy\b|\bwater on the brain\b|\bhydro?c\w*|\bhydr\w*ph\w*|'
                                            r'\bhydros\w*|\bhy drosyphlus\b|\boverflow of water to the brain\b|\beffusion of brain\b'),
    ('Dropsy', r'\bdropsy\b'),
    # --- kidney, urinary, diabetes ---
    ('Kidney / Urinary Disease (Bright\'s disease, nephritis, gravel)', r'\bkidney\w*|\bbright\w*|\bbrits\b|\bbrite\b|\bneph\w*|\bnephr\w*|\bnaphris\b|\bneprighris\b|\burinia\b|\bnepherities\b|'
                                                     r'\bur\w*mi\w*|\buraemia\b|\burama\b|\burenic\b|\buremisa\b|\bgravel\w*|\bgraval\b|\bbla[d]+er\b|\bstrictu?r\w*|'
                                                     r'\bsticture\b|\bcy\w*titis\b|\bcyititis\b|\bamyloid degeneration kidney\b'),
    ('Diabetes', r'\bdiab\w*'),
    # --- infection, skin, blood ---
    ('Blood Poisoning (septicemia)', r'\bblood (p\w*|parson)\b|\bboold poison\b|\bbood poison\b|\bsept\w*|\bperperal septicacema\b|\bpy\w*mia\b'),
    ('Gangrene (mortification)', r'\bgan\s*gre\w*|\bmortification\b'),
    ('Abscess / Fistula / Carbuncle', r'\bab\w*ss\w*|\babcese\b|\bacute abesses\b|\bcarbun\w*|\bcarbunkle\b|\bcow buncal\b|\bfistu\w*|\bfisterlow\b'),
    ('Tetanus (lockjaw)', r'\blockjaw\b|\btetan\w*|\btetamus\b|\b(t|p)r[ei]s?mus nas\w*|\bprimis nasc\w*'),
    ('Rheumatism (incl. rheumatic fever)', r'\brheum\w*|\binflammatory rheumatism\b|\binfl rheumatism\b'),
    ('Syphilis', r'\bsyphi\w*|\bsyplaletic\b'),
    ('Anemia', r'\ban\w*mia\b|\bamemia\b|\banamis\b|\banaemia\b'),
    ('Pellagra', r'\bpel+agr\w*|\bpellegr\w*|\bbellagrd\b'),
    ('Cancer', r'\bcancer\w*|\bcanser\b|\bcansor\b|\bcansar\b|\bcarcin\w*|\bcarcenonic\b|\bcarcemmia\b|\bcarcerona\b|\bcarimoua\b|\bcavenoma\b|\beating cancer\b'),
    ('Tumor', r'\btumou?r\w*|\btumer\b'),
    ('Ulcer', r'\bulc\w*'),
    ('Spinal Disease', r'\bspin\w*|\bspimabefida\b'),
    ('Uterine Disease (womb)', r'\bwomb\b|\bmetritis\b|\bhysteritis\b|\buter\w*'),
    ('Broken Heart', r'\bbrokin heart\b|\bbroken heart\b'),
    ('Vaccination Complication', r'\bvaccination\b'),
    ('Hemorrhage', r'\bhem\w*r\w*g\w*|\bhemrage\b|\bhermerage\b|\bhermorage\b|\bhemerag\w*|\bhemegathe\b|\bhemege\b|\bhemigate\b|\bgemerage\b|\bbarsting of blood vessel\b|\brupture of blood vessel\b'),
    # --- mind and nerves ---
    ('Meningitis', r'\bmeningitis\b|\bmitgen\w*|\bmitigen\w*|\bmitiginites\b|\bmitifinites\b'),
    ('Epilepsy', r'\bep+ilep\w*'),
    ('Insanity', r'\binsan\w*|\blunatic\w*|\bderangement$|\bmania\b(?!\s*(a\s*)?po)'),
    ('Nervous Disorders', r'\bnerv\w*|\bnev\b|\bnevp\b|\bnewvous\b|\bneural\w*|\bhystero\b|\bnurutrals\b|\bnewnouss\b|\bneruety\b'),
    ('Debility / Exhaustion', r'\bdebility\b|\bdibility\b|\bdebelity\b|\bdability\b|\bexha\w*|\bexastion\b|\bexauston\b|\bprostration\b|\brapid decline\b|'
                              r'\binanition\b|\binnition\b|\binamition\b|\bjnanetion\b|\blingerin\w*'),
    ('Old Age', r'\bold age\b|^age$|\bold ages\b|\bold ave\b|\bsenil\w*|\bsenulity\b|\bcenility\b|\binfirm of age\b'),
    # --- external causes ---
    ('Suicide', r'\bsuicid\w*|\bsucide\b|\bsuecide\b|\bsueside\b|\bsuiside\b|\bsuaside\b|\bsalecide\b|\bsuide\b|\bhung himself\b|\bpousoned suicide\b'),
    ('Drowning', r'\baccidental drowning\b|\bdrowned\b|\bdrowning\b|\bfound (dead )?in river\b|\bfell in the well\b|\bfound dead in a well\b'),
    ('Burns / Scalds', r'\bacidental burn\b|\bburn\w*|\bburnt\b|\bburnd\b|\bbuned\b|\bscald\w*|\bscalled\b'),
    ('Gunshot', r'\bkilled by (being )?shot\w*|\bkilled by shooting\b|\bkilled by accidental shooting\b|\baccident\w* shot\w*|\baxidental shott\b|\bgunshot\b|\bpistol\b|\bpistal\b|\bshot\w*|\bshooting\b|\bshotting\b|\bshott\b'),
    ('Homicide / Violence', r'\bmurder\w*|\bmurd\w*|\bstab\w*|\bknife\b|\baffray\b|\bviolence\b|\bvyolence\b|\bkilled by (j|s|l|w|c|james|thomas)\b|'
                            r'\bkilled by the hand\b|\bkilled by the mother\b|\bkilled or murdered\b|'
                            r'\bkilled with a knife\b|\bkilled in an affray\b|\bkilled by being stab\w*'),
    ('Execution (hanged by law)', r'\bhanged by law\b'),
    ('Killed in War', r'\bkilled (at|in) (battle|combat|monterey|mexico)\b|\bkilled at battle\b|\bwonded in army\b'),
    ('Poisoning / Overdose', r'\bpoison\w*|\bposion\w*|\blaud\w*|\blandanum\b|\bopi\w*m\b|\bopeum\b|\bmorphine\b|\bchloral\b|\bnarcot\w*|\barsn?ick\b|\barsenic\b|'
                             r'\barsentic\b|\bcarbolic\b|\bcorbolic\b|\bover ?dose\w*|\bover portion\b|\boverdose\w*|\bmercury\b|\beffects of medicine\b|\bonania poisan\b'),
    ('Alcoholism (intemperance)', r'\bintem\w*|\bintermperance\b|\balc\w*hol\w*|\bdrunk\w*|\bwhisk\w*|\bwhsky\b|\bdis+[ai]pation\b|\bintoxication\b|\bman\w*\s*(a\s*)?po\w*|\bmamaportu\b|\bmaniapotia\b'),
    ('Suffocation (smothered, overlaid)', r'\bsmo\w*th\w*r\w*|\boverlaid\b|\bsuf+ocat\w*|\bsufucation\b|\bstrang\w*|\bchoo?ked\b|\beff of grain in windpipe\b'),
    ('Exposure (heat or cold)', r'\bfro[sz]en\b|\bfrost\b|\bexp\w*sure\b|\bsun stro\w*|\bsunstroke\b|\bheat\b|\bovr het\b'),
    ('Wound (unspecified)', r'\bwound\w*|\bwonded\b'),
    ('Sudden Death', r'\bdied sudd?enly\b|\bsudden\w*|\bsuden\w*|\bsudenly\b|\bfound dead\b|\bfound dedd\b|\bfell dead\b'),
    ('Accident', r'\baccid\w*|\bacci\w*|\bacident\w*|\bacedent\w*|\bacehente\b|\bacedores\b|\baxident\w*|\bayiental\b|\bkill\w*|\bkild\b|\bkiled\b|'
                 r'\bfall\w*|\bfell\b|\bthrown\b|\bkick\w*|\brun over\b|\bcrushed\b|\bexplo\w*|\bblown up\b|\bblasting\b|\brailroad\b|'
                 r'\bfract\w*|\bfreture\b|\bbroken (back|limb)\b|\bconcus\w*|\binjury\b|\brat bite\b|\bhouse fell\b|'
                 r'\bauto\b|\bboun up\b|\bdrowned by\b|\bcut with\b'),
    ('Complications (unspecified)', r'\bcomplicat\w*|\bcomplation\b'),
    ('Fever (unspecified)', r'^(chronic |continued |cointinued |slow |nervous |winter |catar |inftn |inflammation |infl |catarrh |camp |coy |lifor fosell |worn )?fever$|'
                            r'^chills?$|^chill$|^catarrh$'),
    ('Inflammation (unspecified)', r'^inflammation$|^infl$|^inflmation$|^inflammation fever$'),
    ('Congestion (unspecified)', r'^congestion$|^conestion$|^conjeston$|^conjestion$|^congestion of s$|^cong of internalongon$'),
]
RULES_C = [(cat, re.compile(p)) for cat, p in RULES]


def clean_text(raw):
    """Normalized text with phrase and spelling fixes applied (used for matching and for the fallback label)."""
    t = ' '.join(SPELLING.get(w, w) for w in normalize(raw).split())
    for pat, rep in PHRASES:
        t = re.sub(pat, rep, t)
    return ' '.join(SPELLING.get(w, w) for w in t.split())


# Categories that win wherever they appear in the text: "liver cancer" is Cancer, not Liver Disease.
WINS_ANYWHERE = {'Cancer'}


def categorize(raw):
    """Return (Cause of Death Updated, how it was decided) for one raw value.

    Usually the category matched earliest in the text wins ("cancer and dropsy" -> Cancer,
    "dropsy of the heart" -> Dropsy); ties go to the rule listed first.
    """
    t = clean_text(raw)
    best = None
    for i, (cat, rx) in enumerate(RULES_C):
        m = rx.search(t)
        if not m:
            continue
        if cat in WINS_ANYWHERE:
            return cat, 'rule'
        if best is None or m.start() < best[0]:
            best = (m.start(), i, cat)
    if best is not None:
        return best[2], 'rule'
    return (t.title() if t else UNKNOWN), 'spelling only'
