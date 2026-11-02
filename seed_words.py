"""
seed_words.py — inserts 200 Farsi words into the database.
Run once:  python seed_words.py
"""
import database as db

WORDS = [
    # ── Greetings & Basics (15) ─────────────────────────────────────────────
    ("سلام",           "Greetings",  "salām",           "Hello"),
    ("خداحافظ",        "Greetings",  "khodāhāfez",      "Goodbye"),
    ("ممنون",          "Greetings",  "mamnun",           "Thank you"),
    ("بله",            "Greetings",  "bale",             "Yes"),
    ("نه",             "Greetings",  "na",               "No"),
    ("ببخشید",         "Greetings",  "bebakhshid",       "Excuse me / Sorry"),
    ("لطفاً",          "Greetings",  "lotfan",           "Please"),
    ("خوش آمدید",      "Greetings",  "khosh āmadid",    "Welcome"),
    ("چطوری؟",         "Greetings",  "chetori?",         "How are you?"),
    ("خوبم",           "Greetings",  "khubam",           "I am fine"),
    ("نمی‌فهمم",        "Greetings",  "nemifahmam",       "I don't understand"),
    ("کمک",            "Greetings",  "komak",            "Help"),
    ("مرسی",           "Greetings",  "mersi",            "Thanks (casual)"),
    ("صبح بخیر",       "Greetings",  "sobh bekheyr",     "Good morning"),
    ("شب بخیر",        "Greetings",  "shab bekheyr",     "Good night"),

    # ── Numbers (20) ────────────────────────────────────────────────────────
    ("صفر",            "Numbers",    "sefr",             "Zero"),
    ("یک",             "Numbers",    "yek",              "One"),
    ("دو",             "Numbers",    "do",               "Two"),
    ("سه",             "Numbers",    "se",               "Three"),
    ("چهار",           "Numbers",    "chahār",           "Four"),
    ("پنج",            "Numbers",    "panj",             "Five"),
    ("شش",             "Numbers",    "shesh",            "Six"),
    ("هفت",            "Numbers",    "haft",             "Seven"),
    ("هشت",            "Numbers",    "hasht",            "Eight"),
    ("نه",             "Numbers",    "noh",              "Nine"),
    ("ده",             "Numbers",    "dah",              "Ten"),
    ("یازده",          "Numbers",    "yāzdah",           "Eleven"),
    ("دوازده",         "Numbers",    "davāzdah",         "Twelve"),
    ("بیست",           "Numbers",    "bist",             "Twenty"),
    ("سی",             "Numbers",    "si",               "Thirty"),
    ("چهل",            "Numbers",    "chehel",           "Forty"),
    ("پنجاه",          "Numbers",    "panjāh",           "Fifty"),
    ("صد",             "Numbers",    "sad",              "One hundred"),
    ("هزار",           "Numbers",    "hezār",            "One thousand"),
    ("نیم",            "Numbers",    "nim",              "Half"),

    # ── Colors (10) ─────────────────────────────────────────────────────────
    ("قرمز",           "Colors",     "ghermez",          "Red"),
    ("آبی",            "Colors",     "ābi",              "Blue"),
    ("سبز",            "Colors",     "sabz",             "Green"),
    ("زرد",            "Colors",     "zard",             "Yellow"),
    ("سفید",           "Colors",     "sefid",            "White"),
    ("مشکی",           "Colors",     "meshki",           "Black"),
    ("نارنجی",         "Colors",     "nāranji",          "Orange"),
    ("بنفش",           "Colors",     "banafsh",          "Purple"),
    ("صورتی",          "Colors",     "surati",           "Pink"),
    ("قهوه‌ای",         "Colors",     "ghahveh-i",        "Brown"),

    # ── Family (10) ─────────────────────────────────────────────────────────
    ("مادر",           "Family",     "mādar",            "Mother"),
    ("پدر",            "Family",     "pedar",            "Father"),
    ("برادر",          "Family",     "barādar",          "Brother"),
    ("خواهر",          "Family",     "khāhar",           "Sister"),
    ("پسر",            "Family",     "pesar",            "Son"),
    ("دختر",           "Family",     "dokhtar",          "Daughter"),
    ("مادربزرگ",       "Family",     "mādarbozorg",      "Grandmother"),
    ("پدربزرگ",        "Family",     "pedarbozorg",      "Grandfather"),
    ("شوهر",           "Family",     "showhar",          "Husband"),
    ("زن",             "Family",     "zan",              "Wife / Woman"),

    # ── Body Parts (15) ─────────────────────────────────────────────────────
    ("سر",             "Body",       "sar",              "Head"),
    ("چشم",            "Body",       "cheshm",           "Eye"),
    ("گوش",            "Body",       "gush",             "Ear"),
    ("بینی",           "Body",       "bini",             "Nose"),
    ("دهان",           "Body",       "dahān",            "Mouth"),
    ("دست",            "Body",       "dast",             "Hand"),
    ("پا",             "Body",       "pā",               "Foot / Leg"),
    ("قلب",            "Body",       "qalb",             "Heart"),
    ("پشت",            "Body",       "posht",            "Back"),
    ("شکم",            "Body",       "shekam",           "Stomach"),
    ("مو",             "Body",       "mu",               "Hair"),
    ("دندان",          "Body",       "dandān",           "Tooth"),
    ("گردن",           "Body",       "gardan",           "Neck"),
    ("زانو",           "Body",       "zānu",             "Knee"),
    ("انگشت",          "Body",       "angosht",          "Finger"),

    # ── Food & Drink (20) ───────────────────────────────────────────────────
    ("آب",             "Food",       "āb",               "Water"),
    ("نان",            "Food",       "nān",              "Bread"),
    ("برنج",           "Food",       "berenj",           "Rice"),
    ("چای",            "Food",       "chāy",             "Tea"),
    ("قهوه",           "Food",       "qahve",            "Coffee"),
    ("شیر",            "Food",       "shir",             "Milk"),
    ("گوشت",           "Food",       "gusht",            "Meat"),
    ("مرغ",            "Food",       "morgh",            "Chicken"),
    ("ماهی",           "Food",       "māhi",             "Fish"),
    ("سبزی",           "Food",       "sabzi",            "Herbs / Greens"),
    ("میوه",           "Food",       "mive",             "Fruit"),
    ("سیب",            "Food",       "sib",              "Apple"),
    ("پرتقال",         "Food",       "porteghāl",        "Orange (fruit)"),
    ("انار",           "Food",       "anār",             "Pomegranate"),
    ("خرما",           "Food",       "khormā",           "Date (fruit)"),
    ("نمک",            "Food",       "namak",            "Salt"),
    ("شکر",            "Food",       "shekar",           "Sugar"),
    ("روغن",           "Food",       "roghan",           "Oil"),
    ("تخم‌مرغ",         "Food",       "tokhmmorgh",       "Egg"),
    ("سوپ",            "Food",       "sup",              "Soup"),

    # ── Animals (15) ────────────────────────────────────────────────────────
    ("سگ",             "Animals",    "sag",              "Dog"),
    ("گربه",           "Animals",    "gorbe",            "Cat"),
    ("اسب",            "Animals",    "asb",              "Horse"),
    ("گاو",            "Animals",    "gāv",              "Cow"),
    ("گوسفند",         "Animals",    "gusfand",          "Sheep"),
    ("فیل",            "Animals",    "fil",              "Elephant"),
    ("شتر",            "Animals",    "shotor",           "Camel"),
    ("پرنده",          "Animals",    "parande",          "Bird"),
    ("خرس",            "Animals",    "khers",            "Bear"),
    ("روباه",          "Animals",    "rubāh",            "Fox"),
    ("گرگ",            "Animals",    "gorg",             "Wolf"),
    ("خرگوش",          "Animals",    "khargush",         "Rabbit"),
    ("مار",            "Animals",    "mār",              "Snake"),
    ("موش",            "Animals",    "mush",             "Mouse / Rat"),
    ("ببر",            "Animals",    "babr",             "Tiger"),

    # ── Time & Calendar (15) ────────────────────────────────────────────────
    ("امروز",          "Time",       "emruz",            "Today"),
    ("فردا",           "Time",       "fardā",            "Tomorrow"),
    ("دیروز",          "Time",       "diruz",            "Yesterday"),
    ("صبح",            "Time",       "sobh",             "Morning"),
    ("ظهر",            "Time",       "zohr",             "Noon"),
    ("شب",             "Time",       "shab",             "Night"),
    ("هفته",           "Time",       "hafte",            "Week"),
    ("ماه",            "Time",       "māh",              "Month / Moon"),
    ("سال",            "Time",       "sāl",              "Year"),
    ("ساعت",           "Time",       "sāat",             "Hour / Clock"),
    ("دقیقه",          "Time",       "daghighe",         "Minute"),
    ("الان",           "Time",       "alān",             "Now"),
    ("زود",            "Time",       "zud",              "Early / Soon"),
    ("دیر",            "Time",       "dir",              "Late"),
    ("همیشه",          "Time",       "hamishe",          "Always"),

    # ── Places & Directions (15) ─────────────────────────────────────────────
    ("خانه",           "Places",     "khāne",            "Home / House"),
    ("مدرسه",          "Places",     "madrase",          "School"),
    ("بیمارستان",      "Places",     "bimārestān",       "Hospital"),
    ("بازار",          "Places",     "bāzār",            "Market / Bazaar"),
    ("مسجد",           "Places",     "masjed",           "Mosque"),
    ("رستوران",        "Places",     "restorān",         "Restaurant"),
    ("هتل",            "Places",     "hotel",            "Hotel"),
    ("راست",           "Places",     "rāst",             "Right"),
    ("چپ",             "Places",     "chap",             "Left"),
    ("مستقیم",         "Places",     "mostaghim",        "Straight ahead"),
    ("بالا",           "Places",     "bālā",             "Up / Above"),
    ("پایین",          "Places",     "pāyin",            "Down / Below"),
    ("نزدیک",          "Places",     "nazdik",           "Near / Close"),
    ("دور",            "Places",     "dur",              "Far"),
    ("خیابان",         "Places",     "khiābān",          "Street"),

    # ── Common Verbs (25) ───────────────────────────────────────────────────
    ("رفتن",           "Verbs",      "raftan",           "To go"),
    ("آمدن",           "Verbs",      "āmadan",           "To come"),
    ("خوردن",          "Verbs",      "khordan",          "To eat"),
    ("نوشیدن",         "Verbs",      "nushidan",         "To drink"),
    ("خوابیدن",        "Verbs",      "khābidan",         "To sleep"),
    ("نشستن",          "Verbs",      "neshestan",        "To sit"),
    ("ایستادن",        "Verbs",      "istādan",          "To stand"),
    ("دیدن",           "Verbs",      "didan",            "To see"),
    ("شنیدن",          "Verbs",      "shenidan",         "To hear"),
    ("گفتن",           "Verbs",      "goftan",           "To say / speak"),
    ("دانستن",         "Verbs",      "dānestan",         "To know"),
    ("خواستن",         "Verbs",      "khāstan",          "To want"),
    ("دوست داشتن",     "Verbs",      "dust dāshtan",     "To like / love"),
    ("داشتن",          "Verbs",      "dāshtan",          "To have"),
    ("بودن",           "Verbs",      "budan",            "To be"),
    ("خریدن",          "Verbs",      "kharidan",         "To buy"),
    ("فروختن",         "Verbs",      "forukhtan",        "To sell"),
    ("نوشتن",          "Verbs",      "neveshtan",        "To write"),
    ("خواندن",         "Verbs",      "khāndan",          "To read"),
    ("کار کردن",       "Verbs",      "kār kardan",       "To work"),
    ("بازی کردن",      "Verbs",      "bāzi kardan",      "To play"),
    ("فهمیدن",         "Verbs",      "fahmidan",         "To understand"),
    ("پرسیدن",         "Verbs",      "porsidan",         "To ask"),
    ("باز کردن",       "Verbs",      "bāz kardan",       "To open"),
    ("بستن",           "Verbs",      "bastan",           "To close"),

    # ── Common Adjectives (20) ──────────────────────────────────────────────
    ("بزرگ",           "Adjectives", "bozorg",           "Big / Large"),
    ("کوچک",           "Adjectives", "kuchak",           "Small / Little"),
    ("خوب",            "Adjectives", "khub",             "Good"),
    ("بد",             "Adjectives", "bad",              "Bad"),
    ("زیبا",           "Adjectives", "zibā",             "Beautiful"),
    ("قشنگ",           "Adjectives", "ghashang",         "Pretty / Nice"),
    ("قدیمی",          "Adjectives", "ghadimi",          "Old (object)"),
    ("جدید",           "Adjectives", "jadid",            "New"),
    ("گران",           "Adjectives", "gerān",            "Expensive"),
    ("ارزان",          "Adjectives", "arzān",            "Cheap"),
    ("سریع",           "Adjectives", "sari",             "Fast"),
    ("کند",            "Adjectives", "kond",             "Slow"),
    ("گرم",            "Adjectives", "garm",             "Warm / Hot"),
    ("سرد",            "Adjectives", "sard",             "Cold"),
    ("خوشحال",         "Adjectives", "khoshhāl",         "Happy"),
    ("غمگین",          "Adjectives", "ghamgin",          "Sad"),
    ("خسته",           "Adjectives", "khaste",           "Tired"),
    ("گرسنه",          "Adjectives", "gorosne",          "Hungry"),
    ("تشنه",           "Adjectives", "teshne",           "Thirsty"),
    ("سنگین",          "Adjectives", "sangin",           "Heavy"),

    # ── Pronouns & Connectors (10) ──────────────────────────────────────────
    ("من",             "Pronouns",   "man",              "I / Me"),
    ("تو",             "Pronouns",   "to",               "You (informal)"),
    ("شما",            "Pronouns",   "shomā",            "You (formal/plural)"),
    ("او",             "Pronouns",   "u",                "He / She / It"),
    ("ما",             "Pronouns",   "mā",               "We"),
    ("آنها",           "Pronouns",   "ānhā",             "They"),
    ("این",            "Pronouns",   "in",               "This"),
    ("آن",             "Pronouns",   "ān",               "That"),
    ("و",              "Pronouns",   "va",               "And"),
    ("یا",             "Pronouns",   "yā",               "Or"),

    # ── Clothes & Accessories (10) ──────────────────────────────────────────
    ("لباس",           "Clothes",    "lebās",            "Clothes / Dress"),
    ("پیراهن",         "Clothes",    "pirāhan",          "Shirt"),
    ("شلوار",          "Clothes",    "shalvār",          "Trousers / Pants"),
    ("کفش",            "Clothes",    "kafsh",            "Shoes"),
    ("جوراب",          "Clothes",    "jurāb",            "Socks"),
    ("کت",             "Clothes",    "kat",              "Jacket / Coat"),
    ("کلاه",           "Clothes",    "kolāh",            "Hat"),
    ("کیف",            "Clothes",    "kif",              "Bag"),
    ("عینک",           "Clothes",    "eynak",            "Glasses"),
    ("دستکش",          "Clothes",    "dastkash",         "Gloves"),
]


def seed():
    db.init_db()
    conn = db.get_conn()

    # Only seed if words table is empty
    existing = conn.execute('SELECT COUNT(*) FROM words').fetchone()[0]
    if existing > 0:
        print(f"Database already has {existing} words. Skipping seed.")
        conn.close()
        return

    for farsi, category, translit, english in WORDS:
        cur = conn.execute(
            'INSERT INTO words (farsi, english, transliteration, category) VALUES (?, ?, ?, ?)',
            (farsi, english, translit, category)
        )
        word_id = cur.lastrowid
        conn.execute(
            'INSERT INTO word_stats (word_id) VALUES (?)',
            (word_id,)
        )

    conn.commit()
    conn.close()
    print(f"✓  Seeded {len(WORDS)} Farsi words into the database.")


if __name__ == '__main__':
    seed()
