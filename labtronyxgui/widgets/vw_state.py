from . import vw_Base

import Tkinter as Tk

class vw_Trigger(vw_Base):
    def __init__(self, master, cb_func, **kwargs):
        """
        :param cb_func: Callback function
        :type cb_func: method
        :param label: Widget label
        :type label: str
        :param button_label: Button Label
        :type button_label: str
        """
        vw_Base.__init__(self, master, 12, 1)
        
        # Label
        if 'label' in kwargs:
            self.l_name = Tk.Label(self, width=15, 
                                   text=kwargs.get('label'), 
                                   anchor=Tk.W, justify=Tk.LEFT)
            self.l_name.pack(side=Tk.LEFT)

        # Button
        self.b_button = Tk.Button(self, text=kwargs.get('button_label', 'Execute'), 
                                  command=cb_func)
        self.b_button.pack(side=Tk.LEFT)
        
class vw_Toggle(vw_Base):
    """
    View Widget: State Toggle
    
    :param cb_func: method called when state is changed. Must accept 1 argument
    :type cb_func: bound_method    
    """
        
    def __init__(self, master, cb_func, **kwargs): #label, states=None, cb=None):
        vw_Base.__init__(self, master, 8, 1)
        
        self.states = kwargs.get('states', ['Off', 'On'])
        self.state = 0
        self.cb_func = cb_func
        
        # Label
        if 'label' in kwargs:
            label = kwargs.get('label')
            self.l_name = Tk.Label(self, width=15, font=("Purisa", 12), text=label, anchor=Tk.W, justify=Tk.LEFT)
            self.l_name.pack(side=Tk.LEFT)
        
        self.val = Tk.StringVar()
        self.b_state = Tk.Button(self, textvariable=self.val, command=self.cb_buttonPressed)
        self.b_state.pack(side=Tk.RIGHT)
        
        # Init
        self.setState(self.state)
        
        self.update_interval = kwargs.get('update_interval', None)
        self._schedule_update()
        
    def cb_buttonPressed(self):
        next_state = (self.state + 1) % len(self.states)
        
        self.setState(next_state)
        
        self.cb_func(self.state)
        
    def setState(self, new_state):
        if new_state < len(self.states):
            self.state = new_state
            self.val.set(self.states[self.state])
        else:
            raise IndexError
        
    def getState(self):
        return self.state
    
    def cb_update(self):
        pass

class vw_BinaryFields(vw_Base):
    
    def __init__(self, master, cb_get, cb_set, fields, names, **kwargs):
        """
        fields = { bit (int) : field_tag (str) }
        names = { field_tag (str) : field_name (str) } 
        """
        elems = len(fields)
        
        vw_Base.__init__(self, master, 8, elems)
        
        self.cb_get = cb_get
        self.cb_set = cb_set
        
        self.field_objects = {}
        
        bits = fields.keys()
        bits.sort()
        
        for bit in bits:
            field_tag = fields.get(bit)
            field_name = names.get(field_tag, field_tag)
            
            if cb_set is None:
                obj_temp = self.g_field_readonly(self, field_tag, field_name)
            else:
                obj_temp = self.g_field_readwrite(self, cb_set, field_tag, field_name)
                
            obj_temp.pack()
            self.field_objects[field_tag] = obj_temp 
            
        self.update_interval = kwargs.get('update_interval', None)
        self._schedule_update()

    def cb_update(self):
        field_vals = self.cb_get()
        
        for obj in self.field_objects.values():
            obj.cb_update(field_vals)

    class g_field_readwrite(Tk.Frame):
        def __init__(self, master, cb_func, field_tag, field_desc):
            Tk.Frame.__init__(self, master)
            
            self.master_widget = master
            self.field_tag = field_tag
            self.cb_set = cb_func
            
            # Label
            self.l_name = Tk.Label(self, width=22, font=("Purisa", 12), text=field_desc, anchor=Tk.W, justify=Tk.LEFT)
            self.l_name.pack(side=Tk.LEFT)

            # Field Status
            self.field_state = Tk.StringVar()
            self.b_status = Tk.Button(self, width=3, textvariable=self.field_state, command=self.cb_buttonPressed)
            self.b_status.pack(side=Tk.RIGHT)
            
            self.state = 0
            
        def cb_update(self, val):
            val_field = val.get(self.field_tag, 0)
            
            if val_field:
                self.state = 1
                self.field_state.set('1')
            else:
                self.state = 0
                self.field_state.set('0')
        
        def cb_buttonPressed(self):
            self.state = not self.state # invert
            field_dict = {}
            field_dict[self.field_tag] = self.state
            self.cb_set(**field_dict)
            
            self.master_widget.cb_update()

    class g_field_readonly(Tk.Frame):
        def __init__(self, master, field_tag, field_desc):
            Tk.Frame.__init__(self, master)
            
            #self.master_widget = master
            self.field_tag = field_tag
            
            # Label
            self.l_name = Tk.Label(self, width=22, font=("Purisa", 12), text=field_desc, anchor=Tk.W, justify=Tk.LEFT)
            self.l_name.pack(side=Tk.LEFT)

            # Field Status
            self.field_state = Tk.StringVar()
            self.b_status = Tk.Button(self, width=3, textvariable=self.field_state, state=Tk.DISABLED)
            self.b_status.pack(side=Tk.RIGHT)
            
            self.state = 0
            
        def cb_update(self, val):
            try:
                val_field = val.get(self.field_tag, 0)
            except AttributeError:
                val_field = 0
                
            self.state = val_field
            
            if val_field:
                self.field_state.set('1')
            else:
                self.field_state.set('0')
                    
            
            
