import sys
import wx
import wx.lib
import numpy
import copy
import math
from sans.models.dispersion_models import ArrayDispersion, GaussianDispersion

from sans.guicomm.events import StatusEvent   
from sans.guiframe.utils import format_number
(ModelEventbox, EVT_MODEL_BOX) = wx.lib.newevent.NewEvent()
_BOX_WIDTH = 80



class ModelPage(wx.ScrolledWindow):
    """
        ModelPage is a panel that allows the user to view information related to a 
        model. 
  
    """
    ## Internal name for the AUI manager
    window_name = "Fit page"
    ## Title to appear on top of the window
    window_caption = "Fit Page"
    # name of the panel directly related to the model name selected
    name =" "

    def __init__(self, parent,model=None,name=None,data=None, *args, **kwargs):
        wx.ScrolledWindow.__init__(self, parent, *args, **kwargs)
        """ 
            Initialization of the Panel
        """
        # model on which the fit would be performed
        self.model=model
        
        ## Data member to store the dispersion object created
        self._disp_obj_dict = {}
        
        #list of dispersion parameters
        self.disp_list=[]
        try:
            self.disp_list=self.model.getDispParamList()
        except:
            pass 
        self.manager = None
        self.parent  = parent
        self.event_owner = None
        # this panel does contain data .existing data allow a different drawing
        #on set_model parameters
        self.data=data
        
        
        # contains link between  model ,all its parameters, and panel organization
        self.parameters=[]
        #list of parameters that cannot be fitted and panel object related to this parameters
        #values
        self.fixed_param=[]
        #
        self.fittable_param=[]
        self.polydisp= {}
        #contains link between a model and selected parameters to fit 
        self.param_toFit=[]
        
        self.prevmodel_name=name
        self.draw_panel()
        #dictionary of model name and model class
        self.model_list_box={}
        #Draw initial panel
        if self.model!=None:
            self.set_panel(self.model)
        self.theta_cb=None
        # flag to allow data2D plot
        self.enable2D=False
        
    
        self.Centre()
        self.Layout()
        self.parent.GetSizer().Layout()
        
    def draw_panel(self):   
        #panel interface
        self.vbox  = wx.BoxSizer(wx.VERTICAL)
        self.sizer11 = wx.BoxSizer(wx.HORIZONTAL)
        #self.sizer10 = wx.GridBagSizer(5,5)
        self.sizer9 = wx.GridBagSizer(5,5)
        self.sizer8 = wx.GridBagSizer(5,5)
        self.sizer7 = wx.GridBagSizer(5,5)
        self.sizer6 = wx.GridBagSizer(5,5)
        self.sizer5 = wx.GridBagSizer(5,5)
        self.sizer4 = wx.GridBagSizer(5,5)
        #model selection
        self.vbox.Add(wx.StaticLine(self, -1), 0, wx.EXPAND, 0)
        self.vbox.Add(self.sizer4)
        #model description
        self.vbox.Add(self.sizer11)
        #model paramaters layer
        self.vbox.Add(self.sizer5)
        #polydispersion selected
        self.vbox.Add(wx.StaticLine(self, -1), 0, wx.EXPAND, 0)
        self.vbox.Add(self.sizer6)
        #combox box for type of dispersion
        self.vbox.Add(self.sizer7)
        #dispersion parameters layer
        self.vbox.Add(self.sizer8)
        # plotting range
        self.vbox.Add(self.sizer9)
    
        #------------------ sizer 4  draw------------------------  
        # define combox box
        self.modelbox = wx.ComboBox(self, -1)
         # preview selected model name
        
        #print "model view prev_model",name
        self.modelbox.SetValue(self.prevmodel_name)
        #enable model 2D draw
        self.enable2D= False
        #filling sizer2
        ix = 0
        iy = 1
        self.sizer4.Add(wx.StaticText(self,-1,'Model'),(iy,ix),(1,1)\
                  , wx.LEFT|wx.EXPAND|wx.ADJUST_MINSIZE, 15)
        ix += 1
        self.sizer4.Add(self.modelbox,(iy,ix),(1,1),  wx.EXPAND|wx.ADJUST_MINSIZE, 0)
        ix += 1
        id = wx.NewId()
        self.model_view =wx.Button(self,id,'View 2D')
        self.model_view.Bind(wx.EVT_BUTTON, self.onModel2D,id=id)
        self.model_view.SetToolTipString("View model in 2D")
        
        self.sizer4.Add(self.model_view,(iy,ix),(1,1),\
                   wx.LEFT|wx.EXPAND|wx.ADJUST_MINSIZE, 15)
        
        self.model_view.Enable()
        self.model_view.SetFocus()
        
        ix = 0
        iy += 1
        self.sizer4.Add((20,20),(iy,ix),(1,1),wx.LEFT|wx.EXPAND|wx.ADJUST_MINSIZE, 15)

        #----------sizer6-------------------------------------------------
        self.disable_disp = wx.RadioButton(self, -1, 'No', (10, 10), style=wx.RB_GROUP)
        self.enable_disp = wx.RadioButton(self, -1, 'Yes', (10, 30))
        self.Bind(wx.EVT_RADIOBUTTON, self.set_Dispers_Param, id=self.disable_disp.GetId())
        self.Bind(wx.EVT_RADIOBUTTON, self.set_Dispers_Param, id=self.enable_disp.GetId())
        ix= 0
        iy=1
        self.sizer6.Add(wx.StaticText(self,-1,'Polydispersity: '),(iy,ix),(1,1)\
                  , wx.LEFT|wx.EXPAND|wx.ADJUST_MINSIZE, 15)
        ix += 1
        self.sizer6.Add(self.enable_disp ,(iy,ix),(1,1),  wx.EXPAND|wx.ADJUST_MINSIZE, 0)
        ix += 1
        self.sizer6.Add(self.disable_disp ,(iy,ix),(1,1),  wx.EXPAND|wx.ADJUST_MINSIZE, 0)
        ix =0
        iy+=1
        self.sizer6.Add((20,20),(iy,ix),(1,1),wx.LEFT|wx.EXPAND|wx.ADJUST_MINSIZE, 15)  
        #---------sizer 9 draw----------------------------------------
        ## Q range
        self.qmin_x= 0.001
        self.qmax_x= 0.1
        self.num_points= 100
        
        
        self.qmin    = wx.TextCtrl(self, -1,size=(_BOX_WIDTH,20))
        self.qmin.SetValue(format_number(self.qmin_x))
        self.qmin.SetToolTipString("Minimun value of Q in linear scale.")
        self.qmin.Bind(wx.EVT_KILL_FOCUS, self._onparamEnter)
        self.qmin.Bind(wx.EVT_TEXT_ENTER, self._onparamEnter)
     
        self.qmax    = wx.TextCtrl(self, -1,size=(_BOX_WIDTH,20))
        self.qmax.SetValue(format_number(self.qmax_x))
        self.qmax.SetToolTipString("Maximum value of Q in linear scale.")
        self.qmax.Bind(wx.EVT_KILL_FOCUS, self._onparamEnter)
        self.qmax.Bind(wx.EVT_TEXT_ENTER, self._onparamEnter)
     

        self.npts    = wx.TextCtrl(self, -1,size=(_BOX_WIDTH,20))
        self.npts.SetValue(format_number(self.num_points))
        self.npts.SetToolTipString("Number of point to plot.")
        self.npts.Bind(wx.EVT_KILL_FOCUS, self._onparamEnter)
        self.npts.Bind(wx.EVT_TEXT_ENTER, self._onparamEnter)
       
        ix = 0
        iy = 1 
        self.sizer9.Add(wx.StaticText(self, -1, 'Plotting Range'),(iy, ix),(1,1),\
                            wx.LEFT|wx.EXPAND|wx.ADJUST_MINSIZE, 15)
        ix += 1 
        self.sizer9.Add(wx.StaticText(self, -1, 'Min'),(iy, ix),(1,1),\
                            wx.EXPAND|wx.ADJUST_MINSIZE, 0)
        ix += 1
        self.sizer9.Add(wx.StaticText(self, -1, 'Max'),(iy, ix),(1,1),\
                            wx.EXPAND|wx.ADJUST_MINSIZE, 0)
        ix += 1
        self.sizer9.Add(wx.StaticText(self, -1, 'Npts'),(iy, ix),(1,1),\
                            wx.EXPAND|wx.ADJUST_MINSIZE, 0)
        ix = 0
        iy += 1
        self.sizer9.Add(wx.StaticText(self, -1, 'Q range'),(iy, ix),(1,1),\
                            wx.LEFT|wx.EXPAND|wx.ADJUST_MINSIZE, 15)
        ix += 1
        self.sizer9.Add(self.qmin,(iy, ix),(1,1), wx.LEFT|wx.EXPAND|wx.ADJUST_MINSIZE, 0)
        ix += 1
        self.sizer9.Add(self.qmax,(iy,ix),(1,1), wx.LEFT|wx.EXPAND|wx.ADJUST_MINSIZE, 0)
        ix += 1
        self.sizer9.Add(self.npts,(iy,ix),(1,1), wx.LEFT|wx.EXPAND|wx.ADJUST_MINSIZE, 0)
        
        ix =0
        iy+=1 
        self.sizer9.Add((20,20),(iy,ix),(1,1), wx.LEFT|wx.EXPAND|wx.ADJUST_MINSIZE, 0)
        self.vbox.Layout()
        self.vbox.Fit(self) 
        self.SetSizer(self.vbox)
        self.SetScrollbars(20,20,55,40)
        
        
    def set_model_description(self, model):
        """
            Set a sizer with model description field
            @param model: the model select that provides the description
        """
        if model !=None and str(model.description)!=""and self.data==None:
            self.sizer11.Clear(True)
            self.box_description= wx.StaticBox(self, -1, 'Model Description')
            boxsizer1 = wx.StaticBoxSizer(self.box_description, wx.VERTICAL)
            boxsizer1.SetMinSize((320,20))
            self.description = wx.StaticText(self,-1,str(model.description))
            boxsizer1.Add(self.description, 0, wx.EXPAND)  
            self.sizer11.Add(boxsizer1,1, wx.EXPAND | wx.ALL, 2)
      
        
    def set_owner(self,owner):
        """ 
            set owner of fitpage
            @param owner: the class responsible of plotting
        """
        self.event_owner=owner    
   
  
    def set_manager(self, manager):
        """
             set panel manager
             @param manager: instance of plugin fitting
        """
        self.manager = manager  
        
    def populate_box(self, dict):
        """
            Populate each combox box of each page
            @param page: the page to populate
        """
        id=0
        self.model_list_box=dict
        list_name=[]
        for item in  self.model_list_box.itervalues():
            name = item.__name__
            if hasattr(item, "name"):
                name = item.name
            list_name.append(name)
        list_name.sort() 
         
        for name in list_name:
            self.modelbox.Insert(name,int(id))
            id+=1
        wx.EVT_COMBOBOX(self.modelbox,-1, self._on_select_model) 
        return 0
    

    def set_Dispers_Param(self, event):
        """
             set a sizer with dispersion parameters 
        """
        if self.enable_disp.GetValue():
            # The user selected to use dispersion/averaging
            if len(self.disp_list)==0:
                # This model contains no parameter to which we can apply dispersion/averaging
                ix=0
                iy=1
                self.fittable_param=[]
                self.fixed_param=[]
                self.sizer8.Clear(True)
                model_disp = wx.StaticText(self, -1, 'No PolyDispersity for this model')
                self.sizer7.Add(model_disp,( iy, ix),(1,1),  wx.LEFT|wx.EXPAND|wx.ADJUST_MINSIZE, 15)
                self.vbox.Layout()
                self.SetScrollbars(20,20,55,40)
                self.Layout()
                self.parent.GetSizer().Layout()
                return 
            else:
                # allow to recognize data panel from model panel
                if self.data !=None and self.model !=None: 
                    
                    self.cb1.SetValue(False)
                    self.select_all_param_helper()
                
                self.populate_disp_box()
                self.set_panel_dispers(self.disp_list)
                
        else:
            # The user selected not to use dispersion/averaging            
            # Make sure all parameters have the default Gaussian
            # dispersion object with only a single point (no dispersion).
            for p in self.model.dispersion.keys():
                disp_model = GaussianDispersion()
                
                # Store the object to make it persist outside the scope of this method
                #TODO: refactor model to clean this up?
                self._disp_obj_dict[p] = disp_model
                    
                # Set the new model as the dispersion object for the selected parameter
                self.model.set_dispersion(p, disp_model)
                    
            # Redraw the model
            self._draw_model()
                
            self.fittable_param=[]        
            self.fixed_param=[]
            self.sizer7.Clear(True)
            self.sizer8.Clear(True)
            self.vbox.Layout()
            self.SetScrollbars(20,20,55,40)
            self.Layout()
            self.parent.GetSizer().Layout()
            
    def populate_disp_box(self):
        """
            populate polydispersion combo box 
        """
        self.sizer7.Clear(True)
        if len(self.disp_list)>0:
            ix=0
            iy=1
            model_disp = wx.StaticText(self, -1, 'Model Disp')
            self.sizer7.Add(model_disp,( iy, ix),(1,1),  wx.LEFT|wx.EXPAND|wx.ADJUST_MINSIZE, 15)
            ix += 1 
            # set up the combox box
            id = 0
            import sans.models.dispersion_models 
            self.polydisp= sans.models.dispersion_models.models
            self.disp_box = wx.ComboBox(self, -1)
            self.disp_box.SetValue("GaussianModel")
            for k,v in self.polydisp.iteritems():
                if str(v)=="MyModel":
    				# Remove the option until the rest of the code is ready for it
                    #self.disp_box.Insert("Select customized Model",id)
                    pass  
                else:
                    self.disp_box.Insert(str(v),id)         
                id+=1
            
            wx.EVT_COMBOBOX(self.disp_box,-1, self._on_select_Disp) 
            self.sizer7.Add(self.disp_box,( iy, ix),(1,1), wx.EXPAND|wx.ADJUST_MINSIZE, 0)
            self.vbox.Layout()
            self.SetScrollbars(20,20,55,40)
            self.Layout()
            self.parent.GetSizer().Layout()  
            
            
    def set_range(self, qmin_x, qmax_x, npts):
        """
            Set the range for the plotted models
            @param qmin: minimum Q
            @param qmax: maximum Q
            @param npts: number of Q bins
        """
        # Set the data members
        self.qmin_x = qmin_x
        self.qmax_x = qmax_x
        self.num_points = npts
        
        # Set the controls
        self.qmin.SetValue(format_number(self.qmin_x))
        self.qmax.SetValue(format_number(self.qmax_x))
        self.npts.SetValue(format_number(self.num_points))
        
        
    def checkFitRange(self):
        """
            Check the validity of fitting range
            @note: qmin should always be less than qmax or else each control box
            background is colored in pink.
        """
        flag = True
        valueMin = self.qmin.GetValue()
        valueMax = self.qmax.GetValue()
        # Check for possible values entered
        try:
            if (float(valueMax)> float(valueMin)):
                self.qmax.SetBackgroundColour(wx.WHITE)
                self.qmin.SetBackgroundColour(wx.WHITE)
            else:
                flag = False
                self.qmin.SetBackgroundColour("pink")
                self.qmax.SetBackgroundColour("pink")      
        except:
            flag = False
            self.qmin.SetBackgroundColour("pink")
            self.qmax.SetBackgroundColour("pink")
            
        self.qmin.Refresh()
        self.qmax.Refresh()
        return flag
    
        
    def onModel2D(self, event):
        """
         call manager to plot model in 2D
        """
        # If the 2D display is not currently enabled, plot the model in 2D 
        # and set the enable2D flag.
        if self.enable2D==False:
            self.enable2D=True
            self._draw_model()
            self.model_view.Disable()
            
    
    def select_model(self, model, name):
        """
            Select a new model
            @param model: model object 
        """
        self.model = model
        self.parent.model_page.name = name
        self.parent.draw_model_name = name
        
        self.set_panel(model)
        self._draw_model(name)
        
        # Select the model from the combo box
        items = self.modelbox.GetItems()
        for i in range(len(items)):
            if items[i]==name:
                self.modelbox.SetSelection(i)
                self.model_view.SetFocus()
                
    def _on_select_Disp(self,event):
        """
             allow selecting different dispersion
             self.disp_list should change type later .now only gaussian
        """
        type =event.GetString()
        self.set_panel_dispers( self.disp_list,type )
          
     
    def _on_select_model(self,event):
        """
            react when a model is selected from page's combo box
            post an event to its owner to draw an appropriate theory
        """
        self.disable_disp.SetValue(True)
        self.sizer8.Clear(True)
        self.sizer7.Clear(True)       
        self.vbox.Layout()
        self.SetScrollbars(20,20,55,40)
        self.Layout()
        self.parent.GetSizer().Layout()
        for item in self.model_list_box.itervalues():
            name = item.__name__
            if hasattr(item, "name"):
                name = item.name
            if name ==event.GetString():
                model=item()
                self.model= model
                self.set_panel(model)
                self.name= name
                self.model_view.SetFocus()
                self.parent.model_page.name=name
                self.parent.draw_model_name=name
               
                self._draw_model(name)
            
            
    def get_model_box(self): 
        """ return reference to combox box self.model"""
        return self.modelbox

    
    def get_param_list(self):
        """
            @return self.param_toFit: list containing  references to TextCtrl
            checked.Theses TextCtrl will allow reference to parameters to fit.
            @raise: if return an empty list of parameter fit will nnote work 
            properly so raise ValueError,"missing parameter to fit"
        """
        if self.param_toFit !=[]:
            return self.param_toFit
        else:
            raise ValueError,"missing parameter to fit"
        
        
    def set_panel(self,model):
        """
            Build the panel from the model content
            @param model: the model selected in combo box for fitting purpose
        """
       
        self.sizer5.Clear(True)
        self.parameters = []
        self.param_toFit=[]
        self.fixed_param=[]
        self.model = model
        
        self.set_model_description( self.model) 
        
        keys = self.model.getParamList()
        #list of dispersion paramaters
        self.disp_list=self.model.getDispParamList()
       
        keys.sort()
        ik=0
        im=1
        
        iy = 1
        ix = 0
        self.cb1 = wx.CheckBox(self, -1,"Select all", (10, 10))
        if self.data!=None:
            wx.EVT_CHECKBOX(self, self.cb1.GetId(), self.select_all_param)
            self.cb1.SetValue(False)
        else:
            self.cb1.Disable()
            self.cb1.Hide()
       
        self.sizer5.Add(self.cb1,(iy, ix),(1,1),\
                          wx.LEFT|wx.EXPAND|wx.ADJUST_MINSIZE, 15)
        ix +=1
        self.text2_2 = wx.StaticText(self, -1, 'Values')
        self.sizer5.Add(self.text2_2,(iy, ix),(1,1),\
                            wx.EXPAND|wx.ADJUST_MINSIZE, 0) 
        ix +=2
        self.text2_3 = wx.StaticText(self, -1, 'Errors')
        self.sizer5.Add(self.text2_3,(iy, ix),(1,1),\
                            wx.EXPAND|wx.ADJUST_MINSIZE, 0)
        self.text2_3.Hide() 
        
        ix +=1
        self.text2_4 = wx.StaticText(self, -1, 'Units')
        self.sizer5.Add(self.text2_4,(iy, ix),(1,1),\
                            wx.EXPAND|wx.ADJUST_MINSIZE, 0) 
        self.text2_4.Hide()
        disp_list=self.model.getDispParamList()
        # 
        for item in keys:
            if not item in disp_list:
                iy += 1
                ix = 0
    
                cb = wx.CheckBox(self, -1, item, (10, 10))
                if self.data!=None:
                    cb.SetValue(False)
                    wx.EVT_CHECKBOX(self, cb.GetId(), self.select_param)
                else:
                    cb.Disable()
                self.sizer5.Add( cb,( iy, ix),(1,1),  wx.LEFT|wx.EXPAND|wx.ADJUST_MINSIZE, 15)
               
                ix += 1
                value= self.model.getParam(item)
                ctl1 = wx.TextCtrl(self, -1, size=(_BOX_WIDTH,20), style=wx.TE_PROCESS_ENTER)
                ctl1.SetValue(str (format_number(value)))
                ctl1.Bind(wx.EVT_KILL_FOCUS, self._onparamEnter)
                ctl1.Bind(wx.EVT_TEXT_ENTER,self._onparamEnter)
                self.sizer5.Add(ctl1, (iy,ix),(1,1), wx.EXPAND)
                
                ix += 1
                text2=wx.StaticText(self, -1, '+/-')
                self.sizer5.Add(text2,(iy, ix),(1,1),\
                                wx.EXPAND|wx.ADJUST_MINSIZE, 0) 
                text2.Hide()  
                ix += 1
                ctl2 = wx.TextCtrl(self, -1, size=(_BOX_WIDTH,20), style=wx.TE_PROCESS_ENTER)
                self.sizer5.Add(ctl2, (iy,ix),(1,1), wx.EXPAND|wx.ADJUST_MINSIZE, 0)
                ctl2.Hide()
               
                ix +=1
                # Units
                try:
                    units = wx.StaticText(self, -1, self.model.details[item][0], style=wx.ALIGN_LEFT)
                except:
                    units = wx.StaticText(self, -1, "", style=wx.ALIGN_LEFT)
                self.sizer5.Add(units, (iy,ix),(1,1),  wx.EXPAND|wx.ADJUST_MINSIZE, 0)
           
                self.parameters.append([cb,ctl1,text2,ctl2])
                
        iy+=1
        self.sizer5.Add((20,20),(iy,ix),(1,1), wx.LEFT|wx.EXPAND|wx.ADJUST_MINSIZE, 15)
        
        #Display units text on panel
        for item in keys:   
            if self.model.details[item][0]!='':
                self.text2_4.Show()
                break
            else:
                self.text2_4.Hide()
        
        self.vbox.Layout()
        self.SetScrollbars(20,20,55,40)
        self.Layout()
        self.parent.GetSizer().Layout()
        
        
        
    def _selectDlg(self):
        """
            Create a dialog to select files
        """
        import os
        dlg = wx.FileDialog(self, "Choose a weight file", os.getcwd(), "", "*.*", wx.OPEN)
        path = None
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
        dlg.Destroy()
        return path
    
    
    def read_file(self, path):
        """
            Read a file  of 2 colons
            @param path: the path to the file
            @return 2 numpy arrays containing numbers
        """
        try:
            if path==None:
                wx.PostEvent(self.parent.parent, StatusEvent(status=\
                            " Selected Distribution was not loaded: %s"%path))
                return None, None
            input_f = open(path, 'r')
            buff = input_f.read()
            lines = buff.split('\n')
            
            angles = []
            weights=[]
            for line in lines:
                toks = line.split()
                if len(toks)==2:
                    try:
                        angle = float(toks[0])
                        weight = float(toks[1])
                    except:
                        # Skip non-data lines
                        pass
                    angles.append(angle)
                    weights.append(weight)
            return numpy.array(angles), numpy.array(weights)
        except:
             msg= "Simultaneous Fit completed but Following error occurred: "
             msg+= "%s"%sys.exc_value
             wx.PostEvent(self.parent.parent, StatusEvent(status=msg))
             return  
        
          
    def select_disp_angle(self, event): 
        """
            Event for when a user select a parameter to average over.
            @param event: check box event
        """
        # Go through the list of dispersion check boxes to identify which one has changed 
        for p in self.disp_cb_dict:
            # Catch which one of the box was just checked or unchecked.
            if event.GetEventObject() == self.disp_cb_dict[p]:              

                
                if self.disp_cb_dict[p].GetValue() == True:
                    # The user wants this parameter to be averaged. 
                    # Pop up the file selection dialog.
                    path = self._selectDlg()
                    
                    # If nothing was selected, just return
                    if path is None:
                        self.disp_cb_dict[p].SetValue(False)
                        return
                    
                    try:
                        values,weights = self.read_file(path)
                    except:
                        wx.PostEvent(self.parent.parent, StatusEvent(status=\
                            "Could not read input file"))
                        return
                    
                    # If any of the two arrays is empty, notify the user that we won't
                    # proceed 
                    if values is None or weights is None:
                        wx.PostEvent(self.parent.parent, StatusEvent(status=\
                            "The loaded %s distrubtion is corrupted or empty" % p))
                        return
                        
                    # Tell the user that we are about to apply the distribution
                    wx.PostEvent(self.parent.parent, StatusEvent(status=\
                            "Applying loaded %s distribution: %s" % (p, path)))  
                    
                    # Create the dispersion objects
                    disp_model = ArrayDispersion()
                    disp_model.set_weights(values, weights)
                    # Store the object to make it persist outside the scope of this method
                    #TODO: refactor model to clean this up?
                    self._disp_obj_dict[p] = disp_model
                    
                    # Set the new model as the dispersion object for the selected parameter
                    self.model.set_dispersion(p, disp_model)
                    
                    
                    # Redraw the model
                    self._draw_model()
                         
                else:
                    # The parameter was un-selected. Go back to Gaussian model (with 0 pts)
                    disp_model = GaussianDispersion()
                    # Store the object to make it persist outside the scope of this method
                    #TODO: refactor model to clean this up?
                    self._disp_obj_dict[p] = disp_model
                    
                    # Set the new model as the dispersion object for the selected parameter
                    self.model.set_dispersion(p, disp_model)
                    
                    # Redraw the model
                    self._draw_model()
        return
       
                      
    def set_panel_dispers(self, disp_list, type="GaussianModel" ):
        """
            Fill sizer with disperstion info
        """
        
        self.fittable_param=[]
        self.fixed_param=[]
        
        ix=0
        iy=1
                ### this will become a separate method
        if type== "Select customized Model":
            ix=0
            iy=1
            self.sizer8.Clear(True)        
            disp1 = wx.StaticText(self, -1, 'Array Dispersion')
            self.sizer8.Add(disp1,( iy, ix),(1,1),  wx.LEFT|wx.EXPAND|wx.ADJUST_MINSIZE, 15)
            
            # Look for model parameters to which we can apply an ArrayDispersion model
            # Add a check box for each parameter.
            self.disp_cb_dict = {}
            for p in self.model.dispersion.keys():
                ix+=1 
                self.disp_cb_dict[p] = wx.CheckBox(self, -1, p, (10, 10))
                
                wx.EVT_CHECKBOX(self, self.disp_cb_dict[p].GetId(), self.select_disp_angle)
                self.sizer8.Add(self.disp_cb_dict[p], (iy, ix), (1,1), wx.EXPAND|wx.ADJUST_MINSIZE, 0)
            
            ix =0
            iy +=1 
            self.sizer8.Add((20,20),(iy,ix),(1,1), wx.LEFT|wx.EXPAND|wx.ADJUST_MINSIZE, 15)        
            self.vbox.Layout()
            self.SetScrollbars(20,20,55,40)
            self.Layout()
            self.parent.GetSizer().Layout()  
           
        if type== "GaussianModel" :

            self.sizer8.Clear(True)
            disp = wx.StaticText(self, -1, 'Dispersion')
            self.sizer8.Add(disp,( iy, ix),(1,1),  wx.LEFT|wx.EXPAND|wx.ADJUST_MINSIZE, 15)
            ix += 1 
            values = wx.StaticText(self, -1, 'Values')
            self.sizer8.Add(values,( iy, ix),(1,1), wx.EXPAND|wx.ADJUST_MINSIZE, 0)
            ix +=2
            self.text2_3 = wx.StaticText(self, -1, 'Errors')
            self.sizer8.Add(self.text2_3,(iy, ix),(1,1),\
                            wx.EXPAND|wx.ADJUST_MINSIZE, 0)
            self.text2_3.Hide() 
           
            ix += 1 
            npts = wx.StaticText(self, -1, 'Npts')
            self.sizer8.Add(npts,( iy, ix),(1,1), wx.EXPAND|wx.ADJUST_MINSIZE, 0)
            ix += 1 
            nsigmas = wx.StaticText(self, -1, 'Nsigmas')
            self.sizer8.Add(nsigmas,( iy, ix),(1,1), wx.EXPAND|wx.ADJUST_MINSIZE, 0)
            
            disp_list.sort()
            #print disp_list,self.model.dispersion
            for item in self.model.dispersion.keys():
                name1=item+".width"
                name2=item+".npts"
                name3=item+".nsigmas"
                iy += 1
                for p in self.model.dispersion[item].keys():
                    #print "name 1 2 3", name1, name2, name3
                    if p=="width":
                        ix = 0
                        cb = wx.CheckBox(self, -1, name1, (10, 10))
                        if self.data !=None:
                            cb.SetValue(False)
                            wx.EVT_CHECKBOX(self, cb.GetId(), self.select_param)
                        else:
                            cb.Disable()
                        self.sizer8.Add( cb,( iy, ix),(1,1),  wx.LEFT|wx.EXPAND|wx.ADJUST_MINSIZE, 15)
                        ix = 1
                        value= self.model.getParam(name1)
                        ctl1 = wx.TextCtrl(self, -1, size=(_BOX_WIDTH,20), style=wx.TE_PROCESS_ENTER)
                        ctl1.SetValue(str (format_number(value)))
                        ctl1.Bind(wx.EVT_KILL_FOCUS, self._onparamEnter)
                        ctl1.Bind(wx.EVT_TEXT_ENTER,self._onparamEnter)
                        self.sizer8.Add(ctl1, (iy,ix),(1,1), wx.EXPAND)
                        
                        ix = 2
                        text2=wx.StaticText(self, -1, '+/-')
                        self.sizer8.Add(text2,(iy, ix),(1,1),\
                                        wx.EXPAND|wx.ADJUST_MINSIZE, 0) 
                        text2.Hide()  
                        ix = 3
                        ctl2 = wx.TextCtrl(self, -1, size=(_BOX_WIDTH,20), style=wx.TE_PROCESS_ENTER)
                        self.sizer8.Add(ctl2, (iy,ix),(1,1), wx.EXPAND|wx.ADJUST_MINSIZE, 0)
                        ctl2.Hide()
                        self.fittable_param.append([cb,ctl1,text2,ctl2])
                       
                        
                    elif p=="npts":
                            ix =4 
                            value= self.model.getParam(name2)
                            Tctl = wx.TextCtrl(self, -1, size=(_BOX_WIDTH/2,20), style=wx.TE_PROCESS_ENTER)
                            Tctl.SetValue(str (format_number(value)))
                            Tctl.Bind(wx.EVT_KILL_FOCUS, self._onparamEnter)
                            Tctl.Bind(wx.EVT_TEXT_ENTER,self._onparamEnter)
                            self.sizer8.Add(Tctl, (iy,ix),(1,1), wx.EXPAND|wx.ADJUST_MINSIZE, 0)
                            self.fixed_param.append([name2, Tctl])
                    elif p=="nsigmas":
                            ix =5 
                            value= self.model.getParam(name3)
                            Tctl = wx.TextCtrl(self, -1, size=(_BOX_WIDTH/2,20), style=wx.TE_PROCESS_ENTER)
                            Tctl.SetValue(str (format_number(value)))
                            Tctl.Bind(wx.EVT_KILL_FOCUS, self._onparamEnter)
                            Tctl.Bind(wx.EVT_TEXT_ENTER,self._onparamEnter)
                            self.sizer8.Add(Tctl, (iy,ix),(1,1), wx.EXPAND|wx.ADJUST_MINSIZE, 0)
                            self.fixed_param.append([name3, Tctl])
                wx.PostEvent(self.parent.parent, StatusEvent(status=\
                            " Selected Distribution: Gaussian"))   
            ix =0
            iy +=1 
            self.sizer8.Add((20,20),(iy,ix),(1,1), wx.LEFT|wx.EXPAND|wx.ADJUST_MINSIZE, 15)        
            self.vbox.Layout()
            self.SetScrollbars(20,20,55,40)
            self.Layout()
            self.parent.GetSizer().Layout()  
          
          
    def checkFitValues(self,val_min, val_max):
        """
            Check the validity of input values
        """
        flag = True
        min_value = val_min.GetValue()
        max_value = val_max.GetValue()
        # Check for possible values entered
        if min_value.lstrip().rstrip() =="-inf":
            min_value= -numpy.inf
        if max_value.lstrip().rstrip() =="+inf":
            max_value= numpy.inf
        if  min_value==-numpy.inf and max_value== numpy.inf:
            val_min.SetBackgroundColour(wx.WHITE)
            val_min.Refresh()
            val_max.SetBackgroundColour(wx.WHITE)
            val_max.Refresh()
            return flag
        elif max_value== numpy.inf:
            try:
                float(min_value)
                val_min.SetBackgroundColour(wx.WHITE)
                val_min.Refresh()
            except:
                flag = False
                val_min.SetBackgroundColour("pink")
                val_min.Refresh()
            return flag
        elif min_value==-numpy.inf:
            try:
                float(max_value)
                val_max.SetBackgroundColour(wx.WHITE)
                val_max.Refresh()
            except:
                flag = False
                val_max.SetBackgroundColour("pink")
                val_max.Refresh()
            return flag
        else:    
            if (float(min_value)< float(max_value)):
                val_min.SetBackgroundColour(wx.WHITE)
                val_min.Refresh()
            else:
                flag = False
                val_min.SetBackgroundColour("pink")
                val_min.Refresh()
            return flag   
           
        
    def _onparamEnter(self,event):
        """ 
            when enter value on panel redraw model according to changed
        """
        self.set_model_parameter()
        
        
        
    def set_model_parameter(self):
        """
            Value Enter by the user on the parameter fields are used to reset the model
            and model will be drawn again if the user enters different values
        """
        if len(self.parameters) !=0 and self.model !=None:
            # Flag to register when a parameter has changed.
            is_modified = False
            for item in self.fittable_param:
                try:
                     name=str(item[0].GetLabelText())
                     value= float(item[1].GetValue())
                     # If the value of the parameter has changed,
                     # update the model and set the is_modified flag
                     if value != self.model.getParam(name):
                         self.model.setParam(name,value)
                         is_modified = True
                         
                except:
                    wx.PostEvent(self.parent.parent, StatusEvent(status=\
                            "Model Drawing  Error:wrong value entered : %s"% sys.exc_value))
                    return 
                
                
            for item in self.fixed_param:
                try:
                     name=str(item[0])
                     value= float(item[1].GetValue())
                     # If the value of the parameter has changed,
                     # update the model and set the is_modified flag
                     if value != self.model.getParam(name):
                         self.model.setParam(name,value)
                         is_modified = True
                         
                except:
                    wx.PostEvent(self.parent.parent, StatusEvent(status=\
                            "Model Drawing Error:wrong value entered : %s"% sys.exc_value))
                
            for item in self.parameters:
                try:
                     name=str(item[0].GetLabelText())
                     value= float(item[1].GetValue())
                     # If the value of the parameter has changed,
                     # update the model and set the is_modified flag
                     if value != self.model.getParam(name):
                         self.model.setParam(name,value)
                         is_modified = True
                   
                except:
                    #raise 
                    wx.PostEvent(self.parent.parent, StatusEvent(status=\
                           "Model Drawing Error:wrong value entered : %s"% sys.exc_value))
                    return
                
                
            # Here we should check whether the boundaries have been modified.
            # If qmin and qmax have been modified, update qmin and qmax and 
            # set the is_modified flag to True
            if float(self.qmin.GetValue()) != self.qmin_x:
                self.qmin_x = float(self.qmin.GetValue())
                is_modified = True
            if float(self.qmax.GetValue()) != self.qmax_x:
                self.qmax_x = float(self.qmax.GetValue())
                is_modified = True
            
            if float(self.npts.GetValue()) !=  self.num_points:
                self.num_points = float(self.npts.GetValue())
                is_modified = True
          
            if is_modified:
                self._draw_model()            
            
            
    def _draw_model(self, name=None):
        """
            Method to draw or refresh a plotted model.
            The method will use the data member from the model page
            to build a call to the fitting perspective manager.
            
            [Note to coder: This way future changes will be done in only one place.] 
        """
        if name==None:
            name= self.model.name
       
        self.manager.draw_model(self.model, name, data=self.data,
                                qmin=self.qmin_x, qmax=self.qmax_x,
                                qstep= self.num_points,
                                enable2D=self.enable2D)
       
       
    def select_param(self,event):
        """
            Select_parameter is implemented in fitpage.py 
        """
        pass
    
    
    def select_all_param(self,event): 
        """
            Implemented in fitpage.py
        """
        pass
    
    
    def select_all_param_helper(self):
        """
             Allows selecting or unselecting  checkbutton
        """
        self.param_toFit=[]
        if  self.parameters !=[]:
            if  self.cb1.GetValue()==True:
                for item in self.parameters:
                    item[0].SetValue(True)
                    list= [item[0],item[1],item[2],item[3]]
                    self.param_toFit.append(list )
                if len(self.fittable_param)>0:
                    for item in self.fittable_param:
                        item[0].SetValue(True)
                        list= [item[0],item[1],item[2],item[3]]
                        self.param_toFit.append(list )
            else:
                for item in self.parameters:
                    item[0].SetValue(False)
                for item in self.fittable_param:
                    item[0].SetValue(False)
                self.param_toFit=[]
               
                
       