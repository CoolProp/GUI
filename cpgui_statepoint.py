# -*- coding: utf-8 -*-
"""
Created on Fri Feb 27 2015 16:45

@author: mayers
"""
#
#import matplotlib
#matplotlib.use('TkAgg')
import gettext
import sys
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
        self.Caller=Caller#        self.Caller=Caller
        # by module translations
        self.language=cpgui_language
        #print('Statepoint lang : ',self.language)
        localedir=find_data_file('locale')
        self.lang = gettext.translation('cpgStatePoint', localedir=localedir, languages=[self.language])
        self.lang.install()
        #
        self.ref=Caller.get_ref()
        #
        self.frameborder=5
        # General data
        self.OutVal={}
        self.Value1=0
        self.Quantity1=' '
        self.Value2=0
        self.Quantity2=' '
        #
        self.choices=(  label['T'], 
                        label['p'],
                        label['D'],
                        label['H'],
                        label['S'], 
                        label['U'], 
                        label['Q']
                        )
        self.symbols=('T','p','D','H','S','U','Q','M','c','dv')
        #
        self.ObenFrame= LabelFrame(self.dialogframe,relief=GROOVE,bd=self.frameborder,text=_('Select entry txpes and input Values'),font=("Arial", 12))
        self.ObenFrame.grid(row=1,column=1)
        #
        self.UntenFrame= LabelFrame(self.dialogframe,relief=GROOVE,bd=self.frameborder,text=_('Fluid data'),font=("Arial", 12))
        self.UntenFrame.grid(row=2,column=1)
        # Line one input
        self.Line1L1 = Label(self.ObenFrame,text=_('Select input type #1'),font=("Arial", 12) )
        self.Line1L1.grid(row=1,column=1,padx=8,sticky=W,pady=5)
        self.Line1L2 = Label(self.ObenFrame,text=_('Enter input Value #1'),font=("Arial", 12) )
        self.Line1L2.grid(row=1,column=3,padx=8,sticky=W,pady=5)
        self.Line1L3 = Label(self.ObenFrame,text=_(' '),font=("Arial", 12) )
        self.Line1L3.grid(row=1,column=5,padx=8,sticky=W,pady=5)
        #
        self.Line1E1 = Entry(self.ObenFrame,width="15",font=("Arial", 12))
        self.Line1E1.grid(row=1,column=4,sticky=W,padx=8,pady=5)
        self.Line1E1_StringVar = StringVar()
        self.Line1E1.configure(textvariable=self.Line1E1_StringVar)
        #self.Line1E1_StringVar.set("101325")
        self.Line1E1_StringVar_traceName = self.Line1E1_StringVar.trace_variable("w", self.Line1E1_StringVar_Callback)
        #
        self.Line1S1_StringVar = StringVar()
        self.Line1S1_StringVar.set(label['p'])
        self.Line1S1_StringVar_traceName = self.Line1S1_StringVar.trace_variable("w",self.Line1S1_StringVar_Callback)
        
        self.Line1S1 = ttk.Combobox(self.ObenFrame, textvariable=self.Line1S1_StringVar,font=("Arial", 12))
        self.Line1S1['values'] = self.choices
        self.Line1S1.grid(column=2,row=1,padx=8,sticky=W,pady=5)
        self.Line1S1.current(0)
        # Line two input
        self.Line2L1 = Label(self.ObenFrame,text=_('Select input type #2'),font=("Arial", 12) )
        self.Line2L1.grid(row=2,column=1,padx=8,sticky=W,pady=5)
        self.Line2L2 = Label(self.ObenFrame,text=_('Enter input Value #2'),font=("Arial", 12) )
        self.Line2L2.grid(row=2,column=3,padx=8,sticky=W,pady=5)
        self.Line2L3 = Label(self.ObenFrame,text=_('UUU'),font=("Arial", 12) )
        self.Line2L3.grid(row=2,column=5,padx=8,sticky=W,pady=5)
        #
        self.Line2E1 = Entry(self.ObenFrame,width="15",font=("Arial", 12))
        self.Line2E1.grid(row=2,column=4,sticky=W,padx=8,pady=5)
        self.Line2E1_StringVar = StringVar()
        self.Line2E1.configure(textvariable=self.Line2E1_StringVar)
        #self.Line2E1_StringVar.set("298")
        self.Line2E1_StringVar_traceName = self.Line2E1_StringVar.trace_variable("w", self.Line2E1_StringVar_Callback)
        #
        self.Line2S1_StringVar = StringVar()
        self.Line2S1_StringVar.set(label['p'])
        self.Line2S1_StringVar_traceName = self.Line2S1_StringVar.trace_variable("w",self.Line2S1_StringVar_Callback)
        
        self.Line2S1 = ttk.Combobox(self.ObenFrame, textvariable=self.Line2S1_StringVar,font=("Arial", 12))
        self.Line2S1['values'] = self.choices
        self.Line2S1.grid(column=2,row=2,padx=8,sticky=W,pady=5)
        self.Line2S1.current(1)
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
        self.Text_1.insert(END, self.statetext)
        
    # Line 1 Callbacks
    def Line1S1_StringVar_Callback(self, varName, index, mode):
        #
        long_quant=self.Line1S1_StringVar.get()
        #
        mykey=' '
        for key in label.keys():
            if label[key] == long_quant:
                self.Line1L3.config(text=GUI_UNIT(key))
                self.Quantity1=key
        # Now set default Values
        self.Line1E1_StringVar.set(default[GUI_UNIT(self.Quantity1)])
        self.Value1=TO_SI(self.Quantity1,float(self.Line1E1_StringVar.get().replace(',','.')))
         
    def Line1E1_StringVar_Callback(self, varName, index, mode):
        #
        pass

    def Line2S1_StringVar_Callback(self, varName, index, mode):
        #
        long_quant=self.Line2S1_StringVar.get()
        #
        mykey=' '
        for key in label.keys():
            if label[key] == long_quant:
                self.Line2L3.config(text=GUI_UNIT(key))
                self.Quantity2=key
        # Now set default Values
        self.Line2E1_StringVar.set(default[GUI_UNIT(self.Quantity2)])
        self.Value2=TO_SI(self.Quantity2,float(self.Line2E1_StringVar.get().replace(',','.')))
                 
    def Line2E1_StringVar_Callback(self, varName, index, mode):
        #
        pass
        
    def calculate(self,event):
        #
        GoOn=True
        #
        self.Text_1.delete(1.0, END)
        self.ref=self.Caller.get_ref()
        #
        for k in self.symbols:
            try :
                self.OutVal[k]=SI_TO(k,PropsSI(cpcode[k],cpcode[self.Quantity1],self.Value1,cpcode[self.Quantity2],self.Value2,self.ref))
            except ValueError :
                self.Text_1.insert(END, _('Calculation error, check your inputs!'))
                GoOn=False
                break
        #
        if GoOn :
            Phase=CoolProp.CoolProp.PhaseSI(cpcode[self.Quantity1],self.Value1,cpcode[self.Quantity2],self.Value2,self.ref)
            #
            self.var_ref=_('Statepoint calculation for %12s \n\n')
            self.lines=[]
            myline=self.var_ref%self.ref
            self.lines.append(myline)
            #
            for sy in self.symbols :
                one='{:<27}'.format(label[sy])
                two='{:16.4f}'.format(self.OutVal[sy])
                if sy =='Q':
                    three='{:>10} {:<}\n'.format(GUI_UNIT(sy),Phase)
                else :
                    three='{:>10}\n'.format(GUI_UNIT(sy))
                myline=one+two+three
                self.lines.append(myline)
            #
            for l in self.lines :
                self.Text_1.insert(END, l)
        
        def Update(self):
            #
            pass

class _Testdialog:
    
    def __init__(self, master):
        frame = Frame(master)
        frame.pack()
        self.Caller = master
        self.x, self.y, self.w, self.h = -1,-1,-1,-1
        #
        self.ref='R134a'
        #
        App=cpgStatepoint(frame,self)

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
    
