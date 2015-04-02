# -*- coding: utf-8 -*-
#
import sys
import os
import pickle
import json
import gettext
#
from tkinter import *
from tkinter import ttk
from tkinter.simpledialog import Dialog
from tkinter import messagebox
#
from platform import system 
from os import walk,path
from CoolProp.CoolProp import PropsSI

            
def find_data_file(filename):
    if getattr(sys, 'frozen', False):
        # The application is frozen
        datadir = os.path.dirname(sys.executable)
    else:
        # The application is not frozen
        # Change this bit to match where you store your data files:
        datadir = os.path.dirname(__file__)
    return os.path.join(datadir, filename)  

gui_unit={}
cpgui_config={}
#
myfile=find_data_file('cpgui.dat')
try:
    settingsfile = open(myfile)
except FileNotFoundError:
    print('cpgui.dat not found! ... creating file')
    cpgui_config['cpgui']={}
    cpgui_config['cpgui']['language'] = 'en'
    cpgui_config['units']={}
    cpgui_config['units']['T']  ='°C'
    cpgui_config['units']['dT'] ='K'
    cpgui_config['units']['p']  ='bar'
    cpgui_config['units']['D']  ='kg/m³'
    cpgui_config['units']['v']  ='m³/kg'
    cpgui_config['units']['H']  ='kJ/kg'
    cpgui_config['units']['S']  ='kJ/kg/K'
    cpgui_config['units']['Q']  ='kg/kg'
    cpgui_config['units']['P']  ='kW'
    cpgui_config['units']['U']  ='kJ'
    cpgui_config['units']['V']  ='m/s'
    cpgui_config['units']['dv'] ='µPa s'
    cpgui_config['units']['kv'] ='m²/s'
    cpgui_config['units']['Cp'] ='kJ/kg/K'
    cpgui_config['units']['Cv'] ='kJ/kg/K'
    cpgui_config['units']['M']  ='kg/kmol'
    cpgui_config['units']['c']  ='m/s'
    cpgui_config['units']['kxa']='W/K'
    cpgui_config['units']['eta']='1'
    #
    with open(myfile, 'wb') as datafile:
        pickle.dump(cpgui_config,datafile)
# We must have a configfile here!
with open(myfile, 'rb') as configfile:
            cpgui_config = pickle.load(configfile)
# Now set language
cpgui_language=cpgui_config['cpgui']['language']
localedir=find_data_file('locale')
cpgui_lang = gettext.translation('cpgui_all', localedir=localedir, languages=[cpgui_language],fallback=False)
cpgui_lang.install()

# Now read units into gui_unit
for quant in cpgui_config['units'].keys():
    gui_unit[quant]=cpgui_config['units'][quant]
    #print('Gui Unit for {} set to {} .'.format(quant,gui_unit[quant]))

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

