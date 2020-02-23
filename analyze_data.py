
from os.path import isfile
from zipfile import ZipFile
import re
import sqlite3
import vdu_nlp_services.soap_stressor
import vdu_nlp_services.morphological_analyzer
from vdu_nlp_services import stress_text, rebuild_text, fused_stress_replacements
from vdu_nlp_services.fused_stressor import _stress_re
from phonology_engine import PhonologyEngine
from re_map import Processor
import difflib
from corner_cases import cases
from utils import *

fused_prepare_pattern = re.compile(r'(\w)[`~^]')

lett = u'A-Za-zĄ-Žą-ž'

global_replacements = [
    (u'\xa0', u' '),
    (u'\xad', u''),
    (u'…', u'...'),
    #(u'Nebesu-modama', u'Nebesumodama'),
    (r'\(([' + lett + r']+)\)', r' \1 '),
    (r'([' + lett + r']+)[-—]', r'\1 '),
    (r'[-—]([' + lett + r']+)', r' \1'),
    (r'(?<!\w)([A-Z])\.([A-Za-z])', r'\1 \2'),

    (r'([' + lett + r']+)[~`^]([' + lett + r']*)', r'\1\2'),

    (u"[âåãáǎäăāàá]", 'a'),
    (u'[îīíiîīĭíìiıі]', "i"),
    (u'[ùüüûú]', "u"),
    (u'[èêééëё]', 'e'),
    (u'[ôöőóòø]', "o"),
    (u'[ʞ]', "k"),
    (u'[ɯ]', "m"),
    (u'[ǝ]', "e"),
    (u'ð', "d"),
    (u'[ØŐ]', "O"),
    (u'″', '"'),
    (r' a\.a\. ', ' a a '),
    (r' a\. a\. ', ' a a '),
    (r'TU Wien  Viena', 'TU Viena'),
    (u'[−˗‐‐‑‒–—―]', "-"),


    # https://jrgraphix.net/research/unicode_blocks.php
    (u'[\u02B0-\u02FF]', ' '), # Spacing Modifier Letters
    (u'[\u0370-\u03FF]', ' '), #Greek and Coptic
    (u'[\u4E00-\u62FF\u6300-\u77FF\u7800-\u8CFF\u8D00-\u9FFF]', ' '), #CJK Unified Ideographs
    (u"[\u0400-\u04FF\u0500-\u052F]", ' '), #Cyrillic
    (u"[\u0600-\u06FF]", ' '), # Arabic
    (u"[\u1F00-\u1FFF]", ' '), # Greek Extended
    (u"[\u2100-\u214F]", ' '), # Letterlike Symbols
    (u"[\u2150-\u218F]", ' '), # Number Forms
    (u"[\u2200-\u22FF]", ' '), # Mathematical Operators
    (u"[\u2300-\u23FF]", ' '), # Miscellaneous Technical
    (u"[\u2600-\u26FF]", ' '), # Miscellaneous Symbols
    (u"[\u2070-\u209F]", ' '), # Superscripts and Subscripts
    (u"[\uE000-\uF8FF]", ' '), # Private Use Area    
    (u"[\uFE70-\uFEFF]", ' '), # Arabic Presentation Forms-B
    (u"[\U0001D400-\U0001D7FF]", ' '), # Mathematical Alphanumeric Symbols

    #Combining Diacritical Marks
    (u'[\u0300-\u036F]', ''),

    # turkish
    (u"ç", 'c'), (u"Ç", 'C'), (u"ç", 'c'), (u"Ç", 'C'), (u"ğ", 'g'), (u"Ğ", 'G'), 
    (u"Ö", 'O'), (u"ö", 'o'), (u"Ş", 'S'), (u"ş", 's'), (u"Ü", 'U'), (u"ü", 'u'),  
    #hebrew'
    (u'[\u0591-\u05f4]', ' '),

    (u'[\u2184]', ' '),

    

    (u"[🙂😉😀\xba\u2005\u2009\u2002\u202f⁹❖◄¡∝]", ' '),
    (u"Á", 'A'),
    (u'№', 'Nr.'),
    (u'℃', 'C'),
    (u"ñ", 'n'),
    (u'[ʼʿʾ]', "'"),
    (u'[čč]', "č"),
    (u'ỹ', "y"),
    (u'ą', "ą"),
    (u'į', "į"),
    (u'Ê', "E"),
    (u'ū', "ū"),
    (u'ų', "ų"),
    (u'š', "š"),
    (u'ė', "ė"),
    (u'Ṣ', "S"),
    (u'Š', "Š"),
    (u'Ḥ', 'H'),
    (u'ř', 'r'),
    (u"π", 'p'),
    (u"ḥ", 'h'),
    (u"ç", 'c'),
    (u"ƒ", 'f'),
    (u"\u03b2", u'b'),
    (u"₂", '2'),
    (u"[\u200a\u2060]", ' '),

    (r'“\[', r'“ ['),
    #(u"[蔡英文]", ' '),

    (r'(\w+)[\'`](\w+)', r'\1\2'),
    #(u'Kaž-kas', u'Kažkas'),
    #(u'a-ha', u'aha'),
    #(u'Watergate`o', u'Watergateoo'),
    (u'diskusija@circulareconomy', u'diskusija et circulareconomy')
]

