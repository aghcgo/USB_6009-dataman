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

# DataManager Multiple Channels

__author__ = "Diego R. Garzaro"
__copyright__ = "Copyright 2020"
__version__ = "1.0"
__status__ = "Production"

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
        
    def get_server_data(self, ID, ano, mes, dia, hora, minuto, segundo, interval):
        start = datetime.datetime(ano,mes,dia,hora,minuto,segundo).timestamp()
        #start_converted = datetime.datetime.fromtimestamp(start)
        #print(start_converted)
        tempo_adicional = 20
        end = start + self.aq_time + 2*tempo_adicional # Tempo adicional no início e término da aquisição
        #interval = 1
        #ID = 499 # Fase 1 - PMU (Eficiencia - Vega)
        url='url'%(ID,start,end,interval)
        s=r.get(url)
        #print(s)
        values = json.loads(s.text)
        time = []
        data = []
        for i in range(len(values)):
            time.append(values[i][0])
            data.append(values[i][1])
        values = [time, data]
        #for i in time:
        #    print(datetime.datetime.fromtimestamp(int(i/1000)))
        return values

    def plot_graph_measure(self, meas_pmu = None, meas_mult_volt = None, meas_mult_current = None):
        # Start the code to pick the block of datas according to the measured file
        meses = ['jan', 'feb', 'mar', 'abril', 'mai', 'jun', 'jul', 'ago', 'set', 'oct', 'nov', 'dez']
        dia = int(self.file[16:18])
        mes = self.file[18:21]
        mes = int(meses.index(mes)+1)
        ano = 2000 + int(self.file[21:23])

        hora = int(self.time1[0:2])
        minuto = int(self.time1[3:5]) - 2 # Começa a coleta de dados 2 minutos antes de começar a aquisição no NI-USB
        segundo = int(self.time1[6:8])

        print('HORA_GET_DATAS:', ano, mes, dia, hora, minuto, segundo)
        
        # medidores = (Dicionário) { PMU [FASE1[epoch_time, value], FASE2[epoch_time, value], FASE3[epoch_time, value]], MULTPK_VOLT[FASE1, FASE2, FASE3], MULTPK_CURRENT[FASE1, FASE2, FASE3] }
        medidores = {'PMU': [], 'MULTPK_VOLT': [], 'MULTPK_CURRENT': []}  
        epoch_aux = 0
        if (meas_pmu == None):
            for ident in ID_VOLT_PMU_EFC:
                interval = 1
                medidores['PMU'].append(self.get_server_data(ident, ano, mes, dia, hora, minuto, segundo, interval))
                epoch_aux = medidores['PMU'][0]
                print('pmu')
        if (meas_mult_volt == None):
            for ident in ID_VOLT_MULTPK:
                interval = 60
                medidores['MULTPK_VOLT'].append(self.get_server_data(ident, ano, mes, dia, hora, minuto, segundo, interval))
                epoch_aux = medidores['MULTPK_VOLT'][0]
                print('multpk_volt')
        if (meas_mult_current == None):
            for ident in ID_CURRENT_MULTPK:
                inteval = 10
                medidores['MULTPK_CURRENT'].append(self.get_server_data(ident, ano, mes, dia, hora, minuto, segundo, interval))
                epoch_aux = medidores['MULTPK_CURRENT'][0]
                print('multpk_current')
        #print(epoch_aux)
        #print(len(epoch_aux))
        self.pmu_time_epoch = []
        try:
            if epoch_aux == 0:
                print('PLOT_GRAPH_MEASURE: Dados de PMU/Multimedidor não foram habilitados')
            #print(epoch_aux)
            #print(epoch_aux[0][0])
            if epoch_aux[0][0] > 10000000000: # Fase 1 [ [0] (time) [0] (epoch_time) ]
                for j in range(len(epoch_aux[0])):
                    self.pmu_time_epoch.append(int(epoch_aux[0][j] / 1000))
                    #print(int(epoch_aux[j][0] / 1000))
            #print(values)
        except:
            print('PLOT_GRAPH_MEASURE: Dados de PMU/Multimedidor não foram habilitados')
            print(epoch_aux)
            return
        print(len(self.pmu_time_epoch))
        print(self.pmu_time_epoch)

        self.pmu_time = []
        for i in self.pmu_time_epoch:
            self.pmu_time.append(datetime.datetime.fromtimestamp(i))

        pmu_time_string = []                    # STOP HERE. NEED TO CONVERT TO DATETIME BEFORE EXECUTE THIS OPERATION
        for i in range(len(self.pmu_time)):          # Converting from datetime to string (to compare with the date of the NI-USB data date, and fit the data in the timeline)
            pmu_time_string.append(str(self.pmu_time[i])[11:-1] + str(self.pmu_time[i])[-1])

        v_rms = self.volt_rms()
        
        tam_rms = len(v_rms['volt1']) / self.sample_rate
        tam_data = self.pmu_time_epoch[-1] - self.pmu_time_epoch[0]
        
        # End of the block of code responsable to pick the PMU and MULT datas
        
        # Code responsable to compare the time of acquisition and fit the measured data inside the PMU and MULT datas
        
        niusb_time = self.time1[0:8]
        
        #print('HORARIOS PMU', self.pmu_time)
        #print('HORARIO AQUISICAO', niusb_time)
        
        time_initial_epoch = self.pmu_time_epoch[0] + ((tam_data - tam_rms) / 2)
        print('tam vrms', len(v_rms['volt1']))
        print('tam pmu string vetor', len(pmu_time_string))
        for i in range(len(pmu_time_string)):
            if pmu_time_string[i] == niusb_time:
                time_initial_epoch = self.pmu_time_epoch[i]
        
        time_initial = self.pmu_time_epoch[0] - time_initial_epoch
        time_final = self.pmu_time_epoch[-1] - time_initial_epoch
        vetor_x = np.arange(time_initial, time_final, 1)
        #v_rms = self.volt_rms()
        
        # Create figure with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        # Add traces
        
        print(type(medidores['PMU'][0][1]))
        print(medidores['PMU'][0][1])
        
        for i in range(len(v_rms)-1):   # Lista do botao nao entrar no loop
            if len(v_rms['volt'+str(i+1)]) > 0:
                fig.add_trace(go.Scatter(x=np.arange(len(v_rms['volt'+str(i+1)])), y=v_rms['volt'+str(i+1)],
                                     mode='lines',
                                     name='Voltage RMS L' + str(i+1) + '[V]'), secondary_y=False)
        fig.add_trace(go.Scatter(x=np.arange(len(v_rms['buttom'])), y=v_rms['buttom'],
                             mode='lines',
                             name='Buttom Signal'), secondary_y=False)
        
        j = 1
        for med in medidores:
            if len(medidores[med]) > 0:
                if med == 'PMU' or 'MULTPK_VOLT':
                    for i in range(len(medidores[med])):
                        fig.add_trace(
                            go.Scatter(x=vetor_x, y=medidores[med][i][1], name= med + " L" + str(j)),
                            secondary_y=False,
                        )
                        j += 1
                        if j > 3:
                            j = 1
                else:
                    for i in range(len(medidores[med])):
                        fig.add_trace(
                            go.Scatter(x=vetor_x, y=medidores[med][1], name= i + " L" + str(j)),
                            secondary_y=True,
                        )
                        j += 1
                        if j > 3:
                            j = 1
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
