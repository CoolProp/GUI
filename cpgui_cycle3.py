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

class cpg_cycle3(myDialog):
    
    def __init__(self, GridFrame,Caller,Debug=False):
        #
        self.initcomplete=False
        #
        self.Caller=Caller
        #
        # by module translations
        self.language=cpgui_language
        localedir=find_data_file('locale')
        self.lang = gettext.translation('cpg_cycle2', localedir=localedir, languages=[self.language])
        self.lang.install()
        #
        self.Debug=Debug
        #
        #########################################################################################################################
        # add all input variables to the following list 
        self.VarVal         ={
                              't0':268.15,
                              'dt0h':10,
                              'Q0':35000,                              
                              'T_gc_out':273.15+40,
                              'hp':10000000,
                              'mp': 5500000,
                              'sl_dth':10,
                              'comp_lambda':0.87,
                              'comp_eta':0.769
                              }
        # create data structure like below to generate input form
        self.InputPanels    ={'Evaporator':{'Title':_('Evaporator'),
                                            'row':1,                                                # row of Evaporator Frame in InputFrame
                                            'col':1,                                                # coloumn of Evaporator Frame in InputFrame
                                            'order':['t0','dt0h','Q0'],                       # Input fields order of appearance
                                            't0':[_('Temperature'),self.VarVal['t0'],GUI_UNIT('T'),'T'],           # Input fields, Label, Variable to change, Unit Label / this List will be extended by a tkinter StringVar for callback on change
                                            'dt0h':[_('Superheat'),self.VarVal['dt0h'],GUI_UNIT('dT'),'dT'],
                                            'Q0':[_('Capacity'),self.VarVal['Q0'],GUI_UNIT('P'),'P'],
                                            },
                              'Gascooler':{'Title':_('Gascooler'),
                                            'row':1,
                                            'col':2,
                                            'order':['T_gc_out','hp','empty'],
                                            'T_gc_out':[_('T. out'),self.VarVal['T_gc_out'],GUI_UNIT('T'),'T'],
                                            'hp':[_('High pressure'),self.VarVal['hp'],GUI_UNIT('p'),'p'],
                                            'empty':[' '],
                                            },
                              'Receiver':{'Title':_('Receiver'),
                                            'row':1,
                                            'col':3,
                                            'order':['mp','empty','empty'],
                                            'mp':[_('Middle pressure'),self.VarVal['mp'],GUI_UNIT('p'),'p'],
                                            'empty':[' '],
                                            },
                              'Pipes':{'Title':_('Suction line SL'),
                                            'row':2,
                                            'col':2,  
                                            'order':['sl_dth'],
                                            'sl_dth':[_('SL superheat'),self.VarVal['sl_dth'],GUI_UNIT('dT'),'dT'],


                                      },
                              'Compressor':{'Title':_('Compressor'),
                                            'row':2,
                                            'col':1,
                                            'order':['comp_eta','comp_lambda'],
                                            'comp_eta':[_('Isentropic efficiency'),self.VarVal['comp_eta'],GUI_UNIT('eta'),'eta'],
                                            'comp_lambda':[_('Volumetric efficiency'),self.VarVal['comp_lambda'],GUI_UNIT('eta'),'eta'],
                                           },
                              }
        #################################################################################################################################
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
        self.InfoDict={'1'       :('1',             _('Compressor intake =M ')),
                       '2s'      :('2s',            _('Isentropic compression')),
                       '2'       :('2',             _('Real compression')),
                       '3'       :('3',             _('Gascooler out')),
                       'A'       :('A',             _('High pressure controller')),
                       '4'       :('4',             _('Inlet middle pressure receiver')),
                       'C'       :('C',             _('Middle pressure receiver')),
                       '5'       :('5',             _('Liquid out middle pressure receiver')),
                       '6'       :('6',             _('Flashgas middle pressure receiver')),
                       'B'       :('B',             _('middle pressure controller')),
                       '7'       :('7',             _('Evaporator entry')),
                       '8'       :('8',             _('Exit evaporator')),
                       '9'       :('9',             _('Exit middle pressure controller')),
                       '10'      :('10',            _('End of suction line')),
                       'M'       :('M',             _('Mixing point 9 + 10 ')),
                       
                       'order'   :('1','2s','2','3','A','4','C','5','6','B','7','8','9','10','M'),
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
        
        self.cycle1png=find_data_file('co2-abb-5.png')
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
        self.ref='CO2'

    def calculate(self,event):
        #
        self.ref='CO2'
        #
        t0          =   self.VarVal['t0']           # Evaporation temperature in K
        dt0h        =   self.VarVal['dt0h']         # Superheat in K
        Q0          =   self.VarVal['Q0']           # refrigeration capacity in W
        T_gc_out    =   self.VarVal['T_gc_out']       # Gascooler outlet temperature in K
        hp          =   self.VarVal['hp']           # High pressure
        mp          =   self.VarVal['mp']           # Middle pressure
        sl_dth      =   self.VarVal['sl_dth']       # superheat suction line in K
        comp_eta    =   self.VarVal['comp_eta']     # Compressor isentropic efficiency
        comp_lambda =   self.VarVal['comp_lambda']  # Compressor volumetric efficiency
        #
        self.statetext=_('Cycle with middle pressure receiver, statepoint Table for %s\n\n')%self.ref
        self.statetext+=(" Point  |   t    |   p     |      v     |    h    |    s    |    x    | Description \n")
        self.datarow=    " %6s | %6.2f | %6.2f  | %10.5f | %7.2f | %7.4f | %7s | %s \n"
        self.statetext+="        |   {}   |  {}    |    {}   |   {} | {} |  {}  |    \n".format(GUI_UNIT('T'),GUI_UNIT('p'),GUI_UNIT('v'),GUI_UNIT('H'),GUI_UNIT('S'),GUI_UNIT('Q'),)  
        self.statetext+= "-------------------------------------------------------------------------------------------------\n"
        self.row={}
        #
        ### Gascooler Exit #########################################
        #
        name='3'
        p3=hp
        t3=T_gc_out
        h3=PropsSI('H','P',p3,'T',t3,self.ref)
        v3=1/PropsSI('D','T',t3,'P',p3,self.ref)
        s3=PropsSI('S','T',t3,'P',p3,self.ref)
        x3='       '
        self.row[name]=self.datarow%(self.InfoDict[name][0],SI_TO('T',t3),SI_TO('p',p3),v3,SI_TO('H',h3),SI_TO('S',s3),x3,self.InfoDict[name][1])
        #
        ### Middle pressure receiver inlet #########################################
        #
        name='4'
        p4=mp
        t4=PropsSI('T','P',p4,'Q',0,self.ref)
        h4=h3
        v4=1/PropsSI('D','P',p4,'H',h4,self.ref)
        s4=PropsSI('S','P',p4,'H',h4,self.ref)
        x4=PropsSI('Q','P',p4,'H',h4,self.ref)
        self.row[name]=self.datarow%(self.InfoDict[name][0],SI_TO('T',t4),SI_TO('p',p4),v4,SI_TO('H',h4),SI_TO('S',s4),'%5.4f'%x4,self.InfoDict[name][1])
        #
        ### Middle pressure receiver Liquid out #########################################
        #
        name='5'
        p5=mp
        t5=PropsSI('T','P',p5,'Q',0,self.ref)
        h5=PropsSI('H','P',p5,'Q',0,self.ref)
        v5=1/PropsSI('D','P',p5,'Q',0,self.ref)
        s5=PropsSI('S','P',p5,'Q',0,self.ref)
        x5='       '
        self.row[name]=self.datarow%(self.InfoDict[name][0],SI_TO('T',t5),SI_TO('p',p5),v5,SI_TO('H',h5),SI_TO('S',s5),x5,self.InfoDict[name][1])      
        #
        ### Middle pressure receiver Gas out #########################################
        #
        name='6'
        p6=mp
        t6=PropsSI('T','P',p6,'Q',1,self.ref)
        v6=1/PropsSI('D','P',p6,'Q',1,self.ref)
        h6=PropsSI('H','P',p6,'Q',1,self.ref)
        s6=PropsSI('S','P',p6,'Q',1,self.ref)
        x6='       '
        self.row[name]=self.datarow%(self.InfoDict[name][0],SI_TO('T',t6),SI_TO('p',p6),v6,SI_TO('H',h6),SI_TO('S',s6),x6,self.InfoDict[name][1])
        #
        ### Evaporator entry #########################################
        #
        name='7'
        p7=PropsSI('P','T',t0,'Q',0,self.ref)
        t7=t0
        h7=h5
        v7=1/PropsSI('D','P',p7,'H',h7,self.ref)
        s7=PropsSI('S','P',p7,'H',h7,self.ref)
        x7=PropsSI('Q','P',p7,'H',h7,self.ref)
        self.row[name]=self.datarow%(self.InfoDict[name][0],SI_TO('T',t7),SI_TO('p',p7),v7,SI_TO('H',h7),SI_TO('S',s7),'%5.4f'%x7,self.InfoDict[name][1])      
        #
        ### Evaporator out #########################################
        #
        name='8'
        p8=p7
        t8=t7+dt0h
        h8=PropsSI('H','P',p8,'T',t8,self.ref)
        v8=1/PropsSI('D','P',p8,'H',h8,self.ref)
        s8=PropsSI('S','P',p8,'H',h8,self.ref)
        x8='       '
        self.row[name]=self.datarow%(self.InfoDict[name][0],SI_TO('T',t8),SI_TO('p',p8),v8,SI_TO('H',h8),SI_TO('S',s8),x8,self.InfoDict[name][1])
        #
        ### Exit middle pressure controller #########################################
        #
        name='9'
        p9=p8
        h9=h6
        t9=t7
        v9=1/PropsSI('D','P',p9,'H',h9,self.ref)
        s9=PropsSI('S','P',p9,'H',h9,self.ref)
        x9=PropsSI('Q','P',p9,'H',h9,self.ref)
        self.row[name]=self.datarow%(self.InfoDict[name][0],SI_TO('T',t9),SI_TO('p',p9),v9,SI_TO('H',h9),SI_TO('S',s9),'%5.4f'%x9,self.InfoDict[name][1])
        #
        ### Suction line out #########################################
        #
        name='10'
        p10=p8
        t10=t8+sl_dth
        h10=PropsSI('H','P',p10,'T',t10,self.ref)
        v10=1/PropsSI('D','P',p10,'H',h10,self.ref)
        s10=PropsSI('S','P',p10,'H',h10,self.ref)
        x10='       '
        self.row[name]=self.datarow%(self.InfoDict[name][0],SI_TO('T',t10),SI_TO('p',p10),v10,SI_TO('H',h10),SI_TO('S',s10),x10,self.InfoDict[name][1])
        #
        ### compressor inlet #########################################
        #
        name='1'
        massflow_evaporator = Q0 /(h8-h7)
        massflow_compressor = massflow_evaporator/(1-x4)
        massflow_flashgas   = massflow_compressor - massflow_evaporator
        #
        p1=p10
        h1=(massflow_evaporator * h10 + massflow_flashgas * h9 ) / massflow_compressor
        t1=PropsSI('T','P',p1,'H',h1,self.ref)
        v1=1/PropsSI('D','H',h1,'P',p1,self.ref)
        h1=PropsSI('H','H',h1,'P',p1,self.ref)
        s1=PropsSI('S','H',h1,'P',p1,self.ref)
        x1=PropsSI('Q','P',p1,'H',h1,self.ref)
        if x1 == -1 :
            x8  ='       '
            xx1 ='sh. gas'
        if x1 >=0 and x1 <=1 :
            xx1 = '%5.4f'%x1
        self.row[name]=self.datarow%(self.InfoDict[name][0],SI_TO('T',t1),SI_TO('p',p1),v1,SI_TO('H',h1),SI_TO('S',s1),xx1,self.InfoDict[name][1])
        #
        ### isentropic compression #########################################
        # 
        name='2s'
        p2s=hp
        s2s=s1
        t2s=PropsSI('T','P',p2s,'S',s2s,self.ref)
        v2s=1/PropsSI('D','T',t2s,'P',p2s,self.ref)
        h2s=PropsSI('H','T',t2s,'P',p2s,self.ref)
        x2s='       '
        self.row[name]=self.datarow%(self.InfoDict[name][0],SI_TO('T',t2s),SI_TO('p',p2s),v2s,SI_TO('H',h2s),SI_TO('S',s2s),x2s,self.InfoDict[name][1])
        #
        ### real compression #########################################
        #
        name='2'
        p2=hp
        #
        isentropic_work = h2s-h1
        real_work       = isentropic_work / comp_eta
        #
        h2= h1 + real_work
        #
        t2=PropsSI('T','P',p2,'H',h2,self.ref)     
        v2=1/PropsSI('D','T',t2,'P',p2,self.ref)
        s2=PropsSI('S','T',t2,'P',p2,self.ref)
        x2='       '
        self.row[name]=self.datarow%(self.InfoDict[name][0],SI_TO('T',t2),SI_TO('p',p2),v2,SI_TO('H',h2),SI_TO('S',s2),x2,self.InfoDict[name][1])
        #
        for point in self.InfoDict['order']:
            try :
                self.statetext+=self.row[point]
            except KeyError :
                pass
        #
        # from here units need to be fixed
        #
        self.statetext+=_('\nPower calculations                      | Key performance values\n')
        self.statetext+=_('Evaporator             %8.2f    kW   | Pressure ratio             %8.2f \n')%(SI_TO('P',Q0),(p2/p1))
        self.statetext+=_('Gascooler              %8.2f    kW   | Pressure difference        %8.2f %s\n')%(((h2-h3)*massflow_compressor/1000),SI_TO('p',p2-p1),GUI_UNIT('p'))
        self.statetext+=_('Compressor             %8.2f    kW   \n\n')%((real_work*massflow_compressor/1000))

        self.statetext+=_('Mass flow Evaporator       %5.5f kg/s | Mass flow flashgas             %8.6f kg/s \n')%(massflow_evaporator,massflow_flashgas)
        self.statetext+=_('Mass flow Compressor       %5.5f kg/s | Volume flow Compressor       %8.4f   m³/h \n')%(massflow_compressor,(massflow_compressor*3600)/(comp_lambda/v1))
        #self.statetext+=_('Compressor                 %8.2f kW  | Volumetric capacity        %8.2f kJ/m³ \n')%(((h2-h1)*self.mdot),(SI_TO('P',self.Q0)/(v1*self.mdot*1000)))
        #self.statetext+=_('                                        | COP                        %8.2f \n')%(SI_TO('P',self.Q0)/((h2-h1)*self.mdot))
        #
        self.Text_1.delete(1.0, END)
        self.Text_1.insert(END, self.statetext)
        self.out_nb.select(1)

        self.Text_1.delete(1.0, END)
        self.Text_1.insert(END, self.statetext)
        self.out_nb.select(1)
        
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
        App=cpg_cycle3(frame,self,Debug=True)

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
    