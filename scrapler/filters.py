"""

Dialect quality filters

Hard Rules

  - Reject if markers from other dialects appears
  - Reject if text is too short or mostly Latin/emoji

"""
import re

# a list of words/slang from the Iraqi dialect
IRAQI_DIALECT_MARKERS = [
    "شكو ماكو", "شكو", "ماكو", "أكو", 
    "لعد", "چا", "هسة", "هسه", 
    "شلونك", "شلونچ", "شلونج", "شگد", "شكد", 
    "هيج", "هيچ", "ياخويا", "يمعود", "يمعودة", "عيني",
    "صدگ", "صدك", "عبالي", "بلكت", "فد", "خوش", "كلش",
    "باوع", "تباوع", 
    "يندل", "أندل",
    "طفر", "يطفر",
    "يطب", "طب",
    "دير بالك",
    "عوف", "عوفه",
    "سديت", "سده",
    "دا",
    "هواية", "هوايه",
    "باجر", "باچر",
    "خطية", "ختية",
    "فدوة", "فدوه",
    "دربونة", "دربونه",
    "خاشوكة", "خاشوگه",
    "چطل", "جطل",
    "ميز", "قنفة",
    "صوندة", "صونده",
    "بنكة", "بنكه",
    "جام",
    "بطانية", "بطانيه"
]

# a list of distinct words/slang from other Arabic dialects 
# (Egyptian, Levantine, Maghrebi, Gulf, Sudanese)
BAD_DIALECT_MARKERS = [
    "دلوقتي", "عشان", "ازيك", "كده", "أوي", "بتاع", "بتاعتي", "إزاي", 
    "بص", "ليه", "فين", "مين", "امبارح", "بكره", "يسطا", "بجد", 
    "معلش", "خالص", "برضه", "عامل ايه", "ياعم", "جوا", "برا",
    "هيك", "بدي", "بدك", "شو", "عم", "مشان", "كيفك", "هلق", 
    "زلمة", "بركي", "قديش", "هاد", "هيدا", "كتير", "منيح", 
    "بكرة", "ليش", "وينك", "هلا",
    "بزاف", "واخا", "دابا", "ديالي", "ديالك", "واش", "برشا", 
    "يزي", "شنوة", "هدرة", "كيداير", "مليح", "صافي", "زوين", 
    "خايب", "كنبغيك", "باهي", "علاش", "فاش", "هكا",
    "وايد", "أبي", "تكفى", "وش", "ايش", "وشلونك", "ابشر", 
    "صج", "مره", "طال عمرك", "ريال", "دريشة", "وشو",
    "زول", "داير", "اسي", "سمح", "ياخ", "صاح"
]

