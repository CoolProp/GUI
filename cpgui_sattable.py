# -*- coding: utf-8 -*-
"""
Created on Fri Feb 27 2015 16:45

@author: mayers
"""

import sys
import gettext

from tkinter import *
from tkinter import ttk

import CoolProp
from CoolProp.CoolProp import PropsSI

from cpgui_all import *

import numpy as np
       
class cpgSatTable(myDialog):
    
    def __init__(self, GridFrame,Caller):
        #
        self.initcomplete=False
        #
        self.dialogframe=GridFrame
        #
        self.Caller=Caller
        # by module translations
        self.language=cpgui_language
        localedir=find_data_file('locale')
        self.lang = gettext.translation('cpgSatTable', localedir=localedir, languages=[self.language])
        self.lang.install()
        #
        self.kmstring=_('Refrigerant          : %10s     \n')
        self.titel=_('Saturated Table calculation for %10s \n')
        #
        self.ref=Caller.get_ref()
        #
        self.frameborder=5
        #
        self.choices=(  label['T'], 
                        label['p'],
                        )
        self.symbols=('T','p')
        #
        self.ObenFrame= LabelFrame(self.dialogframe,relief=GROOVE,bd=self.frameborder,text=_('Select order type and input Values'),font=("Arial", 12))
        self.ObenFrame.grid(row=1,column=1)
        #
        self.UntenFrame= LabelFrame(self.dialogframe,relief=GROOVE,bd=self.frameborder,text=_('Fluid data'),font=("Arial", 12))
        self.UntenFrame.grid(row=2,column=1)
        #
        self.Input1Label1 = Label(self.ObenFrame,text=_('Select order type'),font=("Arial", 12) )
        self.Input1Label1.grid(row=1,column=1,padx=8,sticky=W,pady=5)
        self.Input1Label2 = Label(self.ObenFrame,text=_('        min value'),font=("Arial", 12) )
        self.Input1Label2.grid(row=1,column=3,padx=8,sticky=W,pady=5)
        self.Input1LabelU1 = Label(self.ObenFrame,text=_('x '),font=("Arial", 12) )
        self.Input1LabelU1.grid(row=1,column=5,padx=8,sticky=W,pady=5)
        self.Input1Label3 = Label(self.ObenFrame,text=_('        max value'),font=("Arial", 12) )
        self.Input1Label3.grid(row=2,column=3,padx=8,sticky=W,pady=5)
        self.Input1LabelU2 = Label(self.ObenFrame,text=_('x '),font=("Arial", 12) )
        self.Input1LabelU2.grid(row=2,column=5,padx=8,sticky=W,pady=5)
        self.Input1Label4 = Label(self.ObenFrame,text=_('        step size'),font=("Arial", 12) )
        self.Input1Label4.grid(row=3,column=3,padx=8,sticky=W,pady=5)
        self.Input1LabelU3 = Label(self.ObenFrame,text=_('x '),font=("Arial", 12) )
        self.Input1LabelU3.grid(row=3,column=5,padx=8,sticky=W,pady=5)
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
        self.CBOX1_StringVar.set(label['p'])
        self.CBOX1_StringVar_traceName = self.CBOX1_StringVar.trace_variable("w",self.CBOX1_StringVar_Callback)
        self.CBOX1 = ttk.Combobox(self.ObenFrame, textvariable=self.CBOX1_StringVar,font=("Arial", 12))
        self.CBOX1['values'] = self.choices
        self.CBOX1.grid(column=2,row=1,padx=8,sticky=W,pady=5)
        self.CBOX1.current(1)
        self.ordertype=self.CBOX1_StringVar.get()
        #
        self.Button_1 = Button(self.ObenFrame,text=_('Calculate' ))
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
        #self.statetext=KM.KM_Info(self.refrigerant)
        self.Text_1.insert(END, self.statetext)
        #
        self.initcomplete=True
            
    def CBOX1_StringVar_Callback(self, varName, index, mode):
        #
        long_quant=self.CBOX1_StringVar.get()
        #
        mykey=' '
        for key in label.keys():
            if label[key] == long_quant:
                self.Input1LabelU1.config(text=GUI_UNIT(key))
                self.Input1LabelU2.config(text=GUI_UNIT(key))
                if key == 'T' :
                    self.Input1LabelU3.config(text=GUI_UNIT('dT'))
                    
                else :
                    self.Input1LabelU3.config(text=GUI_UNIT(key))
                self.Quantity=key
        # Now set default Values
        #self.Line1E1_StringVar.set(default[GUI_UNIT(self.Quantity1)])
        #self.Value1=TO_SI(self.Quantity1,float(self.Line1E1_StringVar.get().replace(',','.')))
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
        self.Text_1.delete(1.0, END)
        self.ref=self.Caller.get_ref()
        #
        self.statetext=self.titel%self.ref
        self.statetext+='\n'
        self.statetext+=u"   T     |     p     |    \u03C1\'   |    \u03C1\'\'   |    h\'  |   h\'\'  |    s\'  |   s\'\'   |   cv    |   cp    \n"  
        self.statetext+= "-----------------------------------------------------------------------------------------------------\n"
        self.Text_1.insert(END, self.statetext)
        self.datarow=" %7.2f | %9.4f | %6.2f | %8.4f | %6.2f | %6.2f | %6.2f | %6.2f | %6.3f | %6.3f \n"
        
        #self.Value1=TO_SI(self.Quantity1,float(self.Line1E1_StringVar.get().replace(',','.')))
        if self.Quantity == 'T' :
            self.Tmin=TO_SI(self.Quantity,float(self.Input1Entry1_StringVar.get().replace(',','.')))
            self.Tmax=TO_SI(self.Quantity,float(self.Input1Entry2_StringVar.get().replace(',','.')))
            self.steps=TO_SI('dT',float(self.Input1Entry3_StringVar.get().replace(',','.')))
            temperatures=np.arange(self.Tmin,self.Tmax,self.steps)

            for T in range(len(temperatures)):
                TLIQ=temperatures[T]
                try :
                    PLIQ,DLIQ,HLIQ,SLIQ=PropsSI(['P','D','H','S'],'T',temperatures[T],'Q',0,self.ref)
                except ValueError :
                    PLIQ,DLIQ,HLIQ,SLIQ=np.NaN,np.NaN,np.NaN,np.NaN
                try :
                    PVAP,DVAP,HVAP,SVAP,CV,CP=PropsSI(['P','D','H','S','CVMASS','CPMASS'],'T',temperatures[T],'Q',1,self.ref)
                except ValueError :
                    PVAP,DVAP,HVAP,SVAP,CV,CP=np.NaN,np.NaN,np.NaN,np.NaN,np.NaN,np.NaN                 
                mydatarow=self.datarow%(
                                        SI_TO('T',TLIQ),
                                        SI_TO('p',PLIQ),
                                        SI_TO('D',DLIQ),
                                        SI_TO('D',DVAP),
                                        SI_TO('H',HLIQ),
                                        SI_TO('H',HVAP),
                                        SI_TO('S',SLIQ),
                                        SI_TO('S',SVAP),
                                        SI_TO('Cv',CV),
                                        SI_TO('Cp',CP)
                                        )
                self.Text_1.insert(END, mydatarow)
        else :
            self.Pmin=TO_SI(self.Quantity,float(self.Input1Entry1_StringVar.get().replace(',','.')))
            self.Pmax=TO_SI(self.Quantity,float(self.Input1Entry2_StringVar.get().replace(',','.')))
            self.steps=TO_SI(self.Quantity,float(self.Input1Entry3_StringVar.get().replace(',','.')))
            pressures=np.arange(self.Pmin,self.Pmax,self.steps)

            for P in range(len(pressures)):
                PLIQ=pressures[P]
                try :
                    TLIQ,DLIQ,HLIQ,SLIQ=PropsSI(['T','D','H','S'],'P',pressures[P],'Q',0,self.ref)
                except ValueError :
                    PLIQ,DLIQ,HLIQ,SLIQ=np.NaN,np.NaN,np.NaN,np.NaN
                try :
                    TVAP,DVAP,HVAP,SVAP,CV,CP=PropsSI(['T','D','H','S','CVMASS','CPMASS'],'P',pressures[P],'Q',1,self.ref)
                except ValueError :
                    PVAP,DVAP,HVAP,SVAP,CV,CP=np.NaN,np.NaN,np.NaN,np.NaN,np.NaN,np.NaN  
                mydatarow=self.datarow%(
                                        SI_TO('T',TLIQ),
                                        SI_TO('p',PLIQ),
                                        SI_TO('D',DLIQ),
                                        SI_TO('D',DVAP),
                                        SI_TO('H',HLIQ),
                                        SI_TO('H',HVAP),
                                        SI_TO('S',SLIQ),
                                        SI_TO('S',SVAP),
                                        SI_TO('Cv',CV),
                                        SI_TO('Cp',CP)
                                        )
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
            if self.ordertype == label['T']:
                self.Input1Entry1_StringVar.set('{:+12.2f}'.format(SI_TO('T',self.Tmin)))
                self.Input1Entry2_StringVar.set('{:+12.2f}'.format(SI_TO('T',self.Tmax)))
                self.Input1Entry3_StringVar.set("%d"%1)
            else :
                self.Input1Entry1_StringVar.set('{:12.2f}'.format(SI_TO('p',self.Pmin)))
                self.Input1Entry2_StringVar.set('{:12.2f}'.format(SI_TO('p',self.Pmax)))
                self.Input1Entry3_StringVar.set('{:12.2f}'.format(SI_TO('p',10000)))          
                
            self.Text_1.delete(1.0, END)
            #
            self.statetext= 'Coolprop Version     : %s     \n'%str(CoolProp.__version__)
            self.statetext+='Coolprop gitrevision : %s     \n'%str(CoolProp.__gitrevision__)
            self.statetext+=self.kmstring%str(self.ref)
            self.Text_1.insert(END,self.statetext)
            
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
        App=cpgSatTable(frame,self)
        App.Update()
        
    def get_ref(self):
        return 'R134a'
    def get_language(self):
        return 'en'

def main():
    root = Tk()
    app = _Testdialog(root)
    root.mainloop()
    
if __name__ == '__main__':
    main()
