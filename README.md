# Current status
- Stress
  - [This release](https://github.com/aleksas/lt-stress-project/releases/tag/0.0.2) contains
    - [jupyter notebook](https://github.com/aleksas/lt-stress-project/releases/download/0.0.2/Cleanup_of_Transformer_translate.ipynb) for running in google colloab. It uses google drive to store intermediate data, checkponts and export model to.
    - [exported tf model](https://github.com/aleksas/lt-stress-project/releases/download/0.0.2/1607278770-20201206T182228Z-001.zip) ready for serving.
    - dockerfile for running model server
- Synth
  - dockerfile for running jupyter notebook with sinthesizer

# Todo

- Update phonology engine to allow exact stressing withoutnormalizing.

# References

[Automatizuotas lietuvių kalbos veiksmažodžių kirčiavimas : problemos ir jų sprendimas](https://www.vdu.lt/cris/handle/20.500.12259/47002)
[Vytauto Zinkevičiaus sukurtas bei Vido Daudaravičiaus ir Erikos Rimkutės patobulintas](http://donelaitis.vdu.lt/main.php?id=4&nr=7_1)

VDU stressor authors:
- Giedrius Norkevičius:
  - [Lietuvių kalbos žodžio priešdėlių analizė](https://www.vdu.lt/cris/handle/20.500.12259/41362)
- Asta Kazlauskienė
- Gailius Raškinis
- Airenas Vaičiūnas
- Adas Petrovas

Morphological analizer made using tools made by:
- Vytauto Zinkevičiaus (lemavimo įrankį ir Vido Daudaravičiaus parengtą vienareikšminimo įrankį.


[AUTOMATIC STRESSING OF LITHUANIAN TEXT USING DECISION TREES - Tomas Anbinderis 2010](https://pdfs.semanticscholar.org/c000/163fd3697a219b412754b7e43bd8e9613181.pdf?_ga=2.60224045.1610844738.1577029476-2121941291.1577029476)

# Questions
- How many times fused and liepa stress are equal when vdu stress is not, and other combinations.
- How well different stressors perform on homoforms?
