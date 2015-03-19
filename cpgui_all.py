# -*- coding: latin-1 -*-
"""
Created on Fri Feb 27 2015 16:45

@author: mayers
"""
#
import sys
import os

if sys.version_info[0] < 3:
    from Tkinter import *
    from tkSimpleDialog import Dialog
    import ttk

else:
    from tkinter import *
    from tkinter import ttk
    from tkinter.simpledialog import Dialog
#
from platform import system 
from os import walk,path
from CoolProp.CoolProp import PropsSI

class myDialog(Dialog):
    # use dialogOptions dictionary to set any values in the dialog
    def __init__(self, parent, title = None,dialogOptions = None):
        self.initComplete = 0
        self.dialogOptions = dialogOptions
        Dialog.__init__(self, parent, 'Coolprop GUI')
        self.master = parent
        self.x, self.y, self.w, self.h = -1,-1,-1,-1
        #self.master.bind('<Enter>', self.bindConfigure)
        
def refprop_mixname(reflist,masslist):
    '''
    Creates a refprop mixture string from names and mass fractions
    e.G. 
    reflist   = list of refrigerants in a mixture
    masslist  = massfraction in kg/kg
    '''
    # Calculate total
    molelist=[]
    molefrac=[]
    namelist=[]
    denominator=0
    # Get moles and calculate denominator
    for index in range(len(reflist)):
        m=PropsSI("M",reflist[index])
        molelist.append(m)
        namelist.append(reflist[index].split(':')[-1])
        denominator+=(masslist[index]/molelist[index])
    # Denominator is calculated, now molefractions
    for index in range(len(reflist)):
        #
        mol=(masslist[index]/molelist[index])/denominator
        molefrac.append(mol)       
    # now create string from data
    refpropstring='REFPROP::'
    add_ampersand=False
    #
    for index in range(len(namelist)):
        if add_ampersand :
            refpropstring+='&'+namelist[index]+'[%0.16f]'%molefrac[index]
        else :
            refpropstring+=namelist[index]+'[%0.16f]'%molefrac[index]
            add_ampersand=True
    #
    return refpropstring,molefrac

def get_refprop_fluids():
    #
    mysys=system()
    if mysys=='Linux' or mysys=='Darwin':
        if path.isdir('/opt/refprop') :
            rpfluids1 = next(walk('/opt/refprop/fluids'))[2]
            rpfluids1.sort()
            rpfluids=[]
            for fluid in rpfluids1 :
                rpfluids.append((fluid.split('.')[0]))
            rpmixtures1 = next(walk('/opt/refprop/mixtures'))[2]
            rpmixtures1.sort()
            rpmixtures=[]
            for mixture in rpmixtures1 :
                rpfluids.append((mixture))
        else :
            rpfluids=['Refprop not found']
        return rpfluids
        #
    elif mysys=='Windows':
        if path.isdir('C:\\Program Files (x86)\\Refprop') :
            rpfluids1 = next(walk('C:\\Program Files (x86)\\Refprop\\fluids'))[2]
            rpfluids1.sort()
            rpfluids=[]
            for fluid in rpfluids1 :
                rpfluids.append((fluid.split('.')[0]))
            rpmixtures1 = next(walk('C:\\Program Files (x86)\\Refprop\\mixtures'))[2]
            rpmixtures1.sort()
            rpmixtures=[]
            for mixture in rpmixtures1 :
                rpfluids.append((mixture))
            return rpfluids
        else :
            rpfluids=['No Refprop']
        return rpfluids
    #return ['R134a']
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
            
def find_data_file(filename):
    if getattr(sys, 'frozen', False):
        # The application is frozen
        datadir = os.path.dirname(sys.executable)
    else:
        # The application is not frozen
        # Change this bit to match where you store your data files:
        datadir = os.path.dirname(__file__)

    return os.path.join(datadir, filename)  

class GridInputPanel():
    #
    def entryupdate(self, sv, i):
        try :
            self.InputLines[i][1]=float(sv.get().replace(',','.'))
        except ValueError :
            pass
        print(sv, i, self.InputLines[i][1], sv.get())
        print(self.Q0)
    #
    def __init__(self, ParentFrame,grid_row,grid_col,Title,InputLines,tfont=("Arial", 10, "bold"),font=("Arial", 10)):
        #
        self.InputLines=InputLines
        GIPanel=LabelFrame(ParentFrame,relief=GROOVE,bd=5,text=Title,font=tfont)
        GIPanel.grid(row=1,column=1,padx=8,pady=5,sticky=W)
        self.gilist = []
        for gi_name,gi_var,gi_unit in InputLines :
            i=len(self.gilist)
            self.gilist.append(StringVar())
            self.gilist[i].set('%f'%gi_var)
            self.gilist[i].trace("w", lambda name, index, mode, var=self.gilist[i], i=i:
                              self.entryupdate(var, i))
            Label(GIPanel, text=gi_name,font=font).grid(column=1, row=i,padx=8,pady=5,sticky=W)
            Entry(GIPanel, width=15, textvariable=self.gilist[i],font=font).grid(column=2, row=i,padx=8,pady=5,sticky=W)
            Label(GIPanel, text=gi_unit,font=font).grid(column=3, row=i,padx=8,pady=5,sticky=W)

class GridInputLine():
    #
    def __init__(self, GIPanel,grid_row,grid_col,gi_label,gi_var,gi_unit,font=("Arial", 10)):
        #
        self.Initcomplete=False
        self.gi_sv=StringVar()
        self.gi_sv.set('%f'%gi_var)
        self.gi_sv.trace("w", lambda name, index, mode, var=self.gi_sv : self.lineupdate(var))
        #
        Label(GIPanel, text=gi_label,font=font).grid(column=grid_col, row=grid_row,padx=8,pady=5,sticky=W)
        Entry(GIPanel, width=15, textvariable=self.gi_sv,font=font).grid(column=grid_col+1, row=grid_row,padx=8,pady=5,sticky=W)
        Label(GIPanel, text=gi_unit,font=font).grid(column=grid_col+2, row=grid_row,padx=8,pady=5,sticky=W)
        self.Initcomplete=True

    def lineupdate(self, sv):
        if self.Initcomplete :
            try :
                gi_var=float(sv.get().replace(',','.'))
            except ValueError :
                pass
            print(sv, self.gi_sv, sv.get())
            print(gi_var)
        
if __name__=='__main__':
    #
    print(refprop_mixname(['REFPROP::R134a','REFPROP::R1234ze'],[0.42,0.58]))
    print(refprop_mixname(['R125','R143a','R134a'],[0.44,0.52,0.04]))
        
