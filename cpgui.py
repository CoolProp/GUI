# -*- coding: utf-8 -*-
#
import sys
import gettext
import numpy as np
np.seterr(divide='ignore', invalid='ignore')
#
if sys.version_info[0] < 3:
    pass
else : 
    import tkinter
    from tkinter import filedialog, simpledialog
    from tkinter import messagebox
    from tkinter import *
    from tkinter import ttk
    import CoolProp
    from cpgui_all import *
    from cpgui_settings import cpg_settings
    from cpgui_basics import cpgbasics
    from cpgui_statepoint import cpgStatepoint
    from cpgui_diagram import cpgDiagram
    from cpgui_sattable import cpgSatTable
    from cpgui_cycle1 import cpg_cycle1
    from cpgui_cycle2 import cpg_cycle2
    
    class CPGUI(Frame):
        def __init__(self,parent):
                Frame.__init__(self)
                self.initcomplete=False
                self.ref=' '
                self.tkref=StringVar()
                self.parent=parent
                
                self.set_ref('R134a')
    
                self.Tmin=273.15
                self.Tcrit=273.15
                            
                self.frameborder=5
                
                self.master.geometry('1000x800')
                self.master.title('Coolprop GUI')
                #
                self.language=cpgui_language
                #
                localedir=find_data_file('locale')
                self.lang = gettext.translation('cpgui', localedir=localedir, languages=[self.language],fallback=False)
                self.lang.install()
                #
                self.grid()
                self.master.columnconfigure(0, weight=1)
                #
                # Menu
                #
                self.menu = Menu(tearoff=False)
                self.master.config(menu = self.menu)
                # File menu
                filemenu = self.file_menu = None
                filemenu = Menu(self.menu, tearoff=False)
                self.menu.add_cascade(label=_('File'), menu = filemenu)
                filemenu.add_separator()
                filemenu.add_command(label=_('Quit'), command = self.quit)
                #Options menu
                setmenu = Menu(self.menu, tearoff=False)
                self.menu.add_cascade(label=_("Settings"), menu=setmenu)
                setmenu.add_separator()
                setmenu.add_command(label=_('English'), command = lambda: self.set_language('en') )
                setmenu.add_command(label=_('German'), command = lambda: self.set_language('de') )
                
                #Help menu
                helpmenu = Menu(self.menu, tearoff=False)
                self.menu.add_cascade(label=_("Help"), menu=helpmenu)
                helpmenu.add_command(label=_('About...'), command = self.about )
                
                self.NotebookFrame=Frame(self.master)
                self.TitleFrame=Frame(self.master)
                self.NotebookFrame.grid(row=1, column=0, columnspan=20,rowspan=20,sticky=W+E)
                self.TitleFrame.grid(row=0, column=0, columnspan=20,sticky=W+E)
                
                self.TitleLabel = Label(self.TitleFrame,textvariable=self.tkref,font=("Arial", 8) )
                self.TitleLabel.grid(row=0,column=0,padx=8,columnspan=5,sticky=W,pady=5)
            
                self.notebook = ttk.Notebook(self.NotebookFrame)
                self.notebook.pack(fill = 'both', expand = 1, padx = 5, pady = 5)
                #
                self.dialogframe0 = ttk.Frame(self.NotebookFrame)
                self.dialogframe1 = ttk.Frame(self.NotebookFrame)
                self.dialogframe2 = ttk.Frame(self.NotebookFrame)
                self.dialogframe3 = ttk.Frame(self.NotebookFrame)
                self.dialogframe4 = ttk.Frame(self.NotebookFrame)
                self.dialogframe5 = ttk.Frame(self.NotebookFrame)
                self.dialogframe6 = ttk.Frame(self.NotebookFrame)
                self.dialogframe7 = ttk.Frame(self.NotebookFrame)
                #
                self.nb0_text=_('Settings')
                self.nb1_text=_('Select fluid')
                self.nb2_text=_('State Point')
                self.nb3_text=_('Saturation table')
                self.nb4_text=_('Diagrams')
                self.nb5_text=_('SimpleCycle')
                self.nb6_text=_('Cycle with heat exchanger')
                #
                self.notebook.add(self.dialogframe0,text=self.nb0_text)
                self.cpgsettings=cpg_settings(self.dialogframe0,self)
                
                self.notebook.add(self.dialogframe1,text=self.nb1_text)
                self.cpgbasics1=cpgbasics(self.dialogframe1,self)
    
                self.notebook.add(self.dialogframe2,text=self.nb2_text)
                self.cpgstatepoint1=cpgStatepoint(self.dialogframe2,self)
                            
                self.notebook.add(self.dialogframe3,text=self.nb3_text)
                self.cpgtable1=cpgSatTable(self.dialogframe3,self)
                
                self.notebook.add(self.dialogframe4,text=self.nb4_text)
                self.cpgDiagram1=cpgDiagram(self.dialogframe4,self)
                
                self.notebook.add(self.dialogframe5,text=self.nb5_text)
                self.cpgNewClass=cpg_cycle1(self.dialogframe5,self)
    
                self.notebook.add(self.dialogframe6,text=self.nb6_text)
                self.cpgNewClass=cpg_cycle2(self.dialogframe6,self)
                '''
                How to add a tab :
                Copy a class file like cpgui_SatTable.py to a new name
                Create your class and actions in there
                The Update method can be called on selection of the tab, see tabChangedEvent below
                Create translation .pot file e.g. python \Py34_64\Tools\i18n\pygettext.py -d de -o cpgSatTable.pot cpgui_sattable.py
                '''
                self.notebook.select(1)
                self.notebook.bind_all("<<NotebookTabChanged>>", self.tabChangedEvent)
                self.initcomplete=True
                self.mainloop()
            
        def about(self):
            messagebox.showinfo(_("About"), "Coolprop GUI 0.3 (c) Reiner J. Mayers 2015")
        
        def set_ref(self,ref):
            self.ref=ref
            self.tkref.set(ref)
            
        def get_ref(self):
            return self.ref
        
        def get_language(self):
            return self.language
        
        def set_language(self,lang):
            if self.initcomplete :
                cpgui_config['cpgui']['language'] = lang 
                save_settings()
                    
        def bindConfigure(self, event):
            if not self.initComplete:
                self.master.bind("<Configure>", self.Master_Configure)
                self.initComplete = 1
    
        def Master_Configure(self, event):
            pass
            if event.widget != self.master:
                if self.w != -1:
                    return
            x = int(self.master.winfo_x())
            y = int(self.master.winfo_y())
            w = int(self.master.winfo_width())
            h = int(self.master.winfo_height())
            if (self.x, self.y, self.w, self.h) == (-1,-1,-1,-1):
                self.x, self.y, self.w, self.h = x,y,w,h
    
            if self.w!=w or self.h!=h:
                print("Master reconfigured... make resize adjustments")
                self.w=w
                self.h=h
    
        def apply(self):
            pass #print 'apply called'
        
        def tabChangedEvent(self,event):
            updatebook=event.widget.tab(event.widget.index("current"),"text")
            if updatebook ==self.nb3_text:
                self.cpgtable1.Update()
                           
if __name__ == '__main__':
    if sys.version_info[0] < 3:
        import Tkinter
        from Tkinter import *
        print "Coolprop GUI requires Python 3 or later!"
        top = Tkinter.Tk()
        AlarmLabel = Label(top,text="Coolprop GUI requires Python 3 or later!",font=("Arial",22) )
        AlarmLabel.grid(row=1,column=0,padx=8,columnspan=5,sticky=W,pady=5)
        top.mainloop()
    else :
        root =Tk()
        # cx_freeze needs find file
        cpgui_icon=find_data_file('CoolPropLogo.ico')
        try :
            root.call('wm', 'iconbitmap', root._w, '-default', cpgui_icon)
        except tkinter.TclError :
            pass
            # On Ubuntu we ignore the .ico file for now
        CPGUI(root)


