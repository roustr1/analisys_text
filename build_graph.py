import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
#from sklearn import datasets
import matplotlib.ticker as ticker
from itertools import groupby
from analysis_service import AnalysisService

class BuildGraph:
    @staticmethod
    def build_diagramm(elements):
        fig, ax = plt.subplots(2, 1)

        count_sounds = AnalysisService.count_all_words(elements)
        s = {}
        mas = []

        number = lambda d: d['number'] 
        for key, value in {k:list(v) for k,v in groupby(sorted(elements, key=number), number)}.items():
            lam = 0.0
            for i in value:
                if i["sound"] in s:
                    ax[0].bar(int(key) + lam, len(i["words"]), 0.1, color=s[i["sound"]])
                    ax[1].bar(int(key) + lam, len(i["words"]) / count_sounds[i["sound"]] * 100, 0.1, color=s[i["sound"]])
                else:
                    color = np.random.rand(255, 3)
                    s[i["sound"]] = color
                    ax[0].bar(int(key) + lam, len(i["words"]), 0.1, color=color, label=i["sound"])
                    ax[1].bar(int(key) + lam, len(i["words"]) / count_sounds[i["sound"]] * 100, 0.1, color=color, label=i["sound"])
                lam = lam + 0.1
        leg = plt.legend( loc = 'upper right', fontsize="smaller", handlelength=2)
        leg.set_draggable(True)
        plt.subplots_adjust(right=0.85)
        
        #  Устанавливаем интервал основных делений:
        ax[0].xaxis.set_major_locator(ticker.MultipleLocator(1))
        #  Устанавливаем интервал основных делений:
        ax[0].yaxis.set_major_locator(ticker.MultipleLocator(1))
        
        plt.show()

    @staticmethod
    def Graph(data, languge):
        cur = {}
        if languge=="french" :
            cur = BuildGraph.getDataFranchView(data)
        else:
             cur = BuildGraph.getDataSpanishView(data)
        x = cur["x"]
        y = cur["y"]
        # Построение графика
        #plt.title("Зависимости: y1 = x, y2 = x^2") # заголовок
        plt.xlabel("Номер межударного интервала")         # ось абсцисс
        plt.ylabel("Количество безударных слогов")    # ось ординат
        plt.grid()              # включение отображение сетки
        plt.plot(x, y)  # построение графика
        plt.show()

    @staticmethod
    def getDataFranchView(data):
        count_interval = 0
        slogs = []
        for element in data:
          #if(element["group_slog_letter"][len(element["group_slog_letter"]) - 1] > 1):
            #element["group_slog_letter"][len(element["group_slog_letter"]) - 1] = element["group_slog_letter"][len(element["group_slog_letter"]) - 1] - 1   
          slogs = slogs + element["group_slog_letter"]
          count_interval = count_interval + len(element["group_slog_letter"])
        
        if(len(slogs) > 0):  
            return {"x": range(0, count_interval), "y": slogs}
        
        return None

    @staticmethod
    def getDataSpanishView(objects):
        count_interval = 0
        slogs = []
        for element in objects:
          slogs.append(element["count_bezud"]) 
          count_interval = count_interval + 1
        
        if(len(slogs) > 0):  
            return {"x": range(0, count_interval), "y": slogs}
        
        return None
                  