re_global_replacement = '|'.join([p for p,_ in global_replacements])
global_replacement_pattern = re.compile(re_global_replacement)


valid_letter_pattern = re.compile(u"[a-zą-ž–-]", re.IGNORECASE)

exceptions = [
    {
        'article_url': 'http://pakeliui.popo.lt/2019/01/23/apie-tikejima-ir-pasitikejima/',
        'block_index': [4, 5, 7],
        'sub': (u'Doubeyazt', u'Dogubeyazit')
    }, 
    {
        'article_url': 'http://pakeliui.popo.lt/2019/01/23/apie-tikejima-ir-pasitikejima/',
        'block_index': [4, 5, 7],
        'sub': (u'Doubeyazt', u'Dogubeyazit')
    }, 
    {
        'article_url': 'http://www.technologijos.lt/n/mokslas/istorija_ir_archeologija/S-77994/straipsnis/Radinys-naciu-stovykloje-irodo-tai-ka-politikai-bande-paneigti',
        #'block_index': [2, 3, 8],
        'sub': (u'Vaeka', u'Vareka')
    },
    {
        'article_url': 'http://www.technologijos.lt/n/mokslas/istorija_ir_archeologija/S-77994/straipsnis/Radinys-naciu-stovykloje-irodo-tai-ka-politikai-bande-paneigti',
        #'block_index': [2, 3, 8],
        'sub': (u'Vaekos', u'Varekos')
    },
    {
        'article_url': 'http://www.technologijos.lt/n/mokslas/idomusis_mokslas/S-77663/straipsnis/Skaiciavimo-masinu-istorija-kur-yra-pati-silpniausia-daugumos-siuolaikiniu-procesoriu-vieta-kaip-atsirado-ir-kas-negerai-su-voniNeumanno-architektura-ir-ka-tokio-ekspertai-surado-Intel-procesoriuose-',
        #'block_index': [2, 3, 8],
        'sub': (u'Erds', u'Erdős')
    }
]

_except_stress_pattern = re.compile('[^~`^]')
_subblock_pattern = re.compile(r'(.*[!?\.]?)(\s+\n)|(.*[!?\.]?)([ \n]*)|([ \n]*)([A-ZĄ-Ž].*)')

def stress_text_ex(text, version='8.0'):
    res = ''

    output = stress_text('_.' + text, version)[2:]
    res = restore_vdu_stressed_text(text, output)
    return res

def collapse_stress_options(word, output):
    raw_stress_options = filter(None, output.split('\n'))
    stress_options = []
    max_opts = 0

    for rso in raw_stress_options:
        m = _stress_re.match(rso)
        if m:
            stressed_word = m.word(1)
            grammar_specs = m.group(2).split(' ') if m.group(2) else []
            stress_options.append( (stressed_word, grammar_specs) )
        else:
            if word == rso or ' ' not in rso:
                stress_options.append( (rso, []) )
                max_opts = 1
            else:
                raise Exception()

    if max_opts and len(stress_options) > max_opts:
        raise Exception()

    return stress_options[0][0]

def create_tables(cursor):
    queries = [
        '''CREATE TABLE IF NOT EXISTS "stress_text_cache" (
            "hash"	INTEGER NOT NULL PRIMARY KEY UNIQUE,
            "text"	TEXT NOT NULL
        )'''
        ,
        '''CREATE TABLE IF NOT EXISTS "morphology_cache" (
            "hash"	INTEGER NOT NULL PRIMARY KEY UNIQUE,
            "text"	TEXT NOT NULL
        )'''
    ]
    
    for q in queries:
        cursor.execute(q)

def load_cache(cursor):
    cursor.execute('SELECT `hash`, `text` FROM `stress_text_cache`')
    for h, out in cursor:
        result = {'out': out, 'Info': None, 'Klaida': None}
        vdu_nlp_services.soap_stressor._stress_text_cache[h] = result

    cursor.execute('SELECT `hash`, `text` FROM `morphology_cache`')
    for h, text in cursor:
        vdu_nlp_services.morphological_analyzer._morphology_cache[h] = text
  

