SUPPORTED_TRANSLATORS = [
    "google",
    "deepl",
    "yandex",
    "libre-translate",
    "microsoft",
    "chatgpt"
]
TRANSCRIPTION_SUPPORTED_LANGS = {"afrikaans":"af", "albanian":"sq", "amharic":"am", "arabic":"ar", "armenian":"hy", "assamese":"as", "azerbaijani":"az", "bashkir":"ba", "basque":"eu", "belarusian":"be", "bengali":"bn", "bosnian":"bs", "breton":"br", "bulgarian":"bg", "myanmar (burmese)":"my", "burmese (myanmar)": "my", "catalan":"ca", "valencian":"ca", "cantonese":"yue","chinese (cantonese / yue chinese)":"yue", "chinese (mandarin)": "zh", "mandarin":"zh", "croatian":"hr", "czech":"cs", "danish":"da", "dutch":"nl", "flemish":"nl", "english":"en", "estonian":"et", "faroese":"fo", "finnish":"fi", "french":"fr", "galician":"gl", "georgian":"ka", "german":"de", "greek":"el", "gujarati":"gu", "haitian creole":"ht", "haitian":"ht", "hausa":"ha", "hawaiian":"haw", "hebrew":"iw", "hindi":"hi", "hungarian":"hu", "icelandic":"is", "indonesian":"id", "italian":"it", "japanese":"ja", "javanese":"jw", "kannada":"kn", "kazakh":"kk", "cambodian (khmer)": "km", "khmer (cambodian)":"km", "korean":"ko", "lao":"lo", "latin":"la", "latvian":"lv", "lingala":"ln", "lithuanian":"lt", "luxembourgish":"lb", "lëtzebuergesch":"lb", "macedonian":"mk", "malagasy":"mg", "malay":"ms", "malayalam":"ml", "maltese":"mt", "maori":"mi", "marathi":"mr", "mongolian":"mn", "nepali":"ne", "norwegian":"no", "nynorsk":"nn", "occitan":"oc", "pushto (pashto)":"ps", "pashto (pushto)":"ps","farsi (persian)":"fa", "persian (farsi)":"fa", "polish":"pl", "portuguese":"pt", "punjabi (panjabi)":"pa", "panjabi (punjabi)": "pa", "romanian":"ro","moldavian (moldovan)":"ro", "moldovan (moldavian)":"ro", "russian":"ru", "sanskrit":"sa", "serbian":"sr", "shona":"sn", "sindhi":"sd", "sinhala (sinhalese)":"si", "sinhalese (sinhala)":"si", "slovak":"sk", "slovenian":"sl", "somali":"so", "spanish":"es", "castilian":"es", "sundanese":"su", "swahili":"sw", "swedish":"sv", "tagalog":"tl", "tajik":"tg", "tamil":"ta", "tatar":"tt", "telugu":"te", "thai":"th", "tibetan":"bo", "turkish":"tr", "turkmen":"tk", "ukrainian":"uk", "urdu":"ur", "uzbek":"uz", "vietnamese":"vi", "welsh":"cy", "yiddish":"yi", "yoruba":"yo"}
TRANSCRIPTION_SUPPORTED_MODELS = {"turbo","large-v3", "large-v2", "large", "medium", "small", "base", "tiny"}
TRANSLATION_SUPPORTED_LANGS = {'afrikaans': 'af', 'albanian': 'sq', 'amharic': 'am', 'arabic': 'ar', 'armenian': 'hy', 'assamese': 'as', 'aymara': 'ay', 'azerbaijani': 'az', 'bambara': 'bm', 'basque': 'eu', 'belarusian': 'be', 'bengali': 'bn', 'bhojpuri': 'bho', 'bosnian': 'bs', 'bulgarian': 'bg', 'catalan': 'ca', 'cebuano': 'ceb', 'chichewa': 'ny', 'chinese (simplified)': 'zh-CN', 'chinese (traditional)': 'zh-TW', 'corsican': 'co', 'croatian': 'hr', 'czech': 'cs', 'danish': 'da', 'dhivehi': 'dv', 'dogri': 'doi', 'dutch': 'nl', 'english': 'en', 'esperanto': 'eo', 'estonian': 'et', 'ewe': 'ee', 'filipino': 'tl', 'finnish': 'fi', 'french': 'fr', 'frisian': 'fy', 'galician': 'gl', 'georgian': 'ka', 'german': 'de', 'greek': 'el', 'guarani': 'gn', 'gujarati': 'gu', 'haitian creole': 'ht', 'hausa': 'ha', 'hawaiian': 'haw', 'hebrew': 'iw', 'hindi': 'hi', 'hmong': 'hmn', 'hungarian': 'hu', 'icelandic': 'is', 'igbo': 'ig', 'ilocano': 'ilo', 'indonesian': 'id', 'irish': 'ga', 'italian': 'it', 'japanese': 'ja', 'javanese': 'jw', 'kannada': 'kn', 'kazakh': 'kk', 'khmer': 'km', 'kinyarwanda': 'rw', 'konkani': 'gom', 'korean': 'ko', 'krio': 'kri', 'kurdish (kurmanji)': 'ku', 'kurdish (sorani)': 'ckb', 'kyrgyz': 'ky', 'lao': 'lo', 'latin': 'la', 'latvian': 'lv', 'lingala': 'ln', 'lithuanian': 'lt', 'luganda': 'lg', 'luxembourgish': 'lb', 'macedonian': 'mk', 'maithili': 'mai', 'malagasy': 'mg', 'malay': 'ms', 'malayalam': 'ml', 'maltese': 'mt', 'maori': 'mi', 'marathi': 'mr', 'meiteilon (manipuri)': 'mni-Mtei', 'mizo': 'lus', 'mongolian': 'mn', 'myanmar': 'my', 'nepali': 'ne', 'norwegian': 'no', 'odia (oriya)': 'or', 'oromo': 'om', 'pashto': 'ps', 'persian': 'fa', 'polish': 'pl', 'portuguese': 'pt', 'punjabi': 'pa', 'quechua': 'qu', 'romanian': 'ro', 'russian': 'ru', 'samoan': 'sm', 'sanskrit': 'sa', 'scots gaelic': 'gd', 'sepedi': 'nso', 'serbian': 'sr', 'sesotho': 'st', 'shona': 'sn', 'sindhi': 'sd', 'sinhala': 'si', 'slovak': 'sk', 'slovenian': 'sl', 'somali': 'so', 'spanish': 'es', 'sundanese': 'su', 'swahili': 'sw', 'swedish': 'sv', 'tajik': 'tg', 'tamil': 'ta', 'tatar': 'tt', 'telugu': 'te', 'thai': 'th', 'tigrinya': 'ti', 'tsonga': 'ts', 'turkish': 'tr', 'turkmen': 'tk', 'twi': 'ak', 'ukrainian': 'uk', 'urdu': 'ur', 'uyghur': 'ug', 'uzbek': 'uz', 'vietnamese': 'vi', 'welsh': 'cy', 'xhosa': 'xh', 'yiddish': 'yi', 'yoruba': 'yo', 'zulu': 'zu'}
GUI_MENU=[{
    'name': 'Help',
    'items': [{
        'type':'AboutDialog',
        'menuTitle':'About',
        'name': 'Subtitler',
        'description': "Use the power of Whisper to transcribe any video clip \nand generate it's subtitles (srt) file. \nAlso, use cutting-edge AI-power translation-services \nto translate the generated subtitles to any language you want.",
        'website': 'https://github.com/anupamkumar/subtitler',
        'developer': 'Anupam Kumar <https://anupamkumar.me>',
        'license': 'GPLv3'
    }, {
        'menuTitle': 'Documentation & Guide',
        'type': 'Link',
        'url': 'https://github.com/anupamkumar/subtitler/blob/master/README.md'
    }, {
        'menuTitle': 'License',
        'type': 'Link',
        'url': 'https://github.com/anupamkumar/subtitler/blob/master/LICENSE'
    }]
}]
