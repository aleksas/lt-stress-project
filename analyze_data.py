
from os.path import isfile
from zipfile import ZipFile
import sqlite3
import vdu_nlp_services.soap_stressor
import vdu_nlp_services.morphological_analyzer
from vdu_nlp_services import *

'''for bi, annotated in enumerate(block.get_annotated()):
    elif isinstance(annotated, AnnotatedWord):
        word = annotated.get_word()
        wt = word.get_word()
        annotated_type = annotated.get_type()
        annotated_type_set = set(annotated_type.split(','))https://venturebeat.com/2019/12/03/google-details-ai-that-classifies-chest-x-rays-with-human-level-accuracy/amp/?fbclid=IwAR0-uKZT9s7xMpOitPFe3poXev-CV_jOQH6Gn0J4Yu1glk8Pgx1zdNU_RTw
        stressed_words = {}
        for stress in word.get_stress_options():
            stress_type = stress.get_type()
            stress_type_set = set(stress_type.split(','))
            stressed_words[stress.get_word()] = len(annotated_type_set.intersection(stress_type_set))
        
        if len(set(stressed_words.keys())) == 0:
            stressed_block += wt
        elif len(set(stressed_words.keys())) == 1:
            stressed_block += list(stressed_words.keys())[0]
        else:
            sorted_stressed_words = sorted(stressed_words.items(), key=lambda kv: kv[1], reverse=True)
            stressed_block += sorted_stressed_words[0][0]
        print (stressed_block)
    else:
        raise Exception()'''




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
        soap_stressor._stress_text_cache[h] = result

    cursor.execute('SELECT `hash`, `text` FROM `morphology_cache`')
    for h, text in cursor:
        morphological_analyzer._morphology_cache[h] = text

if __name__ == "__main__":
    '''strings = [
        'Kiti ekspertai sako, kad pasikeitę prekybos keliai ir vidiniai nesutarimai galėjo privesti milžinišką ir galingą civilizaciją prie išnykimo.',
        'Dėl to galėjo būti kalti patys majai.',
        'A. Hitleriui buvo paskirti sargybiniai ir uždėta neperšaunama liemenė.',
        'Į žvalgybą buvo išsiųsti lėktuvai.',
        'Šį akmenį A. Hitleris iš karto įsakė pašalinti.',
        'Žinoma, pirmiausia turime apibrėžti kas, šiuo atveju, yra frontas.',
        'Šį akmenį A. Hitleris iš karto įsakė pašalinti.',
        'Šioje vietoje trūksta namo.',
        'Einam namo. Nerandu namo.',
        'laba\n–--–-diena',
        'Laba diena–draugai!\nKaip\njums -sekasi? Vienas, du, trys.',
        'namo',
        'shit fantastish dog',
        'Tuo metu kai čia lankėsi A. Hitleris nebuvo jokios realios kovos - tačiau ji labai greitai galėjo įsižiebti.',
        'Antrajame pasauliniame kare kartu su savo kariais nesitraukė iš Stalingrado mūšio lauko',
    ]

    for s in strings:
        print ( s )
        replacements, augmented_elements = fused_stress_text(s)
        fused_text = rebuild_text(augmented_elements, replacements)
        print ( fused_text )
        print ( stress_text(s) )
        print (  )'''


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
        soap_stressor._stress_text_cache[h] = result
        try:
            cache_cursor.execute("INSERT INTO stress_text_cache (hash, text) VALUES (?,?)", (h, result['out']))
        except Exception as e:
            print(e)

    def set_morphology_cache(h, text):
        morphological_analyzer._morphology_cache[h] = text
        try:
            cache_cursor.execute("INSERT INTO morphology_cache (hash, text) VALUES (?,?)", (h, text))
        except Exception as e:
            print(e)

    soap_stressor.set_stress_text_cache = set_stress_text_cache
    morphological_analyzer.set_morphology_cache = set_morphology_cache

    load_cache(cursor)

    for i, exception in enumerate(exceptions):
        cursor.execute('SELECT id FROM articles WHERE `url` = ?', (exception['article_url'],))
        for res in cursor:
            if 'article_id' not in exceptions[i]:
                exceptions[i]['article_id'] = []
            exceptions[i]['article_id'].append(res[0])

    cursor.execute('SELECT article_id, `index`, block, url FROM article_blocks JOIN articles ON article_id = id WHERE article_id >= 4838')

    for i, (article_id, index, block, url) in enumerate(cursor):
        if not block:
            continue

        if i % 10 == 0:
            conn.commit()

        exc_ = [e for e in exceptions if article_id in e['article_id']]
        fused_replacements, augmented_elements = fused_stress_replacents(block, exc_)
        fused_stressed_text = rebuild_text(augmented_elements, fused_replacements)
        stressed_text = stress_text(block)
        localizations = localize_stressed_text(stressed_text, augmented_elements)

        comparison_replacements, has_inequalities = compare_replacements([fused_replacements, localizations])

        print (article_id, index)
        if has_inequalities:
            rebuilt_text = rebuild_text(augmented_elements, comparison_replacements)
            
            print ()
            print (block)
            print ()
            print (rebuilt_text)
                
        print ('\n=====================')

    conn.close()