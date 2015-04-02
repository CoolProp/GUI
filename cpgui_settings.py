# -*- coding: utf-8 -*-
#
import sys
import gettext

from tkinter import *
from tkinter import ttk
from tkinter import filedialog, simpledialog
from cpgui_all import *

from PIL import ImageTk, Image

import configparser
import gettext

class bDialog(Dialog):
    # use dialogOptions dictionary to set any values in the dialog
    def __init__(self, parent, title = None, dialogOptions=None):
        self.initComplete = 0
        self.dialogOptions = dialogOptions
        Dialog.__init__(self, parent, Titel)
        
class cpg_settings(bDialog):
    
    def __init__(self, GridFrame,Caller,Debug=False):
        #
        self.initcomplete=False
        #
        self.dialogframe=GridFrame
        self.Caller=Caller
        self.Debug=Debug
        #
        self.frameborder=1
        # by module translations
        self.language=cpgui_language
        localedir=find_data_file('locale')
        self.lang = gettext.translation('cpgui', localedir=localedir, languages=[self.language])
        self.lang.install()
        #
        self.InputFrame= LabelFrame(self.dialogframe,relief=GROOVE,bd=self.frameborder,text=_('Unit settings'),font=("Arial", 10, "bold"))
        self.InputFrame.grid(row=1,column=1,padx=8,pady=5,sticky=W)
        #
        self.SettingsPanel = {}
        #
        LT1 = Label(self.InputFrame,text='{:<27}'.format(_('Quantity')),font=("Arial", 12) )
        LT1.grid(row=1,column=1,padx=8,sticky=W,pady=5)
        LT2 = Label(self.InputFrame,text='{:<27}'.format(_('Select Unit')),font=("Arial", 12) )
        LT2.grid(row=1,column=2,padx=8,sticky=W,pady=5)
        LT3 = Label(self.InputFrame,text='{:<27}'.format(_('Current Unit')),font=("Arial", 12) )
        LT3.grid(row=1,column=3,padx=8,sticky=W,pady=5) 
        #
        self.SettingsInputPanel(self.InputFrame)
        self.initcomplete=True
        
    def SettingsInputPanel(self,GridFrame,Debug=False,tfont=("Arial", 10, "bold"),font=("Arial", 10)):
        #
        srow=2
        for quant in sorted(units.keys()) :
            self.SettingsPanel[quant] = []
            Label(GridFrame,text='{:<27}'.format(label[quant]),font=font ).grid(row=srow,column=1,padx=8,sticky=W,pady=5)
            self.SettingsPanel[quant].append(StringVar())
            self.SettingsPanel[quant][0].set(gui_unit[quant])
            self.SettingsPanel[quant][0].trace("w", lambda name, index, mode, var=self.SettingsPanel[quant][0], key=quant: self.SettingsInputPanelUpdate(var, key))
            cbox=ttk.Combobox(GridFrame, textvariable=self.SettingsPanel[quant][0],font=font)
            cbox.grid(row=srow,column=2,padx=8,sticky=W,pady=5)
            cbox['values'] = units[quant]
            I1=units[quant].index(gui_unit[quant])
            cbox.current(I1)
            self.SettingsPanel[quant].append(Label(GridFrame,text='{:<20}'.format(gui_unit[quant]),font=font ))
            self.SettingsPanel[quant][-1].grid(row=srow,column=3,padx=8,sticky=W,pady=5)
            #print(type(self.SettingsPanel[quant][-1]))
            #self.SettingsPanel[quant].append(LU)
            srow+=1  
        #
        if cpgui_config['debug']['ShowPanel'] :
            toggletext=_('Message Panel will be shown' )
        else :
            toggletext=_('Message Panel will be hidden' )
            
        self.Button_2 = Button(GridFrame,text=toggletext)
        self.Button_2.grid(row=srow,rowspan=1,column=2,pady=5,sticky=W,padx=8)
        self.Button_2.bind("<ButtonRelease-1>", self.dbg_toggle)
        #
        srow+=1
        self.Button_1 = Button(GridFrame,text=_('Save for startup' ))
        self.Button_1.grid(row=srow,rowspan=1,column=1,pady=5,sticky=W,padx=8)
        self.Button_1.bind("<ButtonRelease-1>", self.calculate)
        #
                                  
        
    #
    def SettingsInputPanelUpdate(self, sv,key):
        #print('SettingsInputPanelUpdate sv,key ',sv,key, sv.get())
        if self.initcomplete :
            self.SettingsPanel[key][-1].config(text=str(sv.get()),fg='red')
            cpgui_config['units'][key] = str(sv.get())

    def tabChangedEvent(self,event):
        self.ref=self.Caller.get_ref()

    def calculate(self,event):
        #
        if self.initcomplete :
            save_settings()

    def dbg_toggle(self,event):
        #
        if self.initcomplete :
            if cpgui_config['debug']['ShowPanel'] :
                cpgui_config['debug']['ShowPanel'] = False
                toggletext=_('Message Panel will be hidden' )
            else :
                cpgui_config['debug']['ShowPanel'] = True
                toggletext=_('Message Panel will be shown' )
        self.Button_2.config(text=toggletext)
            
                                    
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
        App=cpg_settings(frame,self,Debug=True)

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
    