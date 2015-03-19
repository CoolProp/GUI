"""
Created on Fri Feb 27 2015 16:45

@author: mayers
"""
#
import matplotlib
matplotlib.use('TkAgg')

import sys
if sys.version_info[0] < 3:
    from Tkinter import *
    import ttk
else:
    from tkinter import *
    from tkinter import ttk

import CoolProp
from CoolProp.CoolProp import PropsSI

from cpgui_all import *
 
class cpgStatepoint(myDialog):
    
    def __init__(self, GridFrame,Caller):
        #
        self.dialogframe=GridFrame
        #
        self.Caller=Caller#
        self.ref=Caller.get_ref()
        #
        self.frameborder=5
        #
        self.choices=('Density         [kg/m*m*m]', 'Pressure        [Pa]', 'Temperature     [K]', 'Enthalpy        [J/kg]',
                      'Entropy         [J/kg/K]', 'Internal Energy [J/kg]', 'Vapour Quality  [kg/kg]')
        self.symbols=('D','P','T','H','S','GMASS','Q')
        self.ObenFrame= LabelFrame(self.dialogframe,relief=GROOVE,bd=self.frameborder,text='Select entry txpes and input Values',font=("Arial", 12))
        self.ObenFrame.grid(row=1,column=1)
        #
        self.UntenFrame= LabelFrame(self.dialogframe,relief=GROOVE,bd=self.frameborder,text='Fluid data',font=("Arial", 12))
        self.UntenFrame.grid(row=2,column=1)
        #
        self.Input1Label1 = Label(self.ObenFrame,text='Select input type #1',font=("Arial", 12) )
        self.Input1Label1.grid(row=1,column=1,padx=8,sticky=W,pady=5)
        self.Input1Label2 = Label(self.ObenFrame,text='Enter input Value #1',font=("Arial", 12) )
        self.Input1Label2.grid(row=1,column=3,padx=8,sticky=W,pady=5)
        #
        self.Input1Entry1 = Entry(self.ObenFrame,width="15",font=("Arial", 12))
        self.Input1Entry1.grid(row=1,column=4,sticky=W,padx=8,pady=5)
        self.Input1Entry1_StringVar = StringVar()
        self.Input1Entry1.configure(textvariable=self.Input1Entry1_StringVar)
        self.Input1Entry1_StringVar.set("101325")
        self.Input1Entry1_StringVar_traceName = self.Input1Entry1_StringVar.trace_variable("w", self.Input1Entry1_StringVar_Callback)
        #
        self.CBOX1_StringVar = StringVar()
        self.CBOX1_StringVar.set('Pressure        [Pa]')
        self.CBOX1_StringVar_traceName = self.CBOX1_StringVar.trace_variable("w",self.CBOX1_StringVar_Callback)
        
        self.CBOX1 = ttk.Combobox(self.ObenFrame, textvariable=self.CBOX1_StringVar,font=("Arial", 12))
        self.CBOX1['values'] = self.choices
        self.CBOX1.grid(column=2,row=1,padx=8,sticky=W,pady=5)
        self.CBOX1.current(1)
        #
        #
        #
        self.Input2Label1 = Label(self.ObenFrame,text='Select input type #2',font=("Arial", 12) )
        self.Input2Label1.grid(row=2,column=1,padx=8,sticky=W,pady=5)
        self.Input2Label2 = Label(self.ObenFrame,text='Enter input Value #2',font=("Arial", 12) )
        self.Input2Label2.grid(row=2,column=3,padx=8,sticky=W,pady=5)
        #
        self.Input2Entry1 = Entry(self.ObenFrame,width="15",font=("Arial", 12))
        self.Input2Entry1.grid(row=2,column=4,sticky=W,padx=8,pady=5)
        self.Input2Entry1_StringVar = StringVar()
        self.Input2Entry1.configure(textvariable=self.Input2Entry1_StringVar)
        self.Input2Entry1_StringVar.set("298")
        self.Input2Entry1_StringVar_traceName = self.Input2Entry1_StringVar.trace_variable("w", self.Input2Entry1_StringVar_Callback)
        #
        self.CBOX2_StringVar = StringVar()
        self.CBOX2_StringVar.set('Pressure        [Pa]')
        self.CBOX2_StringVar_traceName = self.CBOX2_StringVar.trace_variable("w",self.CBOX2_StringVar_Callback)
        
        self.CBOX2 = ttk.Combobox(self.ObenFrame, textvariable=self.CBOX2_StringVar,font=("Arial", 12))
        self.CBOX2['values'] = self.choices
        self.CBOX2.grid(column=2,row=2,padx=8,sticky=W,pady=5)
        self.CBOX2.current(2)
        #
        self.Button_1 = Button(self.ObenFrame,text='Calculate' )
        self.Button_1.grid(row=1,rowspan=2,column=6,pady=5,sticky=W,padx=8)
        self.Button_1.bind("<ButtonRelease-1>", self.calculate)
        #
        # Textbox
        #
        self.statetext=''
        lbframe1 = Frame( self.UntenFrame )
        self.Text_1_frame = lbframe1
        scrollbar1 = Scrollbar(lbframe1, orient=VERTICAL)
        self.Text_1 = Text(lbframe1, width="110", height="20", yscrollcommand=scrollbar1.set)
        scrollbar1.config(command=self.Text_1.yview)
        scrollbar1.pack(side=RIGHT, fill=Y)
        self.Text_1.pack(side=LEFT, fill=BOTH, expand=1)
        self.Text_1_frame.grid(row=1,column=1,columnspan=1,padx=2,sticky=W+E,pady=4)
        self.Text_1.delete(1.0, END)
        #self.Ausgabetext=KM.KM_Info(self.refrigerant)
        self.Text_1.insert(END, self.statetext)
        
    def CBOX1_StringVar_Callback(self, varName, index, mode):
        #
        pass
         
    def Input1Entry1_StringVar_Callback(self, varName, index, mode):
        #
        pass

    def CBOX2_StringVar_Callback(self, varName, index, mode):
        #
        pass
         
    def Input2Entry1_StringVar_Callback(self, varName, index, mode):
        #
        pass
    
    def calculate(self,event):
        #
        self.statetext=''
        self.Text_1.delete(1.0, END)
        self.ref=self.Caller.get_ref()
        Input1Code=self.symbols[self.choices.index(self.CBOX1_StringVar.get())]
        Input1Value=float(self.Input1Entry1_StringVar.get())
        Input2Code=self.symbols[self.choices.index(self.CBOX2_StringVar.get())]
        Input2Value=float(self.Input2Entry1_StringVar.get())
        #
        T1,P1,Q1,D1,H1,S1=PropsSI(['T','P','Q','D','H','S'],Input1Code,Input1Value,Input2Code,Input2Value,self.ref)
        #
        Phase=CoolProp.CoolProp.PhaseSI(Input1Code,Input1Value,Input2Code,Input2Value,self.ref)
        self.statetext='Statepoint calculation for %s \n\n'%self.ref
        self.statetext+=    u'Temperature       %16.4f K  \n                  %16.4f degC  \n'%(T1,T1-273.15)
        self.statetext+=    u'Pressure          %16.4f Pa \n'%P1
        self.statetext+=    u'Quality                   %s \n'%(Phase)
        self.statetext+=    u'Density           %16.4f kg/m*m*m \n'%D1
        self.statetext+=    u'Enthalpy          %16.4f J/kg \n'%H1
        self.statetext+=    u'Entropy           %16.4f J/kg/K \n'%S1
        self.Text_1.insert(END, self.statetext)
        
        def Update(self):
            #
            pass

    
