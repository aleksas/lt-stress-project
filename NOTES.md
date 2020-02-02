## Double stressed word by vdu
```python

from vdu_nlp_services import stress_text

text = u'(1) Ejk Tatuszeli i bytiu darża\n(2) Tinai saldej migosi bis\n(3) Wieielis puti, bitelis hużé\n(4) Oużolelis subavos bis\n(5) Tinaj saldei migoie bis\n\n(6) Atjo żałnieros par łauka,\n(7) O musu niera kam isz joti'

stressed_text = stress_text(text)

res.split()[5]
# u'da^r\u017ca~'
```