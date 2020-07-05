from analysis_service import AnalysisService
from rules_syllables import SpanishRuleSyllables, FranchRuleSyllables
from build_graph import BuildGraph
from features import Feature
from nltk.tokenize import sent_tokenize
import re

def main():

    #Чтение файла и разбиение текста на предложения для дальнейшего анализа
    file1 = open('Soldados de Salamina.txt','r', encoding="utf-8")
    text= file1.read()
    sentences = sent_tokenize(text)
    file1.close()

    #Поиск аллитерации и ассонанаса для французского языка
    obj1 = AnalysisService(Feature.spanish_alliteration, Feature.spanish_assonance, sentences)
    obj1.start()

    #Поиск аллитерации и ассонанаса для испанского языка
    #obj1 = AnalysisService(Feature.franch_alliteration, Feature.franch_assonance, sentences)
    #obj1.start()

    print("__________________Search Alliteration's and Assonance's_________________________________")
    print(obj1.print_result_dict())
    print("__________________END_________________________________")

    #Отображение результатов нализа ритма текста для французского языка
    #franch = FranchRuleSyllables()
    #franch.start(sentences)

    #Отображение результатов анализа ритма текста для испанского языка
    spanish = SpanishRuleSyllables()
    spanish.start(sentences)

    print("__________________Analysis rhythm text's_________________________________")
    print(spanish.Q,spanish.x_sr_text, sep=";")
    #print(franch.Q,franch.x_sr_text, sep=";")
    print("__________________END_________________________________")

    BuildGraph.Graph(spanish.objects, "spanish")
    #BuildGraph.Graph(franch.data, "french")

if __name__ == "__main__":
    main()
