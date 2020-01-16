import csv
import numpy as np
import pandas as pd
#from matplotlib import pyplot as plt
from pylab import *
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime
import time

class Dataman:

    def __init__(self, filename):
        '''
        filename sem extensao!
        '''
        self.file = filename
        self.extensao_botao='.bot'
        self.extensao_sinal='.txt'
        self.extensao_obs='.obs'
        self.volt=[]
        self.buttom=[]
        self.open_file()
        #self.volt_rms()

    # Leitura arquivo .txt (dados)
    def open_file(self):
        with open(self.file+self.extensao_sinal) as file:
            spam = csv.reader(file, delimiter='\n')
            for j,row in enumerate(spam):
                if j != 0:
                    self.volt.append(float(row[0].replace(',', '.'))*18.54)
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
        aq_time = len(self.volt) / self.sample_rate
        if aq_time > 60:
            minute = int(aq_time / 60)
            if aq_time % 60 != 0:
                self.aquisition_time = str(minute) + " min e " + str(aq_time - 60*minute) + " seg"
            else:
                self.aquisition_time = str(minute) + " min"
        else:
            self.aquisition_time = str(int(aq_time)) + ' seg'

        dev = time_nsample1.find('Dev')
        self.port = time_nsample1[dev+13:dev+21]

    def volt_rms(self):
        frame = []
        frame_buttom= []
        v_rms = []
        buttom_psec = []
        j = 1
        for i in range(len(self.volt)):
            if i >= (self.sample_rate-1)*j:
                j = j+1
                v_rms.append((sum(frame)/self.sample_rate)**(1/2))
                buttom_psec.append(sum(frame_buttom)/self.sample_rate)
                del frame[:]
                del frame_buttom[:]
            else:
                frame.append(self.volt[i]**2)
                frame_buttom.append(self.buttom[i])
        v_saida = [v_rms, buttom_psec]
        return v_saida        # Dois vetores, um é o sinal em volts, e o outro é o sinal do botao
        #print(v_rms)

    def plot_graph_no_filter(self):
        # Create traces
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=np.arange(len(self.volt)), y=self.volt,
                            mode='lines',
                            name='Signal Voltage [V]'))
        fig1.add_trace(go.Scatter(x=np.arange(len(self.volt)), y=self.buttom,
                            mode='lines',
                            name='Buttom Signal'))
        fig1.show()

    def plot_graph_rms(self):
        fig2 = go.Figure()
        v_rms = self.volt_rms()
        fig2.add_trace(go.Scatter(x=np.arange(len(v_rms[0])), y=v_rms[0],
                             mode='lines',
                             name='Voltage RMS [V]'))
        fig2.add_trace(go.Scatter(x=np.arange(len(v_rms[1])), y=v_rms[1],
                             mode='lines',
                             name='Buttom Signal'))
        fig2.show()

    def plot_graph(self, data):
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=np.arange(len(data)), y=data,
                            mode = 'lines', name='Data'))
        fig3.show()

    def read_pmu_file(self, filename):
        '''
        File name without extension
        '''
        extensao = '.csv'
        with open(filename+extensao) as file:
            spam = csv.reader(file, delimiter=',')
            value = []
            self.pmu_time = []
            for j,row in enumerate(spam):
                if j != 0:
                    value.append(float(row[1]))
                    pmu_time = float(row[0])/1000
                    pmu_time = datetime.datetime.fromtimestamp(pmu_time)
                    self.pmu_time.append(pmu_time)
        return value

    def plot_graph_rmsXcurrent(self, file_volt1, file_volt2, file_volt3, points_volt, file_curr1, file_curr2, file_curr3, points_curr):
        curr1_pmu = self.read_pmu_file(file_curr1)
        curr2_pmu = self.read_pmu_file(file_curr2)
        curr3_pmu = self.read_pmu_file(file_curr3)

        pmu_volt1 = self.adjust_data(self.volt_rms()[0], self.read_pmu_file(file_volt1), points_volt)
        pmu_volt2 = self.adjust_data(self.volt_rms()[0], self.read_pmu_file(file_volt2), points_volt)
        pmu_volt3 = self.adjust_data(self.volt_rms()[0], self.read_pmu_file(file_volt3), points_volt)

        data_current1 = self.adjust_data(self.volt_rms()[0], curr1_pmu, points_curr)
        data_current2 = self.adjust_data(self.volt_rms()[0], curr2_pmu, points_curr)
        data_current3 = self.adjust_data(self.volt_rms()[0], curr3_pmu, points_curr)

        tam_ax = len(self.volt_rms()[0])

        # Create figure with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        # Add traces
        fig.add_trace(
            go.Scatter(x=np.arange(tam_ax), y=self.volt_rms()[0], name="RMS Voltage"),
            secondary_y=False,
        )
        fig.add_trace(
            go.Scatter(x=np.arange(tam_ax), y=pmu_volt1, name="Voltage PMU P1"),
            secondary_y=False,
        )
        fig.add_trace(
            go.Scatter(x=np.arange(tam_ax), y=pmu_volt2, name="Voltage PMU P2"),
            secondary_y=False,
        )
        fig.add_trace(
            go.Scatter(x=np.arange(tam_ax), y=pmu_volt3, name="Voltage PMU P3"),
            secondary_y=False,
        )
        fig.add_trace(
            go.Scatter(x=np.arange(tam_ax), y=data_current1, name="Current P1"),
            secondary_y=True,
        )
        fig.add_trace(
            go.Scatter(x=np.arange(tam_ax), y=data_current2, name="Current P2"),
            secondary_y=True,
        )
        fig.add_trace(
            go.Scatter(x=np.arange(tam_ax), y=data_current3, name="Current P3"),
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
        
    def plot_graph_current(self, file_curr1, file_curr2, file_curr3, points):
        curr1_pmu = self.read_pmu_file(file_curr1)
        curr2_pmu = self.read_pmu_file(file_curr2)
        curr3_pmu = self.read_pmu_file(file_curr3)

        data_current1 = self.adjust_data(self.volt_rms()[0], curr1_pmu, points)
        data_current2 = self.adjust_data(self.volt_rms()[0], curr2_pmu, points)
        data_current3 = self.adjust_data(self.volt_rms()[0], curr3_pmu, points)

        tam_ax = len(self.volt_rms()[0])

        # Create figure with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        # Add traces
        fig.add_trace(
            go.Scatter(x=np.arange(tam_ax), y=self.volt_rms()[0], name="RMS Voltage"),
            secondary_y=False,
        )
        fig.add_trace(
            go.Scatter(x=np.arange(tam_ax), y=data_current1, name="Current P1"),
            secondary_y=True,
        )
        fig.add_trace(
            go.Scatter(x=np.arange(tam_ax), y=data_current2, name="Current P2"),
            secondary_y=True,
        )
        fig.add_trace(
            go.Scatter(x=np.arange(tam_ax), y=data_current3, name="Current P3"),
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

    def plot_graph_voltage(self, file_v1, file_v2, file_v3, points):
        volt1_pmu = self.read_pmu_file(file_v1)
        volt2_pmu = self.read_pmu_file(file_v2)
        volt3_pmu = self.read_pmu_file(file_v3)

        data_volt1 = self.adjust_data(self.volt_rms()[0], volt1_pmu, points)
        data_volt2 = self.adjust_data(self.volt_rms()[0], volt2_pmu, points)
        data_volt3 = self.adjust_data(self.volt_rms()[0], volt3_pmu, points)

        tam_ax = len(self.volt_rms()[0])

        # Create figure with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        # Add traces
        fig.add_trace(
            go.Scatter(x=np.arange(tam_ax), y=self.volt_rms()[0], name="RMS Voltage"),
            secondary_y=False,
        )
        fig.add_trace(
            go.Scatter(x=np.arange(tam_ax), y=data_volt1, name="Voltage P1"),
            secondary_y=True,
        )
        fig.add_trace(
            go.Scatter(x=np.arange(tam_ax), y=data_volt2, name="Voltage P2"),
            secondary_y=True,
        )
        fig.add_trace(
            go.Scatter(x=np.arange(tam_ax), y=data_volt3, name="Voltage P3"),
            secondary_y=True,
        )
        # Add figure title
        fig.update_layout(
            title_text="RMS Voltage x Mult/PMU Voltage"
        )
        # Set x-axis title
        fig.update_xaxes(title_text="Time [s]")
        # Set y-axes titles
        fig.update_yaxes(title_text="<b>RMS Voltage</b> Volts [V]", secondary_y=False)
        fig.update_yaxes(title_text="<b>Current Phase</b> Ampere [A]", secondary_y=True)
        fig.show()
        
    def plot_phase(self, file_pmu_curr, points):
        curr_pmu = self.adjust_data(self.volt_rms()[0], self.read_pmu_file(file_pmu_curr), points)

        tam_ax = len(self.volt_rms()[0])

        # Create figure with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        # Add traces
        fig.add_trace(
            go.Scatter(x=np.arange(tam_ax), y=self.volt_rms()[0], name="RMS Voltage"),
            secondary_y=False,
        )
        fig.add_trace(
            go.Scatter(x=np.arange(tam_ax), y=self.volt_rms()[1], name="Buttom"),
            secondary_y=False,
        )
        fig.add_trace(
            go.Scatter(x=np.arange(tam_ax), y=curr_pmu, name="Current P2"),
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

    def adjust_data(self, data_ref, data_adj, dots):
        '''
        Calc to adapt the 2 graphs
        Calcula numero de pontos maximos para que seja possivel plotar os 2 graficos
        com a mesma distribuicao no eixo x.

        Equação da Reta
        (y - yo) = m * (x - xo)
        m = (y - yo) / (x - xo)

        reta[posicao] = m * ( n(ponto da reta) * (y - yo) / res_points)

        |---n---*---*---*---*---*---*---*---|
        |---*---n---*---*---*---*---*---*---|
        |---*---*---n---*---*---*---*---*---|
        |---*---*---*---n---*---*---*---*---|
        |---*---*---*---*---n---*---*---*---|
        |---*---*---*---*---*---n---*---*---|
        |---*---*---*---*---*---*---n---*---|
        |---*---*---*---*---*---*---*---n---|
        '''
        tam_ref = len(data_ref)
        tam_adj = len(data_adj)
        

        if (tam_ref - tam_adj) > (tam_ref*0.01):
            #points = tam_ref
            res_points = dots    # dots segundos -> 1 segundo
            #res_points = points / tam_adj +1
            #res_points = np.ceil(res_points)        # Arredonda para o teto
            data_adjusted = []
            for i in range(1, tam_adj):
                y = data_adj[i]
                yo = data_adj[i-1]
                x = i
                xo = i-1
                m = (y - yo) / (x - xo)
                for k in range(int(res_points)):
                    data_adjusted.append(m * ((k+1) * (x - xo) / res_points) + yo)
        else:
            return data_adj

        '''
        if (tam_ref - tam_adj) > (tam_ref*0.01):
            points = tam_ref
            res_points = points / tam_adj
            res_points = np.ceil(res_points)        # Arredonda para o teto
            data_adjusted = []
            for i in range(1, tam_adj):
                y = data_adj[i]
                yo = data_adj[i-1]
                reta = np.arange(yo, y, res_points)
                for k in range(len(reta)):
                    data_adjusted.append(reta[k])
        else:
            return data_adj
        '''
        
        return data_adjusted

    def plot_2graphs(self, data1, data2, points):
        # Plot 2 graphs

        if len(data1) > len(data2):
            data_ref = data1
            data_adj = data2
        else:
            data_ref = data2
            data_adj = data1

        data_adjusted = self.adjust_data(data_ref, data_adj, points)

        # Create figure with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        # Add traces
        fig.add_trace(
            go.Scatter(x=np.arange(len(data_ref)), y=data_ref, name="Data 1"),
            secondary_y=False,
        )
        fig.add_trace(
            go.Scatter(x=np.arange(len(data_adjusted)), y=data_adjusted, name="Data 2"),
            secondary_y=True,
        )
        # Add figure title
        #fig.update_layout(
        #    title_text="RMS Voltage x Current"
        #)
        # Set x-axis title
        #fig.update_xaxes(title_text="Time [s]")
        # Set y-axes titles
        #fig.update_yaxes(title_text="<b>RMS Voltage</b> Volts [V]", secondary_y=False)
        #fig.update_yaxes(title_text="<b>Current</b> Phase 2 - Ampere [A]", secondary_y=True)
        fig.show()
