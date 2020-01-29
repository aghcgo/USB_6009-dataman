import csv
import numpy as np
import pandas as pd
#from matplotlib import pyplot as plt
from pylab import *
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime
import time
import json
import requests as r
import datetime #datetime.datetime().totimestamp()

# Definitions
ID_VOLT_PMU_EFC = [499, 501, 503]          # Fase 1, Fase 2 e Fase 3
ID_VOLT_MULTPK = [7247, 7248, 7249]        # Fase 1, Fase 2 e Fase 3
ID_CURRENT_MULTPK = [7252, 7253, 7254]     # Fase 1, Fase 2 e Fase 3

# DataManager With Multiple Channels

__author__ = "Diego R. Garzaro"
__copyright__ = "Copyright 2020"
__version__ = "1.0"
__status__ = "Production"

# beta
class DatamanMChannel:

    def __init__(self, filename):
        '''
        filename sem extensao!
        '''
        self.file = filename
        self.extensao_botao='.bot'
        self.extensao_sinal='.txt'
        self.extensao_obs='.obs'
        self.voltage={'volt1': [], 'volt2': [], 'volt3': [], 'volt4': [], 'volt5': [], 'volt6': [], 'volt7': [], 'volt8': []}
        self.buttom=[]
        self.open_file()
        #self.volt_rms()

    # Leitura arquivo .txt (dados)
    def open_file(self):
        RELACAO_TRAFO = [36.6476, 36.8195, 36.7143]
        with open(self.file+self.extensao_sinal) as file:
            spam = csv.reader(file, delimiter='\t')
            for j,row in enumerate(spam):
                if j != 0:
                    k = 0
                    try:
                        for i in self.voltage:
                            self.voltage[i].append(float(row[k].replace(',', '.'))*RELACAO_TRAFO[k])
                            k += 1
                    except Exception as e:
                        #print(e)
                        continue
                else:
                    time_nsample1 = row[0]
        # Leitura arquivo .botao
        with open(self.file+self.extensao_botao) as file:
            spam = csv.reader(file, delimiter='\n')
            for j,row in enumerate(spam):
                if j != 0:
                    self.buttom.append(int(row[0])*(10)+118)
                else:
                    time_nsample2 = row[0]
        # Leitura arquivo .observacao
        try:
            with open(self.file+self.extensao_obs, encoding = 'iso-8859-1') as f:
                mylist = list(f.read())
            self.obs = (''.join(mylist))
        except:
            self.obs = "Não existem observações"
            
        #self.time1 = time_nsample1[0:12].replace(':', '.')
        self.time1 = time_nsample1[0:12]
        self.time1 = self.time1.replace(',', '.')
        #self.time2 = time_nsample2[0:12].replace(':', '.')
        self.time2 = time_nsample2[0:12]
        self.time2 = self.time2.replace(',', '.')
        
        self.sample_rate = float((time_nsample1[time_nsample1.find('Hz')+5:-1].replace(',', '.')) + time_nsample1[-1])
        self.periodo = 1 / self.sample_rate
        
        #self.aquisition_time = len(self.volt) / self.sample_rate
        self.aq_time = int(len(self.voltage['volt1']) / self.sample_rate)
        if self.aq_time > 60:
            minute = int(self.aq_time / 60)
            if self.aq_time % 60 != 0:
                self.aquisition_time = str(minute) + " min e " + str(self.aq_time - 60*minute) + " seg"
            else:
                self.aquisition_time = str(minute) + " min"
        else:
            self.aquisition_time = str(int(self.aq_time)) + ' seg'

        dev = time_nsample1.find('Dev')
        self.port = time_nsample1[dev+13:dev+23]
            
    def volt_rms(self):
        voltage_rms = {'volt1': [], 'volt2': [], 'volt3': [], 'volt4': [], 'volt5': [], 'volt6': [], 'volt7': [], 'volt8': [], 'buttom': []}
        buttom_psec = []
        frame_buttom= []
        j = 1
        for i in range(len(self.buttom)):
                if i >= (self.sample_rate-1)*j:
                    j = j+1
                    voltage_rms['buttom'].append(sum(frame_buttom)/self.sample_rate)
                    del frame_buttom[:]
                else:
                    frame_buttom.append(self.buttom[i])
        for i in self.voltage:
            frame = []
            j = 1
            for k in range(len(self.voltage[i])):
                if k >= (self.sample_rate-1)*j:
                    j = j+1
                    voltage_rms[i].append((sum(frame)/self.sample_rate)**(1/2))
                    del frame[:]
                else:
                    frame.append(self.voltage[i][k]**2)
        return voltage_rms        # Dicionário que contém 8 sinais em volts, e o sinal do botao
    
    def plot_graph_rms(self):
        fig2 = go.Figure()
        v_rms = self.volt_rms()
        for i in range(len(v_rms)-1):   # Lista do botao nao entrar no loop
            if len(v_rms['volt'+str(i+1)]) > 0:
                fig2.add_trace(go.Scatter(x=np.arange(len(v_rms['volt'+str(i+1)])), y=v_rms['volt'+str(i+1)],
                                     mode='lines',
                                     name='Voltage RMS L' + str(i+1) + '[V]'))
        fig2.add_trace(go.Scatter(x=np.arange(len(v_rms['buttom'])), y=v_rms['buttom'],
                             mode='lines',
                             name='Buttom Signal'))
        fig2.show()
        
    def get_server_data(self, ID, ano, mes, dia, hora, minuto, segundo):
        start = datetime.datetime(ano,mes,dia,hora,minuto,segundo).timestamp()
        #start_converted = datetime.datetime.fromtimestamp(start)
        #print(start_converted)
        end = start + self.aq_time + 2*60 # Coleta até 2 minutos após o término da aquisição
        interval = 1
        #ID = 499 # Fase 1 - PMU (Eficiencia - Vega)
        url='url'
        s=r.get(url)
        #print(s)
        values = json.loads(s.text)
        return values

    def plot_graph_measure(self, meas1 = None, meas2 = None, meas3 = None):
        # Start the code to pick the block of datas according to the measured file
        meses = ['jan', 'feb', 'mar', 'abril', 'mai', 'jun', 'junho', 'ago', 'set', 'oct', 'nov', 'dez']
        dia = int(self.file[16:18])
        mes = self.file[18:21]
        mes = int(meses.index(mes)+1)
        ano = 2000 + int(self.file[21:23])

        hora = int(self.time1[0:2])
        minuto = int(self.time1[3:5]) - 2 # Começa a coleta de dados 2 minutos antes de começar a aquisição no NI-USB
        segundo = int(self.time1[6:8])

        medidores = []  # medidores = [[epoch_time_dado1, dado1], [epoch_time_dado2, dado2], [epoch_time_dado3, dado3], ... ] 
        for ident in ID_VOLT_PMU_EFC:
            medidores.append(self.get_server_data(ident, ano, mes, dia, hora, minuto, segundo))
        for ident in ID_VOLT_MULTPK:
            medidores.append(self.get_server_data(ident, ano, mes, dia, hora, minuto, segundo))
        for ident in ID_CURRENT_MULTPK:
            medidores.append(self.get_server_data(ident, ano, mes, dia, hora, minuto, segundo))
        
        if values[0][0] > 10000000000:
            for j in range(len(values[0])):
                values[0][j] = int(values[0][j] / 1000)
        self.pmu_time_epoch = values[0]
        #print(values)

        self.pmu_time = []
        for i in pmu_time_epoch:
            self.pmu_time.append(datetime.datetime.fromtimestamp(i))

        pmu_time_string = []                    # STOP HERE. NEED TO CONVERT TO DATETIME BEFORE EXECUTE THIS OPERATION
        for i in range(len(pmu_time)):          # Converting from datetime to string (to compare with the date of the NI-USB data date, and fit the data in the timeline)
            pmu_time_string.append(str(self.pmu_time[i])[11:-1] + str(self.pmu_time[i])[-1])

        tam_rms = len(self.voltage['volt1']) / self.sample_rate
        tam_data = self.pmu_time_epoch[-1] - self.pmu_time_epoch[0]
        
        # End of the block of code responsable to pick the PMU and MULT datas
        
        # Code responsable to compare the time of acquisition and fit the measured data inside the PMU and MULT datas
        
        niusb_time = self.time1[0:8]
        
        time_initial_epoch = self.pmu_time_epoch[0] + ((tam_data - tam_rms) / 2)
        
        for i in range(len(self.voltage['volt1'])):
            if pmu_time_string[i] == niusb_time:
                time_initial_epoch = self.pmu_time_epoch[i]
        
        time_initial = self.pmu_time_epoch[0] - time_initial_epoch
        time_final = self.pmu_time_epoch[-1] - time_initial_epoch
        vetor_x = np.arange(time_initial, time_final, 1)
        
        v_rms = self.volt_rms()
        
        # Create figure with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        # Add traces
        
        for i in range(len(v_rms)-1):   # Lista do botao nao entrar no loop
            if len(v_rms['volt'+str(i+1)]) > 0:
                fig2.add_trace(go.Scatter(x=np.arange(len(v_rms['volt'+str(i+1)])), y=v_rms['volt'+str(i+1)],
                                     mode='lines',
                                     name='Voltage RMS L' + str(i+1) + '[V]'))
        fig2.add_trace(go.Scatter(x=np.arange(len(v_rms['buttom'])), y=v_rms['buttom'],
                             mode='lines',
                             name='Buttom Signal'))
        
        fig.add_trace(
            go.Scatter(x=pmu_volt1[0], y=pmu_volt1[1], name="Voltage PMU L1"),
            secondary_y=False,
        )
        fig.add_trace(
            go.Scatter(x=pmu_volt2[0], y=pmu_volt2[1], name="Voltage PMU L2"),
            secondary_y=False,
        )
        fig.add_trace(
            go.Scatter(x=pmu_volt3[0], y=pmu_volt3[1], name="Voltage PMU L3"),
            secondary_y=False,
        )
        fig.add_trace(
            go.Scatter(x=data_current1[0], y=data_current1[1], name="Current L1"),
            secondary_y=True,
        )
        fig.add_trace(
            go.Scatter(x=data_current2[0], y=data_current2[1], name="Current L2"),
            secondary_y=True,
        )
        fig.add_trace(
            go.Scatter(x=data_current3[0], y=data_current3[1], name="Current L3"),
            secondary_y=True,
        )
        # Add figure title
        fig.update_layout(
            title_text="RMS Voltage x Current Phase"
        )
        # Set x-axis title
        fig.update_xaxes(title_text="Time [s]")
        # Set y-axes titles
        fig.update_yaxes(title_text="<b>RMS Voltage</b> Volts [V]", secondary_y=False)
        fig.update_yaxes(title_text="<b>Current Phase</b> Ampere [A]", secondary_y=True)
        fig.show()
