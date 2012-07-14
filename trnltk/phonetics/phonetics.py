# coding=utf-8
from trnltk.phonetics.alphabet import TurkishAlphabet
from trnltk.stem.dictionaryitem import RootAttribute

class PhoneticExpectation(object):
    VowelStart = 'VowelStart'
    ConsonantStart = 'ConsonantStart'

class PhoneticAttributes(object):
    LastLetterVowel = "LastLetterVowel"
    LastLetterConsonant = "LastLetterConsonant"

    LastVowelFrontal = "LastVowelFrontal"
    LastVowelBack = "LastVowelBack"
    LastVowelRounded = "LastVowelRounded"
    LastVowelUnrounded = "LastVowelUnrounded"

    LastLetterVoiceless = "LastLetterVoiceless"
    LastLetterNotVoiceless = "LastLetterNotVoiceless"
    LastLetterVoicelessStop = "LastLetterVoicelessStop"

    FirstLetterVowel = "FirstLetterVowel"
    FirstLetterConsonant = "FirstLetterConsonant"

    HasNoVowel = "HasNoVowel"

class Phonetics(object):
    @classmethod
    def is_suffix_form_applicable(cls, word, form_str):
        if not form_str or not form_str.strip():
            return True

        if not word or not word.strip():
            return False

        word = word.strip()
        form_str = form_str.strip()

        phonetic_attributes = cls.calculate_phonetic_attributes_of_plain_sequence(word)

        # ci, dik, +yacak, +iyor, +ar, +yi, +im, +yla

        first_form_letter = TurkishAlphabet.get_letter_for_char(form_str[0])
        if first_form_letter.char_value == '+':
            # +yacak, +iyor, +ar, +yi, +im, +yla

            optional_letter = TurkishAlphabet.get_letter_for_char(form_str[1])
            if optional_letter.vowel:
                #+iyor, +ar, +im
                if PhoneticAttributes.LastLetterVowel in phonetic_attributes:
                    # ata, dana
                    return cls.is_suffix_form_applicable(word, form_str[2:])
                else:
                    # yap, kitap
                    return True

            else:
                # +yacak, +yi, +yla
                if PhoneticAttributes.LastLetterVowel in phonetic_attributes:
                    #ata, dana
                    return True
                else:
                    # yap, kitap
                    return cls.is_suffix_form_applicable(word, form_str[2:])

        else:
            if first_form_letter.vowel:
                return PhoneticAttributes.LastLetterVowel not in phonetic_attributes
            else:
                return True

    @classmethod
    def apply(cls, word, phonetic_attributes, form_str, root_attributes=None):
        if not form_str or not form_str.strip():
            return word, u''

        if not word or not word.strip():
            return None, None

        # ci, dik, +yacak, +iyor, +ar, +yi, +im, +yla

        first_form_letter = TurkishAlphabet.get_letter_for_char(form_str[0])
        if first_form_letter.char_value == '+':
            # +yacak, +iyor, +ar, +yi, +im, +yla

            optional_letter = TurkishAlphabet.get_letter_for_char(form_str[1])
            if optional_letter.vowel:
                #+iyor, +ar, +im
                if PhoneticAttributes.LastLetterVowel in phonetic_attributes:
                    # ata, dana
                    return cls.apply(word, phonetic_attributes, form_str[2:], root_attributes)
                else:
                    # yap, kitap
                    return cls._handle_phonetics(word, phonetic_attributes, form_str[1:], root_attributes)

            else:
                # +yacak, +yi, +yla
                if PhoneticAttributes.LastLetterVowel in phonetic_attributes:
                    #ata, dana
                    return cls._handle_phonetics(word, phonetic_attributes, form_str[1:], root_attributes)
                else:
                    # yap, kitap
                    return cls.apply(word, phonetic_attributes, form_str[2:], root_attributes)

        else:
            if first_form_letter.vowel:
                if PhoneticAttributes.LastLetterVowel not in phonetic_attributes:
                    return cls._handle_phonetics(word, phonetic_attributes, form_str, root_attributes)
                else:
                    raise Exception(u'Form "{}" should not be applicable for word "{}"'.format(form_str, word))

            else:
                return cls._handle_phonetics(word, phonetic_attributes, form_str, root_attributes)

    @classmethod
    def _handle_phonetics(cls, word, phonetic_attributes, form_str, root_attributes=None):
        root_attributes = root_attributes or []
        phonetic_attributes = phonetic_attributes or []

        first_letter_of_form = TurkishAlphabet.get_letter_for_char(form_str[0])

        # first apply voicing if possible
        if RootAttribute.NoVoicing not in root_attributes and PhoneticAttributes.LastLetterVoicelessStop in phonetic_attributes and first_letter_of_form.vowel:
            voiced_letter = TurkishAlphabet.voice(TurkishAlphabet.get_letter_for_char(word[-1]))
            if voiced_letter:
                word = word[:-1] + voiced_letter.char_value

        # then try devoicing
        if PhoneticAttributes.LastLetterVoiceless in phonetic_attributes and TurkishAlphabet.devoice(first_letter_of_form):
            form_str = TurkishAlphabet.devoice(first_letter_of_form).char_value + form_str[1:]

        applied = u''

        for i in range(len(form_str)):
            c = form_str[i]
            next_c = form_str[i+1] if i+1<len(form_str) else None

            if c=='!':
                continue

            letter = TurkishAlphabet.get_letter_for_char(c)
            if letter.vowel and letter.upper_case_char_value==c:
                if c==u'A':
                    if PhoneticAttributes.LastVowelBack in phonetic_attributes:
                        applied += u'a'
                    else:
                        applied += u'e'
                elif c==u'I':
                    if PhoneticAttributes.LastVowelBack in phonetic_attributes:
                        if PhoneticAttributes.LastVowelUnrounded in phonetic_attributes or next_c=='!':
                            applied += u'ı'
                        else:
                            applied += u'u'
                    else:
                        if PhoneticAttributes.LastVowelUnrounded in phonetic_attributes or next_c=='!':
                            applied += u'i'
                        else:
                            applied += u'ü'
                elif c==u'O':
                    if PhoneticAttributes.LastVowelBack in phonetic_attributes:
                        applied += u'o'
                    else:
                        applied += u'ö'

            else:
                applied = applied + c

        return word, applied

    @classmethod
    def expectations_satisfied(cls, phonetic_expectations, form_str):
        if not phonetic_expectations:
            return True

        if not form_str or not form_str.strip():
            return False

        form_str = form_str.strip()

        expectation_satisfaction_map = dict()

        for phonetic_expectation in phonetic_expectations:
            expectation_satisfaction_map[phonetic_expectation] = cls._expectation_satisfied(phonetic_expectation,
                form_str)

        return all(expectation_satisfaction_map.values())


    @classmethod
    def _expectation_satisfied(cls, phonetic_expectation, form_str):
        if phonetic_expectation == PhoneticExpectation.VowelStart:
            first_char = form_str[0]
            if first_char == '+':
                return cls._expectation_satisfied(phonetic_expectation, form_str[1:]) or cls._expectation_satisfied(
                    phonetic_expectation, form_str[2:])
            else:
                return TurkishAlphabet.get_letter_for_char(first_char).vowel

        elif phonetic_expectation == PhoneticExpectation.ConsonantStart:
            first_char = form_str[0]
            if first_char == '+':
                return cls._expectation_satisfied(phonetic_expectation, form_str[1:]) or cls._expectation_satisfied(
                    phonetic_expectation, form_str[2:])
            else:
                return not TurkishAlphabet.get_letter_for_char(first_char).vowel

        else:
            raise Exception('Unknown phonetic_expectation', phonetic_expectation)

    @classmethod
    def calculate_phonetic_attributes(cls, word, root_attributes):
        phonetic_attributes = None

        if word==u'd' or word==u'y':  #verbs demek, yemek
            phonetic_attributes = cls.calculate_phonetic_attributes_of_plain_sequence(word + u'e')
            phonetic_attributes.remove(PhoneticAttributes.LastLetterVowel)
        else:
            phonetic_attributes = cls.calculate_phonetic_attributes_of_plain_sequence(word)
            if root_attributes and RootAttribute.InverseHarmony in root_attributes:
                if PhoneticAttributes.LastVowelBack in phonetic_attributes:
                    phonetic_attributes.remove(PhoneticAttributes.LastVowelBack)
                    phonetic_attributes.add(PhoneticAttributes.LastVowelFrontal)

                elif PhoneticAttributes.LastVowelFrontal in phonetic_attributes:
                    phonetic_attributes.remove(PhoneticAttributes.LastVowelFrontal)
                    phonetic_attributes.add(PhoneticAttributes.LastVowelBack)

        return phonetic_attributes

    @classmethod
    def calculate_phonetic_attributes_of_plain_sequence(cls, seq):
        attrs = []

        last_vowel = cls._get_last_vowel(seq)
        last_letter = TurkishAlphabet.get_letter_for_char(seq[-1])
        if last_vowel:
            if last_vowel.rounded:
                attrs.append(PhoneticAttributes.LastVowelRounded)
            else:
                attrs.append(PhoneticAttributes.LastVowelUnrounded)

            if last_vowel.frontal:
                attrs.append(PhoneticAttributes.LastVowelFrontal)
            else:
                attrs.append(PhoneticAttributes.LastVowelBack)

        if last_letter.vowel:
            attrs.append(PhoneticAttributes.LastLetterVowel)
        else:
            attrs.append(PhoneticAttributes.LastLetterConsonant)

        if last_letter.voiceless:
            attrs.append(PhoneticAttributes.LastLetterVoiceless)
            if last_letter.stop_consonant:
                attrs.append(PhoneticAttributes.LastLetterVoicelessStop)
        else:
            attrs.append(PhoneticAttributes.LastLetterNotVoiceless)

        return set(attrs)

    @classmethod
    def _get_last_vowel(cls, seq):
        for s in reversed(seq):
            turkish_letter = TurkishAlphabet.get_letter_for_char(s)
            if turkish_letter.vowel:
                return turkish_letter

    @classmethod
    def application_matches(cls, word, applied_str, voicing_allowed):
        if not applied_str or len(applied_str)>len(word):
            return False

        elif word==applied_str or word.startswith(applied_str):
            return True

        if  voicing_allowed and word.startswith(applied_str[:-1]):
            last_letter_of_application = TurkishAlphabet.get_letter_for_char(applied_str[-1])
            last_letter_of_word_part = TurkishAlphabet.get_letter_for_char(word[len(applied_str)-1])
            return TurkishAlphabet.voice(last_letter_of_application)==last_letter_of_word_part

        else:
            return False