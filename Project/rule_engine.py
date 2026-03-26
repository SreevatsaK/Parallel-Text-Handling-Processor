import re
from collections import Counter

# ──────────────────────────────────────────────────────────────
#  POSITIVE WORDS
#  Comprehensive — covers everyday language, reviews, news
# ──────────────────────────────────────────────────────────────
POSITIVE_WORDS = {
    # Food / taste / experience
    "delicious","tasty","yummy","scrumptious","appetizing","flavorful",
    "flavourful","savory","savoury","fresh","crispy","tender","juicy",
    "satisfying","enjoyable","pleasant","pleasing","lovely","nice",
    "wonderful","beautiful","gorgeous","stunning","charming","elegant",
    "stylish","cozy","comfortable","welcoming","warm","friendly",

    # Quality / excellence
    "good","great","excellent","outstanding","superb","fantastic",
    "brilliant","perfect","exceptional","remarkable","impressive",
    "magnificent","splendid","terrific","phenomenal","extraordinary",
    "incredible","marvelous","awesome","best","fine","solid","decent",
    "quality","premium","superior","flawless","spotless","immaculate",

    # Emotions — positive
    "happy","happiness","joy","joyful","joyous","glad","pleased",
    "delighted","cheerful","excited","elated","proud","thrilled",
    "grateful","thankful","love","loved","loving","hope","hopeful",
    "optimistic","inspired","peaceful","content","satisfied","amused",
    "enthusiastic","passionate","confident","calm","relaxed","serene",

    # Performance / productivity
    "productive","productive","efficient","effective","capable","skilled",
    "talented","proficient","competent","expert","professional","dedicated",
    "diligent","hardworking","focused","motivated","proactive","resourceful",
    "accurate","precise","thorough","organized","punctual","reliable",
    "consistent","dependable","responsible","committed","cooperative",

    # Success / achievement
    "success","successful","achieve","achieved","achievement","accomplish",
    "accomplished","accomplishment","win","won","victory","triumph",
    "triumphant","champion","championship","award","reward","rewarded",
    "celebrate","celebrated","celebration","breakthrough","milestone",
    "record","secure","secured","approved","passed","promoted","recognized",

    # Growth / improvement
    "growth","grow","grew","improve","improved","improvement","progress",
    "progressed","advance","advanced","advancement","rise","rising","risen",
    "gain","gained","increase","increased","expand","expanded","expansion",
    "boost","boosted","thrive","thriving","flourish","flourishing","develop",
    "developed","development","enhance","enhanced","upgrade","upgraded",

    # Finance / business — positive
    "profit","profits","profitable","revenue","benefit","beneficial",
    "opportunity","opportunities","invest","investment","returns","savings",
    "affordable","reasonable","valuable","worthy","worthwhile","rewarding",

    # Innovation
    "innovative","innovation","creative","creativity","discover","discovered",
    "discovery","invent","invented","invention","solution","solve","solved",
    "smart","intelligent","clever","ingenious","insightful","visionary",

    # Strength / support
    "strong","stronger","strongest","strength","powerful","power",
    "support","supported","helpful","help","cooperation","unity","together",
    "safe","safety","protected","recover","recovered","recovery","restore",
    "restored","resolution","resolved","fixed","repaired","healed","cured",

    # Service / experience
    "fast","quick","prompt","swift","speedy","responsive","attentive",
    "courteous","polite","kind","caring","generous","helpful","accommodating",
    "smooth","seamless","easy","simple","convenient","accessible","clear",

    # Common everyday positive words often missed
    "amazing","love","fun","cool","brilliant","happy","perfect","enjoy",
    "enjoyed","enjoying","delight","delightful","pleasure","pleasurable",
    "memorable","spectacular","outstanding","fabulous","glorious","radiant",
    "vibrant","lively","energetic","exciting","thrilling","uplifting","heartfelt",
    "touching","moving","inspiring","refreshing","rejuvenating","revitalizing",
    "nourishing","healthy","wholesome","natural","authentic","genuine","honest",
    "transparent","fair","just","ethical","responsible","sustainable","green",
    "clean","tidy","neat","organized","efficient","streamlined","optimized",
    "improved","better","best","top","leading","outstanding","award",
    "praised","acclaimed","celebrated","recognized","respected","trusted",
    "popular","preferred","recommended","approved","endorsed","verified",
}