# Units, SI unit must be first in list
units={}
units['T']  =['K','°C']
units['dT'] =['K']
units['p']  =['Pa','kPa','bar']
units['D']  =['kg/m³','kg/dm³']
units['v']  =['m³/kg']
units['H']  =['J/kg','kJ/kg']
units['S']  =['J/kg/K','kJ/kg/K']
units['Q']  =['kg/kg']
units['P']  =['kW','W']
units['U']  =['J','kJ']
units['V']  =['m/s']
units['dv'] =['Pa s','mPa s','µPa s']
units['kv'] =['m²/s']
units['Cp'] =['J/kg/K','kJ/kg/K']
units['Cv'] =['J/kg/K','kJ/kg/K']
units['M']  =['kg/mol','kg/kmol']
units['c']  =['m/s']
# now the wired stuff
units['kxa']  =['W/K']
units['eta']  =['1']
# we have to convert all those units to SI
tosi = {
  'K'       : lambda x: x,
  '°C'      : lambda x: x +273.15,
  'bar'     : lambda x: x * 100000.0,
  'Pa'      : lambda x: x,
  'kPa'     : lambda x: x*1000.0,
  'kg/m³'   : lambda x: x,
  'kg/dm³'  : lambda x: x*1000.0,
  'm³/kg'   : lambda x: x,
  'J/kg'    : lambda x: x,
  'kJ/kg'   : lambda x: x/1000.0,
  'J/kg/K'  : lambda x: x,
  'kJ/kg/K' : lambda x: x*1000.0,
  'kg/kg'   : lambda x: x,
  'kW'      : lambda x: x*1000.0,
  'W'       : lambda x: x,
  'J'       : lambda x: x,
  'kJ'      : lambda x: x*1000.0,
  'm/s'     : lambda x: x,
  'Pa s'    : lambda x: x,
  'mPa s'   : lambda x: x/1000.0,
  'µPa s'   : lambda x: x/1000000.0,
  'm²/s'    : lambda x: x,
  'kg/mol'  : lambda x: x,
  'kg/kmol' : lambda x: x/1000,
  'W/K'     : lambda x: x,
  '1'       : lambda x: x,  
}
# and from SI
sito = {
  'K'       : lambda x: x,
  '°C'      : lambda x: x -273.15,
  'bar'     : lambda x: x / 100000.0,
  'Pa'      : lambda x: x,
  'kPa'     : lambda x: x/1000.0,
  'kg/m³'   : lambda x: x,
  'kg/dm³'  : lambda x: x/1000.0,
  'm³/kg'   : lambda x: x,
  'J/kg'    : lambda x: x,
  'kJ/kg'   : lambda x: x/1000.0,
  'J/kg/K'  : lambda x: x,
  'kJ/kg/K' : lambda x: x/1000.0,
  'kg/kg'   : lambda x: x,
  'kW'      : lambda x: x/1000.0,
  'W'       : lambda x: x,
  'J'       : lambda x: x,
  'kJ'      : lambda x: x/1000.0,
  'm/s'     : lambda x: x,
  'Pa s'    : lambda x: x,
  'mPa s'   : lambda x: x*1000.0,
  'µPa s'   : lambda x: x*1000000.0,
  'm²/s'    : lambda x: x,
  'kg/mol'  : lambda x: x,
  'kg/kmol' : lambda x: x*1000,
  'W/K'     : lambda x: x,
  '1'       : lambda x: x,
}
# default Values for forms as string
default = {
  'K'       : '273.15',
  '°C'      : '0',
  'bar'     : '1.01325',
  'Pa'      : '101325',
  'kPa'     : '101.325',
  'kg/m³'   : '1000.0',
  'kg/dm³'  : '1.0',
  'm³/kg'   : '0.001',
  'J/kg'    : '200000.0',
  'kJ/kg'   : '200.0',
  'J/kg/K'  : '1000.0',
  'kJ/kg/K' : '1.0',
  'kg/kg'   : '1.0',
  'kW'      : '1.0',
  'W'       : '1000.0',
  'J'       : '1000.0',
  'kJ'      : '1.0',
  'm/s'     : '1.0',
  'Pa s'    : '1000000.0',
  'mPa s'   : '1000.0',
  'µPa s'   : '1.0',
  'm²/s'    : '1.0',
  'kg/mol'  : '0.1',
  'kg/kmol' : '100.0',
  '1'       : '0.6',
  'W/K'     : '23',
}
label={}
label['T']  = _('Temperature')
label['dT'] = _('Temperature difference')
label['p']  = _('Pressure')
label['D']  = _('Density')
label['v']  = _('Specific Volume')
label['H']  = _('Specific Enthalpy')
label['S']  = _('Specific Entropy')
label['Q']  = _('Quality')
label['P']  = _('Power')
label['U']  = _('Internal Energy')
label['V']  = _('Speed')
label['dv'] = _('Dynamic Viscosity')
label['kv'] = _('Kinematic Viscosity')
label['Cp'] = _('Isobaric heat Capacity')
label['Cv'] = _('Iscochoric heat Capacity')
label['M']  = _('Molar mass')
label['c']  = _('Speed of sound')
label['kxa']  = _('Heat transfer k x A')
label['eta']  = _('Efficiency')
#
cpcode={}
cpcode['T']  = 'T'
cpcode['p']  = 'P'
cpcode['D']  = 'D'
cpcode['H']  = 'H'
cpcode['S']  = 'S'
cpcode['Q']  = 'Q'
cpcode['U']  = 'U'
cpcode['dv'] = 'V'
cpcode['Cp'] = 'C'
cpcode['Cv'] = 'CVMASS'
cpcode['M']  = 'M'
cpcode['c']  = 'A'
# 
def german_units():
    if 'units' in cpgui_config.sections() :
        pass
    else :
        cpgui_config.add_section('units')
    #
    cpgui_config['units']['T']  = units['T'][1]
    cpgui_config['units']['dT']  = units['dT'][0]
    cpgui_config['units']['p']  = units['p'][2]
    cpgui_config['units']['D']  = units['D'][0]
    cpgui_config['units']['v']  = units['v'][0]
    cpgui_config['units']['H']  = units['H'][1]
    cpgui_config['units']['S']  = units['S'][1]
    cpgui_config['units']['Q']  = units['Q'][0]
    cpgui_config['units']['P']  = units['P'][0]
    cpgui_config['units']['U']  = units['U'][1]
    cpgui_config['units']['V']  = units['V'][0]
    cpgui_config['units']['dv'] = units['dv'][1]
    cpgui_config['units']['kv'] = units['kv'][0]
    cpgui_config['units']['Cp'] = units['Cp'][1]
    cpgui_config['units']['Cv'] = units['Cv'][1]
    cpgui_config['units']['M'] = units['M'][1]
    cpgui_config['units']['c']  = units['c'][0]
    cpgui_config['units']['kxa']  = units['kxa'][0]
    cpgui_config['units']['eta']  = units['eta'][0]
    with open(myfile, 'wb') as datafile:
        pickle.dump(cpgui_config,datafile)
    messagebox.showinfo( _('Units changed'), _('Units changed ! \nRestart GUI for Unit change to take effect!'))