# a simple Iraqi dialect lexicon, used to determine the topic 
# of the  scraped text, uses regex to catch variations such as 
# (ة / ه), (ك / گ), and (ج / چ)
TOPICS_MAP = {
  "politics": [
        r"سياس[ةه]", r"حكوم[ةه]", r"انتخاب", r"انتخابات",  r"برلمان", r"نواب", 
        r"مظاهرات", r"احزاب", r"خضراء", r"باكونا", r"باگونا", r"حرامي[ةه]", 
        r"بوك", r"بوگ",  r"فساد", r"مسؤول", r"ديموقراطي", r"ديمقراطي[ةه]",
  ],
    "food": [
        r"[أا]كل", r"مطعم", r"دولم[ةه]", r"باج[ةه]", r"قوزي", 
        r"تمن", r"تشريب", r"لف[ةه]", r"ل[گك]مة", r"زقنبوت", 
        r"عزيم[ةه]", r"[جچ]اي", r"ريو[گك]", r"غد[ةه]", r"عش[ةها]"
    ],
    "sports": [
        r"طوب[ةه]", r"لعب[ةه]", r"فريق", r"ملعب", r"دوري", 
        r"[گك]ول", r"حكم", r"منتخب", r"اسود", r"كلاسيكو", r"لواعيب"
    ],
    "religion": [
        r"دين", r"صلا[ةه]", r"جامع", r"حسيني[ةه]", r"زيار[ةه]", 
        r"مشاي[ةه]", r"مرجعي[ةه]", r"موكب", r"لطمي[ةه]", r"سيد", 
        r"شيخ", r"دعاء", r"ثواب", r"رسول", "الامام"
    ],
    "humor": [
        r"تحشيش", r"حشاش[ةه]", r"ضحك", r"خربان[ةه]", r"متت", 
        r"طر[گك]اع[ةه]", r"كارث[ةه]", r"نكت[ةه]", r"فاصل", r"يفطس"
    ],
    "family": [
        r"ع[يا]ل[ةه]", r"[أا]هل", r"جهال", r"مر[ةه]", r"زلم[ةه]", 
        r"رجال", r"اخوي[ةه]", r"اختي", r"ياب[ةه]", r"يم[ةه]", 
        r"بيبي", r"نساب[ةه]", r"رايب[گك]"
    ],
    "news": [
        r"خبر", r"عاجل", r"شكو ماكو", r"صد[گك]", r"انفجار", 
        r"ط[گك]", r"مقتل", r"وفا[ةه]", r"بيان", r"مراسل"
    ],
    "questions": [
        r"شنو", r"شلون", r"شون", r"ش[گك]د", r"ليش", r"شوكت", r"يمت[ىه]", 
        r"اكو واحد", r"بلا زحم[ةه]", r"س[ؤا]ال", r"استفسار", r"فدو[ةه]", 
        r"ممكن", r"منو يعرف", r"محتاج مساعد[ةه]"
    ],
    "discussions": [
        r"ر[أا]يكم", r"شرايكم", r"موضوع", r"نناقش", r"شاركونا", 
        r"تتفقون", r"شنو ر[أا]يك", r"وجه[ةه] نظر", r"نقاش", 
        r"شباب بنات", r"سالفتنا", r"وياي"
    ],
    "venting": [
        r"فضفض[ةه]", r"فظفظ[ةه]", r"مخنو[گكق]", r"ضايج", r"ط[گك]ت روحي", 
        r"تعبان", r"مقهور", r"[گك]لبي", r"كلبي", r"مهموم", 
        r"اريد احجي", r"طالع[ةه] روحي", r"واصل[ةه] لخشمي", 
        r"اكتئاب", r"حبيت افضفض"
    ],
    "jobs_education": [
        r"تعيين", r"شغل", r"دوام", r"راتب", r"واسط[ةه]", 
        r"سادس", r"جامع[ةه]", r"كلي[ةه]", r"امتحان", r"وزاري", 
        r"مدرس[ةه]", r"طالب", r"معدل", r"مكرم[ةه]", r"عطوة"
    ],
    "commerce": [
        r"بيع", r"شراء", r"مستعمل", r"سعر", r"توصيل", 
        r"للبيع", r"بيج", r"متوفر", r"قياسات", r"مارك[ةه]", 
        r"بال[ةه]", r"خاص", r"قطعة", r"عروض"
    ],
    "tech_gaming": [
        r"بوبجي", r"ببجي", r"نت", r"راوتر", r"فرمت[ةه]", 
        r"ايفون", r"جهاز", r"حاسب[ةه]", r"لابتوب", r"شحن", 
        r"رصيد", r"حساب", r"تهكير", r"تطبيق"
    ],
    "relationships": [
        r"حب", r"زواج", r"خطب[ةه]", r"عرس", r"حبيب", 
        r"خيان[ةه]", r"قسم[ةه]", r"نصيب", r"مكبل", r"حديق[ةه]",
        r"علاق[ةه]", r"زعلان"
    ],
    "health": [
        r"دكتور", r"مستشف[ىه]", r"مريض", r"صيدلي[ةه]", r"علاج", 
        r"وجع", r"عملي[ةه]", r"دوه", r"طبيب", r"تحاليل",
        r"عياد[ةه]", r"سلامتك"
    ]
}

def has_bad_markers(text: str) -> bool:
  """
  returns whether the data/text includes a bad dialect marker
  """
  words = set(text.split())
  return bool(words & BAD_DIALECT_MARKERS)

def has_iraqi_marker(text: str) -> bool:
  """
  returns whether the text includes an Iraqi dialect marker
  """
  return any(marker in text for marker in IRAQI_DIALECT_MARKERS)

def ratio(text: str) -> float:
  """
  fraction of characters that are Arabic scripts
  """
  if not text:
    return 0.0

  chars = sum(1 for char in text if "\u0600" <= char <= "\u06ff")
  return chars / len(text)

def clean(text: str) -> str:
  """
  normalizes the input text
  - removes (ـ) Tatweel from text (مـــرحـــبـــا) => (مرحبا)
  - removes repated characters (مررررححححببااا) => (مرحبا)
  """
  text = re.sub(r"_+", "", text)
  text = re.sub(r"(.)\1{2,}", r"\1\1", text)

  return text

def textray(text: str, title: str = "") -> list:
  """
  Like an X-ray for the input text

  Analyzes the input text and returns a sorted list of detecated topic(s),
  highest score first, if multiple topics have the same score, both of the
  topics are returned, sometimes I'll be 3 topics, and so on
  """
  combined = f"{title} {text}".strip()
  combined = clean(combined)

  scores = {topic: 0 for topic in TOPICS_MAP.keys()}
  for topic, patterns in TOPICS_MAP.items():
    for pattern in patterns:
      scores[topic] += len(re.findall(pattern, combined))

  active_topics = {topic: score for topic, score in scores.items() if score > 0}
  if not active_topics:
    return ["general"]

  topics = sorted(active_topics.keys(), key=lambda t: active_topics[t], reverse=True)
  return topics


def filter(text: str, min_ratio: float = .4) -> bool:
  """
  Runs the quality filters
  A minimal version for now, needs more strictness in the future
  """
  text = text.strip()
  if len(text) < 30:
    return False

  if ratio(text) < min_ratio:
    return False

  if has_bad_markers(text):
    return False
  
  return True