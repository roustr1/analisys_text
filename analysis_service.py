import re
import json
import math
from itertools import groupby

class AnalysisService:
    _rulebook_alliteration = {}
    _rulebook_assonance = {}
    _offers = []
    result_dict = {}

    def __init__(self, rulebook_alliteration, rulebook_assonance, offers):
        self._rulebook_alliteration = rulebook_alliteration
        self._rulebook_assonance = rulebook_assonance
        self._offers = offers

    def print_result_dict(self):
        print(json.dumps(self.result_dict["features_one"], indent=4))

    # подумать как объединить
    #def union_dict_analysis_offers(self, dict1, dict2):
        #if dict1 is not None:
            #return self.join_list_dictionary(dict1, dict2)
        #else:
            #return None

    @staticmethod
    def find_not_include_situation(current_word, next_word, list_exception):
        for element in list_exception:
            if len(element.split("_")) > 1 and next_word is not None:
                simbols = element.split("_")
                res1 = re.findall(simbols[0]+"$", current_word)
                res2 = re.findall("^" + simbols[1], next_word)
                if len(res1) > 0 and len(res2) > 0:
                    return simbols[0]
            else:        
                flag = re.findall(element, current_word)
                if len(flag) > 0 and len(element) > 0:
                    return flag[0]
        return None

    def start(self):
        alliterations = self.search_sounds_particular_rulebook("alliteration", self._rulebook_alliteration)
        assonance = self.search_sounds_particular_rulebook("assonance", self._rulebook_assonance)
        self.result_dict = {
            "features": alliterations["union"] + assonance["union"],
            "features_one": alliterations["one_offer"] + assonance["one_offer"],
            "features_two": alliterations["two_offer"] + assonance["two_offer"] 
        }

    def search_sounds_particular_rulebook(self, type_analysis, rulebook):
        feature = {"one_offer":[],"two_offer":[], "union":[]}
        prev_result = []
        for index, offer in enumerate(self._offers):
            index_end_offer = 1 if index - 1 < 0 else index + 1
            index_begin_offer = index

            begin_offer_first = len(re.findall(r'\w+', ''.join(self._offers[0:index_begin_offer])))
            last_offer_first = len(re.findall(r'\w+', ''.join(self._offers[0:index_begin_offer + 1]))) - 1
            begin_offer_two = len(re.findall(r'\w+', ''.join(self._offers[0:index_end_offer])))
            last_offer_two = len(re.findall(r'\w+', ''.join(self._offers[0:index_end_offer + 1]))) - 1

            #sounds_two = self.search_sound_in_offer(
             #   re.findall(r'\w+', self._offers[index + 1]),
              #  len(re.findall(r'\w+', ''.join(self._offers[0:index_end_offer]))),
               # rulebook,
                #begin_offer_two,
                #last_offer_two,
                #type_analysis
            #) if index + 1 != len(self._offers) else None
            sounds_first = self.search_sound_in_offer_one(
                re.findall(r'\w+', self._offers[index]),
                None,
                #len(re.findall(r'\w+', ''.join(self._offers[0:index_begin_offer]))),
                rulebook,
                begin_offer_first,
                last_offer_first,
                type_analysis,
                index + 1
            )
            #sounds_two = self.search_sound_in_offer_one(
                #re.findall(r'\w+', self._offers[index + 1]),
                #sounds_first,
                #len(re.findall(r'\w+', ''.join(self._offers[0:index_end_offer]))),
                #rulebook,
                #begin_offer_two,
                #last_offer_two,
                #type_analysis,
                #index + 1
            #) if index + 1 != len(self._offers) else []

            if len(sounds_first) > 0:
                #union_sounds = self.delete_unsuitable_elements(sounds_first) + sounds_two
                feature["one_offer"] = feature["one_offer"] + self.delete_unsuitable_elements(sounds_first)
                #feature["two_offer"] = feature["one_offer"] + sounds_two
                #feature["union"] = feature["union"] + union_sounds
            #union_sounds = self.union_dict_analysis_offers(sounds_first, sounds_two)

            #if union_sounds is not None:
                #feature = feature + union_sounds
        return feature

    def get_sound_list(self, current_list):
        result = []
        for element in current_list:
            result.append(element["sound"])
        return result  

    def get_words_rule(self, current_list, rule):
        if (current_list is None):
            return None 

        for element in current_list:
            if(element["sound"] == rule):
                return element
        return None   

    def search_sound_in_offer_one(self, words, word_prev_offer, rulebook, begin, end, type_analysis, number_offer):
        result_search_sound = []
        keys = sorted(rulebook, key=lambda l: len(l), reverse=True)
        if(word_prev_offer is not None):
           keys =  set(keys) & set(self.get_sound_list(word_prev_offer))
        for current_rule in keys:
            cur_position = begin
            result = {"sound": current_rule, "words": [], "context": [begin, end], "type": type_analysis, "number": number_offer}
            for index, word in enumerate(words):
                next_word = None if len(words) <= index + 1 else words[index + 1]
                sound = self.find_not_include_situation(word, next_word, rulebook[current_rule][0].split(";"))
                if sound is not None:
                    if self.find_not_include_situation(word, next_word, rulebook[current_rule][1].split(";")) is None:
                        search_feature_sound_word = self.get_ids_rule_in_word(current_rule, word)
                        resulting = self.check_include_sound_in_current_sound(
                            sound,
                            word,
                            cur_position,
                            result_search_sound
                        )

                        if resulting is not None:
                            search_current_sound_word = self.get_ids_rule_in_word(
                                result_search_sound[resulting[1]]["sound"],
                                word
                            )

                            if len(set(search_feature_sound_word) & set(search_current_sound_word)) > 0:
                                if resulting[2] and len(set(search_feature_sound_word) - set(search_current_sound_word)) > 0:
                                    result["words"].append({
                                        "word": word,
                                        "index": cur_position,
                                        "index_b": list(
                                            set(search_feature_sound_word) - set(search_current_sound_word))})
                                else:
                                    cur_position = cur_position + 1
                                    continue
                        else:
                            result["words"].append({
                                'word': word,
                                'index': cur_position,
                                "index_b": list(set(search_feature_sound_word))})
                cur_position = cur_position + 1
            if len(result["words"]) > 0:
                temp = self.get_words_rule(word_prev_offer, current_rule)
                if (temp is not None):
                    result["context"] = [min(temp["context"]), max(result["context"])]     
                    result["words"] = result["words"] + temp["words"]
                result_search_sound.append(result)
        return result_search_sound
    
    @staticmethod
    def delete_unsuitable_elements(current_list):
        result = []
        for element in current_list:
            if(len(element["words"]) > 1):
                result.append(element)
        return result   

    def search_sound_in_offer(self, words, position, rulebook, begin, end, type_analysis):
        result_search_sound = []
        keys = sorted(rulebook, key=lambda l: len(l), reverse=True)

        for current_rule in keys:
            cur_position = position
            povtor = 0
            for index, word in enumerate(words):
                next_word = None if len(words) <= index + 1 else words[index + 1]
                sound = self.find_not_include_situation(word, next_word, rulebook[current_rule][0].split(";"))
                if sound is not None:
                #if self.find_not_include_situation(word, next_word, rulebook[current_rule][1].split(";")) is None:
                    #sound = self.find_not_include_situation(word, next_word, rulebook[current_rule][0].split(";"))
                    #if sound is not None:
                    if self.find_not_include_situation(word, next_word, rulebook[current_rule][1].split(";")) is None:
                        result = {"sound": current_rule, "words": [], "context": [begin, end], "type": type_analysis}
                        search_feature_sound_word = self.get_ids_rule_in_word(current_rule, word)
                        resulting = self.check_include_sound_in_current_sound(
                            sound,
                            word,
                            cur_position,
                            result_search_sound
                        )

                        if resulting is not None:
                            search_current_sound_word = self.get_ids_rule_in_word(
                                result_search_sound[resulting[1]]["sound"],
                                word
                            )

                            if len(set(search_feature_sound_word) & set(search_current_sound_word)) > 0:
                                if resulting[2] and len(set(search_feature_sound_word) - set(search_current_sound_word)) > 0:
                                    result["words"].append({
                                        "word": word,
                                        "index": cur_position,
                                        "index_b": list(
                                            set(search_feature_sound_word) - set(search_current_sound_word))})
                                else:
                                    cur_position = cur_position + 1
                                    continue
                        else:
                            result["words"].append({
                                'word': word,
                                'index': cur_position,
                                "index_b": list(set(search_feature_sound_word))})
                        result_search_sound.append(result)
                cur_position = cur_position + 1
        return self.union_equal_sound_in_list_dictionary(result_search_sound)

    @staticmethod
    def check_include_sound_in_current_sound(sound_rule, current_word, current_word_index, res_new):
        for index_feature, obj in enumerate(res_new):
            if (sound_rule in obj["sound"]) or (len(set(sound_rule) & set(obj["sound"])) > 0):
                for index_word, word in enumerate(obj["words"]):
                    if word["word"] == current_word and word["index"] == current_word_index:
                        flag = sound_rule in obj["sound"]
                        return [index_word, index_feature, flag]
        return None

    @staticmethod
    def get_ids_rule_in_word(rule, word):
        id_s = []
        first_id = [m.start() for m in re.finditer("(?=" + rule + ")", word)]
        for i in range(0, len(rule)):
            for j in first_id:
                id_s.append(j + i)
        return id_s

    @staticmethod
    def union_equal_sound_in_list_dictionary(list_dictionary):
        result = []
        list_sounds = set()
        for key in list_dictionary:
            list_sounds.add(key["sound"])

        for key in list_sounds:
            new_dict = {"sound": key, "words": [], "context": []}
            for d in list_dictionary:
                if key == d["sound"]:
                    new_dict["context"] = [ min(new_dict["context"] + d["context"]), max(new_dict["context"] + d["context"])]
                    new_dict["words"] = new_dict["words"] + d["words"]
                    new_dict["type"] = d["type"]
            result.append(new_dict)
        return result

    def join_list_dictionary(self, list_dictionary1, list_dictionary2, prev_result):
        if list_dictionary2 is not None:
            for ind, obj in enumerate(list_dictionary1):
                for obj2 in list_dictionary2:
                    if obj["sound"] == obj2["sound"]:
                        obj["words"] = obj["words"] + obj2["words"]
                        obj["context"] = [min(obj["context"] + obj2["context"]), max(obj["context"] + obj2["context"])]

        for key in prev_result:
            for ind, key2 in enumerate(list_dictionary1):
                if key["sound"] == key2["sound"] and max(key["context"]) == max(key2["context"]):
                    list_dictionary1.pop(ind)
        return list_dictionary1

    @staticmethod
    def delete_elements_dict(list_dictionary):
        result = []
        list_sounds = set()
        for key in list_dictionary:
            list_sounds.add(key["sound"])

        for key in list_sounds:
            new_dict = {"sound": key, "words": [], "context": []}
            for d in list_dictionary:
                if key == d["sound"]:
                    new_dict["context"] = [ min(new_dict["context"] + d["context"]), max(new_dict["context"] + d["context"])]
                    new_dict["words"] = new_dict["words"] + d["words"]
                    new_dict["type"] = d["type"]
            result.append(new_dict)
        return result

    @staticmethod
    def comparison(obj1, obj2):
        count_sounds_mas1 = AnalysisService.count_all_words(obj1.result_dict["features_one"])
        count_sounds_mas2 = AnalysisService.count_all_words(obj2.result_dict["features_one"])

        chislitel = 0
        znamenatel = 0
        for key, value in count_sounds_mas1.items():
            if(key in count_sounds_mas2):
                chislitel = chislitel +((count_sounds_mas1[key]/ count_sounds_mas2[key]) * min(count_sounds_mas1[key], count_sounds_mas2[key]))
                znamenatel = znamenatel +((count_sounds_mas1[key]/ count_sounds_mas2[key]) * max(count_sounds_mas1[key], count_sounds_mas2[key]))
        minmax = chislitel / znamenatel
        return round(minmax, 3)
    @staticmethod
    def count_all_words(elements):
        sound = lambda d: d['sound']
        count_sounds = {}
        for key, value in {k:list(v) for k,v in groupby(sorted(elements, key=sound), sound)}.items():
            summer = 0
            for i in value:
                summer = summer + len(i["words"])
            count_sounds[key] = summer     
        return count_sounds     