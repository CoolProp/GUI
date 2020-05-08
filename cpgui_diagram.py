# -*- coding: utf-8 -*- 
#
import matplotlib
matplotlib.use('TkAgg')
import gettext
import sys

from tkinter import *
from tkinter import ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.backend_bases import key_press_handler
import matplotlib.ticker as mplticker
from matplotlib.figure import Figure
import matplotlib.lines  as mpllines

import CoolProp
from CoolProp.CoolProp import PropsSI
#from CoolProp.Plots.Plots import PT,Ph,Prho,Ps,Trho,Ts,hs, drawIsoLines
#from CoolProp.Plots import PsychChart
#from CoolProp.Plots import PropsPlot

import numpy as np

from cpgui_all import *
#
def pa2bar(pascal):
    return pascal/100000.0

def bar2pa(bar):
    return bar*100000

def j2kj(joule):
    return joule/1000.0

def C2K(temperatur):
    return temperatur+273.15

def K2C(temperatur):
    return temperatur-273.15
#
class cpgDiagram(myDialog):
    
    def __init__(self, GridFrame,Caller):
        #
        self.dialogframe=GridFrame
        #
        self.Caller=Caller
        # by module translations
        self.language=cpgui_language
        localedir=find_data_file('locale')
        self.lang = gettext.translation('cpgDiagram', localedir=localedir, languages=[self.language])
        self.lang.install()
        #
        self.ref=Caller.get_ref()
        #
        self.frameborder=5
        #
        self.h_color='DarkCyan' # b
        self.t_color='r' # r
        self.d_color='SeaGreen' # g
        self.x_color='k' # k
        self.p_color='brown'
        self.s_color='blue'
        self.cp_color='MediumPurple'
        self.BubbleLine_color='MediumVioletRed'
        self.DewLine_color='DarkBlue'
        self.labelfontsize=10
        self.tickfontsize=8
        #
        self.ObenFrame= LabelFrame(self.dialogframe,relief=GROOVE,bd=self.frameborder,text=_('Available Diagrams'))
        self.ObenFrame.grid(row=1,column=1)
        #
        self.UntenFrame= LabelFrame(self.dialogframe,relief=GROOVE,bd=self.frameborder,text=_('Diagram'))
        self.UntenFrame.grid(row=1,column=2)
        #
        #self.l1=Label(self.ObenFrame,text='Text',font=("Arial", 12) )
        #self.l1.grid(row=0,column=0,padx=8,columnspan=5,sticky=W,pady=5)
        #
        self.RG1_Frame=Frame(self.ObenFrame,relief=GROOVE,bd=self.frameborder)
        self.RG1_Frame.grid(row=1,column=1,sticky=W,padx=5,pady=5)
        self.RG1_row=0
        
        self.RG1_StringVar = StringVar()
        self.RG1_StringVar.set("0")
        self.RG1_StringVar_traceName = self.RG1_StringVar.trace_variable("w", self.RG1_StringVar_Callback)

        self.RG1_Button_01 = Radiobutton(self.RG1_Frame,text='PT', value='PT', relief="raised",indicatoron=False,width=5 )
        self.RG1_Button_01.grid(column=1,row=self.RG1_row+1,padx=8,sticky=W)
        self.RG1_Button_01.configure(variable=self.RG1_StringVar)
        #
        self.RG1_Button_02 = Radiobutton(self.RG1_Frame,text='Ph', value='Ph', relief="raised",indicatoron=False,width=5 )
        self.RG1_Button_02.grid(column=1,row=self.RG1_row+2,padx=8,sticky=W)
        self.RG1_Button_02.configure(variable=self.RG1_StringVar )
        #
        self.RG1_Button_03 = Radiobutton(self.RG1_Frame,text='Prho', value='Prho', relief="raised",indicatoron=False,width=5 )
        self.RG1_Button_03.grid(column=1,row=self.RG1_row+3,padx=8,sticky=W)
        self.RG1_Button_03.configure(variable=self.RG1_StringVar )
        #
        self.RG1_Button_04 = Radiobutton(self.RG1_Frame,text='Ps', value='Ps', relief="raised",indicatoron=False,width=5 )
        self.RG1_Button_04.grid(column=1,row=self.RG1_row+4,padx=8,sticky=W)
        self.RG1_Button_04.configure(variable=self.RG1_StringVar)

        self.RG1_Button_05 = Radiobutton(self.RG1_Frame,text='Trho', value='Trho', relief="raised",indicatoron=False,width=5 )
        self.RG1_Button_05.grid(column=1,row=self.RG1_row+5,padx=8,sticky=W)
        self.RG1_Button_05.configure(variable=self.RG1_StringVar)
        #
        self.RG1_Button_06 = Radiobutton(self.RG1_Frame,text='Ts', value='Ts', relief="raised",indicatoron=False,width=5 )
        self.RG1_Button_06.grid(column=1,row=self.RG1_row+6,padx=8,sticky=W)
        self.RG1_Button_06.configure(variable=self.RG1_StringVar )
        #
        self.RG1_Button_07 = Radiobutton(self.RG1_Frame,text='hs', value='hs', relief="raised",indicatoron=False,width=5 )
        self.RG1_Button_07.grid(column=1,row=self.RG1_row+7,padx=8,sticky=W)
        self.RG1_Button_07.configure(variable=self.RG1_StringVar )
        #
        self.RG1_Button_08 = Radiobutton(self.RG1_Frame,text='Psyc', value='PsycChart', relief="raised",indicatoron=False,width=5 )
        self.RG1_Button_08.grid(column=1,row=self.RG1_row+8,padx=8,sticky=W)
        self.RG1_Button_08.configure(variable=self.RG1_StringVar )
        #
        self.fig = Figure(figsize=(9,6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        #Ph(str(self.ref),axis = self.ax,Tmin = PropsSI(str(self.ref),'Ttriple')+0.01)
        #a.plot(t,s)
        # a tk.DrawingArea
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.UntenFrame)
        self.canvas.show()
        self.canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
        
        self.toolbar = NavigationToolbar2TkAgg( self.canvas, self.UntenFrame )
        self.toolbar.update()
        self.canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)
        self.fig.canvas.set_window_title('Coolprop GUI plots')
    
    def format_ph_coord(self,x, y):
        #
        t,d,s=PropsSI(['T','D','S'],'P',y*1000,'H',x*1000,self.ref)
        v=1/d
        return 't=%1.2f K | h=%1.2f kJ/kg | p=%1.2f kPa | d=%1.4f kg/m*| v=%1.6f m*/kg | s=%1.4f J/kg/K '%(t,x,y,d,v,s)

    def format_coord(self,x, y):
        #
        return ' x = %4.4f   y = %4.4f '%(x,y)


    def RG1_StringVar_Callback(self, varName, index, mode):
        #
        self.ref=self.Caller.get_ref()
        #
        try:
            dia=self.RG1_StringVar.get()
        except(AttributeError):
            pass
        #
        insert=False
        #
        if dia=="PT" :
            self.ax.cla()
            try:
                PT(str(self.ref),axis = self.ax,Tmin = PropsSI(str(self.ref),'Ttriple')+0.01)
            except ValueError :
                self.plot_err()
            self.ax.format_coord = self.format_coord
            self.canvas.show()
        elif dia=="Ph" :
            self.ax.cla()
            #
            try :
                Pmin=PropsSI(self.ref,'ptriple')
            except ValueError :    
                Pmin=50000
            try :
                Tmin=PropsSI('T','P',Pmin,'Q',1,self.ref)
            except ValueError :
                print('Value error, setting Tmin to 0°C')
                Tmin=273.15
            Tmax=(220+273.15)
            Hmax=PropsSI('H','P',Pmin,'T',Tmax,self.ref)
            try :
                Hmin=PropsSI('H','P',Pmin,'Q',0,self.ref)-10000
            except ValueError :
                print('Value error, setting Hmin to 200000')
                Hmin=0
            Pmax=PropsSI(self.ref,'pcrit')*1.01
            #x-axis
            self.ax.xaxis.grid(True,which='both',color=self.h_color)
            self.ax.tick_params(axis='x',direction='in',which='both',pad=10)
            self.ax.set_xlim(j2kj(Hmin),j2kj(Hmax))
            if (j2kj(Hmax)-j2kj(Hmin)) > 1500 :
                self.ax.xaxis.set_major_locator(mplticker.MultipleLocator(200))
                self.ax.xaxis.set_minor_locator(mplticker.MultipleLocator(100))
            elif (j2kj(Hmax)-j2kj(Hmin)) > 870 :
                self.ax.xaxis.set_major_locator(mplticker.MultipleLocator(50))
                self.ax.xaxis.set_minor_locator(mplticker.MultipleLocator(25))
            else:
                self.ax.xaxis.set_major_locator(mplticker.MultipleLocator(20))
                self.ax.xaxis.set_minor_locator(mplticker.MultipleLocator(10))
                #
            for i in self.ax.xaxis.get_majorticklabels():
                i.set_fontsize(self.tickfontsize)
            for line in self.ax.get_xticklines():
                line.set_marker(mpllines.TICKDOWN)
            for tick in self.ax.xaxis.get_major_ticks():
                tick.label1.set_color(self.h_color)
                tick.label2.set_color(self.h_color)
            # y-axis
            self.ax.set_yscale('log')
            self.ax.yaxis.grid(True,which='both',color=self.p_color)
            self.ax.set_ylim(Pmin/1000,Pmax/1000)
            #base=10.0, subs=[1.0], numdecs=0,
            self.ax.yaxis.set_major_formatter(mplticker.FormatStrFormatter('%5.0f'))
            self.ax.yaxis.set_minor_formatter(mplticker.FormatStrFormatter('%5.0f'))
            self.ax.yaxis.set_major_locator(mplticker.LogLocator( numticks=48))
            for i in self.ax.yaxis.get_majorticklabels():
                i.set_fontsize(self.tickfontsize)
            for i in self.ax.yaxis.get_minorticklabels():
                i.set_fontsize(self.tickfontsize)
            for tick in self.ax.yaxis.get_major_ticks():
                tick.label1.set_color(self.p_color)
                tick.label2.set_color(self.p_color)
            for tick in self.ax.yaxis.get_minor_ticks():
                tick.label1.set_color(self.p_color)
                tick.label2.set_color(self.p_color)
            #
            print('Plots PH Tmin = ',Tmin)
            try :
                self.ph_plot=PropsPlot(self.ref, 'Ph',axis = self.ax)
            except ValueError :
                self.plot_err()
            # Overwrite ugly labels
            self.ax.set_ylabel(_('Pressure in kPa'),color=self.p_color,fontsize=self.labelfontsize)
            self.ax.set_xlabel(_('Specific enthalpy in kJ/kg'),color=self.h_color,fontsize=self.labelfontsize)
            # Show values of Mousepointer
            self.ax.format_coord = self.format_ph_coord
            #
            pressures=np.arange(Pmin, Pmax, 1000)
            temperatures=self.PH_Isothermal_values(Tmin,Tmax,10)
            for t in range(len(temperatures)):
                enthalpies=pressures*0.0
                for p in range(len(pressures)):
                    enthalpies[p]=PropsSI('H','P',pressures[p],'T',temperatures[t],self.ref)
                self.ax.plot(enthalpies/1000,pressures/1000,'r',linewidth=0.5)
                #print(t,enthalpies/1000,pressures/1000)
            try :
                self.ph_plot=PropsPlot(self.ref, 'Ph',axis = self.ax)
            except ValueError :
                self.plot_err()
            #
            self.canvas.show()
        elif dia=="Prho" :
            self.ax.cla()
            try:
                Prho(str(self.ref),axis = self.ax,Tmin = PropsSI(str(self.ref),'Ttriple')+0.01)
            except ValueError :
                self.plot_err()
            self.ax.format_coord = self.format_coord
            self.canvas.show()
        elif dia=="Ps" :
            self.ax.cla()
            try:
                Ps(str(self.ref),axis = self.ax,Tmin = PropsSI(str(self.ref),'Ttriple')+0.01)
            except ValueError :
                self.plot_err()
            self.ax.format_coord = self.format_coord
            self.canvas.show()
        elif dia=="Trho" :
            self.ax.cla()
            try:
                Trho(str(self.ref),axis = self.ax,Tmin = PropsSI(str(self.ref),'Ttriple')+0.01)
            except ValueError :
                self.plot_err()
            self.ax.format_coord = self.format_coord
            self.canvas.show()
        elif dia=="Ts" :
            self.ax.cla()
            try:
                Ts(str(self.ref),axis = self.ax,Tmin = PropsSI(str(self.ref),'Ttriple')+0.01)
            except ValueError :
                self.plot_err()
            self.ax.format_coord = self.format_coord
            self.canvas.show()
        elif dia=="hs" :
            self.ax.cla()
            try:
                hs(str(self.ref),axis = self.ax,Tmin = PropsSI(str(self.ref),'Ttriple')+0.01)
            except ValueError :
                self.plot_err()
            self.ax.format_coord = self.format_coord
            self.canvas.show()
        elif dia=="PsycChart" :
            self.ax.cla()
            Tmin = 263.15
            Tmax=333.15
            p = 101325
            PsychChart.p = p
            PsychChart.Tdb = np.linspace(Tmin,Tmax)
            SL = PsychChart.SaturationLine()
            SL.plot(self.ax)
            RHL = PsychChart.HumidityLines([0.05,0.1,0.15,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9])
            RHL.plot(self.ax)
            HL = PsychChart.EnthalpyLines(range(-20,100,10))
            HL.plot(self.ax)
            PF = PsychChart.PlotFormatting()
            PF.plot(self.ax)
            
            self.ax.format_coord = self.format_coord
            self.canvas.show()    

    def plot_err(self):
        self.ax.plot([0,1],[0,1],'r')
        self.ax.plot([0,1],[1,0],'r')
        self.ax.text(0.1,0.5,_('Only Coolprop single components can be used for plots!'))
            
    def Update(self):
        #
        pass

    def PH_Isothermal_values(self,Tmin,Tmax,steps):
        #
        t_high=round((Tmax-(steps/1.9999))/steps)*steps
        t_low=round((Tmin+(steps/1.9999))/steps)*steps
        answer=np.arange(t_low,t_high+steps,steps)
        return answer  
    
class _Testdialog:
    
    def __init__(self, master):
        frame = Frame(master)
        frame.pack()
        self.Caller = master
        self.x, self.y, self.w, self.h = -1,-1,-1,-1
        #
        self.ref='R134a'
        #
        App=cpgDiagram(frame,self)

    def get_ref(self):
        return 'R134a'
    def get_language(self):
        return 'de'
    
def main():
    root = Tk()
    
    app = _Testdialog(root)
    root.mainloop()
    
if __name__ == '__main__':
    main()  
