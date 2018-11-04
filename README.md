# CompEval Generation System

This is the code for the generation system described in 'Assessing Composition in Sentence Vector Representations' (COLING 2018), by Allyson Ettinger, Ahmed Elgohary, Colin Phillips, and Philip Resnik.

The **classification datasets** for the experiments described in the paper can be found [here](https://aetting.github.io/compeval.html).

# Citation

```
@inproceedings{ettinger2018assessing,
  author = {Allyson Ettinger and Ahmed Elgohary and Colin Phillips and Philip Resnik},
  title = {Assessing Composition in Sentence Vector Representations},
  booktitle = {Proceedings of COLING},
  year = {2018},
 }
```

# Prerequisites
* NumPy
* NLTK

# Basic usage

You can generate sentences that will vary freely within the built-in system parameters using the command below

```
python gen_from_meaning.py --setname sent --setdir . --configfile config1.example.json --mpo 10
```

This will generate 10 sentences for each structural category that the system uses, and write them to `sent.txt` in the `generation_system` directory, with annotation objects written to `sent-annot.json`.

* `setname` is used in naming the output files and will also be used in sentence IDs
* `setdir` specifies the location to write the output files
* `configfile` specifies the config file, described in more detail below
* `mpo` specifies the maximum number of sentences to be generated for a given structural category
* `adv` you can also include this option with an integer argument, in which case the system will insert a variable number of adverbs before verbs (as long as your vocabulary includes adverbs), with the integer specifying the maximum number of adverbs to precede a given verb

# Modifying config files

## Specifying EVENT constraints

When using the `needEv` and `avoidEv` constraints in the config files, you will use EVENT objects. `config2.example.json` and `config3.example.json` give examples of using these objects to specify these constraints. EVENT objects allow specification of the following properties:

EVENT objects can specify the following:
* `name`: the lemma describing the event (verb)
* `tense`: tense of the event (`past` or `pres`, e.g., 'sleeps' vs 'slept')
* `aspect`: aspect of the event (`neut` or `prog`, e.g., 'sleeps' vs 'is sleeping')
* `voice`: voice of the event (`active` or `passive`, e.g., 'x chased y' vs 'y was chased by x')
* `pol`: polarity of the event (`pos` or `neg`, e.g., 'slept' vs 'did not sleep')
* `frame`: transitivity of the event (`transitive` or `intransitive`)
* `participants`: participants in the event - an object with possible keys of `agent` and `patient`

The participant keys (`agent` or `patient`) map to CHARACTER objects, within which you can specify the following:
* `name`: the lemma describing the participant (noun)
* `num`: number of the participant (`sg` or `pl`, e.g., 'student' vs 'students')
* `attributes`: attributes of the participant - another object. Currently the only supported attribute is a relative clause, the key for which is `rc`, and the value for which is another object.

The RC object can specify the following:
* `rtype`: object-relative or subject-relative (`orc` or `src`)
* `event`: the event described by the relative clause. The value here will be another EVENT object, as described above.

Note that at present only one event object can be specified for a given constraint.

## Config file examples

Config files are used to specify a) the input constraints for the sentences to be generated, and b) possible structures for the sentences.

The three example config files give some illustrations of how you can specify constraints.

`config1.example.json` specifies no input constraints. Sentences can vary freely within the built-in parameters of the system.

`config2.example.json` uses all of the categories of input constraint, to illustrate usage of each.
* With `needEv`, it specifies an event that all sentences must include: in this case, an event with *lawyer* as AGENT of *recommend*. This is a JSON object.
* With `avoidEv`, it specifies an event that no sentences can include: in this case, an event with *lawyer* as AGENT of *shout*. This is a JSON object.
* With `needList`, it specifies lemmas that need to be present in every sentence. This is a JSON object with keys for 'noun','transitive' (verb), and 'intransitive' (verb), and arrays of lemmas as values.
* With `avoidList`, it specifies lemmas that cannot be present in any sentence. This is a JSON object with keys for 'noun','transitive' (verb), and 'intransitive' (verb), and arrays of lemmas as values.

`config3.example.json` demonstrates a more complex usage of the EVENT object in specifying the `needEv` constraint. In this case, the constraint specifies that

These examples leave constant the `role_rc_structures` object, which lists the different possible structures that the sentences can be made up of. The structures listed in this object specify whether different participants have relative clauses, so for example `{"agent":"none","patient":"transitive"}` describes a sentence in which the agent has no relative clause attribute, and the patient has a transitive relative clause.

# Modifying vocabulary

`lexical/vocabulary.json` already contains a usable vocabulary (containing only human nouns and verbs that are compatible with human participants, to preserve plausibility).

If you want to modify the vocabulary, you can do this by first modifying `lexical/vocabulary.json`. The vocabulary object in this file has four keys corresponding to lemma categories: nouns, transitive verbs, intransitive verbs, and adverbs. New vocabulary items must be placed in the array corresponding to the correct key, and must be lemmas (dictionary forms - e.g., 'sleep') and NOT inflected forms (e.g., 'sleeps').

You can then build the lexical variables that the system will use by running `get_lexicon.py`.

```
python get_lexicon.py
```

This will read from `lexical/vocabulary.json` and write a new `gensys_lexvars.json` (which contains an inflection dictionary and other lexical variables for the system to use) based on the new vocabulary.

`get_lexicon.py` uses the [XTAG morphology database](https://www.cis.upenn.edu/~xtag/swrelease.html) to look up inflections, and will remove any lemmas from the vocabulary that are missing inflections in that lookup.
