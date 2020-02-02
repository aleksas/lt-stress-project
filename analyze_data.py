
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
from utils import *

global_replacements = [
    (u'\xa0', u' '),
    (u'\xad', u''),
    (u'Nebesu-modama', u'Nebesumodama'),
    (u'Kaž-kas', u'Kažkas')
]
re_global_replacement = '|'.join([p for p,_ in global_replacements])
global_replacement_pattern = re.compile(re_global_replacement)

liepa_single_char_re_replacements = [
    (u"[А-Яа-яμ🙂😀\xba\u2005\u202fΔ❖]", ' '),
    (u"[ú]", 'u'),
    (u"[âãáāà]", 'a'),
    (u"ñ", 'n'),
    (u'[ʼʿʾ]', "'"),
    (u'ī', "i"),
    (u'Ṣ', "S"),
    (u'Ḥ', 'H'),
    (u"π", 'p'),
    (u"ç", 'c'),
    (u"î", 'i'),
    (u"₂", '2'),
    (u"[\u200a\u2060]", ' '),
]
liepa_re_char_replacement = '|'.join([p for p,_ in liepa_single_char_re_replacements])
liepa_re_char_replacement_pattern = re.compile(liepa_re_char_replacement)

valid_letter_pattern = re.compile(u"[a-zą-ž–-]", re.IGNORECASE)

exceptions = [
    {
        'article_url': 'http://pakeliui.popo.lt/2019/01/23/apie-tikejima-ir-pasitikejima/',
        'block_index': [4, 5, 7],
        'sub': (u'Doubeyazt', u'Doğubeyazıt')
    }, 
    {
        'article_url': 'http://pakeliui.popo.lt/2019/01/23/apie-tikejima-ir-pasitikejima/',
        'block_index': [4, 5, 7],
        'sub': (u'Doubeyazt', u'Doğubeyazıt')
    }, 
    {
        'article_url': 'http://www.technologijos.lt/n/mokslas/istorija_ir_archeologija/S-77994/straipsnis/Radinys-naciu-stovykloje-irodo-tai-ka-politikai-bande-paneigti',
        #'block_index': [2, 3, 8],
        'sub': (u'Vaeka', u'Vařeka')
    },
    {
        'article_url': 'http://www.technologijos.lt/n/mokslas/istorija_ir_archeologija/S-77994/straipsnis/Radinys-naciu-stovykloje-irodo-tai-ka-politikai-bande-paneigti',
        #'block_index': [2, 3, 8],
        'sub': (u'Vaekos', u'Vařekos')
    },
    {
        'article_url': 'http://www.technologijos.lt/n/mokslas/idomusis_mokslas/S-77663/straipsnis/Skaiciavimo-masinu-istorija-kur-yra-pati-silpniausia-daugumos-siuolaikiniu-procesoriu-vieta-kaip-atsirado-ir-kas-negerai-su-voniNeumanno-architektura-ir-ka-tokio-ekspertai-surado-Intel-procesoriuose-',
        #'block_index': [2, 3, 8],
        'sub': (u'Erds', u'Erdős')
    }
]

_except_stress_pattern = re.compile('[^~`^]')


def stress_text_ex(text, version='8.0'):
    single_word = len(text.strip().split()) == 1

    output = stress_text(text, version)

    if single_word:
        return collapse_stress_options(text.strip(), output)
    
    return output

def collapse_stress_options(word, output):
    raw_stress_options = filter(None, output.split('\n'))
    stress_options = []
    max_opts = 0

    for rso in raw_stress_options:
        m = _stress_re.match(rso)
        if m:
            stressed_word = m.group(1)
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

def stress_text_liepa(pe, block):
    if liepa_re_char_replacement_pattern.search(block):
        for r, v in liepa_single_char_re_replacements:
            block = re.sub(r, v, block, flags=re.IGNORECASE)

    for processed_entry in pe.process(block):
        if isinstance(processed_entry, str):
            continue
        word_details, a, b, letter_map = processed_entry
        for word_detail in word_details:    
            if not word_detail['word_span']:
                continue
            span = word_detail['word_span']
            word_letter_map = letter_map[span[0]:span[1]]
            word_letter_map_set = set( word_letter_map )
            normalized = len ( word_letter_map_set ) != len (word_letter_map)
            if normalized:
                continue
            source_span = letter_map[span[0]], letter_map[span[1] - 1] + 1
            word = word_detail['ascii_stressed_word']
            orig_word = block[source_span[0]:source_span[1]]
            if not set(word).intersection(set('^`~')):
                continue
            orig_word_ = block[max(0, source_span[0] - 2):min(len(block), source_span[1] + 2)]
            if orig_word.replace("'", '').lower() != word.replace('`', '').replace('^', '').replace('~', '').lower():
                raise Exception()
            yield word, source_span        

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

    cursor.execute('SELECT article_id, `index`, block, url FROM article_blocks JOIN articles ON article_id = id WHERE article_id >= 5825')

    pe = PhonologyEngine()
    letter_pattern = u'A-ZĄ-Ža-zą-ž'
    strip_acc = lambda x: re.sub(r'[\^~`]', '', x)
    pattern_acc = re.compile(r'[\^~`]')

    make_results = lambda dst_text, mappings: [
            (dst_text[dst_span[0]:dst_span[1]], src_span) 
            for src_span, dst_span in mappings if pattern_acc.search(dst_text[dst_span[0]:dst_span[1]])
        ]

    for i, (article_id, index, block, url) in enumerate(cursor):
        if not block:
            continue

        if i % 10 == 0:
            conn.commit()
        

        if global_replacement_pattern.search(block):
            for p,v in global_replacements:
                block = block.replace(p, v)

        exc_ = [e for e in exceptions if article_id in e['article_id']]
        fused_replacements, augmented_elements = fused_stress_replacements(block, exc_)
        fused_stress_text, fused_stress_mappings = rebuild_text(augmented_elements, fused_replacements)
        fused_stress_results = make_results(fused_stress_text, fused_stress_mappings)

        pattern =  r'([' + letter_pattern + r']+[\^~`]([' + letter_pattern + r']*[\^~`]?))'

        pattern_exceptions = []
        for m in re.finditer(pattern, block):
            pattern_exceptions.append(m.group(0))
        
        stressed_text = stress_text_ex(block)
        with Processor(stressed_text) as processor:
            replacement_map = { 1: strip_acc }
            processor.process(pattern, replacement_map, exceptions=pattern_exceptions)
            processor.swap()
            
        stressed_results = make_results(stressed_text, processor.span_map)

        if processor.text != block:
            raise Exception()

        try:
            liepa_results = list(stress_text_liepa(pe, block))
        except UnicodeEncodeError as e:
            bad_string = e.object[e.start:e.end]
            liepa_results = list(stress_text_liepa(pe, block))

        spans, different_spans = compare_replacements(block, [fused_stress_results, stressed_results, liepa_results])
        print (article_id, index)
        print ()
        print (block)
        print ()
        show_different_spans(block, different_spans)
        print ('\n=====================')

    conn.close()