# ──────────────────────────────────────────────────────────────
#  NEGATIVE WORDS
#  Comprehensive — covers everyday language, reviews, news
# ──────────────────────────────────────────────────────────────
NEGATIVE_WORDS = {
    # Food / experience — negative
    "bland","tasteless","stale","cold","overcooked","undercooked","burnt",
    "soggy","greasy","oily","spicy","bitter","sour","rotten","spoiled",
    "disgusting","revolting","nauseating","unpleasant","awful","terrible",
    "horrible","dreadful","appalling","atrocious","mediocre","inferior",

    # Service / performance — negative
    "slow","slower","slowest","sluggish","delayed","overdue","late","tardy",
    "longer","lengthy","prolonged","extended","dragged","dragging","tedious",
    "boring","dull","monotonous","repetitive","redundant","wasteful",
    "inefficient","ineffective","incompetent","careless","negligent",
    "unprofessional","unreliable","inconsistent","disorganized","chaotic",
    "confusing","complicated","difficult","hard","tough","challenging",
    "frustrating","annoying","irritating","aggravating","overwhelming",
    "exhausting","tiring","draining","stressful","demanding","burdensome",

    # Quality — negative
    "bad","worst","poor","inferior","defective","flawed","faulty","broken",
    "damaged","worn","dirty","messy","cluttered","cramped","noisy","loud",
    "uncomfortable","inconvenient","impractical","useless","worthless",
    "disappointing","disappointed","unsatisfactory","inadequate","lacking",
    "insufficient","limited","restricted","overpriced","expensive","costly",

    # Emotions — negative
    "sad","sadness","unhappy","sorrow","sorrowful","grief","grieve",
    "miserable","misery","despair","desperate","hopeless","depressed",
    "depression","anxiety","anxious","fear","fearful","scared","frightened",
    "panic","panicked","stress","stressed","worry","worried","anger",
    "angry","rage","furious","hatred","hate","disgusted","shame","shameful",
    "guilt","guilty","lonely","loneliness","suffering","suffer","anguish",
    "agony","upset","distressed","troubled","concerned","nervous","uneasy",

    # Failure / loss
    "fail","failed","failure","lose","lost","loss","defeat","defeated",
    "collapse","collapsed","decline","declined","fall","fell","fallen",
    "drop","dropped","decrease","decreased","shrink","shrunk","worsen",
    "worsened","deteriorate","deteriorated","regress","regressed",

    # Conflict / harm
    "war","wars","conflict","conflicts","violence","violent","attack",
    "attacked","assault","assaulted","kill","killed","death","deaths",
    "murder","murdered","crime","criminal","terror","terrorist","terrorism",
    "threat","threats","danger","dangerous","harm","harmful","hurt",
    "injury","injure","injured","damage","damaged","destroy","destroyed",
    "destruction","abuse","abused","exploit","exploited","oppress",
    "oppressed","oppression","corrupt","corruption","fraud","fraudulent",
    "steal","stolen","theft","lie","lied","lies","cheat","cheated",

    # Economic / social — negative
    "crisis","crises","disaster","disasters","catastrophe","catastrophic",
    "tragedy","tragic","emergency","recession","bankrupt","bankruptcy",
    "debt","deficit","shortage","shortages","poverty","inequality",
    "injustice","unjust","discrimination","prejudice","protest","protests",
    "riot","riots","scandal","scandals","controversy","controversial",

    # Health — negative
    "disease","illness","sick","sickness","pandemic","epidemic","virus",
    "infection","infected","contaminate","contaminated","pollution",
    "polluted","toxic","poison","poisoned","unhealthy","unwell","painful",

    # Weakness / problems
    "weak","weaker","weakness","problem","problems","issue","issues",
    "error","errors","bug","bugs","flaw","flaws","mistake","mistakes",
    "wrong","incorrect","false","fake","invalid","breach","breached",
    "leak","leaked","hack","hacked","risk","risks","vulnerable",
    "vulnerability","unstable","instability","uncertain","uncertainty",
    "doubt","doubtful","suspicious","suspect","unreliable","untrustworthy",
}

# ──────────────────────────────────────────────────────────────
#  CONTRAST CONJUNCTIONS
#  Words that signal a shift in sentiment within the sentence
#  e.g. "good BUT slow" → the clause after BUT often contradicts
# ──────────────────────────────────────────────────────────────
CONTRAST_WORDS = {
    "but","yet","however","though","although","nevertheless","nonetheless",
    "despite","whereas","while","whilst","except","except","unfortunately",
    "sadly","regrettably","disappointingly","still","even","though",
}

