import re
import difflib

#restore_pattern = re.compile(r'(\s+)([~`^])')
letter_pattern = re.compile(r'[A-Za-z' + u'Ą-Žą-ž' + r']')

def restore_vdu_stressed_text(text, stressed_text):
    '''
    For some sentences spaces and endlines appear or dissapear
    '''
    c = ''
    li = -1
    for s in difflib.ndiff(text, stressed_text):
        op, ch = s[0], s[-1]

        if op == '+' and ch in '^~`' and li != -1:
            c = c[:li] + ch + c[li:]
            li = -1
        elif op in '- ':
            c += ch
            li = len(c) if letter_pattern.match(ch) else li

    return c#restore_pattern.sub(r'\2\1', c)

def intersect(span_a, span_b):
    return max(span_a[0], span_b[0]) < min(span_a[1], span_b[1])

def compare_replacements(text, replacement_results):
    spans = []
    result_len = len(replacement_results)

    for r, result in enumerate(replacement_results):
        for word, span in result:
            index = None
            for i, (other_span, _) in enumerate(spans):
                if span == other_span:
                    index = i
                    break
                elif intersect(span, other_span):
                    raise Exception('Misaligned words')
            if index == None:
                index = len(spans)
                spans.append((span, {}))
            spans[index][1][r] = word

    spans.sort(key=lambda x: x[0])
    different_spans = []
    for span, words in spans:
        words = {k:v for k,v in words.items()}
        word_set = set(words.values())
        if len(words) == result_len and len(word_set) == 1:
            different_spans.append( (span, list(word_set)[0]) )
        else:
            different_spans.append( (span, words) )

    return spans, different_spans

def show_different_spans(text, different_spans):
    for span, words in reversed(different_spans):
        if isinstance(words, dict):
            text = text[:span[0]] + '|> ' + ' '.join(['%d:%s' % each for each in words.items() ]) + ' <|' + text[span[1]:]
        else: # str
            text = text[:span[0]] + words + text[span[1]:] 

    print (text)

liepa_single_char_re_replacements = []
liepa_re_char_replacement = '|'.join([p for p,_ in liepa_single_char_re_replacements])
liepa_re_char_replacement_pattern = re.compile(liepa_re_char_replacement)

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
            word = word_detail['word']
            stressed_word = word_detail['ascii_stressed_word']
            case_recovered_stressed_word = ''

            li, last_i = 0, 0
            for l in stressed_word:
                li = word.find(l, last_i)
                last_i = max(li, last_i)
                case_recovered_stressed_word += l if li == -1 else block[letter_map[span[0] + li]]
            #orig_word = block[source_span[0]:source_span[1]]
            if not set(case_recovered_stressed_word).intersection(set('^`~')):
                continue
            #orig_word_ = block[max(0, source_span[0] - 2):min(len(block), source_span[1] + 2)]
            #if orig_word.replace("'", '').replace(")", '').replace("-", '').lower() != word.replace('`', '').replace('^', '').replace('~', '').lower():
            #    raise Exception()
            yield case_recovered_stressed_word, source_span      