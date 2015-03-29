# -*- coding: utf-8 -*-
#
import sys

from tkinter import *
from tkinter import ttk

import CoolProp
from CoolProp.CoolProp import PropsSI

from cpgui_all import *
import gettext

import numpy as np

from PIL import ImageTk, Image
from scipy.optimize import bisect

class cpg_cycle1(myDialog):
    
    def __init__(self, GridFrame,Caller,Debug=False):
        #
        self.initcomplete=False
        #
        self.Caller=Caller
        #
        # by module translations
        self.language=cpgui_language
        localedir=find_data_file('locale')
        self.lang = gettext.translation('cpg_cycle1', localedir=localedir, languages=[self.language])
        self.lang.install()
        #
        self.Debug=Debug
        #
        # add all input variables to the following list 
        self.VarVal         ={'t0':273.15,'dt0h':10,'dp0':10000,'Q0':1000,'tc':273.15+45,'dtu':5,'dpc':10000,'sl_dth':10,'sl_dp':10000,'dl_dtu':18,'dl_dp':10000,'comp_eta':0.6}
        # create data structure like below to generate input form
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
                       '5'       :('5',             _('Evaporator entry')),
                       '5m6dew'  :('5m6\'\'',       _('Average between 5 and 6\'\'')),
                       '6dew'    :('6\'\'',         _('Dewpoint inside evaporator')),
                       '6'       :('6',             _('Exit evaporator')),
                       'order'   :('1','2s','2','3','3dew','3dewm4bub','4bub','4','5','5m6dew','6dew','6'),
                       }    
        # Frames for input and output
        self.InputFrame= LabelFrame(self.dialogframe,relief=GROOVE,bd=self.frameborder,text=_('Cycle inputs'),font=("Arial", 10, "bold"))
        self.InputFrame.grid(row=1,column=1,padx=8,pady=5,sticky=W)
        self.OutputFrame= LabelFrame(self.dialogframe,relief=GROOVE,bd=self.frameborder,text=_('Cycle outputs'),font=("Arial", 10,"bold"))
        self.OutputFrame.grid(row=3,column=1,padx=8,pady=5,sticky=EW,rowspan=10,columnspan=3)
        #
        # create Inputs form
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
        
        self.cycle1png=find_data_file('simplecycle.png')
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
                #print('cycle 1 : GridInputPanel : SI_TO : ',outval)
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
        #print(sv, key, sv.get(),quantity)
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
        self.Q0=self.VarVal['Q0']   # refrigeration capacity in W
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
        #
        self.statetext=_('Simple DX cycle statepoint Table for %s\n\n')%self.ref
        self.statetext+=(" Point  |   t    |   p     |      v     |    h    |    s    |    x    | Description \n")
        self.datarow=    " %6s | %6.2f | %6.2f  | %10.5f | %7.2f | %7.4f | %7s | %s \n"
        self.statetext+="        |   {}   |  {}    |    {}   |   {} | {} |  {}  |    \n".format(GUI_UNIT('T'),GUI_UNIT('p'),GUI_UNIT('v'),GUI_UNIT('H'),GUI_UNIT('S'),GUI_UNIT('Q'),)  
        self.statetext+= "-------------------------------------------------------------------------------------------------\n"
        self.row={}
        # point 6dew
        name='6dew'
        p6dew=PropsSI('P','T',self.t0,'Q',1,self.ref)
        t6dew=self.t0
        v6dew=1/PropsSI('D','T',self.t0,'Q',1,self.ref)
        h6dew=PropsSI('H','T',self.t0,'Q',1,self.ref)
        s6dew=PropsSI('S','T',self.t0,'Q',1,self.ref)
        x6dew='       '
        self.row[name]=self.datarow%(self.InfoDict[name][0],SI_TO('T',t6dew),SI_TO('p',p6dew),v6dew,SI_TO('H',h6dew),SI_TO('S',s6dew),x6dew,self.InfoDict[name][1])
        # superheat on evaporator exit
        name='6'
        p6=p6dew
        t6=self.t0+self.dt0h
        v6=1/PropsSI('D','T',t6,'P',p6,self.ref)
        h6=PropsSI('H','T',t6,'P',p6,self.ref)
        s6=PropsSI('S','T',t6,'P',p6,self.ref)
        x6='       '
        self.row[name]=self.datarow%(self.InfoDict[name][0],SI_TO('T',t6),SI_TO('p',p6),v6,SI_TO('H',h6),SI_TO('S',s6),x6,self.InfoDict[name][1])
        # + superheat and pressure drop suction line
        name='1'
        p1=p6-self.sl_dp
        t1=t6+self.sl_dth
        v1=1/PropsSI('D','T',t1,'P',p1,self.ref)
        h1=PropsSI('H','T',t1,'P',p1,self.ref)
        s1=PropsSI('S','T',t1,'P',p1,self.ref)
        x1='       '
        self.row[name]=self.datarow%(self.InfoDict[name][0],SI_TO('T',t1),SI_TO('p',p1),v1,SI_TO('H',h1),SI_TO('S',s1),x1,self.InfoDict[name][1])
        # isentropic compression
        name='2s'
        p2s=PropsSI('P','T',self.tc,'Q',1,self.ref)+self.dl_dp
        s2s=s1
        try :
            t2s=PropsSI('T','P',p2s,'S',s2s,self.ref)
        except ValueError :
            t2s=bisect(lambda T: PropsSI('S','T',T,'P',p2s,self.ref)-s2s,t1,493,xtol=0.01)
            print('t2s : ',t2s)
        v2s=1/PropsSI('D','T',t2s,'P',p2s,self.ref)
        h2s=PropsSI('H','T',t2s,'P',p2s,self.ref)
        x2s='       '
        self.row[name]=self.datarow%(self.InfoDict[name][0],SI_TO('T',t2s),SI_TO('p',p2s),v2s,SI_TO('H',h2s),SI_TO('S',s2s),x2s,self.InfoDict[name][1])
        # real compression
        name='2'
        p2=p2s
        h2=h1+(h2s-h1)/self.comp_eta
        try :
            t2=PropsSI('T','P',p2,'H',h2,self.ref)
        except ValueError :
            t2=bisect(lambda T: PropsSI('H','T',T,'P',p2,self.ref)-h2,t2s,493,xtol=0.01)
            print('t2 : ',t2)        
        v2=1/PropsSI('D','T',t2,'P',p2,self.ref)
        s2=PropsSI('S','T',t2,'P',p2,self.ref)
        x2='       '
        self.row[name]=self.datarow%(self.InfoDict[name][0],SI_TO('T',t2),SI_TO('p',p2),v2,SI_TO('H',h2),SI_TO('S',s2),x2,self.InfoDict[name][1])
        # condenser entry
        name='3'
        p3=p2-self.dl_dp
        t3=t2-self.dl_dtu
        h3=PropsSI('H','P',p3,'T',t3,self.ref)
        v3=1/PropsSI('D','T',t3,'P',p3,self.ref)
        s3=PropsSI('S','T',t3,'P',p3,self.ref)
        x3='       '
        self.row[name]=self.datarow%(self.InfoDict[name][0],SI_TO('T',t3),SI_TO('p',p3),v3,SI_TO('H',h3),SI_TO('S',s3),x3,self.InfoDict[name][1])
        # inside condenser dewpoint
        name='3dew'
        t3dew=self.tc
        p3dew=PropsSI('P','T',t3dew,'Q',1,self.ref)
        h3dew=PropsSI('H','P',p3dew,'Q',1,self.ref)
        v3dew=1/PropsSI('D','P',p3dew,'Q',1,self.ref)
        s3dew=PropsSI('S','P',p3dew,'Q',1,self.ref)
        x3dew='       '
        self.row[name]=self.datarow%(self.InfoDict[name][0],SI_TO('T',t3dew),SI_TO('p',p3dew),v3dew,SI_TO('H',h3dew),SI_TO('S',s3dew),x3dew,self.InfoDict[name][1])
        # inside condenser bubblepoint
        name='4bub'
        p4bub=p3dew-self.dpc
        t4bub=PropsSI('T','P',p4bub,'Q',0,self.ref)
        h4bub=PropsSI('H','P',p4bub,'Q',0,self.ref)
        v4bub=1/PropsSI('D','P',p4bub,'Q',0,self.ref)
        s4bub=PropsSI('S','P',p4bub,'Q',0,self.ref)
        x4bub='       '
        self.row[name]=self.datarow%(self.InfoDict[name][0],SI_TO('T',t4bub),SI_TO('p',p4bub),v4bub,SI_TO('H',h4bub),SI_TO('S',s4bub),x4bub,self.InfoDict[name][1])
        # condenser exit
        name='4'
        p4=p4bub
        t4=t4bub-self.dtu
        h4=PropsSI('H','P',p4,'T',t4,self.ref)
        v4=1/PropsSI('D','P',p4,'T',t4,self.ref)
        s4=PropsSI('S','P',p4,'T',t4,self.ref)
        x4='       '
        self.row[name]=self.datarow%(self.InfoDict[name][0],SI_TO('T',t4),SI_TO('p',p4),v4,SI_TO('H',h4),SI_TO('S',s4),x4,self.InfoDict[name][1])
        # evaporator entry
        name='5'
        p5=p6dew+self.dp0
        t5=PropsSI('T','P',p5,'H',h4,self.ref)
        h5=h4
        v5=1/PropsSI('D','P',p5,'H',h5,self.ref)
        s5=PropsSI('S','P',p5,'H',h5,self.ref)
        x5=PropsSI('Q','P',p5,'H',h5,self.ref)
        self.row[name]=self.datarow%(self.InfoDict[name][0],SI_TO('T',t5),SI_TO('p',p5),v5,SI_TO('H',h5),SI_TO('S',s5),'%5.4f'%x5,self.InfoDict[name][1])      
        # 
        name='3dewm4bub'
        p3dewm4bub=(p4bub+p3dew)/2
        t3dewm4bub=(t4bub+t3dew)/2
        h3dewm4bub=(h4bub+h3dew)/2
        v3dewm4bub=(v4bub+v3dew)/2
        s3dewm4bub=(s4bub+s3dew)/2
        x3dewm4bub='       '
        self.row[name]=self.datarow%(self.InfoDict[name][0],SI_TO('T',t3dewm4bub),SI_TO('p',p3dewm4bub),v3dewm4bub,SI_TO('H',h3dewm4bub),SI_TO('S',s3dewm4bub),x3dewm4bub,self.InfoDict[name][1])   
        # 
        name='5m6dew'
        p5m6dew=(p5+p6dew)/2
        t5m6dew=(t5+t6dew)/2
        h5m6dew=(h5+h6dew)/2
        v5m6dew=(v5+v6dew)/2
        s5m6dew=(s5+s6dew)/2
        x5m6dew='       '
        self.row[name]=self.datarow%(self.InfoDict[name][0],SI_TO('T',t5m6dew),SI_TO('p',p5m6dew),v5m6dew,SI_TO('H',h5m6dew),SI_TO('S',s5m6dew),x5m6dew,self.InfoDict[name][1])
        #
        for point in self.InfoDict['order']:
            self.statetext+=self.row[point]
        #massflux
        # from here units need to be fixed
        self.mdot=SI_TO('P',self.Q0)/(h6-h5)
        self.statetext+=_('\nPower calculations                      | Key performance values\n')
        self.statetext+=_('Evaporator                 %8.2f kW  | Pressure ratio             %8.2f (%8.2f)\n')%(SI_TO('P',self.Q0),(p3dew/p6),(p2/p1))
        self.statetext+=_('Condenser                  %8.2f kW  | Pressure difference        %8.2f (%8.2f) %s\n')%(((h3-h4)*self.mdot),SI_TO('p',p3dew-p6),SI_TO('p',p2-p1),GUI_UNIT('p'))
        self.statetext+=_('Suction line               %8.2f kW  | Mass flow                  %8.6f g/s \n')%(((h1-h6)*self.mdot),(self.mdot*1000*1000))
        self.statetext+=_('Discharge line             %8.2f kW  | Volume flow (suction line) %8.4f m³/h \n')%(((h2-h3)*self.mdot),(self.mdot*1000*3600*v1))
        self.statetext+=_('Compressor                 %8.2f kW  | Volumetric capacity        %8.2f kJ/m³ \n')%(((h2-h1)*self.mdot),(SI_TO('P',self.Q0)/(v1*self.mdot*1000)))
        self.statetext+=_('                                        | COP                        %8.2f \n')%(SI_TO('P',self.Q0)/((h2-h1)*self.mdot))
        #
        self.Text_1.delete(1.0, END)
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
        App=cpg_cycle1(frame,self,Debug=True)

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
    