# ──────────────────────────────────────────────────────────────
#  NEGATION WORDS
# ──────────────────────────────────────────────────────────────
NEGATION_WORDS = {
    "not","no","never","neither","nor","nobody","nothing","nowhere",
    "hardly","barely","scarcely","without","lack","lacking","lacks",
    "cannot","cant","wont","dont","doesnt","didnt","isnt","wasnt",
    "wouldnt","shouldnt","couldnt","havent","hasnt","hadnt",
}

# ──────────────────────────────────────────────────────────────
#  PREFIX MORPHOLOGY
#  Only applied when root is confirmed in word lists
# ──────────────────────────────────────────────────────────────
_NEG_PREFIXES = ("un","dis","mis","im","in","ir","il","non","anti","de","mal")
_POS_PREFIXES = ("super","ultra","hyper","mega","over","re","pro")

# ──────────────────────────────────────────────────────────────
#  THEME DETECTION
# ──────────────────────────────────────────────────────────────
THEME_SEEDS = {
    "Economy":     {"market","inflation","gdp","economy","currency","growth",
                    "trade","revenue","profit","investment","fiscal","monetary",
                    "stock","shares","tax","budget","finance","economic"},
    "Politics":    {"government","minister","parliament","policy","election",
                    "president","senate","congress","law","regulation","vote",
                    "political","party","democracy","governor","legislation"},
    "Technology":  {"software","ai","technology","platform","system","data",
                    "algorithm","machine","network","digital","code","cyber",
                    "internet","computer","robot","automation","cloud","app"},
    "Sports":      {"team","match","league","coach","tournament","player",
                    "game","score","win","champion","athlete","stadium",
                    "football","cricket","basketball","soccer","tennis"},
    "Health":      {"health","medical","hospital","disease","virus","vaccine",
                    "patient","doctor","treatment","cure","pandemic","wellness",
                    "medicine","surgery","therapy","nurse","clinic","drug"},
    "World":       {"international","global","summit","organization","conflict",
                    "country","nation","border","treaty","alliance","foreign",
                    "united","nations","diplomatic","ambassador","military"},
    "Environment": {"climate","environment","pollution","energy","carbon",
                    "renewable","solar","emission","forest","ocean","species",
                    "earthquake","flood","drought","wildfire","sustainability"},
    "Education":   {"school","university","student","education","research",
                    "learning","teacher","curriculum","degree","knowledge",
                    "college","professor","exam","scholarship","academic"},
    "Business":    {"company","corporation","business","industry","market",
                    "ceo","executive","merger","acquisition","startup",
                    "brand","product","sales","customer","supply","demand"},
    "Crime":       {"crime","criminal","police","arrest","court","prison",
                    "sentence","verdict","murder","robbery","theft","fraud",
                    "investigation","suspect","evidence","trial","judge"},
}

# ──────────────────────────────────────────────────────────────
#  SCORING THRESHOLDS
# ──────────────────────────────────────────────────────────────
def _score_to_label(score: int) -> str:
    if score == 0:
        return "Neutral"
    elif score >= 5:
        return "Strongly Positive"
    elif score >= 1:
        return "Positive"
    elif score <= -5:
        return "Strongly Negative"
    else:
        return "Negative"   # score <= -1


# ──────────────────────────────────────────────────────────────
#  WORD POLARITY LOOKUP
# ──────────────────────────────────────────────────────────────
def _word_polarity(word: str) -> int:
    """Returns +1, -1, or 0. No suffix guessing."""
    w = word.lower()

    # 1. Direct match
    if w in POSITIVE_WORDS:
        return 1
    if w in NEGATIVE_WORDS:
        return -1

    # 2. Negative prefix — only if root is in POSITIVE_WORDS
    for pfx in _NEG_PREFIXES:
        if w.startswith(pfx) and len(w) > len(pfx) + 2:
            root = w[len(pfx):]
            if root in POSITIVE_WORDS:
                return -1   # un+happy, dis+honest, mis+trust

    # 3. Positive prefix — only if root is in POSITIVE_WORDS
    for pfx in _POS_PREFIXES:
        if w.startswith(pfx) and len(w) > len(pfx) + 2:
            root = w[len(pfx):]
            if root in POSITIVE_WORDS:
                return 1

    return 0


