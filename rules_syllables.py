import re
import regex
import math
import nltk
from features import Feature
from nltk.tokenize import sent_tokenize
import spacy
from string import ascii_letters, whitespace, punctuation

class SpanishRuleSyllables:

    Q = 0
    x_sr_text = 0
    objects = []
    #сильная гласная
    strong_vowels = ["a", "e", "i"]
    #слабая гласная
    low_vowels = ["o", "u"]
    #ударные гласные
    percussion_sound = [chr(225), chr(233), chr(237), chr(243), chr(250)]

    diphthongs = {
        # Нисходящий дифтонг – это сочетание сильного гласного со слабым.
        "descending":["ai", "au", "ei", "eu", "oi", "ou"],
        #Восходящий дифтонг – это сочетание слабого гласного с сильным.
        "ascendant":["ia", "ie", "io", "ua", "ue", "ui", "uo"],
        #Также встречаются дифтонги, в которых сочетаются две слабые гласные:
        "weak": ["iu", "ui"]
    }

    #если в слове появляется комбинация из трех идущих подряд гласных, то это уже трифтон
    triphthongs = ["iai", "iau", "iei", "ioi", "uai", "uei", "uau"]

    def split_syllables(self, word):
        if re.search('\d+', word) is not None:
            return {}
        word = word.lower()
        syllables = []
        slog = ""
        result = {}
        index = 0
        while(len(word) > 0):
            two_symbol = None if (index + 1) >= len(word) else word[index + 1]
            three_symbol =  None if (index + 2) >= len(word) else word[index + 2]

            if (index + 1) > len(word):
                if len(word) > 1:
                    last_element = word[len(word) -1]
                    predpos_element = word[len(word) - 2]
                    if (last_element not in self.strong_vowels and
                        last_element not in self.low_vowels and
                        last_element not in self.percussion_sound and
                        (predpos_element in self.strong_vowels or predpos_element in self.low_vowels or predpos_element in self.percussion_sound)):
                        syllables[len(syllables) - 1] = syllables[len(syllables) - 1] + last_element
                break

            if( (word[index] not in self.strong_vowels) and (word[index] not in self.low_vowels) and (word[index] not in self.percussion_sound)):
                slog = slog + word[index]
                index = index + 1
                continue

            check_diphthong = self.check_diphthongs(word[index],two_symbol, three_symbol)

            if(check_diphthong is None):
                slog = slog + self.check_consonant_sequence(word[index], word[index + 1: len(word)])
            else:
                slog = slog + check_diphthong

            syllables.append(slog)
            index = len(''.join(syllables))
            slog = ""
        if(len(syllables) > 0):
            result = {
                "syllables" : syllables,
                "percussion_syllable": self.get_percussion_syllable(syllables)
            }

        return result

    def check_diphthongs(self, slog, two_symbol, three_symbol):

        if(two_symbol is None):
            return None

        for key, value in self.diphthongs.items():
            for element in value:
                if( (slog + two_symbol) in element):
                    if three_symbol is not None:
                        triphthong = self.check_triphthongs(slog + two_symbol, three_symbol)
                        if(triphthong is not None):
                            return triphthong
                    return slog + two_symbol
        return None

    def check_triphthongs(self, symbol, next_symbol):
        for element in self.triphthongs:
            if (symbol + next_symbol) in element:
                return symbol + next_symbol
        return None

    def check_consonant_sequence(self, symbol, word):
        nedelim_group1 = ['pr', 'pl', 'br', 'bl', 'fr', 'fl', 'tr', 'dr', 'cl', 'cr', 'gr', 'gl']
        nedelim_group2 = [ 'ch','ll', 'rr']
        other = nedelim_group1 + nedelim_group2 + self.percussion_sound

        one_symbol = two_symbol = three_symbol = four_symbol =  None

        try:
            one_symbol = word[0]
            two_symbol = word[1]
            three_symbol = word[2]
            four_symbol = word[3]
        except Exception:
            message = 'Выход за пределы массива'
        if(one_symbol is not None):
            check_sogl_one_symbol = (one_symbol not in self.strong_vowels) and (one_symbol not in self.low_vowels) and (one_symbol not in self.percussion_sound)
            check_sogl_two_symbol = (two_symbol not in self.strong_vowels) and (two_symbol not in self.low_vowels) and (two_symbol not in self.percussion_sound)
            check_sogl_three_symbol = (three_symbol not in self.strong_vowels) and (three_symbol not in self.low_vowels) and (three_symbol not in self.percussion_sound)
            check_sogl_four_symbol = (four_symbol not in self.strong_vowels) and (four_symbol not in self.low_vowels) and (four_symbol in self.percussion_sound)

            if(two_symbol is not None and check_sogl_two_symbol):
                if(three_symbol is not None and check_sogl_three_symbol):
                    if(four_symbol is not None and check_sogl_four_symbol):
                        return symbol + one_symbol + two_symbol + three_symbol
                    else:
                        return symbol + one_symbol + two_symbol
                if((one_symbol + two_symbol) in other):
                    return symbol
                else:
                    if check_sogl_one_symbol:
                        return symbol + one_symbol
        return symbol

    def get_percussion_syllable(self, syllables):
        for index, element in enumerate(syllables):
            for el in self.percussion_sound:
                if el in element:
                    return index

        last_syllable =  syllables[len(syllables) - 1]
        if last_syllable[len(last_syllable) - 1] == 'n' or last_syllable[len(last_syllable) - 1] == 's' or last_syllable[len(last_syllable) - 1] in self.low_vowels or last_syllable[len(last_syllable) - 1] in self.strong_vowels:
            return 0 if len(syllables) - 2 < 0 else len(syllables) - 2
        else:
            return 0 if len(syllables) - 1 < 0 else len(syllables) - 1

    def start(self, data):
        self.x_sr_text = round(self.obscurity_text(data), 3)
        q = 0
        for index_offer, offer in enumerate(data):
            count_interval = 0
            result_syllables = []
            index_percussion_syllables = []
            prev_percussion_syllable = 0
            words =  re.findall(r'\w+', offer)

            # Прохождение по разделенным словам
            for index, word in enumerate(words):
                if(re.findall('XL|XXXIX|XXXVIII|XXXVII|XXXVI|XXXV|XXXIV|XXXIII|XXXII|XXXI|XXX|XXIX|XXVIII|XXVII|XXVI|XXV|XXIV|XXIII|XXII|XXI|XX|XIX|XVIII|XVII|XVI|XV|XIV|XIII|XII|XI|X|IX|VIII|VII|VI|V|IV|III|II|I ',word)):
                    continue
                res = self.split_syllables(word)
                if res:
                    result_syllables = result_syllables + res["syllables"]
                    index_percussion_syllables.append( prev_percussion_syllable + res["percussion_syllable"])
                    prev_percussion_syllable = prev_percussion_syllable + len(res["syllables"])

            #unstressed_count = len(result_syllables) - len(index_percussion_syllables)
            summer = 0
            #count_bezud_interval = 0
            # Прохожусь по интервалам
            for index, element in enumerate(index_percussion_syllables):
                begin = element + 1
                end = None if index + 1 >= len(index_percussion_syllables) else index_percussion_syllables[index + 1]
                if(end is not None):
                    count_bezud = len(result_syllables[begin:end])
                    if(count_bezud > 0):
                        summer = summer + ((count_bezud - self.x_sr_text) ** 2)
                        #count_bezud_interval = count_bezud_interval + 1
                        count_interval = count_interval + 1
                        self.objects.append({"count_bezud":count_bezud, "index_interval":index})
            if(count_interval > 0):
                q = q + math.sqrt(summer/count_interval)
        self.Q = q/len(data)

    def obscurity_text(self, data):
        count_bezud_res = 0
        count_interval = 0
        for index_offer, offer in enumerate(data):
            result_syllables = []
            index_percussion_syllables = []
            prev_percussion_syllable = 0
            words =  re.findall(r'\w+', offer)
            # Прохождение по разделенным словам
            for index, word in enumerate(words):
                if(re.findall('XL|XXXIX|XXXVIII|XXXVII|XXXVI|XXXV|XXXIV|XXXIII|XXXII|XXXI|XXX|XXIX|XXVIII|XXVII|XXVI|XXV|XXIV|XXIII|XXII|XXI|XX|XIX|XVIII|XVII|XVI|XV|XIV|XIII|XII|XI|X|IX|VIII|VII|VI|V|IV|III|II|I ',word)):
                    continue
                res = self.split_syllables(word)
                if res:
                    result_syllables = result_syllables + res["syllables"]
                    index_percussion_syllables.append( prev_percussion_syllable + res["percussion_syllable"])
                    prev_percussion_syllable = prev_percussion_syllable + len(res["syllables"])

            # Прохожусь по интервалам
            for index, element in enumerate(index_percussion_syllables):
                begin = element + 1
                end = None if index + 1 >= len(index_percussion_syllables) else index_percussion_syllables[index + 1]
                if(end is not None):
                    count_bezud = len(result_syllables[begin:end])
                    if(count_bezud > 0):
                        count_bezud_res = count_bezud_res + count_bezud
                        count_interval = count_interval + 1
        return  count_bezud_res /  count_interval