if __name__ == "__main__":
    dbfname = 'data3.sqlite.db'
    dbzipfname = 'data3.zip'

    if not isfile(dbfname) and isfile(dbzipfname):
        with ZipFile(dbzipfname, 'r') as zipObj:
            zipObj.extractall()
        
    conn = sqlite3.connect(dbfname)
    cursor = conn.cursor()
    cache_cursor = conn.cursor()

    create_tables(cursor)

    def set_stress_text_cache(h, result):
        vdu_nlp_services.soap_stressor._stress_text_cache[h] = result
        try:
            cache_cursor.execute("INSERT INTO stress_text_cache (hash, text) VALUES (?,?)", (h, result['out']))
        except Exception as e:
            print(e)

    def set_morphology_cache(h, text):
        vdu_nlp_services.morphological_analyzer._morphology_cache[h] = text
        try:
            cache_cursor.execute("INSERT INTO morphology_cache (hash, text) VALUES (?,?)", (h, text))
        except Exception as e:
            print(e)

    vdu_nlp_services.soap_stressor.set_stress_text_cache = set_stress_text_cache
    vdu_nlp_services.morphological_analyzer.set_morphology_cache = set_morphology_cache

    load_cache(cursor)

    for i, exception in enumerate(exceptions):
        cursor.execute('SELECT id FROM articles WHERE `url` = ?', (exception['article_url'],))
        for res in cursor:
            if 'article_id' not in exceptions[i]:
                exceptions[i]['article_id'] = []
            exceptions[i]['article_id'].append(res[0])

    cursor.execute('SELECT article_id, `index`, block, url FROM article_blocks JOIN articles ON article_id = id WHERE article_id >= 0')

    pe = PhonologyEngine()
    strip_acc = lambda x: re.sub(r'[\^~`]', '', x)
    pattern_acc = re.compile(r'[\^~`]')

    letter_pattern = u'A-ZĄ-Ža-zą-ž'
    pattern =  r'([' + letter_pattern + r']+[\^~`]([' + letter_pattern + r']+[\^~`]?)*)'

    make_stress_results = lambda dst_text, mappings: [
            (dst_text[dst_span[0]:dst_span[1]], src_span) 
            for src_span, dst_span in mappings if pattern_acc.search(dst_text[dst_span[0]:dst_span[1]])
        ]

    for i, (article_id, index, block, url) in enumerate(cursor):
        if not block:
            continue

        if i % 10 == 0:
            conn.commit()
        

        if global_replacement_pattern.search(block):
            for p, repl in global_replacements:
                block = re.sub(p, repl, block)
    
        pattern_exceptions = []
        for m in re.finditer(pattern, block):
            word = m.group()
            pattern_exceptions.append((re.escape(word), word))
            pattern_exceptions.append((re.escape(stress_text_ex(word)), word))

        if (article_id, index) in cases:
            article_id = article_id
            
        exc_ = [e for e in exceptions if article_id in e['article_id']]
        fused_replacements, augmented_elements = fused_stress_replacements(block, exc_)
        fused_stress_text, fused_stress_mappings = rebuild_text(augmented_elements, fused_replacements)
        fused_stress_results = make_stress_results(fused_stress_text, fused_stress_mappings)
        
        stressed_text = stress_text_ex(block)
        with Processor(stressed_text) as processor:
            replacement_map = { 1: strip_acc }
            processor.process(pattern, replacement_map, exceptions=pattern_exceptions)
            processor.swap()
            
        stressed_results = make_stress_results(stressed_text, processor.span_map)

        if processor.text.strip() != block.strip(): 
            print()   
            for i,s in enumerate(difflib.ndiff(block, re.sub(r'[~`^]', '', stressed_text))):
                if s[0]==' ': continue
                elif s[0]=='-':
                    print(u'Delete "{}" from position {}'.format(s[-1],i))
                elif s[0]=='+':
                    print(u'Add "{}" to position {}'.format(s[-1],i)) 
                    pos = None
                       
            print()   
            raise Exception()

        try:
            liepa_results = list(stress_text_liepa(pe, block))
        except UnicodeEncodeError as e:
            bad_string = e.object[e.start:e.end]
            liepa_results = list(stress_text_liepa(pe, block))

        spans, different_spans = compare_replacements(block, [fused_stress_results, stressed_results, liepa_results])
        print ('\r%d, %d     ' % (article_id, index), end='')
        test_different_stresses(block, spans)
        #print (article_id, index)
        #print ()
        #print (block)
        #print ()
        #show_different_spans(block, different_spans)
        #print ('\n=====================')

    conn.close()