# ──────────────────────────────────────────────────────────────
#  CLAUSE SCORER
#  Scores a list of tokens as a single clause
#  Handles negation within the clause
# ──────────────────────────────────────────────────────────────
def _score_clause(tokens: list) -> tuple:
    """
    Returns (score, pos_hits, neg_hits) for a list of tokens.

    Negation rules:
      - "not good"  → negated positive  → -1  (absence of good = bad)
      - "not bad"   → negated negative  →  0  (absence of bad ≠ good,
                                               just means not bad)
      - "not great" → negated positive  → -1
      - "not terrible" → negated negative → 0

    Reasoning: "not bad" only means something isn't bad — it does NOT
    confirm it is good. So it contributes 0, not +1.
    Only a directly positive word earns a +1.
    """
    score     = 0
    pos_hits  = {}
    neg_hits  = {}
    negated   = False

    for word in tokens:
        if word in NEGATION_WORDS:
            negated = True
            continue

        polarity = _word_polarity(word)

        if polarity != 0:
            if negated:
                if polarity > 0:
                    # "not good" → flip positive to negative → -1
                    polarity = -1
                    neg_hits[word] = neg_hits.get(word, 0) + 1
                    score -= 1
                else:
                    # "not bad" → negated negative → 0 (neutral, not positive)
                    polarity = 0   # contributes nothing
            else:
                if polarity > 0:
                    pos_hits[word] = pos_hits.get(word, 0) + 1
                    score += 1
                else:
                    neg_hits[word] = neg_hits.get(word, 0) + 1
                    score -= 1

            negated = False   # reset after consuming sentiment word

    return score, pos_hits, neg_hits


# ──────────────────────────────────────────────────────────────
#  MAIN ANALYSIS FUNCTION
# ──────────────────────────────────────────────────────────────
def analyze_chunk(text: str) -> dict:
    """
    Analyze text with:
      - Clause-level scoring split at contrast conjunctions
        (but / yet / however / although / etc.)
      - Each clause scored independently then summed
      - Negation within each clause
      - No intensifiers, no suffix guessing
      - Repetition counts per clause
    """
    if not text or not text.strip():
        return _empty_result()

    # Tokenize
    tokens = re.findall(r"\b[a-zA-Z']+\b", text.lower())
    if not tokens:
        return _empty_result()

    # ── Split into clauses at contrast conjunctions ───────────
    # e.g. "productive yet took longer" →
    #      clause1: ["productive"]
    #      clause2: ["took", "longer"]
    clauses = []
    current = []
    for token in tokens:
        if token in CONTRAST_WORDS:
            if current:
                clauses.append(current)
            current = []
        else:
            current.append(token)
    if current:
        clauses.append(current)

    if not clauses:
        clauses = [tokens]

    # ── Score each clause independently ───────────────────────
    total_score = 0
    all_pos     = {}
    all_neg     = {}

    for clause in clauses:
        c_score, c_pos, c_neg = _score_clause(clause)
        total_score += c_score
        for w, v in c_pos.items():
            all_pos[w] = all_pos.get(w, 0) + v
        for w, v in c_neg.items():
            all_neg[w] = all_neg.get(w, 0) + v

    # ── Label ─────────────────────────────────────────────────
    sentiment_label = _score_to_label(total_score)

    # ── Theme detection ───────────────────────────────────────
    token_set = set(tokens)
    detected_themes = [
        theme for theme, kws in THEME_SEEDS.items()
        if token_set & kws
    ]
    if not detected_themes:
        detected_themes.append("General")

    all_keywords = list(all_pos.keys()) + list(all_neg.keys())
    word_counts  = Counter(tokens)

    return {
        "sentiment_score":  total_score,
        "sentiment_label":  sentiment_label,
        "themes":           detected_themes,
        "keywords":         all_keywords,
        "keyword_count":    len(all_keywords),
        "positive_words":   list(all_pos.keys()),
        "negative_words":   list(all_neg.keys()),
        "word_frequencies": dict(word_counts.most_common(20)),
    }


def _empty_result() -> dict:
    return {
        "sentiment_score":  0,
        "sentiment_label":  "Neutral",
        "themes":           ["General"],
        "keywords":         [],
        "keyword_count":    0,
        "positive_words":   [],
        "negative_words":   [],
        "word_frequencies": {},
    }