class FranchRuleSyllables:
    nlp = spacy.load("fr_core_news_md")
    Q = 0
    x_sr_text = 0
    data = []
    #чистые гласные
    voyelles_orales = [ "a", "e", "i", chr(226), "er", "ed", "ez", chr(233),
                        "ai", "ais", chr(232), chr(234), "ei", "y", "o", chr(244),
                        "au", "ou", "eu", chr(339), chr(339)+"u", "ue", "u", "eu", "eau", "oi", "ui", "eau",
                        "ill", "ail", "aill", "eil", "eill", "euil", "euill", "ouil", "ouill", "ou",
                        chr(251), "ien", chr(224), chr(255), chr(238), chr(249)
                      ]

    #носовые гласные(если после этих буквосочетаний не следует гласная)
    voyelles_nasales =  [   "am", "an", "em", "en", "in", "im",
                            "yn", "ym", "ain", "aim", "ein", "eim",
                            "on", "om", "un", "um"
                        ]
    #Полугласные приоритет(буквосочетания, которые не образуют отдельный слог (в определенных ситуациях))
    semi_voyelles = [ "ou", "u", "i"]

    #Слова которые не учитываются и раположены в конце слова
    not_taken_symbols_end = ["e", "t", "d", "s", "x", "z", "p", "g", "es", "ts", "ds", "ps", "ent", "ue"]

    #согласные
    consonnes = ["b", "bb", "d", "dd", "f", "ff", "ph", "g",
                 "g", "gg", "x", "c", "cc", "ch", "k", "l",
                 "ll", "m", "mm", "n", "nn", "gn", "p", "pp",
                 "r", "rr", "rh", "s", "ss",   "j"]
    #шумные
    shum = ["p", "b", "t", "d", "k", "g", "f", "v", "s", "z", "ch", "j"]

    #сонанты
    sonant = ["m", "n", "w", "l", "r"]

    #знаки препинания
    punctuation_mark = [",", ":", ";", "'", "\"", "-", "(", ")"]

    #Стоп-слова(по которым можно разделить на ритмические группы)
    stop_words = [  "un", "une", "des", "la", "le", "les", "de", "à", "par", "pour", "avec",
                    "malgré", "contre", "sauf", "sans", "envers", "en", "selon", "depuis",
                    "pendant", "dans", "après", "vers", "avant", "jusqu’à", "sur", "sous",
                    "chez", "entre", "près", "côté", "derrière", "devant", "mon", "ma", "ton",
                    "ta", "son", "sa", "notre", "votre", "leur", "mes", "tes", "ses", "nos",
                    "vos", "leurs", "d’une", "d’un", "du", "me", "te", "se", "ce", "cet",
                    "cette", "ces", "au", "aux", "tout", "tous", "toutes", "chaque", "dès",
                    "y", "s’y", "en", "s’en", "presque", "quelque", "quelques", "quel",
                    "quels", "quelle", "quelles", "même", "très", "beaucoup", "beaucoup de",
                    "trop", "trop de", "tout", "si", "tellement", "tant", "tant de", "autant",
                    "autant de", "combien", "combien de", "davantage", "encore", "fort", "plus",
                    "plus de", "absolument", "complètement", "et", "ni", "ou", "tantôt", "moins",
                    "dont", "où", "lequel", "lequels", "laquelle", "laquelles", "lesquels", "lesquelles",
                    "que", "quand", "comme", "lorsque", "car"
                ]

    def counting_square_deviation(self):
        summer_bezyd = 0
        count_interval = 0
        for element in self.data:
          summer = sum(element["group_slog_letter"])
          summer_bezyd = summer_bezyd + summer
          count_interval = count_interval + len(element["group_slog_letter"])

        self.x_sr_text = summer_bezyd / count_interval
        q = 0
        for element in self.data:
            count_bezud = 0
            index_one_slog = 0
            for count_slog in element["group_slog_letter"]:
                if index_one_slog == 0 : 
                    index_one_slog = 1
                    continue               
                count_bezud = count_bezud + ((count_slog - self.x_sr_text) ** 2)
            q = q + math.sqrt(count_bezud / len(element["group_slog_letter"]))

        self.Q = q / len(self.data)

    def split_syllables(self, word):
        if re.search('\d+', word.text) is not None:
            return 0
        #word = word.text.lower()
        word = self.check_end_word(word)
        count = 0
        check_res = []
        sord_default_voyelle = sorted(self.voyelles_orales + self.voyelles_nasales, key= len, reverse=True)
        for syllable in sord_default_voyelle:
            indexs = [m.start() for m in re.finditer("(?=" + syllable + ")", word)]
            for el in indexs :
                if syllable in self.semi_voyelles:
                    index_one = el
                    index_last = el + 1 if len(syllable) > 1 else el
                    if( index_one > 0 and len(word) > index_last + 1):
                        if(word[index_one - 1] in sord_default_voyelle  or word[index_last + 1] in sord_default_voyelle):
                            continue
                if el not in check_res:
                   check_res = check_res + [i for i in range(el, len(syllable) + el)]
                   count = count + 1
        return count

    def clean(self,text):
        asciis = []
        for asc in (ascii_letters):
            asciis.append(asc)
        asciis = asciis + [chr(226), chr(233),chr(232),chr(234),chr(244) ,chr(339),chr(251) ,chr(224) ,chr(255), chr(238), chr(249), "'", "\s", chr(8217)]
        
        return '|'.join(asciis)
        #strings = (ascii_letters + whitespace + " " + chr(226) + " " + chr(233) + " " + chr(232) + " " + chr(234) + " " + chr(244) + " " + chr(339) + " " + chr(224) + " " + chr(251) + " " + '\'')
        #test = ''.join(asciis).encode()
        byte_arr = []
        for b in set(range(0x100)):
            if( b not in asciis):
                byte_arr.append(b)
        good_chars = asciis

        print(good_chars)
        print(set(good_chars))
        print(byte_arr)

        #junk_chars = bytearray(set(byte_arr))

        #print(junk_chars)
        #return text.encode('ascii', 'ignore').translate(None, junk_chars).decode()

    def start(self, letters):
        index_letter = 0

        for letter in letters:

            result = []
            #разбиение по знакам припенания
            for split_letter in re.split(';|,|:|"', letter):
                reg = self.clean(split_letter)
                #l = self.clean(split_letter)
                l = regex.sub(r"\ufeff|\n|\r|\t|\"","", split_letter)
                l = ''.join(regex.findall(r""+ reg, l))
                filter_stop_words = self.check_include_stop_word(l)
                result.append(self.recSplit(l, filter_stop_words))
            print(set(self.listmerge3(result)))
        
            group_count_slog = []
            group = []
            for offer in set(self.listmerge3(result)):
                count_slog_group = 0
                #Попробывать разделить с помощью билиотеки!!!
                for word in self.nlp(offer):
                    count_slog_group = count_slog_group + self.split_syllables(word) 
                if( count_slog_group > 1):
                    group_count_slog.append(count_slog_group - 1)
                    group.append(offer)

                    self.data.append(
                    {
                        "number_letter" : index_letter,
                        "group_slog_letter" : group_count_slog,
                        "group": group
                    }
            )

            index_letter = index_letter + 1

        self.counting_square_deviation()

        #count_slogs = self.split_syllables(token)

    def recSplit(self, split_letter, filter_stop_words):
        if(split_letter == 'On la traitait avec une familiarité sans gêne que cachait une sorte de bonté un peu méprisante pour la vieille fille'):
            ds = "dsa"
        doc = self.nlp(split_letter.lower())
        count_word_letter = len(re.findall(r'\w+', doc.text))

        res = [split_letter]
        spliter = [split_letter]
        for stop in filter_stop_words:
            letters = []
            i = 0
            for sp in spliter:
                indexs = [m.start() for m in re.finditer(stop, sp)]
                if(len(indexs) > 0):
                    indexs.append(0)
                    indexs.append(len(sp))

                    set_indexs = sorted(set(indexs), reverse=False)
                    for index, ind in enumerate(set_indexs):
                        if (index + 1 == len(set_indexs)): break

                        letters.append(sp[set_indexs[index]: set_indexs[index + 1]].strip())
                    res[i] = letters
                i = i + 1
                    #letters - массив из подстрок - тут нужна проверка на наличие определительного слова во всех частей - если в каком то нету, его преписывают к ближайшему
            res = list(set(self.listmerge3(res)))

            j = 0
            while(True):
                if(j >= len(res)): break

                start_index = j if j == 0  else j + len(re.findall(r'\w+', res[ j - 1]))
                end_index = len(re.findall(r'\w+', res[j]))
                count_t = len(re.findall('\\s|\'', res[j][start_index:end_index]))
                tokeniz = doc[start_index : end_index+count_t]    
                #tokeniz = self.nlp(doc.text.strip()[start_index : end_index].strip())
                #tokeniz = self.nlp(res[j])
                check = False

                if(len(re.findall(r'\w+', res[j])) < 2): 
                    check = True

                #for tok in tokeniz:
                    #if(tok.pos_ == "PROPN" or tok.pos_ == "VERB" or tok.pos_ == "VERB"):
                        #check = False
                        #break    

                if(check):
                    if(j == len(res) - 1):
                        res[j - 1] = res[j - 1] + " " + res[j]      
                    else:
                        res[j + 1] = res[j] + " " + res[j + 1]
                    res.remove(res[j])
                else:        
                    j = j + 1

            spliter = res

        return spliter

    def listmerge3(self, _list):
        all = []
        for ist in _list:
            if isinstance(ist, list):
                all.extend(ist)
            else:
                all.append(ist)
        return all

    def check_include_stop_word(self, split_letter):
        result = list(set(self.stop_words) & set(split_letter.split(" ")))
        return result

    def check_end_word(self, word):
        if len(word.text) == 3:
            check = True
            for w in word.text:
                if w in  (self.shum + self.sonant): check = False
            if ((word.text[len(word.text) - 2] + word.text[len(word.text) - 1]) in self.not_taken_symbols_end and check):
                return word.text[0:len(word.text) - 2]
            elif(word.text[len(word.text) - 1] in self.not_taken_symbols_end) :
                return word.text[0:len(word.text) - 1]
        elif len(word.text) > 3:
            if ((word.text[len(word.text) - 3] + word.text[len(word.text) - 2] + word.text[len(word.text) - 1]) in self.not_taken_symbols_end):
                return word.text[0:len(word.text) - 3]
            elif ((word.text[len(word.text) - 2] + word.text[len(word.text) - 1]) in self.not_taken_symbols_end):
                return word.text[0:len(word.text) - 2]
            elif(word.text[len(word.text) - 1] in self.not_taken_symbols_end):
                return word.text[0:len(word.text) - 1]
        return word.text





