# -*- coding: latin-1 -*-
#
import sys
if sys.version_info[0] < 3:
    from Tkinter import *
    import ttk
    from tkSimpleDialog import Dialog
else:
    from tkinter import *
    from tkinter import ttk

import CoolProp
from CoolProp.CoolProp import PropsSI,get_global_param_string

from cpgui_all import myDialog,get_refprop_fluids,refprop_mixname

class MyDialog(myDialog):

    def body(self, master):
        #
        Label(master, text="Enter Mass fraction of components in kg/kg " ).grid(row=1,column=1,columnspan=2,sticky=NW)
        #
        mrow=2
        self.en=[]
        for ref in self.dialogOptions :
            dummy=Label(master, text=" %s "%ref ).grid(row=mrow,column=1)
            enx = Entry(master)
            enx.grid(row=mrow, column=2)
            self.en.append(enx)
            mrow+=1
        #
        return self.en[0] # initial focus

    def apply(self):
        mymasslist=[]
        for ent in range(len(self.dialogOptions)) :
            mymasslist.append(float(self.en[ent].get()))
            #print(' %s  Mass : %4.3f '%(self.dialogOptions[ent],float(self.en[ent].get())))
            self.mymasslist=mymasslist
               
class cpgbasics(myDialog):
    
    def __init__(self, GridFrame,Caller, title = None, dialogOptions=None):
        #
        self.initcomplete=False
        #
        fluids=CoolProp.__fluids__
        mixtures=get_global_param_string('predefined_mixtures').split(',')
        for mix in mixtures :
            fluids.append(mix)
        fluids.sort()
        self.Caller=Caller
        self.dialogframe1=GridFrame
        self.Ausgabetext=""
        self.tkref=StringVar()
        self.tkref.set(' ')
        self.frameborder=5
        self.mixnamelist=[]
        self.mixmasslist=[]
        self.mixmollist=[]
        #
        #
        # Beschriftungen
        #
        self.Label_1 = Label(self.dialogframe1,text='Refrigerant setup',font=("Arial", 14) )
        self.Label_1.grid(row=1,column=1,padx=8,columnspan=5,sticky=W,pady=5)

        self.Label_2 = Label(self.dialogframe1,text='Coolprop Refrigerant',font=("Arial", 10) )
        self.Label_2.grid(row=2,column=1,padx=8,sticky=W,columnspan=2)

        self.Label_3 = Label(self.dialogframe1,text='Chosen Refrigerant :',font=("Arial", 10) )
        self.Label_3.grid(row=4,column=1,padx=8,sticky=W,pady=4)

        self.Label_4 = Label(self.dialogframe1,text='Refprop Refrigerant',font=("Arial", 10) )
        self.Label_4.grid(row=2,column=2,padx=8,sticky=W,columnspan=2)
         
        self.reflabel = Label(self.dialogframe1,textvariable=self.tkref,font=("Arial", 10) )
        self.reflabel.grid(row=4,column=2,padx=8,sticky=W,pady=4,columnspan=3)

        self.Label_5 = Label(self.dialogframe1,text='Use Refprop fluids for Refprop mixtures and Coolprop fluids for HEOS mixtures. Choose backend later',font=("Arial", 12) )
        self.Label_5.grid(row=5,column=1,padx=8,sticky=W,pady=4,columnspan=7)
        #
        # Coolprop Refrigerants
        #
        lbframe = Frame( self.dialogframe1 )
        self.Listbox_1_frame = lbframe
        scrollbar = Scrollbar(lbframe, orient=VERTICAL)
        self.Listbox_1 = Listbox(lbframe, width="18", height="12", selectmode=BROWSE, yscrollcommand=scrollbar.set,font=("Arial", 10))
        for item in sorted(fluids):
            self.Listbox_1.insert(END, item)
        scrollbar.config(command=self.Listbox_1.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.Listbox_1.pack(side=LEFT, fill=BOTH, expand=1)
        #
        self.Listbox_1_frame.grid(row=3,column=1,sticky=W,padx=5,pady=5, columnspan=1,rowspan=1)
        self.Listbox_1.bind("<ButtonRelease-1>", self.Listbox_1_Click)
        #
        self.Listbox_1.select_set(13)
        #
        #
        # Refprop Refrigerants
        #
        lbframe2 = Frame( self.dialogframe1 )
        self.Listbox_2_frame = lbframe2
        scrollbar2 = Scrollbar(lbframe2, orient=VERTICAL)
        self.Listbox_2 = Listbox(lbframe2, width="18", height="12", selectmode=BROWSE, yscrollcommand=scrollbar2.set,font=("Arial", 10))
        rpfluids=get_refprop_fluids()
        for item in sorted(rpfluids):
            self.Listbox_2.insert(END, item)
        scrollbar2.config(command=self.Listbox_2.yview)
        scrollbar2.pack(side=RIGHT, fill=Y)
        self.Listbox_2.pack(side=LEFT, fill=BOTH, expand=1)
        #
        self.Listbox_2_frame.grid(row=3,column=2,sticky=W,padx=5,pady=5, columnspan=1,rowspan=1)
        self.Listbox_2.bind("<ButtonRelease-1>", self.Listbox_2_Click)
        #
        self.Listbox_2.select_set(13)
        #
        # Textbox
        #
        lbframe1 = Frame( self.dialogframe1 )
        self.Text_1_frame = lbframe1
        scrollbar1 = Scrollbar(lbframe1, orient=VERTICAL)
        self.Text_1 = Text(lbframe1, width="80", height="13", yscrollcommand=scrollbar1.set)
        scrollbar1.config(command=self.Text_1.yview)
        scrollbar1.pack(side=RIGHT, fill=Y)
        self.Text_1.pack(side=LEFT, fill=BOTH, expand=1)
        self.Text_1_frame.grid(row=3,column=3,columnspan=3,padx=2,sticky=W+E,pady=4)
        self.Text_1.delete(1.0, END)
        #self.Ausgabetext=KM.KM_Info(self.refrigerant)
        self.Text_1.insert(END, self.Ausgabetext)
        #
        self.BT1_Frame=LabelFrame(self.dialogframe1 ,relief=GROOVE,bd=self.frameborder,text='Mixture components',font=("Arial", 10))
        self.BT1_Frame.grid(row=6,column=1,sticky=W,padx=5,pady=5,columnspan=1,rowspan=4)
        #
        self.Button_addmix = Button(self.BT1_Frame,text='Add fluid to mixture',font=("Arial", 10, "bold") )
        self.Button_addmix.grid(row=1,rowspan=1,column=1,pady=5,sticky=W,padx=8)
        self.Button_addmix.bind("<ButtonRelease-1>", self.AddToMix)
        #
        self.Button_delmix = Button(self.BT1_Frame,text='Delete mixture' ,font=("Arial", 10, "bold"))
        self.Button_delmix.grid(row=2,rowspan=1,column=1,pady=5,sticky=W,padx=8)
        self.Button_delmix.bind("<ButtonRelease-1>", self.DeleteMix)
        #
        self.Button_setmix = Button(self.BT1_Frame,text='Define mixture' ,font=("Arial", 10, "bold"))
        self.Button_setmix.grid(row=3,rowspan=1,column=1,pady=5,sticky=W,padx=8)
        self.Button_setmix.bind("<ButtonRelease-1>", self.SetMix)
        #
        mixframe1 = Frame( self.dialogframe1 )
        self.Text_2_frame = mixframe1
        scrollbar3 = Scrollbar(mixframe1, orient=VERTICAL)
        self.Text_3 = Text(mixframe1, width="12", height="12", yscrollcommand=scrollbar3.set,font=("Arial", 10))
        scrollbar3.config(command=self.Text_3.yview)
        scrollbar3.pack(side=RIGHT, fill=Y)
        self.Text_3.pack(side=LEFT, fill=BOTH, expand=1)
        self.Text_2_frame.grid(row=6,column=2,columnspan=1,rowspan=7,padx=2,sticky=W+E,pady=4)
        self.Text_3.delete(1.0, END)
        #self.Ausgabetext=KM.KM_Info(self.refrigerant)
        self.Text_3.insert(END,' ')    
        #
        self.mixframe2 = Frame( self.dialogframe1 )
        self.mixframe2.grid(row=7,column=2,columnspan=2,padx=2,sticky=W+E,pady=4)
        #
        self.RG1_Frame=LabelFrame(self.dialogframe1 ,relief=GROOVE,bd=self.frameborder,text='Choose mixture backend',font=("Arial", 10))
        self.RG1_Frame.grid(row=10,column=1,sticky=W,padx=5,pady=5,columnspan=1,rowspan=3)
        
        self.RG1_StringVar = StringVar()
        self.RG1_StringVar.set('HEOS')
        self.RG1_StringVar_traceName = self.RG1_StringVar.trace_variable("w", self.RG1_StringVar_Callback)

        self.RG1_Button_01 = Radiobutton(self.RG1_Frame,text='HEOS', value='HEOS', relief="raised",indicatoron=False,width=15 )
        self.RG1_Button_01.grid(column=1,row=1,padx=8,sticky=W,pady=8)
        self.RG1_Button_01.configure(variable=self.RG1_StringVar)
        #
        self.RG1_Button_02 = Radiobutton(self.RG1_Frame,text='REFPROP', value='REFPROP', relief="raised",indicatoron=False,width=15 )
        self.RG1_Button_02.grid(column=1,row=2,padx=8,sticky=W,pady=8)
        self.RG1_Button_02.configure(variable=self.RG1_StringVar )
        #
        self.initcomplete=True   
        self.Update() 

    def AddToMix(self,event):
        if self.ref not in self.mixnamelist :
            if '::' in self.ref :
                self.mixnamelist.append(self.ref.split('::')[1])
            else :
                self.mixnamelist.append(self.ref)
        self.Text_3.delete(1.0,END)
        for mix in self.mixnamelist :
            self.Text_3.insert(END,'%s\n'%mix)
            
    def DeleteMix(self,event):
        self.Text_3.delete(1.0,END)
        self.mixnamelist=[]
        self.mixmasslist=[]
        self.mixmollist=[]
        self.mixframe.grid_forget()

    def SetMix(self,event):
        #
        d=MyDialog(self.Caller.master,dialogOptions=self.mixnamelist)
        self.mixmasslist=d.mymasslist
        mixname,self.mixmollist=refprop_mixname(self.mixnamelist,self.mixmasslist)
        self.Caller.set_ref(mixname)
        self.ShowMix()
        self.Update()

    def ShowMix(self):
        #
        self.mixframe= LabelFrame(self.dialogframe1,relief=GROOVE,bd=self.frameborder,text='Mixture composition',font=("Arial", 10))
        self.mixframe.grid(row=7,column=3,padx=8,sticky=W,pady=4,columnspan=1)
        self.mix_tk_list=[]
        mixrow=1
        mixlabel1 = Label(self.mixframe,text=' Name           kg/kg         mol/mol',font=("Arial", 10) )
        mixlabel1.grid(row=mixrow,column=1,padx=8,columnspan=3,sticky=W,pady=5)
        self.mix_tk_list.append(mixlabel1)
        mixrow+=1
        for i in range(len(self.mixnamelist)):
                    mixlabel1 = Label(self.mixframe,text=self.mixnamelist[i],font=("Arial", 10) )
                    mixlabel1.grid(row=mixrow,column=1,padx=8,columnspan=1,sticky=W,pady=5)
                    mixlabel2 = Label(self.mixframe,text=(' %2.4f'%self.mixmasslist[i]),font=("Arial", 10) )
                    mixlabel2.grid(row=mixrow,column=2,padx=8,columnspan=1,sticky=W,pady=5)
                    mixlabel3 = Label(self.mixframe,text=(' %2.16f'%self.mixmollist[i]),font=("Arial", 10) )
                    mixlabel3.grid(row=mixrow,column=3,padx=8,columnspan=1,sticky=W,pady=5)                    
                    mixrow+=1
                    self.mix_tk_list.append(mixlabel1)
                    self.mix_tk_list.append(mixlabel2)
                    self.mix_tk_list.append(mixlabel3)
                    
    def Listbox_1_Click(self, event):
        #
        index=self.Listbox_1.curselection()
        self.ref=self.Listbox_1.get(index)
        self.tkref.set(self.ref)
        self.Caller.set_ref(self.ref)
        self.Update()
        get_refprop_fluids()

    def Listbox_2_Click(self, event):
        #
        index=self.Listbox_2.curselection()
        if self.Listbox_2.get(index)=='Refprop not found':
            self.ref='R134a'
        else :
            self.ref=('REFPROP::'+self.Listbox_2.get(index))
        self.tkref.set(self.ref)
        self.Caller.set_ref(self.ref)
        self.Update()
        
    def Update(self):
        #
        if self.initcomplete :
            self.ref=self.Caller.get_ref()
            self.Text_1.delete(1.0, END)
            self.Ausgabetext= 'Coolprop Version     : %s     \n'%str(CoolProp.__version__)
            self.Ausgabetext+='Coolprop gitrevision : %s     \n'%str(CoolProp.__gitrevision__)
            self.Ausgabetext+='Refrigerant          : %s     \n'%str(self.ref)
    
    
            self.Ausgabetext+=self.get_GWP100()
            self.Ausgabetext+=self.get_ODP()
            molmassstring=''
            try :
                molmass=PropsSI('M',self.ref)
            except ValueError :
                molmassstring='  N/A '
            if molmassstring=='' :
                molmassstring='%6.2f'%(molmass*1000)
            self.Ausgabetext+='Molar mass           :%s  \n'%molmassstring
            self.Text_1.insert(END,self.Ausgabetext)

    def RG1_StringVar_Callback(self, varName, index, mode):
        #
        backend=self.RG1_StringVar.get()
        self.ref=self.Caller.get_ref()
        if ':' in self.ref :
            try :
                myref=self.ref.split(':')[-1]
            except ValueError :
                pass
            if backend=='HEOS':
                self.ref='HEOS::'+myref
            elif backend=='REFPROP':
                self.ref='REFPROP::'+myref
            #
            self.tkref.set(self.ref)
            self.Caller.set_ref(self.ref)
            self.Update()
        else :
            pass
        
           
    def get_GWP100(self):
        # GWP
        try :
            GWP=PropsSI('GWP100',self.ref)
        except ValueError :
            GWP=-1
        if GWP == -1:
            GWP100='GWP100               : N/A    \n'
        else :
            GWP100='GWP100               : %d     \n'%GWP
        return GWP100
    
    def get_ODP(self):
        # ODP
        try :
            ODP=PropsSI('ODP',self.ref)
        except ValueError :
            ODP=-1
        if ODP == -1 or ODP==0 :
            ODP1='ODP                  : N/A    \n'
        else :
            ODP1='Ozone depleting Substance !\nODP                  : %2.3F     \n'%ODP
        return ODP1
    
class _Testdialog:
    
    def __init__(self, master):
        frame = Frame(master)
        frame.pack()
        self.master = master
        self.x, self.y, self.w, self.h = -1,-1,-1,-1
        #
        self.tkref=StringVar()
        self.ref='R134a'
        self.tkref.set(self.ref)
        App=cpgbasics(frame,self)

    def set_ref(self,ref):
        self.ref=ref
        self.tkref.set(ref)

    def get_ref(self):
        return 'R134a'
    
def main():
    root = Tk()
    app = _Testdialog(root)
    root.mainloop()
    
if __name__ == '__main__':
    main()
