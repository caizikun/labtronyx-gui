from Base_Applet import Base_Applet
from widgets import *

import Tkinter as Tk
import tkMessageBox

class MethodTest(Base_Applet):
    
    info = {
        # Description
        'description':          'RPC Method Invoker',  
            
        # List of compatible Models
        'validDrivers':          ['Debug.m_Debug'],
        
        # List of compatible resource types
        'validResourceTypes':   ['Debug', 'VISA', 'Serial', 'ICP']
    }
        
    def run(self):
        self.wm_title("Method Tester")
        
        self.instr = self.getInstrument()
        self.instr._setTimeout(30.0)
        
        #=======================================================================
        # GUI Elements
        #=======================================================================
        # Driver info
        self.w_info = vw_info.vw_DriverInfo(self, self.instr)
        self.w_info.grid(row=0, column=0, columnspan=2)
        
        # Select Method
        Tk.Label(self, text='Method').grid(row=1, column=0)
        
        self.frameMethods = Tk.Frame(self)
        
        self.scrollbar = Tk.Scrollbar(self.frameMethods, orient=Tk.VERTICAL)
        self.methodList = Tk.Listbox(self.frameMethods, yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.methodList.yview)
        self.scrollbar.pack(side=Tk.RIGHT, fill=Tk.Y)
        self.methodList.pack(side=Tk.LEFT, fill=Tk.BOTH, expand=1)
        
        self.frameMethods.grid(row=1,column=1, 
                               sticky=Tk.N+Tk.E+Tk.S+Tk.W, padx=5, pady=5)
        
        self.methodList.bind('<<ListboxSelect>>', self.e_ListBoxClick)
        
        # Eval Box
        Tk.Label(self, text='Command').grid(row=2, column=0)
        self.str_eval = Tk.StringVar()
        self.txtMethod = Tk.Entry(self, textvariable=self.str_eval, width=50)
        self.txtMethod.grid(row=2, column=1, 
                            sticky=Tk.N+Tk.E+Tk.S+Tk.W, padx=5, pady=5)
        
        # Return Box
        Tk.Label(self, text='Return').grid(row=3, column=0)
        self.str_return = Tk.StringVar()
        self.txtReturn = Tk.Entry(self, textvariable=self.str_return, width=50)
        self.txtReturn.grid(row=3, column=1,
                            sticky=Tk.N+Tk.E+Tk.S+Tk.W, padx=5, pady=5)
        
        # Execute Button
        self.btnSend = Tk.Button(self, text="Execute", command=self.cb_Send)
        self.btnSend.grid(row=4, column=0, columnspan=2,
                          padx=5, pady=5)
        
        self.cb_refresh()
        
    def cb_refresh(self):
        # Clear listbox
        self.methodList.delete(0, Tk.END)
        
        # Populate Listbox
        methods = self.instr.rpc_getMethods()
        methods.sort()
        for proc in methods:
            self.methodList.insert(Tk.END, proc)
        
    def cb_Send(self):
        try:
            res = eval('self.instr.' + self.str_eval.get())
            
            if len(str(res)) < 1024:
                self.str_return.set(res)
            else:
                self.str_return.set("DATA TOO BIG")
                
        except Exception as e:
            tkMessageBox.showerror('Exception', str(e))
        
    def e_ListBoxClick(self, event):
        items = self.methodList.curselection()
        method = self.methodList.get(items[0])
        
        self.str_eval.set(str(method) + '()')
        
        