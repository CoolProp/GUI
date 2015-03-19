# -*- coding: latin-1 -*-
#
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

import numpy as np

from PIL import ImageTk, Image
from scipy.optimize import bisect

class cpg_cycle1(myDialog):
    
    def __init__(self, GridFrame,Caller,Debug=False):
        #
        self.initcomplete=False
        #
        self.Debug=Debug
        #
        # add all input variables to the following list 
        self.VarVal         ={'t0':0,'dt0h':10,'dp0':0.1,'Q0':1,'tc':45,'dtu':5,'dpc':0.1,'sl_dth':10,'sl_dp':0.1,'dl_dtu':18,'dl_dp':0.1,'comp_eta':0.6}
        # create data structure like below to generate input form
        self.InputPanels    ={'Evaporator':{'Title':'Evaporator',
                                            'row':1,                                                # row of Evaporator Frame in InputFrame
                                            'col':1,                                                # coloumn of Evaporator Frame in InputFrame
                                            'order':['t0','dt0h','dp0','Q0'],                       # Input fields order of appearance
                                            't0':['Temperature',self.VarVal['t0'],u'°C'],           # Input fields, Label, Variable to change, Unit Label / this List will be extended by a tkinter StringVar for callback on change
                                            'dt0h':['Superheat',self.VarVal['dt0h'],u'K'],
                                            'dp0':['Pressure drop',self.VarVal['dp0'],u'bar'],
                                            'Q0':['Capacity',self.VarVal['Q0'],u'kW'],
                                            },
                              'Condenser':{'Title':'Condenser',
                                            'row':1,
                                            'col':2,
                                            'order':['tc','dtu','dpc','empty'],
                                            'tc':['Temperature',self.VarVal['tc'],u'°C'],
                                            'dtu':['Subcooling',self.VarVal['dtu'],u'K'],
                                            'dpc':['Pressure drop',self.VarVal['dpc'],u'bar'],
                                            'empty':[' '],
                                            },
                              'Pipes':{'Title':'Suction line SL / Discharge line DL',
                                            'row':1,
                                            'col':3,  
                                            'order':['sl_dth','sl_dp','dl_dtu','dl_dp'],
                                            'sl_dth':['SL superheat',self.VarVal['sl_dth'],u'K'],
                                            'sl_dp':['Pressure drop',self.VarVal['sl_dp'],u'bar'],
                                            'dl_dtu':['Temperature loss',self.VarVal['dl_dtu'],u'K'],
                                            'dl_dp':['Pressure drop',self.VarVal['dl_dp'],u'bar'],
                                      },
                              'Compressor':{'Title':'Compressor',
                                            'row':2,
                                            'col':1,
                                            'order':['comp_eta'],
                                            'comp_eta':['Isentropic efficiency',self.VarVal['comp_eta'],u' '],
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
        info=[
            ('1','End of SL / compressor intake'),
            ('2s','Isentropic compression'),
            ('2','Real compression'),
            ('3','Condenser inlet'),
            ('3\'\'','Dewpoint inside condenser'),
            ('3\'\'m4\'','Average between 3\'\' and 4\''),
            ('4\'','Bubblepoint inside condenser'),
            ('4','Exit condenser'),
            ('5','Evaporator entry'),
            ('5m6\'\'','Average between 5 and 6\'\''),
            ('6\'\'','Dewpoint inside evaporator'),
            ('6','Exit evaporator')]
        #    
        # Frames for input and output
        self.InputFrame= LabelFrame(self.dialogframe,relief=GROOVE,bd=self.frameborder,text='Cycle inputs',font=("Arial", 10, "bold"))
        self.InputFrame.grid(row=1,column=1,padx=8,pady=5,sticky=W)
        self.OutputFrame= LabelFrame(self.dialogframe,relief=GROOVE,bd=self.frameborder,text='Cycle outputs',font=("Arial", 10,"bold"))
        self.OutputFrame.grid(row=3,column=1,padx=8,pady=5,sticky=EW,rowspan=10,columnspan=3)
        #
        # create Inputs form
        #
        for key in self.InputPanels :
            self.GridInputPanel(self.InputFrame,key,Debug=False)
        #
        self.Button_1 = Button(self.InputFrame,text=' Calculate ',font=("Arial", 12, "bold") )
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
        self.out_nb.add(self.tab1_frame,text='Cycle information')
        #
        self.InfoFrame= LabelFrame(self.tab1_frame,relief=GROOVE,bd=self.frameborder,text='Statepoints',font=("Arial", 10, "bold"))
        self.InfoFrame.grid(row=1,column=1,padx=8,pady=5,sticky=W)
        inforow=1
        for a,b in info :
            pl=Label(self.InfoFrame,text='{:<10}'.format(a),font=("Arial", 10) )
            pl.grid(row=inforow,rowspan=1,column=1,pady=2,sticky=W,padx=2)
            tl=Label(self.InfoFrame,text='{:<35}'.format(b),font=("Arial", 10) )
            tl.grid(row=inforow,rowspan=1,column=2,pady=2,sticky=W,padx=2)            
            inforow+=1
        
        self.cycle1png=find_data_file('simplecycle.png')
        imgfile = Image.open(self.cycle1png)
        render = ImageTk.PhotoImage(imgfile)
        img = Label(self.tab1_frame, image=render)
        img.image = render
        img.grid(row=1,column=2,pady=5,sticky=NS,padx=8)
        #
        self.out_nb.add(self.tab2_frame,text='Output table')
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
                self.InputPanels[PanelKey][k][-1].set('%f'%self.InputPanels[PanelKey][k][1])
                self.InputPanels[PanelKey][k][-1].trace("w", lambda name, index, mode, var=self.InputPanels[PanelKey][k][-1], key=k: self.GridInputPanelUpdate(var, key))
                Label(GIPanel, text=self.InputPanels[PanelKey][k][0],font=font).grid(column=1, row=i,padx=8,pady=5,sticky=W)
                Entry(GIPanel, width=15, textvariable=self.InputPanels[PanelKey][k][-1],font=font).grid(column=2, row=i,padx=8,pady=5,sticky=W)
                Label(GIPanel, text=self.InputPanels[PanelKey][k][2],font=font).grid(column=3, row=i,padx=8,pady=5,sticky=W)
            else :
                Label(GIPanel, text=' ',font=font).grid(column=1, row=i,padx=8,pady=5,sticky=W)
            #
            i+=1
    #
    def GridInputPanelUpdate(self, sv,key):
        print(sv, key, sv.get())
        self.VarVal[key]=sv.get()
        try :
            self.VarVal[key]=float(sv.get().replace(',','.'))
        except ValueError :
            pass

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
        #
        self.statetext='Simple DX cycle statepoint Table for %s\n\n'%self.ref
        self.statetext+=u" Point  |   t    |   p     |      v     |    h    |    s    |    x    | Description \n"
        self.datarow=    " %6s | %6.2f | %6.2f  | %10.5f | %7.2f | %7.4f | %7s | %s \n"
        self.statetext+=u"        |   °C   |  bar    |    m³/kg   |   kg/kJ | kg/kJ/K |  kg/kg  |    \n"  
        self.statetext+= "-------------------------------------------------------------------------------------------------\n"
        descr='Dewpoint inside evaporator '
        point='6\'\''
        p6dew=PropsSI('P','T',C2K(self.t0),'Q',1,self.ref)
        t6dew=C2K(self.t0)
        v6dew=1/PropsSI('D','T',C2K(self.t0),'Q',1,self.ref)
        h6dew=PropsSI('H','T',C2K(self.t0),'Q',1,self.ref)
        s6dew=PropsSI('S','T',C2K(self.t0),'Q',1,self.ref)
        x6dew='       '
        self.row_6dew=self.datarow%(point,K2C(t6dew),pa2bar(p6dew),v6dew,j2kj(h6dew),j2kj(s6dew),x6dew,descr)
        # superheat on evaporator exit
        descr='Exit evaporator '
        point='6'
        p6=p6dew
        t6=C2K(self.t0)+self.dt0h
        v6=1/PropsSI('D','T',t6,'P',p6,self.ref)
        h6=PropsSI('H','T',t6,'P',p6,self.ref)
        s6=PropsSI('S','T',t6,'P',p6,self.ref)
        x6='       '
        self.row_6=self.datarow%(point,K2C(t6),pa2bar(p6),v6,j2kj(h6),j2kj(s6),x6,descr)
        # + superheat and pressure drop suction line
        descr='End of suction line'
        point='1'
        p1=p6-bar2pa(self.sl_dp)
        t1=t6+self.sl_dth
        v1=1/PropsSI('D','T',t1,'P',p1,self.ref)
        h1=PropsSI('H','T',t1,'P',p1,self.ref)
        s1=PropsSI('S','T',t1,'P',p1,self.ref)
        x1='       '
        self.row_1=self.datarow%(point,K2C(t1),pa2bar(p1),v1,j2kj(h1),j2kj(s1),x1,descr)
        # isentropic compression
        descr='Isentropic compression'
        point='2s'
        p2s=PropsSI('P','T',C2K(self.tc),'Q',1,self.ref)+bar2pa(self.dl_dp)
        s2s=s1
        try :
            t2s=PropsSI('T','P',p2s,'S',s2s,self.ref)
        except ValueError :
            t2s=bisect(lambda T: PropsSI('S','T',T,'P',p2s,self.ref)-s2s,t1,493,xtol=0.01)
            print('t2s : ',t2s)
        v2s=1/PropsSI('D','T',t2s,'P',p2s,self.ref)
        h2s=PropsSI('H','T',t2s,'P',p2s,self.ref)
        x2s='       '
        self.row_2s=self.datarow%(point,K2C(t2s),pa2bar(p2s),v2s,j2kj(h2s),j2kj(s2s),x2s,descr)
        # real compression
        descr='Real compression '
        point='2'
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
        self.row_2=self.datarow%(point,K2C(t2),pa2bar(p2),v2,j2kj(h2),j2kj(s2),x2,descr)
        # condenser entry
        descr='Condenser inlet '
        point='3'
        p3=p2-bar2pa(self.dl_dp)
        t3=t2-self.dl_dtu
        h3=PropsSI('H','P',p3,'T',t3,self.ref)
        v3=1/PropsSI('D','T',t3,'P',p3,self.ref)
        s3=PropsSI('S','T',t3,'P',p3,self.ref)
        x3='       '
        self.row_3=self.datarow%(point,K2C(t3),pa2bar(p3),v3,j2kj(h3),j2kj(s3),x3,descr)
        # inside condenser dewpoint
        descr='Dewpoint inside condenser '
        point='3\'\''
        t3dew=C2K(self.tc)
        p3dew=PropsSI('P','T',t3dew,'Q',1,self.ref)
        h3dew=PropsSI('H','P',p3dew,'Q',1,self.ref)
        v3dew=1/PropsSI('D','P',p3dew,'Q',1,self.ref)
        s3dew=PropsSI('S','P',p3dew,'Q',1,self.ref)
        x3dew='       '
        self.row_3dew=self.datarow%(point,K2C(t3dew),pa2bar(p3dew),v3dew,j2kj(h3dew),j2kj(s3dew),x3dew,descr)
        # inside condenser bubblepoint
        descr='Bubblepoint inside condenser'
        point='4\''
        p4bub=p3dew-bar2pa(self.dpc)
        t4bub=PropsSI('T','P',p4bub,'Q',0,self.ref)
        h4bub=PropsSI('H','P',p4bub,'Q',0,self.ref)
        v4bub=1/PropsSI('D','P',p4bub,'Q',0,self.ref)
        s4bub=PropsSI('S','P',p4bub,'Q',0,self.ref)
        x4bub='       '
        self.row_4bub=self.datarow%(point,K2C(t4bub),pa2bar(p4bub),v4bub,j2kj(h4bub),j2kj(s4bub),x4bub,descr)
        # condenser exit
        descr='Exit condenser'
        point='4'
        p4=p4bub
        t4=t4bub-self.dtu
        h4=PropsSI('H','P',p4,'T',t4,self.ref)
        v4=1/PropsSI('D','P',p4,'T',t4,self.ref)
        s4=PropsSI('S','P',p4,'T',t4,self.ref)
        x4='       '
        self.row_4=self.datarow%(point,K2C(t4),pa2bar(p4),v4,j2kj(h4),j2kj(s4),x4,descr)
        # evaporator entry
        descr='Evaporator entry'
        point='5'
        p5=p6dew+bar2pa(self.dp0)
        t5=PropsSI('T','P',p5,'H',h4,self.ref)
        h5=h4
        v5=1/PropsSI('D','P',p5,'H',h5,self.ref)
        s5=PropsSI('S','P',p5,'H',h5,self.ref)
        x5=PropsSI('Q','P',p5,'H',h5,self.ref)
        self.row_5=self.datarow%(point,K2C(t5),pa2bar(p5),v5,j2kj(h5),j2kj(s5),'%5.4f'%x5,descr)      
        # 
        descr='Average between 3\'\' and 4\' '
        point='3\'\'m4\''
        p3m4=(p4bub+p3dew)/2
        t3m4=(t4bub+t3dew)/2
        h3m4=(h4bub+h3dew)/2
        v3m4=(v4bub+v3dew)/2
        s3m4=(s4bub+s3dew)/2
        x3m4='       '
        self.row_3m4=self.datarow%(point,K2C(t3m4),pa2bar(p3m4),v3m4,j2kj(h3m4),j2kj(s3m4),x3m4,descr)   
        # 
        descr='Average between 5 and 6\'\' '
        point='5m6\'\''
        p5m6=(p5+p6dew)/2
        t5m6=(t5+t6dew)/2
        h5m6=(h5+h6dew)/2
        v5m6=(v5+v6dew)/2
        s5m6=(s5+s6dew)/2
        x5m6='       '
        self.row_5m6=self.datarow%(point,K2C(t5m6),pa2bar(p5m6),v5m6,j2kj(h5m6),j2kj(s5m6),x5m6,descr)
        #
        self.statetext+=self.row_1
        self.statetext+=self.row_2s
        self.statetext+=self.row_2
        self.statetext+=self.row_3
        self.statetext+=self.row_3dew
        self.statetext+=self.row_3m4
        self.statetext+=self.row_4bub
        self.statetext+=self.row_4
        self.statetext+=self.row_5
        self.statetext+=self.row_5m6
        self.statetext+=self.row_6dew
        self.statetext+=self.row_6
        #massflux
        self.mdot=self.Q0/(h6-h5)
        self.statetext+='\nPower calculations                      | Key performance values\n'
        self.statetext+='Evaporator                 %8.2f kW  | Pressure ratio             %8.2f (%8.2f)\n'%(self.Q0,(p3dew/p6),(p2/p1))
        self.statetext+='Condenser                  %8.2f kW  | Pressure difference        %8.2f (%8.2f) bar\n'%(((h3-h4)*self.mdot),pa2bar(p3dew-p6),pa2bar(p2-p1))
        self.statetext+='Suction line               %8.2f kW  | Mass flow                  %8.6f g/s \n'%(((h1-h6)*self.mdot),(self.mdot*1000*1000))
        self.statetext+='Discharge line             %8.2f kW  | Volume flow (suction line) %8.4f m³/h \n'%(((h2-h3)*self.mdot),(self.mdot*1000*3600*v1))
        self.statetext+='Compressor                 %8.2f kW  | Volumetric capacity        %8.2f kJ/m³ \n'%(((h2-h1)*self.mdot),(self.Q0/(v1*self.mdot*1000)))
        self.statetext+='                                        | COP                        %8.2f \n'%(self.Q0/((h2-h1)*self.mdot))
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
        self.ref='R404A'
        #
        App=cpg_cycle1(frame,self,Debug=True)

    def get_ref(self):
        return 'R404A'
    
def main():
    root = Tk()
    

    
    app = _Testdialog(root)
    root.mainloop()
    
if __name__ == '__main__':
    main()
    