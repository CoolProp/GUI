# -*- coding: utf-8 -*-
#
import sys
import gettext

if sys.version_info[0] < 3:
    from Tkinter import *
    import ttk
else:
    from tkinter import *
    from tkinter import ttk

import CoolProp
from CoolProp.CoolProp import PropsSI

from cpgui_all import *

import numpy as np
from math import exp

from PIL import ImageTk, Image
from scipy.optimize import bisect

class cpg_cycle2(myDialog):
    
    def __init__(self, GridFrame,Caller,Debug=False):
        #
        self.initcomplete=False
        #
        self.Caller=Caller
        #
        # by module translations
        self.language=self.Caller.get_language()
        localedir=find_data_file('locale')
        self.lang = gettext.translation('cpg_cycle2', localedir=localedir, languages=[self.language])
        self.lang.install()
        #
        self.euler=exp(1)
        #
        self.Debug=Debug
        #
        self.VarVal         ={'t0':273.15,'dt0h':10,'dp0':10000,'Q0':1000,'tc':273.15+45,'dtu':5,'dpc':10000,'sl_dth':10,'sl_dp':10000,'dl_dtu':18,'dl_dp':10000,'comp_eta':0.6,'hx_kxa':23,'hx_dp':0}
        self.InputPanels    ={'Evaporator':{'Title':_('Evaporator'),
                                            'row':1,                                                # row of Evaporator Frame in InputFrame
                                            'col':1,                                                # coloumn of Evaporator Frame in InputFrame
                                            'order':['t0','dt0h','dp0','Q0'],                       # Input fields order of appearance
                                            't0':[_('Temperature'),self.VarVal['t0'],GUI_UNIT('T'),'T'],           # Input fields, Label, Variable to change, Unit Label / this List will be extended by a tkinter StringVar for callback on change
                                            'dt0h':[_('Superheat'),self.VarVal['dt0h'],GUI_UNIT('dT'),'dT'],
                                            'dp0':[_('Pressure drop'),self.VarVal['dp0'],GUI_UNIT('p'),'p'],
                                            'Q0':[_('Capacity'),self.VarVal['Q0'],GUI_UNIT('P'),'P'],
                                            },
                              'Condenser':{'Title':_('Condenser'),
                                            'row':1,
                                            'col':2,
                                            'order':['tc','dtu','dpc','empty'],
                                            'tc':[_('Temperature'),self.VarVal['tc'],GUI_UNIT('T'),'T'],
                                            'dtu':[_('Subcooling'),self.VarVal['dtu'],GUI_UNIT('dT'),'dT'],
                                            'dpc':[_('Pressure drop'),self.VarVal['dpc'],GUI_UNIT('p'),'p'],
                                            'empty':[' '],
                                            },
                              'Pipes':{'Title':_('Suction line SL / Discharge line DL'),
                                            'row':1,
                                            'col':3,  
                                            'order':['sl_dth','sl_dp','dl_dtu','dl_dp'],
                                            'sl_dth':[_('SL superheat'),self.VarVal['sl_dth'],GUI_UNIT('dT'),'dT'],
                                            'sl_dp':[_('SL Pressure drop'),self.VarVal['sl_dp'],GUI_UNIT('p'),'p'],
                                            'dl_dtu':[_('DL Temperature loss'),self.VarVal['dl_dtu'],GUI_UNIT('dT'),'dT'],
                                            'dl_dp':[_('DL Pressure drop'),self.VarVal['dl_dp'],GUI_UNIT('p'),'p'],
                                      },
                              'Compressor':{'Title':_('Compressor'),
                                            'row':2,
                                            'col':1,
                                            'order':['comp_eta'],
                                            'comp_eta':[_('Isentropic efficiency'),self.VarVal['comp_eta'],GUI_UNIT('eta'),'eta'],
                                           },
                              'InternalHX':{'Title':_('Internal heat exchanger'),
                                            'row':2,
                                            'col':2,
                                            'order':['hx_kxa','hx_dp'],
                                            'hx_kxa':['K x A Value',self.VarVal['hx_kxa'],GUI_UNIT('kxa'),'kxa'],
                                            'hx_dp':[_('Gas pressure drop'),self.VarVal['hx_dp'],GUI_UNIT('p'),'p'],}
                              }
        #
        self.dialogframe=GridFrame
        #
        self.Caller=Caller
        self.ref=Caller.get_ref()
        #
        self.frameborder=5
        #
        self.statetext=' '
        #  
        self.InfoDict={'1'       :('1',             _('End of SL / compressor intake')),
                       '2s'      :('2s',            _('Isentropic compression')),
                       '2'       :('2',             _('Real compression')),
                       '3'       :('3',             _('Condenser inlet')),
                       '3dew'    :('3\'\'',         _('Dewpoint inside condenser')),
                       '3dewm4bub'  :('3\'\'m4\'',  _('Average between 3\'\' and 4\'')),
                       '4bub'    :('4\'',           _('Bubblepoint inside condenser')),
                       '4'       :('4',             _('Exit condenser')),
                       '5'       :('5',             _('Exit Heat exchanger')),
                       '6'       :('6',             _('Evaporator entry')),
                       '6m7dew'  :('6m7\'\'',       _('Average between 6 and 7\'\'')),
                       '7dew'    :('7\'\'',         _('Dewpoint inside evaporator')),
                       '7'       :('7',             _('Exit evaporator / Intake heat exchanger')),
                       '8'       :('8',             _('Exit Heat exchanger')),
                       'order'   :('1','2s','2','3','3dew','3dewm4bub','4bub','4','5','6','6m7dew','7dew','7','8'),
                       }   
        # Frames for input and output
        self.InputFrame= LabelFrame(self.dialogframe,relief=GROOVE,bd=self.frameborder,text=_('Cycle inputs'),font=("Arial", 10, "bold"))
        self.InputFrame.grid(row=1,column=1,padx=8,pady=5,sticky=W)
        self.OutputFrame= LabelFrame(self.dialogframe,relief=GROOVE,bd=self.frameborder,text=_('Cycle outputs'),font=("Arial", 10,"bold"))
        self.OutputFrame.grid(row=3,column=1,padx=8,pady=5,sticky=EW,rowspan=10,columnspan=3)
        #
        # Inputs
        #
        for key in self.InputPanels :
            self.GridInputPanel(self.InputFrame,key,Debug=False)
        #
        self.Button_1 = Button(self.InputFrame,text=_(' Calculate '),font=("Arial", 12, "bold") )
        self.Button_1.grid(row=2,rowspan=1,column=3,pady=5,sticky=W,padx=8)
        self.Button_1.bind("<ButtonRelease-1>", self.calculate)                    
        #
        # Output
        #
        self.out_nb = ttk.Notebook(self.OutputFrame)
        self.out_nb.pack(fill = 'both', expand = 1, padx = 5, pady = 5)
        #
        self.tab1_frame = ttk.Frame(self.OutputFrame)
        self.tab2_frame = ttk.Frame(self.OutputFrame)
        self.tab3_frame = ttk.Frame(self.OutputFrame)
        # tab 1 cycle display and selection
        self.out_nb.add(self.tab1_frame,text=_('Cycle information'))
        #
        self.InfoFrame= LabelFrame(self.tab1_frame,relief=GROOVE,bd=self.frameborder,text=_('Statepoints'),font=("Arial", 10, "bold"))
        self.InfoFrame.grid(row=1,column=1,padx=8,pady=5,sticky=W)
        
        inforow=1
        for point in self.InfoDict['order']:
            pl=Label(self.InfoFrame,text='{:<10}'.format(self.InfoDict[point][0]),font=("Arial", 10) )
            pl.grid(row=inforow,rowspan=1,column=1,pady=2,sticky=W,padx=2)
            tl=Label(self.InfoFrame,text='{:<35}'.format(self.InfoDict[point][1]),font=("Arial", 10) )
            tl.grid(row=inforow,rowspan=1,column=2,pady=2,sticky=W,padx=2)            
            inforow+=1
        
        self.cycle1png=find_data_file('cycle2.png')
        imgfile = Image.open(self.cycle1png)
        render = ImageTk.PhotoImage(imgfile)
        img = Label(self.tab1_frame, image=render)
        img.image = render
        img.grid(row=1,column=2,pady=5,sticky=NS,padx=8)
        #
        self.out_nb.add(self.tab2_frame,text=_('Output table'))
        #
        self.statetext=' '
        lbframe1 = Frame( self.tab2_frame )
        self.Text_1_frame = lbframe1
        scrollbar1 = Scrollbar(lbframe1, orient=VERTICAL)
        self.Text_1 = Text(lbframe1, width="110", height="25", yscrollcommand=scrollbar1.set)
        scrollbar1.config(command=self.Text_1.yview)
        scrollbar1.pack(side=RIGHT, fill=Y)
        self.Text_1.pack(side=LEFT, fill=BOTH, expand=1)
        self.Text_1_frame.grid(row=1,column=1,columnspan=1,padx=2,sticky=W+E,pady=4)
        self.Text_1.delete(1.0, END)
        #
        self.out_nb.bind_all("<<NotebookTabChanged>>", self.tabChangedEvent)
        self.initcomplete=True
    
    def GridInputPanel(self,GridFrame,PanelKey,Debug=False,tfont=("Arial", 10, "bold"),font=("Arial", 10)):
        #
        LineList=self.InputPanels[PanelKey]['order']
        GIPanel=LabelFrame(GridFrame,relief=GROOVE,bd=5,text=self.InputPanels[PanelKey]['Title'])
        GIPanel.grid(row=self.InputPanels[PanelKey]['row'],column=self.InputPanels[PanelKey]['col'],padx=8,pady=5,sticky=W)
        #
        i=1
        for k in self.InputPanels[PanelKey]['order'] :
            if self.InputPanels[PanelKey][k][0] != ' ' :
                self.InputPanels[PanelKey][k].append(StringVar())
                outval=SI_TO(self.InputPanels[PanelKey][k][-2], self.InputPanels[PanelKey][k][1])
                print('cycle 1 : GridInputPanel : SI_TO : ',outval)
                #self.InputPanels[PanelKey][k][-1].set('%f'%self.InputPanels[PanelKey][k][1])
                self.InputPanels[PanelKey][k][-1].set(outval)
                self.InputPanels[PanelKey][k][-1].trace("w", lambda name, index, mode, var=self.InputPanels[PanelKey][k][-1],quantity=self.InputPanels[PanelKey][k][-2], key=k: self.GridInputPanelUpdate(var, key, quantity))
                Label(GIPanel, text=self.InputPanels[PanelKey][k][0],font=font).grid(column=1, row=i,padx=8,pady=5,sticky=W)
                Entry(GIPanel, width=15, textvariable=self.InputPanels[PanelKey][k][-1],font=font).grid(column=2, row=i,padx=8,pady=5,sticky=W)
                Label(GIPanel, text=self.InputPanels[PanelKey][k][2],font=font).grid(column=3, row=i,padx=8,pady=5,sticky=W)
            else :
                Label(GIPanel, text=' ',font=font).grid(column=1, row=i,padx=8,pady=5,sticky=W)
            #
            i+=1
    #
    def GridInputPanelUpdate(self, sv,key,quantity):
        print(sv, key, sv.get(),quantity)
        #self.VarVal[key]=sv.get()
        try :
            self.VarVal[key]=TO_SI(quantity,float(sv.get().replace(',','.')))
        except ValueError :
            pass
        #print( key,self.VarVal[key])

    def tabChangedEvent(self,event):
        self.ref=self.Caller.get_ref()

    def calculate(self,event):
        #
        self.ref=self.Caller.get_ref()
        #
        self.t0=self.VarVal['t0']    # Evaporation temperature in °C
        self.dt0h=self.VarVal['dt0h']     # Superheat in K
        self.dp0=self.VarVal['dp0']      # pressure drop evaporator in bar
        self.Q0=self.VarVal['Q0']   # refrigeration capacity in kW
        #
        self.tc=self.VarVal['tc']    # condensation temperature in °C
        self.dtu=self.VarVal['dtu']    # subcooling in K
        self.dpc=self.VarVal['dpc']     # pressure drop condenser in bar
        #
        self.sl_dth=self.VarVal['sl_dth']   # superheat suction line in K
        self.sl_dp=self.VarVal['sl_dp']    # pressure drop suction line in bar
        self.dl_dtu=self.VarVal['dl_dtu']   # subcooling discharge line in K
        self.dl_dp=self.VarVal['dl_dp']    # pressure drop discharge line in bar
        #
        self.comp_eta=self.VarVal['comp_eta']  # Compressor isentropic efficiency
        self.hx_kxa=self.VarVal['hx_kxa']
        self.hx_dp=self.VarVal['hx_dp']
        #
        self.Qhx=0.0
        self.e_hoch_x=0.0
        #
        self.statetext=_('Simple DX cycle statepoint Table for %s\n\n')%self.ref
        self.statetext+=_(' Point  |   t    |   p     |      v     |    h    |    s    |    x    | Description \n')
        self.datarow=    " %6s | %6.2f | %6.2f  | %10.5f | %7.2f | %7.4f | %7s | %s \n"
        self.statetext+="        |   {}   |  {}    |    {}   |   {} | {} |  {}  |    \n".format(GUI_UNIT('T'),GUI_UNIT('p'),GUI_UNIT('v'),GUI_UNIT('H'),GUI_UNIT('S'),GUI_UNIT('Q'),)
        self.statetext+= "-------------------------------------------------------------------------------------------------\n"
        #
        self.row={}
        #
        dt_gas_out_old=self.iter_run()
        dt_gas_out=self.iter_run(InitialRun=False)
        diff=abs(dt_gas_out_old-dt_gas_out)
        # If gas t out changes by less than a millikelvin we are done
        while diff > 0.001 :
            dt_gas_out_old=dt_gas_out
            dt_gas_out=self.iter_run(InitialRun=False)
            diff=abs(dt_gas_out_old-dt_gas_out)
        #                      
        self.last_run()

    def iter_run(self,InitialRun=True):
        #
        name='7dew'
        self.p7dew=PropsSI('P','T',self.t0,'Q',1,self.ref)
        self.t7dew=self.t0
        self.v7dew=1/PropsSI('D','T',self.t0,'Q',1,self.ref)
        self.h7dew=PropsSI('H','T',self.t0,'Q',1,self.ref)
        self.s7dew=PropsSI('S','T',self.t0,'Q',1,self.ref)
        self.x7dew='       '
        self.row[name]=self.datarow%(self.InfoDict[name][0],SI_TO('T',self.t7dew),SI_TO('p',self.p7dew),self.v7dew,SI_TO('H',self.h7dew),SI_TO('S',self.s7dew),self.x7dew,self.InfoDict[name][1])
        print(self.InfoDict[name][0],SI_TO('T',self.t7dew),SI_TO('p',self.p7dew),self.v7dew,SI_TO('H',self.h7dew),SI_TO('S',self.s7dew),self.x7dew,self.InfoDict[name][1])
        #
        # superheat on evaporator exit
        name='7'
        self.p7=self.p7dew
        self.t7=self.t0+self.dt0h
        self.v7=1/PropsSI('D','T',self.t7,'P',self.p7,self.ref)
        self.h7=PropsSI('H','T',self.t7,'P',self.p7,self.ref)
        self.s7=PropsSI('S','T',self.t7,'P',self.p7,self.ref)
        self.x7='       '
        self.cp7=PropsSI('C','P',self.p7,'T',self.t7,self.ref)
        self.row[name]=self.datarow%(self.InfoDict[name][0],SI_TO('T',self.t7),SI_TO('p',self.p7),self.v7,SI_TO('H',self.h7),SI_TO('S',self.s7),self.x7,self.InfoDict[name][1])
        #
        # we ignore the hx for now
        name='8'
        if InitialRun :
            self.p8=self.p7
            self.t8=self.t7
            self.v8=self.v7
            self.h8=self.h7
            self.s8=self.s7
        else :
            self.p8=self.p7-self.hx_dp
            self.t8=self.t7+self.dt_gas_out
            self.v8=1/PropsSI('D','T',self.t8,'P',self.p8,self.ref)
            self.h8=PropsSI('H','T',self.t8,'P',self.p8,self.ref)
            self.s8=PropsSI('S','T',self.t8,'P',self.p8,self.ref)
        self.x8='       '
        self.row[name]=self.datarow%(self.InfoDict[name][0],SI_TO('T',self.t8),SI_TO('p',self.p8),self.v8,SI_TO('H',self.h8),SI_TO('S',self.s8),self.x8,self.InfoDict[name][1])
        self.cp8=PropsSI('C','P',self.p8,'T',self.t8,self.ref)
        #
        # + superheat and pressure drop suction line
        name='1'
        self.p1=self.p8-self.sl_dp
        self.t1=self.t8+self.sl_dth
        self.v1=1/PropsSI('D','T',self.t1,'P',self.p1,self.ref)
        self.h1=PropsSI('H','T',self.t1,'P',self.p1,self.ref)
        self.s1=PropsSI('S','T',self.t1,'P',self.p1,self.ref)
        self.x1='       '
        self.row[name]=self.datarow%(self.InfoDict[name][0],SI_TO('T',self.t1),SI_TO('p',self.p1),self.v1,SI_TO('H',self.h1),SI_TO('S',self.s1),self.x1,self.InfoDict[name][1])
        #
        # isentropic compression
        name='2s'
        self.p2s=PropsSI('P','T',self.tc,'Q',1,self.ref)+self.dl_dp
        self.s2s=self.s1
        try :
            self.t2s=PropsSI('T','P',self.p2s,'S',self.s2s,self.ref)
        except ValueError :
            self.t2s=bisect(lambda T: PropsSI('S','T',T,'P',self.p2s,self.ref)-self.s2s,self.t1,493,xtol=0.01)
            print('t2s : ',self.t2s)
        self.v2s=1/PropsSI('D','T',self.t2s,'P',self.p2s,self.ref)
        self.h2s=PropsSI('H','T',self.t2s,'P',self.p2s,self.ref)
        self.x2s='       '
        self.row[name]=self.datarow%(self.InfoDict[name][0],SI_TO('T',self.t2s),SI_TO('p',self.p2s),self.v2s,SI_TO('H',self.h2s),SI_TO('S',self.s2s),self.x2s,self.InfoDict[name][1])
        #
        # real compression
        name='2'
        self.p2=self.p2s
        self.h2=self.h1+(self.h2s-self.h1)/self.comp_eta
        try :
            self.t2=PropsSI('T','P',self.p2,'H',self.h2,self.ref)
        except ValueError :
            self.t2=bisect(lambda T: PropsSI('H','T',T,'P',self.p2,self.ref)-self.h2,self.t2s,493,xtol=0.01)
            print('t2 : ',self.t2)        
        self.v2=1/PropsSI('D','T',self.t2,'P',self.p2,self.ref)
        self.s2=PropsSI('S','T',self.t2,'P',self.p2,self.ref)
        self.x2='       '
        self.row[name]=self.datarow%(self.InfoDict[name][0],SI_TO('T',self.t2),SI_TO('p',self.p2),self.v2,SI_TO('H',self.h2),SI_TO('S',self.s2),self.x2,self.InfoDict[name][1])
        #
        # condenser entry
        name='3'
        self.p3=self.p2-self.dl_dp
        self.t3=self.t2-self.dl_dtu
        self.h3=PropsSI('H','P',self.p3,'T',self.t3,self.ref)
        self.v3=1/PropsSI('D','T',self.t3,'P',self.p3,self.ref)
        self.s3=PropsSI('S','T',self.t3,'P',self.p3,self.ref)
        self.x3='       '
        self.row[name]=self.datarow%(self.InfoDict[name][0],SI_TO('T',self.t3),SI_TO('p',self.p3),self.v3,SI_TO('H',self.h3),SI_TO('S',self.s3),self.x3,self.InfoDict[name][1])
        #
        # inside condenser dewpoint
        name='3dew'
        self.t3dew=self.tc
        self.p3dew=PropsSI('P','T',self.t3dew,'Q',1,self.ref)
        self.h3dew=PropsSI('H','P',self.p3dew,'Q',1,self.ref)
        self.v3dew=1/PropsSI('D','P',self.p3dew,'Q',1,self.ref)
        self.s3dew=PropsSI('S','P',self.p3dew,'Q',1,self.ref)
        self.x3dew='       '
        self.row[name]=self.datarow%(self.InfoDict[name][0],SI_TO('T',self.t3dew),SI_TO('p',self.p3dew),self.v3dew,SI_TO('H',self.h3dew),SI_TO('S',self.s3dew),self.x3dew,self.InfoDict[name][1])
        #
        # inside condenser bubblepoint
        name='4bub'
        self.p4bub=self.p3dew-self.dpc
        self.t4bub=PropsSI('T','P',self.p4bub,'Q',0,self.ref)
        self.h4bub=PropsSI('H','P',self.p4bub,'Q',0,self.ref)
        self.v4bub=1/PropsSI('D','P',self.p4bub,'Q',0,self.ref)
        self.s4bub=PropsSI('S','P',self.p4bub,'Q',0,self.ref)
        self.x4bub='       '
        self.row[name]=self.datarow%(self.InfoDict[name][0],SI_TO('T',self.t4bub),SI_TO('p',self.p4bub),self.v4bub,SI_TO('H',self.h4bub),SI_TO('S',self.s4bub),self.x4bub,self.InfoDict[name][1])
        #
        # condenser exit
        name='4'
        self.p4=self.p4bub
        self.t4=self.t4bub-self.dtu
        self.h4=PropsSI('H','P',self.p4,'T',self.t4,self.ref)
        self.v4=1/PropsSI('D','P',self.p4,'T',self.t4,self.ref)
        self.s4=PropsSI('S','P',self.p4,'T',self.t4,self.ref)
        self.x4='       '
        self.cp4=PropsSI('C','P',self.p4,'T',self.t4,self.ref)
        self.row[name]=self.datarow%(self.InfoDict[name][0],SI_TO('T',self.t4),SI_TO('p',self.p4),self.v4,SI_TO('H',self.h4),SI_TO('S',self.s4),self.x4,self.InfoDict[name][1])
        #
        # Exit hx
        name='5'
        self.p5=self.p4
        if InitialRun :

            self.t5=self.t4
            self.h5=self.h4
            self.v5=self.v4
            self.s5=self.s4
        else :
            self.t5=self.t4-self.dt_liq_out
            self.h5=PropsSI('H','P',self.p5,'T',self.t5,self.ref)
            self.v5=1/PropsSI('D','P',self.p5,'T',self.t5,self.ref)
            self.s5=PropsSI('S','P',self.p5,'T',self.t5,self.ref)
        self.x5='       '
        self.cp5=PropsSI('C','P',self.p5,'T',self.t5,self.ref)
        self.row[name]=self.datarow%(self.InfoDict[name][0],SI_TO('T',self.t5),SI_TO('p',self.p5),self.v5,SI_TO('H',self.h5),SI_TO('S',self.s5),self.x5,self.InfoDict[name][1]) 
        #
        # evaporator entry
        name='6'
        self.p6=self.p7dew+self.dp0
        self.t6=PropsSI('T','P',self.p6,'H',self.h5,self.ref)
        self.h6=self.h5
        self.v6=1/PropsSI('D','P',self.p6,'H',self.h6,self.ref)
        self.s6=PropsSI('S','P',self.p6,'H',self.h6,self.ref)
        self.x6=PropsSI('Q','P',self.p6,'H',self.h6,self.ref)
        self.row[name]=self.datarow%(self.InfoDict[name][0],SI_TO('T',self.t6),SI_TO('p',self.p6),self.v6,SI_TO('H',self.h6),SI_TO('S',self.s6),'%5.4f'%self.x6,self.InfoDict[name][1]) 
        #     
        # 
        name='3dewm4bub'
        self.p3dewm4bub=(self.p4bub+self.p3dew)/2
        self.t3dewm4bub=(self.t4bub+self.t3dew)/2
        self.h3dewm4bub=(self.h4bub+self.h3dew)/2
        self.v3dewm4bub=(self.v4bub+self.v3dew)/2
        self.s3dewm4bub=(self.s4bub+self.s3dew)/2
        self.x3dewm4bub='       '
        self.row[name]=self.datarow%(self.InfoDict[name][0],SI_TO('T',self.t3dewm4bub),SI_TO('p',self.p3dewm4bub),self.v3dewm4bub,SI_TO('H',self.h3dewm4bub),SI_TO('S',self.s3dewm4bub),self.x3dewm4bub,self.InfoDict[name][1])   
        # 
        #
        name='6m7dew'
        self.p6m7dew=(self.p6+self.p7dew)/2
        self.t6m7dew=(self.t6+self.t7dew)/2
        self.h6m7dew=(self.h6+self.h7dew)/2
        self.v6m7dew=(self.v6+self.v7dew)/2
        self.s6m7dew=(self.s6+self.s7dew)/2
        self.x6m7dew='       '
        self.row[name]=self.datarow%(self.InfoDict[name][0],SI_TO('T',self.t6m7dew),SI_TO('p',self.p6m7dew),self.v6m7dew,SI_TO('H',self.h6m7dew),SI_TO('S',self.s6m7dew),self.x6m7dew,self.InfoDict[name][1])
        #
        self.mdot=SI_TO('P',self.Q0)*1000/(self.h7-self.h6)
        # average heat capacity of gas and liquid
        self.cpliq=(self.cp4 + self.cp5)/2000
        #print('cp4 %5.4f cp5 %5.4f cpliq %5.4f '%(self.cp4,self.cp4,self.cpliq))
        self.cpgas=(self.cp7 + self.cp8)/2000
        #print('cp7 %5.4f cp8 %5.4f cpgas %5.4f '%(self.cp7,self.cp8,self.cpgas))
        # multiply with mass flow
        self.mdot_x_cpliq   =   (self.mdot   *   self.cpliq)
        self.mdot_x_cpgas   =   (self.mdot   *   self.cpgas)
        #print('mdot %6.5fkg/s mdot*cpliq %6.5f mdot*cpgas %6.5f '%(self.mdot,self.mdot_x_cpliq,self.mdot_x_cpgas))
        self.e_hoch_x=self.euler** ( (self.hx_kxa/(self.mdot_x_cpliq*1000)) - (self.hx_kxa/(self.mdot_x_cpgas*1000)) )
        #print('e hoch  klammer = ',self.e_hoch_x)
        self.Qhx=(self.t7-self.t4 + self.e_hoch_x * (self.t4-self.t7)) /((self.e_hoch_x/self.mdot_x_cpliq)-(1/self.mdot_x_cpgas))
        #print('Q= %5.2f kW '%self.Qhx)
        self.dt_gas_out=self.Qhx/self.mdot_x_cpgas
        self.dt_liq_out=self.Qhx/self.mdot_x_cpliq
        #print('dt gas out = %5.2f / dt liq out = %5.2f K'%(self.dt_gas_out,self.dt_liq_out))
        return self.dt_gas_out
        
    def last_run(self):     
        #
        for point in self.InfoDict['order']:
            self.statetext+=self.row[point]
            #
        # relate massflux back to kW
        self.mdot=self.mdot/1000
        self.statetext+=_('\nPower calculations                      | Key performance values\n')
        self.statetext+=_('Evaporator                 %8.2f kW  | Pressure ratio             %8.2f\n')%(SI_TO('P',self.Q0),(self.p2/self.p1))
        self.statetext+=_('Condenser                  %8.2f kW  | Pressure difference        %8.2f %s\n')%(((self.h3-self.h4)*self.mdot),SI_TO('p',self.p2-self.p1),GUI_UNIT('p'))
        self.statetext+=_('Suction line               %8.2f kW  | Mass flow                  %8.6f g/s \n')%(((self.h1-self.h8)*self.mdot),(self.mdot*1000*1000))
        self.statetext+=_('Discharge line             %8.2f kW  | Volume flow (suction line) %8.4f m³/h \n')%(((self.h2-self.h3)*self.mdot),(self.mdot*1000*3600*self.v1))
        self.statetext+=_('Compressor                 %8.2f kW  | Volumetric capacity        %8.2f kJ/m³ \n')%(((self.h2-self.h1)*self.mdot),(SI_TO('P',self.Q0)/(self.v1*self.mdot*1000)))
        self.statetext+=_('Internal hx                %8.2f kW  | COP                        %8.2f \n')%(((self.h8-self.h7)*self.mdot),SI_TO('P',self.Q0)/((self.h2-self.h1)*self.mdot))
        #
        self.Text_1.delete(1.0, END)
        #self.statetext='I am not yet ready'     
        self.Text_1.insert(END, self.statetext)

        
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
        App=cpg_cycle2(frame,self,Debug=True)

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
    