# -*- coding: latin-1 -*-
"""
Created on Fri Feb 27 2015 16:45

@author: mayers
"""

import sys
if sys.version_info[0] < 3:
    from Tkinter import *
    import ttk
else:
    from tkinter import *
    from tkinter import ttk

import CoolProp
from CoolProp.CoolProp import PropsSI

from cpgui_all import myDialog,get_refprop_fluids
import numpy as np
       
class cpgSatTable(myDialog):
    
    def __init__(self, GridFrame,Caller):
        #
        self.initcomplete=False
        #
        self.dialogframe=GridFrame
        #
        self.Caller=Caller#
        self.ref=Caller.get_ref()
        #
        self.frameborder=5
        #
        self.choices1=('Pressure        [Pa]', 'Temperature     [K]')
        self.symbols1=('P','T')
        self.choices2=('Pure fluid', 'Mixture')
        #
        self.ObenFrame= LabelFrame(self.dialogframe,relief=GROOVE,bd=self.frameborder,text='Select order type and input Values',font=("Arial", 12))
        self.ObenFrame.grid(row=1,column=1)
        #
        self.UntenFrame= LabelFrame(self.dialogframe,relief=GROOVE,bd=self.frameborder,text='Fluid data',font=("Arial", 12))
        self.UntenFrame.grid(row=2,column=1)
        #
        self.Input1Label1 = Label(self.ObenFrame,text='Select order type',font=("Arial", 12) )
        self.Input1Label1.grid(row=1,column=1,padx=8,sticky=W,pady=5)
        self.Input1Label2 = Label(self.ObenFrame,text='        min value',font=("Arial", 12) )
        self.Input1Label2.grid(row=1,column=3,padx=8,sticky=W,pady=5)
        self.Input1Label3 = Label(self.ObenFrame,text='        max value',font=("Arial", 12) )
        self.Input1Label3.grid(row=2,column=3,padx=8,sticky=W,pady=5)
        self.Input1Label4 = Label(self.ObenFrame,text='        step size',font=("Arial", 12) )
        self.Input1Label4.grid(row=3,column=3,padx=8,sticky=W,pady=5)
        #
        self.Input1Entry1 = Entry(self.ObenFrame,width="15",font=("Arial", 12))
        self.Input1Entry1.grid(row=1,column=4,sticky=W,padx=8,pady=5)
        self.Input1Entry1_StringVar = StringVar()
        self.Input1Entry1.configure(textvariable=self.Input1Entry1_StringVar)
        self.Input1Entry1_StringVar.set("250")
        self.Input1Entry1_StringVar_traceName = self.Input1Entry1_StringVar.trace_variable("w", self.Input1Entry1_StringVar_Callback)
        #
        self.Input1Entry2 = Entry(self.ObenFrame,width="15",font=("Arial", 12))
        self.Input1Entry2.grid(row=2,column=4,sticky=W,padx=8,pady=5)
        self.Input1Entry2_StringVar = StringVar()
        self.Input1Entry2.configure(textvariable=self.Input1Entry2_StringVar)
        self.Input1Entry2_StringVar.set("373")
        self.Input1Entry2_StringVar_traceName = self.Input1Entry2_StringVar.trace_variable("w", self.Input1Entry2_StringVar_Callback)
        #
        self.Input1Entry3 = Entry(self.ObenFrame,width="15",font=("Arial", 12))
        self.Input1Entry3.grid(row=3,column=4,sticky=W,padx=8,pady=5)
        self.Input1Entry3_StringVar = StringVar()
        self.Input1Entry3.configure(textvariable=self.Input1Entry3_StringVar)
        self.Input1Entry3_StringVar.set("1")
        self.Input1Entry3_StringVar_traceName = self.Input1Entry3_StringVar.trace_variable("w", self.Input1Entry3_StringVar_Callback)
        #
        self.CBOX1_StringVar = StringVar()
        self.CBOX1_StringVar.set('Pressure        [Pa]')
        self.CBOX1_StringVar_traceName = self.CBOX1_StringVar.trace_variable("w",self.CBOX1_StringVar_Callback)
        self.CBOX1 = ttk.Combobox(self.ObenFrame, textvariable=self.CBOX1_StringVar,font=("Arial", 12))
        self.CBOX1['values'] = self.choices1
        self.CBOX1.grid(column=2,row=1,padx=8,sticky=W,pady=5)
        self.CBOX1.current(1)
        self.ordertype=self.CBOX1_StringVar.get()
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
        #
        self.initcomplete=True
            
    def CBOX1_StringVar_Callback(self, varName, index, mode):
        #
        self.Update()
         
    def Input1Entry1_StringVar_Callback(self, varName, index, mode):
        #
        pass

    def Input1Entry2_StringVar_Callback(self, varName, index, mode):
        #
        pass

    def Input1Entry3_StringVar_Callback(self, varName, index, mode):
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
        #
        #T1,P1,Q1,D1,H1,S1=PropsSI(['T','P','Q','D','H','S'],Input1Code,Input1Value,Input2Code,Input2Value,self.ref)
        #
        self.statetext='Saturated Table calculation for %s \n\n'%self.ref
        self.statetext+=u"   T   |    p    |    \u03C1\'   |    \u03C1\'\'   |    h\'  |   h\'\'  |    s\'  |   s\'\'   |   cv    |   cp    \n"  
        self.statetext+= "-----------------------------------------------------------------------------------------------------\n"
        self.Text_1.insert(END, self.statetext)
        self.datarow=" %5.1f | %7.0f | %6.2f | %8.4f | %6.0f | %6.0f | %6.2f | %6.2f | %6.3f | %6.3f \n"
        if self.ordertype == 'Temperature     [K]' :
            temperatures=np.arange(self.Tmin,self.Tmax+1,1)
            for T in range(len(temperatures)):
                TLIQ=temperatures[T]
                PLIQ,DLIQ,HLIQ,SLIQ=PropsSI(['P','D','H','S'],'T',temperatures[T],'Q',0,self.ref)
                PVAP,DVAP,HVAP,SVAP,CV,CP=PropsSI(['P','D','H','S','CVMASS','CPMASS'],'T',temperatures[T],'Q',1,self.ref)
                mydatarow=self.datarow%(TLIQ,PLIQ,DLIQ,DVAP,HLIQ,HVAP,SLIQ,SVAP,CV,CP)
                self.Text_1.insert(END, mydatarow)
        else :
            pressures=np.arange(self.Pmin,self.Pmax,10000)
            for P in range(len(pressures)):
                PLIQ=pressures[P]
                TLIQ,DLIQ,HLIQ,SLIQ=PropsSI(['T','D','H','S'],'P',pressures[P],'Q',0,self.ref)
                TVAP,DVAP,HVAP,SVAP,CV,CP=PropsSI(['T','D','H','S','CVMASS','CPMASS'],'P',pressures[P],'Q',1,self.ref)
                mydatarow=self.datarow%(TLIQ,PLIQ,DLIQ,DVAP,HLIQ,HVAP,SLIQ,SVAP,CV,CP)
                self.Text_1.insert(END, mydatarow)   
                             
    def Update(self):
        #
        if self.initcomplete :
            self.ref=self.Caller.get_ref()
            self.Tmin=round(self.search_Tmin()+0.5,0)
            self.Pmin=round((self.search_Pmin()+10000)/10000,0)*10000.0
            self.Tmax=self.search_Tmax()
            self.Pmax=self.search_Pmax()
            self.ordertype=self.CBOX1_StringVar.get()
            if self.ordertype == 'Temperature     [K]' :
                self.Input1Entry1_StringVar.set("%d"%self.Tmin)
                self.Input1Entry2_StringVar.set("%d"%self.Tmax)
                self.Input1Entry3_StringVar.set("%d"%1)
            else :
                self.Input1Entry1_StringVar.set("%d"%self.Pmin)
                self.Input1Entry2_StringVar.set("%d"%self.Pmax)
                self.Input1Entry3_StringVar.set("%d"%10000)            
                
            self.Text_1.delete(1.0, END)
            self.Ausgabetext= 'Coolprop Version     : %s     \n'%str(CoolProp.__version__)
            self.Ausgabetext+='Coolprop gitrevision : %s     \n'%str(CoolProp.__gitrevision__)
            self.Ausgabetext+='Refrigerant          : %s     \n'%str(self.ref)
    
            self.Text_1.insert(END,self.Ausgabetext)
            
    def search_Tmax(self):
        try :
            Tmax=round(PropsSI(self.ref,'TCRIT')-0.5,0)
        except ValueError :
            Tmax=0
            suchdruck=np.linspace(100000,10000000,1000)
            for sd in range(len(suchdruck)) :
                Pmax=suchdruck[sd]
                Tmax_old=Tmax
                try :
                    Tmax=PropsSI('T','P',Pmax,'Q',0,self.ref)
                except ValueError :
                    Tmax=Tmax_old
                    break
                
        return(Tmax)

    def search_Pmax(self):
        try :
            Pmax=round((PropsSI(self.ref,'PCRIT')-100)/100,0)*100.0
        except ValueError :
            Tmax=0
            suchdruck=np.linspace(100000,10000000,1000)
            for sd in range(len(suchdruck)) :
                Pmax=suchdruck[sd]
                Pmax_old=Pmax
                try :
                    Tmax=PropsSI('T','P',Pmax,'Q',0,self.ref)
                except ValueError :
                    Pmax=Pmax_old
                    break
                
        return(Pmax)
                    
    def search_Tmin(self):
        #
        self.ref=self.Caller.get_ref()
        try :
            Tmin=PropsSI(self.ref,'Ttriple')
        except ValueError :
            suchdruck=np.linspace(50000,0,1000)
            for sd in range(len(suchdruck)) :
                Pmin=suchdruck[sd]
                try :
                    Tmin=PropsSI('T','P',Pmin,'Q',1,self.ref)
                except ValueError :
                    Pmin=Pmin+50
                    break
            Tmin=PropsSI('T','P',Pmin,'Q',1,self.ref)
        return(Tmin)

    def search_Pmin(self):
        #
        self.ref=self.Caller.get_ref()
        try :
            Pmin=PropsSI(self.ref,'ptriple')
        except ValueError :
            suchdruck=np.linspace(50000,0,1000)
            for sd in range(len(suchdruck)) :
                Pmin=suchdruck[sd]
                try :
                    Tmin=PropsSI('T','P',Pmin,'Q',1,self.ref)
                except ValueError :
                    Pmin=Pmin+50
                    break
        return(Pmin)
    
class _Testdialog:
    
    def __init__(self, master):
        frame = Frame(master)
        frame.pack()
        self.master = master
        self.x, self.y, self.w, self.h = -1,-1,-1,-1
        #
        App=cpgsattable(frame,self)

def main():
    root = Tk()
    app = _Testdialog(root)
    root.mainloop()
    
if __name__ == '__main__':
    main()
