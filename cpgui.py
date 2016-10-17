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
        
        def leave(self):
            self.master.destroy()
            self.master.quit()
    
        def __init__(self,master=None):
                Frame.__init__(self,master)
                # Create Canvas and frame using all the canvas
                self.canvas = Canvas(master, borderwidth=0, background="#ffffff")
                self.frame = Frame(self.canvas, background="#ffffff")
                # Create the scrollbars
                self.vsb = Scrollbar(master, orient="vertical", command=self.canvas.yview)
                self.hsb = Scrollbar(master, orient="horizontal", command=self.canvas.xview)
                # Always adjust length of the scrollbars
                self.canvas.configure(yscrollcommand=self.vsb.set)
                self.canvas.configure(xscrollcommand=self.hsb.set)
                # pack them into their corners
                self.vsb.pack(side="right", fill="y")
                self.hsb.pack(side="bottom", fill="x")
                # pack canvas into window and create it 
                self.canvas.pack(side="left", fill="both", expand=True)
                self.canvas.create_window((4,4), window=self.frame, anchor="nw",tags="self.frame")
                # Changing size will call method
                self.frame.bind("<Configure>", self.OnFrameConfigure)                
                #
                self.initcomplete=False
                self.ref=' '
                self.tkref=StringVar()
                self.master=master
                
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
                #self.grid()
                #self.master.columnconfigure(0, weight=1)
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
                filemenu.add_command(label=_('Quit'), command = self.leave)
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
                
                self.NotebookFrame=Frame(self.frame)
                self.TitleFrame=Frame(self.frame)
                #self.NotebookFrame.grid(row=1, column=0, columnspan=20,rowspan=20,sticky=W+E)
                #self.TitleFrame.grid(row=0, column=0, columnspan=20,sticky=W+E)
                self.TitleFrame.pack(side="top", fill="x", expand=True)
                self.NotebookFrame.pack(side="bottom", fill="both", expand=True)
                self.TitleLabel = Label(self.TitleFrame,textvariable=self.tkref,font=("Arial", 8) )
                self.TitleLabel.grid(row=0,column=0,padx=8,columnspan=5,sticky=W,pady=5)
            
                self.notebook = ttk.Notebook(self.NotebookFrame)
                self.notebook.pack(fill = 'both', expand = 1, padx = 5, pady = 5)
                #
                self.debugframe   = ttk.Frame(self.NotebookFrame)
                self.dialogframe0 = ttk.Frame(self.NotebookFrame)
                self.dialogframe1 = ttk.Frame(self.NotebookFrame)
                self.dialogframe2 = ttk.Frame(self.NotebookFrame)
                self.dialogframe3 = ttk.Frame(self.NotebookFrame)
                self.dialogframe4 = ttk.Frame(self.NotebookFrame)
                self.dialogframe5 = ttk.Frame(self.NotebookFrame)
                self.dialogframe6 = ttk.Frame(self.NotebookFrame)
                self.dialogframe7 = ttk.Frame(self.NotebookFrame)
                #
                self.nbdbg_text=_('Messages')
                self.nb0_text=_('Settings')
                self.nb1_text=_('Select fluid')
                self.nb2_text=_('State Point')
                self.nb3_text=_('Saturation table')
                self.nb4_text=_('Diagrams')
                self.nb5_text=_('SimpleCycle')
                self.nb6_text=_('Cycle with heat exchanger')
                #
                if cpgui_config['debug']['ShowPanel'] :
                    self.notebook.add(self.debugframe,text=self.nbdbg_text)
                    # Debug box
                    scrollbar_dbg = Scrollbar(self.debugframe, orient=VERTICAL)
                    self.dbg_box = Text(self.debugframe, yscrollcommand=scrollbar_dbg.set)
                    scrollbar_dbg.config(command=self.dbg_box.yview)
                    scrollbar_dbg.pack(side=RIGHT, fill=Y)
                    self.dbg_box.pack(side=LEFT, fill=BOTH, expand=1)
                    mydebug = RedirectText(self.dbg_box)
                    sys.stdout = mydebug
                    sys.stderr = mydebug
                    
                self.notebook.add(self.dialogframe0,text=self.nb0_text)
                self.cpgsettings=cpg_settings(self.dialogframe0,self)
                
                self.notebook.add(self.dialogframe1,text=self.nb1_text)
                self.cpgbasics1=cpgbasics(self.dialogframe1,self)
    
                self.notebook.add(self.dialogframe2,text=self.nb2_text)
                self.cpgstatepoint1=cpgStatepoint(self.dialogframe2,self)
                            
                self.notebook.add(self.dialogframe3,text=self.nb3_text)
                self.cpgtable1=cpgSatTable(self.dialogframe3,self)
                
                #self.notebook.add(self.dialogframe4,text=self.nb4_text)
                #self.cpgDiagram1=cpgDiagram(self.dialogframe4,self)
                
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
                if cpgui_config['debug']['ShowPanel'] :
                    self.notebook.select(2)
                else :
                    self.notebook.select(1)
                self.notebook.bind_all("<<NotebookTabChanged>>", self.tabChangedEvent)
                self.initcomplete=True
                
        def OnFrameConfigure(self, event):
            '''Reset the scroll region to encompass the inner frame'''
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            
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
        print("Coolprop GUI requires Python 3 or later!")
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
        mygui=CPGUI(master=root)
        mygui.mainloop()