def si_units():
    if 'units' in cpgui_config.sections() :
        pass
    else :
        cpgui_config.add_section('units')
    #
    cpgui_config['units']['T']  = units['T'][0]
    cpgui_config['units']['dT']  = units['dT'][0]
    cpgui_config['units']['p']  = units['p'][0]
    cpgui_config['units']['D']  = units['D'][0]
    cpgui_config['units']['V']  = units['V'][0]
    cpgui_config['units']['H']  = units['H'][0]
    cpgui_config['units']['S']  = units['S'][0]
    cpgui_config['units']['Q']  = units['Q'][0]
    cpgui_config['units']['P']  = units['P'][0]
    cpgui_config['units']['U']  = units['U'][0]
    cpgui_config['units']['v']  = units['v'][0]
    cpgui_config['units']['dv'] = units['dv'][0]
    cpgui_config['units']['kv'] = units['kv'][0]
    cpgui_config['units']['Cp'] = units['Cp'][0]
    cpgui_config['units']['Cv'] = units['Cv'][0]
    cpgui_config['units']['M'] = units['M'][0]
    cpgui_config['units']['c']  = units['c'][0]
    cpgui_config['units']['kxa']  = units['kxa'][0]
    cpgui_config['units']['eta']  = units['eta'][0]
    with open(myfile, 'wb') as datafile:
        pickle.dump(cpgui_config,datafile)
    messagebox.showinfo( _('Units changed'), _('Units changed ! \nRestart GUI for Unit change to take effect!'))

def save_settings():
    with open(myfile, 'wb') as datafile:
        pickle.dump(cpgui_config,datafile)
    messagebox.showinfo( _('Major settings changed'), _('Settings changed ! \nRestart GUI for change to take effect!'))
    
def SI_UNIT(Quantity):
    return units[Quantity][0]

def GUI_UNIT(Quantity):
    try :
        return gui_unit[Quantity]
    except KeyError :
        return ' '

def TO_SI(Quantity,Value):
    if Quantity in cpgui_config['units'] :
        localunit=gui_unit[Quantity]
        if localunit in tosi.keys():
            #print('converting ',Value,GUI_UNIT(Quantity),' to ', tosi[localunit](Value) ,SI_UNIT(Quantity))
            return tosi[localunit](Value)
        else:
            print('Error in tosi : No conversion for unit ',localunit,' defined')
    else :
        print('Error in get_SI : No unit for Quantity',Quantity,' defined')
        
def SI_TO(Quantity,Value):
    if Quantity in cpgui_config['units'] :
        localunit=gui_unit[Quantity]
        if localunit in sito.keys():
            #print('converting ',Value,SI_UNIT(Quantity),' to ', sito[localunit](Value) ,localunit)
            return sito[localunit](Value)
        else:
            print('Error in sito : No conversion for unit ',localunit,' defined')
    else :
        print('Error in get_SI : No unit for Quantity',Quantity,' defined')
        

        
if __name__=='__main__':
    #
    print(refprop_mixname(['REFPROP::R134a','REFPROP::R1234ze'],[0.42,0.58]))
    print(refprop_mixname(['R125','R143a','R134a'],[0.44,0.52,0.04]))
    #
    #german_units()
    #
    print(type(tosi))
    print(tosi['°C'](0))
    print(sito['°C'](293.15))
    print(TO_SI('T',0))
    #print(SI_TO('H', 300000))


            
    
    