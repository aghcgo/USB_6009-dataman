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

    def read_pmu_file(self, filename):
        '''
        File name without extension
        '''
        extensao = '.csv'
        with open(filename+extensao) as file:
            spam = csv.reader(file, delimiter=',')
            value = []
            self.pmu_time_epoch = []
            self.pmu_time = []
            for j,row in enumerate(spam):
                if j != 0:
                    value.append(float(row[1]))
                    pmu_aux = int(float(row[0])/1000)
                    self.pmu_time_epoch.append(pmu_aux)
                    pmu_time = datetime.datetime.fromtimestamp(pmu_aux)
                    self.pmu_time.append(pmu_time)
        return value
    
    def adjust_data(self, data, dots):
        '''
        Function to adapt 2 graphs (read_pmu_file('file'), points)
        return 2D vector (time, values)
        '''
        
        niusb_time = self.time1[0:8]
        
        pmu_time_string = []
        for i in range(len(self.pmu_time)):
            pmu_time_string.append(str(self.pmu_time[i])[11:-1] + str(self.pmu_time[i])[-1])
        
        #print(pmu_time_string)
        #print(niusb_time)
        
        tam_rms = len(self.volt) / self.sample_rate
        tam_data = self.pmu_time_epoch[-1] - self.pmu_time_epoch[0]
        
        time_initial_epoch = self.pmu_time_epoch[0] + ((tam_data - tam_rms) / 2)
        
        for i in range(len(data)):
            if pmu_time_string[i] == niusb_time:
                time_initial_epoch = self.pmu_time_epoch[i]
        
        time_initial = self.pmu_time_epoch[0] - time_initial_epoch
        time_final = self.pmu_time_epoch[-1] - time_initial_epoch
        vetor_x = np.arange(time_initial, time_final, dots)
        out_data = [vetor_x, data]
        #print(time_initial)
        #print(time1)
        #print(pmu_time1[0])
        #print(pmu_time1[-1])
        #print(time_final)
        #print(vetor)
        #print(len(vetor))
        #print(len(pmu_volt))
        return out_data
        
    def plot_graph(self, data):
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=np.arange(len(data)), y=data,
                            mode = 'lines', name='Data'))
        fig3.show()

    def plot_graph_rmsXcurrent(self, file_volt1, file_volt2, file_volt3, points_volt, file_curr1, file_curr2, file_curr3, points_curr):
        curr1_pmu = self.read_pmu_file(file_curr1)
        curr2_pmu = self.read_pmu_file(file_curr2)
        curr3_pmu = self.read_pmu_file(file_curr3)
        
        data_current1 = self.adjust_data(curr1_pmu, points_curr)
        data_current2 = self.adjust_data(curr2_pmu, points_curr)
        data_current3 = self.adjust_data(curr3_pmu, points_curr)

        pmu_volt1 = self.adjust_data(self.read_pmu_file(file_volt1), points_volt)
        pmu_volt2 = self.adjust_data(self.read_pmu_file(file_volt2), points_volt)
        pmu_volt3 = self.adjust_data(self.read_pmu_file(file_volt3), points_volt)

        tam_ax = len(self.volt_rms()[0])

        # Create figure with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        # Add traces
        fig.add_trace(
            go.Scatter(x=np.arange(tam_ax), y=self.volt_rms()[0], name="RMS Voltage"),
            secondary_y=False,
        )
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
        
    def plot_graph_current(self, file_curr1, file_curr2, file_curr3, points):
        curr1_pmu = self.read_pmu_file(file_curr1)
        curr2_pmu = self.read_pmu_file(file_curr2)
        curr3_pmu = self.read_pmu_file(file_curr3)

        data_current1 = self.adjust_data(curr1_pmu, points)
        data_current2 = self.adjust_data(curr2_pmu, points)
        data_current3 = self.adjust_data(curr3_pmu, points)

        tam_ax = len(self.volt_rms()[0])

        # Create figure with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        # Add traces
        fig.add_trace(
            go.Scatter(x=np.arange(tam_ax), y=self.volt_rms()[0], name="RMS Voltage"),
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

    def plot_graph_voltage(self, file_v1, file_v2, file_v3, points):
        volt1_pmu = self.read_pmu_file(file_v1)
        volt2_pmu = self.read_pmu_file(file_v2)
        volt3_pmu = self.read_pmu_file(file_v3)

        data_volt1 = self.adjust_data(volt1_pmu, points)
        data_volt2 = self.adjust_data(volt2_pmu, points)
        data_volt3 = self.adjust_data(volt3_pmu, points)

        tam_ax = len(self.volt_rms()[0])

        # Create figure with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        # Add traces
        fig.add_trace(
            go.Scatter(x=np.arange(tam_ax), y=self.volt_rms()[0], name="RMS Voltage"),
            secondary_y=False,
        )
        fig.add_trace(
            go.Scatter(x=data_volt1[0], y=data_volt1[1], name="Voltage L1"),
            secondary_y=True,
        )
        fig.add_trace(
            go.Scatter(x=data_volt2[0], y=data_volt2[1], name="Voltage L2"),
            secondary_y=True,
        )
        fig.add_trace(
            go.Scatter(x=data_volt3[0], y=data_volt3[1], name="Voltage L3"),
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
        curr_pmu = self.adjust_data(self.read_pmu_file(file_pmu_curr), points)

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
            go.Scatter(x=curr_pmu[0], y=curr_pmu[1], name="Current L2"),
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

    def plot_2graphs(self, data1, points1, data2, points2):
        # Plot 2 graphs
        data_adjusted1 = self.adjust_data(data1, points1)
        data_adjusted2 = self.adjust_data(data2, points2)

        # Create figure with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        # Add traces
        fig.add_trace(
            go.Scatter(x=data1_adjusted1[0], y=data1_adjusted1[1], name="Data 1"),
            secondary_y=False,
        )
        fig.add_trace(
            go.Scatter(x=data1_adjusted2[0], y=data1_adjusted2[1], name="Data 2"),
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
