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
        words = {k:v.lower() for k,v in words.items()}
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