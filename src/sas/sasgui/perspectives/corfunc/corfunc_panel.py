import wx
import sys
import numpy as np
from wx.lib.scrolledpanel import ScrolledPanel
from sas.sasgui.guiframe.events import PlotQrangeEvent
from sas.sasgui.guiframe.events import StatusEvent
from sas.sasgui.guiframe.panel_base import PanelBase
from sas.sasgui.guiframe.utils import check_float
from sas.sasgui.guiframe.dataFitting import Data1D
from sas.sasgui.perspectives.invariant.invariant_widgets import OutputTextCtrl
from sas.sasgui.perspectives.invariant.invariant_widgets import InvTextCtrl
from sas.sasgui.perspectives.fitting.basepage import ModelTextCtrl
from sas.sasgui.perspectives.corfunc.corfunc_state import CorfuncState
import sas.sasgui.perspectives.corfunc.corfunc
from sas.sascalc.corfunc.corfunc_calculator import CorfuncCalculator
from sas.sasgui.guiframe.documentation_window import DocumentationWindow
from plot_labels import *

OUTPUT_STRINGS = {
    'max': "Long Period (A): ",
    'Lc': "Average Hard Block Thickness (A): ",
    'dtr': "Average Interface Thickness (A): ",
    'd0': "Average Core Thickness: ",
    'A': "Polydispersity: ",
    'fill': "Local Crystallinity: "
}

if sys.platform.count("win32") > 0:
    _STATICBOX_WIDTH = 350
    PANEL_WIDTH = 400
    PANEL_HEIGHT = 700
    FONT_VARIANT = 0
else:
    _STATICBOX_WIDTH = 390
    PANEL_WIDTH = 430
    PANEL_HEIGHT = 700
    FONT_VARIANT = 1

class CorfuncPanel(ScrolledPanel,PanelBase):
    window_name = "Correlation Function"
    window_caption = "Correlation Function"
    CENTER_PANE = True

    def __init__(self, parent, data=None, manager=None, *args, **kwds):
        kwds["size"] = (PANEL_WIDTH, PANEL_HEIGHT)
        kwds["style"] = wx.FULL_REPAINT_ON_RESIZE
        ScrolledPanel.__init__(self, parent=parent, *args, **kwds)
        PanelBase.__init__(self, parent)
        self.SetupScrolling()
        self.SetWindowVariant(variant=FONT_VARIANT)
        self._manager = manager
        # The data with no correction for background values
        self._data = data # The data to be analysed (corrected fr background)
        self._extrapolated_data = None # The extrapolated data set
        self._transformed_data = None # Fourier trans. of the extrapolated data
        self._calculator = CorfuncCalculator()
        self._data_name_box = None # Text box to show name of file
        self._background_input = None
        self._qmin_input = None
        self._qmax1_input = None
        self._qmax2_input = None
        self._transform_btn = None
        self._extract_btn = None
        self.qmin = 0
        self.qmax = (0, 0)
        self.background = 0
        self.extracted_params = None
        self.transform_type = 'fourier'
        # Dictionary for saving refs to text boxes used to display output data
        self._output_boxes = None
        self.state = None
        self._do_layout()
        self._disable_inputs()
        self.set_state()
        self._qmin_input.Bind(wx.EVT_TEXT, self._on_enter_input)
        self._qmax1_input.Bind(wx.EVT_TEXT, self._on_enter_input)
        self._qmax2_input.Bind(wx.EVT_TEXT, self._on_enter_input)
        self._qmin_input.Bind(wx.EVT_MOUSE_EVENTS, self._on_click_qrange)
        self._qmax1_input.Bind(wx.EVT_MOUSE_EVENTS, self._on_click_qrange)
        self._qmax2_input.Bind(wx.EVT_MOUSE_EVENTS, self._on_click_qrange)
        self._background_input.Bind(wx.EVT_TEXT, self._on_enter_input)

    def set_state(self, state=None, data=None):
        """
        Set the state of the panel. If no state is provided, the panel will
        be set to the default state.

        :param state: A CorfuncState object
        :param data: A Data1D object
        """
        if state is None:
            self.state = CorfuncState()
        else:
            self.state = state
        if data is not None:
            self.state.data = data
        self.set_data(data, set_qrange=False)
        if self.state.qmin is not None:
            self.set_qmin(self.state.qmin)
        if self.state.qmax is not None and self.state.qmax != (None, None):
            self.set_qmax(tuple(self.state.qmax))
        if self.state.background is not None:
            self.set_background(self.state.background)
        if self.state.is_extrapolated:
            self.compute_extrapolation()
        else:
            return
        if self.state.is_transformed:
            self.compute_transform()
        else:
            return
        if self.state.outputs is not None and self.state.outputs != {}:
            self.set_extracted_params(self.state.outputs, reset=True)

    def get_state(self):
        """
        Return the state of the panel
        """
        state = CorfuncState()
        state.set_saved_state('qmin_tcl', self.qmin)
        state.set_saved_state('qmax1_tcl', self.qmax[0])
        state.set_saved_state('qmax2_tcl', self.qmax[1])
        state.set_saved_state('background_tcl', self.background)
        state.outputs = self.extracted_params
        if self._data is not None:
            state.file = self._data.title
            state.data = self._data
        if self._extrapolated_data is not None:
            state.is_extrapolated = True
        if self._transformed_data is not None:
            state.is_transformed = True
        self.state = state

        return self.state

    def onSetFocus(self, evt):
        if evt is not None:
            evt.Skip()
        self._validate_inputs()

    def set_data(self, data=None, set_qrange=True):
        """
        Update the GUI to reflect new data that has been loaded in

        :param data: The data that has been loaded
        """
        if data is None:
            return
        self._enable_inputs()
        self._transform_btn.Disable()
        self._extract_btn.Disable()
        self._data_name_box.SetValue(str(data.title))
        self._data = data
        self._calculator.set_data(data)
        # Reset the outputs
        self.set_extracted_params(None, reset=True)
        if self._manager is not None:
            self._manager.clear_data()
            self._manager.show_data(self._data, IQ_DATA_LABEL, reset=True)

        if set_qrange:
            lower = data.x[-1]*0.05
            upper1 = data.x[-1] - lower*5
            upper2 = data.x[-1]
            self.set_qmin(lower)
            self.set_qmax((upper1, upper2))
            self.set_background(self._calculator.compute_background(self.qmax))

    def get_data(self):
        return self._data

    def radio_changed(self, event=None):
        if event is not None:
            self.transform_type = event.GetEventObject().GetName()

    def compute_extrapolation(self, event=None):
        """
        Compute and plot the extrapolated data.
        Called when Extrapolate button is pressed.
        """
        if not self._validate_inputs:
            msg = "Invalid Q range entered."
            wx.PostEvent(self.parent.parent, StatusEvent(status=msg))
            return
        self._calculator.set_data(self._data)
        self._calculator.lowerq = self.qmin
        self._calculator.upperq = self.qmax
        self._calculator.background = self.background
        try:
            self._extrapolated_data = self._calculator.compute_extrapolation()
        except:
            msg = "Error extrapolating data."
            wx.PostEvent(self._manager.parent,
                StatusEvent(status=msg, info="Error"))
            self._transform_btn.Disable()
            return
        # TODO: Find way to set xlim and ylim so full range of data can be
        # plotted but zoomed in
        maxq = self._data.x.max()
        mask = self._extrapolated_data.x <= maxq
        numpts = len(self._extrapolated_data.x[mask]) + 250
        plot_x = self._extrapolated_data.x[0:numpts]
        plot_y = self._extrapolated_data.y[0:numpts]
        to_plot = Data1D(plot_x, plot_y)
        self._manager.show_data(to_plot, IQ_EXTRAPOLATED_DATA_LABEL)
        # Update state of the GUI
        self._transform_btn.Enable()
        self._extract_btn.Disable()
        self.set_extracted_params(reset=True)

    def compute_transform(self, event=None):
        """
        Compute and plot the transformed data.
        Called when Transform button is pressed.
        """
        if not self._calculator.transform_isrunning():
            self._calculator.compute_transform(self._extrapolated_data,
                self.transform_type, background=self.background,
                completefn=self.transform_complete,
                updatefn=self.transform_update)

            self._transform_btn.SetLabel("Stop Tansform")
        else:
            self._calculator.stop_transform()
            self.transform_update("Transform cancelled.")
            self._transform_btn.SetLabel("Tansform")

    def transform_update(self, msg=""):
        """
        Called from FourierThread to update on status of calculation
        """
        wx.PostEvent(self._manager.parent,
            StatusEvent(status=msg))

    def transform_complete(self, transform=None):
        """
        Called from FourierThread when calculation has completed
        """
        self._transform_btn.SetLabel("Tansform")
        if transform is None:
            msg = "Error calculating Transform."
            if self.transform_type == 'hilbert':
                msg = "Not yet implemented"
            wx.PostEvent(self._manager.parent,
                StatusEvent(status=msg, info="Error"))
            self._extract_btn.Disable()
            return
        self._transformed_data = transform
        import numpy as np
        plot_x = transform.x[np.where(transform.x <= 200)]
        plot_y = transform.y[np.where(transform.x <= 200)]
        self._manager.show_data(Data1D(plot_x, plot_y), TRANSFORM_LABEL)
        # Only enable extract params button if a fourier trans. has been done
        if self.transform_type == 'fourier':
            self._extract_btn.Enable()
        else:
            self._extract_btn.Disable()

    def extract_parameters(self, event=None):
        try:
            params = self._calculator.extract_parameters(self._transformed_data)
        except:
            params = None
        if params is None:
            msg = "Error extracting parameters."
            wx.PostEvent(self._manager.parent,
                StatusEvent(status=msg, info="Error"))
            return
        self.set_extracted_params(params)

    def on_help(self, event=None):
        """
        Show the corfunc documentation
        """
        tree_location = "user/sasgui/perspectives/corfunc/corfunc_help.html"
        doc_viewer = DocumentationWindow(self, -1, tree_location, "",
                                          "Correlation Function Help")

    def save_project(self, doc=None):
        """
        Return an XML node containing the state of the panel

        :param doc: Am xml node to attach the project state to (optional)
        """
        data = self._data
        state = self.get_state()
        if data is not None:
            new_doc, sasentry = self._manager.state_reader._to_xml_doc(data)
            new_doc = state.toXML(doc=new_doc, entry_node=sasentry)
            if new_doc is not None:
                if doc is not None and hasattr(doc, "firstChild"):
                    child = new_doc.getElementsByTagName("SASentry")
                    for item in child:
                        doc.firstChild.appendChild(item)
                else:
                    doc = new_doc
        return doc

    def set_qmin(self, qmin):
        self.qmin = qmin
        self._qmin_input.SetValue(str(qmin))

    def set_qmax(self, qmax):
        self.qmax = qmax
        self._qmax1_input.SetValue(str(qmax[0]))
        self._qmax2_input.SetValue(str(qmax[1]))

    def set_background(self, bg):
        self.background = bg
        self._background_input.SetValue(str(bg))
        self._calculator.background = bg

    def set_extracted_params(self, params=None, reset=False):
        self.extracted_params = params
        error = False
        if params is None:
            if not reset: error = True
            for key in OUTPUT_STRINGS.keys():
                self._output_boxes[key].SetValue('-')
        else:
            if len(params) < len(OUTPUT_STRINGS):
                # Not all parameters were calculated
                error = True
            for key, value in params.iteritems():
                rounded = self._round_sig_figs(value, 6)
                self._output_boxes[key].SetValue(rounded)
        if error:
            msg = 'Not all parameters were able to be calculated'
            wx.PostEvent(self._manager.parent, StatusEvent(
                status=msg, info='error'))


    def plot_qrange(self, active=None, leftdown=False):
        if active is None:
            active = self._qmin_input
        wx.PostEvent(self._manager.parent, PlotQrangeEvent(
            ctrl=[self._qmin_input, self._qmax1_input, self._qmax2_input],
            active=active, id=IQ_DATA_LABEL, is_corfunc=True,
            group_id=GROUP_ID_IQ_DATA, leftdown=leftdown))


    def _compute_background(self, event=None):
        self.set_background(self._calculator.compute_background(self.qmax))

    def _on_enter_input(self, event=None):
        """
        Read values from input boxes and save to memory.
        """
        if event is not None: event.Skip()
        if not self._validate_inputs():
            return
        self.qmin = float(self._qmin_input.GetValue())
        new_qmax1 = float(self._qmax1_input.GetValue())
        new_qmax2 = float(self._qmax2_input.GetValue())
        self.qmax = (new_qmax1, new_qmax2)
        self.background = float(self._background_input.GetValue())
        self._calculator.background = self.background
        if event is not None:
            active_ctrl = event.GetEventObject()
            if active_ctrl == self._background_input:
                self._manager.show_data(self._data, IQ_DATA_LABEL,
                    reset=False, active_ctrl=active_ctrl)

    def _on_click_qrange(self, event=None):
        if event is None:
            return
        event.Skip()
        if not self._validate_inputs(): return
        self.plot_qrange(active=event.GetEventObject(),
            leftdown=event.LeftDown())

    def _validate_inputs(self):
        """
        Check that the values for qmin and qmax in the input boxes are valid
        """
        if self._data is None:
            return False
        qmin_valid = check_float(self._qmin_input)
        qmax1_valid = check_float(self._qmax1_input)
        qmax2_valid = check_float(self._qmax2_input)
        qmax_valid = qmax1_valid and qmax2_valid
        background_valid = check_float(self._background_input)
        msg = ""
        if (qmin_valid and qmax_valid and background_valid):
            qmin = float(self._qmin_input.GetValue())
            qmax1 = float(self._qmax1_input.GetValue())
            qmax2 = float(self._qmax2_input.GetValue())
            background = float(self._background_input.GetValue())
            if not qmin > self._data.x.min():
                msg = "qmin must be greater than the lowest q value"
                qmin_valid = False
            elif qmax2 < qmax1:
                msg = "qmax1 must be less than qmax2"
                qmax_valid = False
            elif qmin > qmax1:
                msg = "qmin must be less than qmax"
                qmin_valid = False
            elif background > self._data.y.max():
                msg = "background must be less than highest I"
                background_valid = False
        if not qmin_valid:
            self._qmin_input.SetBackgroundColour('pink')
        if not qmax_valid:
            self._qmax1_input.SetBackgroundColour('pink')
            self._qmax2_input.SetBackgroundColour('pink')
        if not background_valid:
            self._background_input.SetBackgroundColour('pink')
            if msg != "":
                wx.PostEvent(self._manager.parent, StatusEvent(status=msg))
        if (qmin_valid and qmax_valid and background_valid):
            self._qmin_input.SetBackgroundColour(wx.WHITE)
            self._qmax1_input.SetBackgroundColour(wx.WHITE)
            self._qmax2_input.SetBackgroundColour(wx.WHITE)
            self._background_input.SetBackgroundColour(wx.WHITE)
        self._qmin_input.Refresh()
        self._qmax1_input.Refresh()
        self._qmax2_input.Refresh()
        self._background_input.Refresh()
        return (qmin_valid and qmax_valid and background_valid)

    def _do_layout(self):
        """
        Draw the window content
        """
        vbox = wx.GridBagSizer(0,0)

        # I(q) data box
        databox = wx.StaticBox(self, -1, "I(Q) Data Source")
        databox_sizer = wx.StaticBoxSizer(databox, wx.VERTICAL)

        file_sizer = wx.GridBagSizer(5, 5)

        file_name_label = wx.StaticText(self, -1, "Name:")
        file_sizer.Add(file_name_label, (0, 0), (1, 1),
            wx.LEFT | wx.EXPAND | wx.ADJUST_MINSIZE, 15)

        self._data_name_box = OutputTextCtrl(self, -1,
            size=(300,20))
        file_sizer.Add(self._data_name_box, (0, 1), (1, 1),
            wx.CENTER | wx.ADJUST_MINSIZE, 15)

        file_sizer.AddSpacer((1, 25), pos=(0,2))
        databox_sizer.Add(file_sizer, wx.TOP, 15)

        vbox.Add(databox_sizer, (0, 0), (1, 1),
            wx.LEFT | wx.RIGHT | wx.EXPAND | wx.ADJUST_MINSIZE | wx.TOP, 15)


        # Parameters
        qbox = wx.StaticBox(self, -1, "Input Parameters")
        qbox_sizer = wx.StaticBoxSizer(qbox, wx.VERTICAL)
        qbox_sizer.SetMinSize((_STATICBOX_WIDTH, 75))

        q_sizer = wx.GridBagSizer(5, 5)

        # Explanation
        explanation_txt = ("Corfunc will use all values in the lower range for"
            " Guinier back extrapolation, and all values in the upper range "
            "for Porod forward extrapolation.")
        explanation_label = wx.StaticText(self, -1, explanation_txt,
            size=(_STATICBOX_WIDTH, 60))

        q_sizer.Add(explanation_label, (0,0), (1,4), wx.LEFT | wx.EXPAND, 5)

        qrange_label = wx.StaticText(self, -1, "Q Range:", size=(50,20))
        q_sizer.Add(qrange_label, (1,0), (1,1), wx.LEFT | wx.EXPAND, 5)

        # Lower Q Range
        qmin_label = wx.StaticText(self, -1, "Lower:", size=(50,20))
        qmin_dash_label = wx.StaticText(self, -1, "-", size=(10,20),
            style=wx.ALIGN_CENTER_HORIZONTAL)

        qmin_lower = OutputTextCtrl(self, -1, size=(75, 20), value="0.0")
        self._qmin_input = ModelTextCtrl(self, -1, size=(75, 20),
                        style=wx.TE_PROCESS_ENTER, name='qmin_input',
                        text_enter_callback=self._on_enter_input)
        self._qmin_input.SetToolTipString(("Values with q < qmin will be used "
            "for Guinier back extrapolation"))

        q_sizer.Add(qmin_label, (2, 0), (1, 1), wx.LEFT | wx.EXPAND, 5)
        q_sizer.Add(qmin_lower, (2, 1), (1, 1), wx.LEFT, 5)
        q_sizer.Add(qmin_dash_label, (2, 2), (1, 1), wx.CENTER | wx.EXPAND, 5)
        q_sizer.Add(self._qmin_input, (2, 3), (1, 1), wx.LEFT, 5)

        # Upper Q range
        qmax_tooltip = ("Values with qmax1 < q < qmax2 will be used for Porod"
            " forward extrapolation")

        qmax_label = wx.StaticText(self, -1, "Upper:", size=(50,20))
        qmax_dash_label = wx.StaticText(self, -1, "-", size=(10,20),
            style=wx.ALIGN_CENTER_HORIZONTAL)

        self._qmax1_input = ModelTextCtrl(self, -1, size=(75, 20),
            style=wx.TE_PROCESS_ENTER, name="qmax1_input",
            text_enter_callback=self._on_enter_input)
        self._qmax1_input.SetToolTipString(qmax_tooltip)
        self._qmax2_input = ModelTextCtrl(self, -1, size=(75, 20),
            style=wx.TE_PROCESS_ENTER, name="qmax2_input",
            text_enter_callback=self._on_enter_input)
        self._qmax2_input.SetToolTipString(qmax_tooltip)

        q_sizer.Add(qmax_label, (3, 0), (1, 1), wx.LEFT | wx.EXPAND, 5)
        q_sizer.Add(self._qmax1_input, (3, 1), (1, 1), wx.LEFT, 5)
        q_sizer.Add(qmax_dash_label, (3, 2), (1, 1), wx.CENTER | wx.EXPAND, 5)
        q_sizer.Add(self._qmax2_input, (3,3), (1, 1), wx.LEFT, 5)

        background_label = wx.StaticText(self, -1, "Background:", size=(80,20))
        q_sizer.Add(background_label, (4,0), (1,1), wx.LEFT | wx.EXPAND, 5)

        self._background_input = ModelTextCtrl(self, -1, size=(75,20),
            style=wx.TE_PROCESS_ENTER, name='background_input',
            text_enter_callback=self._on_enter_input)
        self._background_input.SetToolTipString(("A background value to "
            "subtract from all intensity values"))
        q_sizer.Add(self._background_input, (4,1), (1,1),
            wx.RIGHT, 5)

        background_button = wx.Button(self, wx.NewId(), "Calculate",
            size=(75, 20))
        background_button.Bind(wx.EVT_BUTTON, self._compute_background)
        q_sizer.Add(background_button, (4, 2), (1, 1), wx.RIGHT, 5)

        qbox_sizer.Add(q_sizer, wx.TOP, 0)

        vbox.Add(qbox_sizer, (1, 0), (1, 1),
            wx.LEFT | wx.RIGHT | wx.EXPAND | wx.ADJUST_MINSIZE, 15)

        # Transform type
        transform_box = wx.StaticBox(self, -1, "Transform Type")
        transform_sizer = wx.StaticBoxSizer(transform_box, wx.VERTICAL)

        radio_sizer = wx.GridBagSizer(5,5)

        fourier_btn = wx.RadioButton(self, -1, "Fourier", name='fourier',
            style=wx.RB_GROUP)
        hilbert_btn = wx.RadioButton(self, -1, "Hilbert", name='hilbert')

        fourier_btn.Bind(wx.EVT_RADIOBUTTON, self.radio_changed)
        hilbert_btn.Bind(wx.EVT_RADIOBUTTON, self.radio_changed)

        radio_sizer.Add(fourier_btn, (0,0), (1,1), wx.LEFT | wx.EXPAND)
        radio_sizer.Add(hilbert_btn, (0,1), (1,1), wx.RIGHT | wx.EXPAND)

        transform_sizer.Add(radio_sizer, wx.TOP, 0)
        vbox.Add(transform_sizer, (2, 0), (1, 1),
            wx.LEFT | wx.RIGHT | wx.EXPAND | wx.ADJUST_MINSIZE, 15)

        # Output data
        outputbox = wx.StaticBox(self, -1, "Output Parameters")
        outputbox_sizer = wx.StaticBoxSizer(outputbox, wx.VERTICAL)

        output_sizer = wx.GridBagSizer(5, 5)

        self._output_boxes = dict()
        i = 0
        for key, value in OUTPUT_STRINGS.iteritems():
            # Create a label and a text box for each poperty
            label = wx.StaticText(self, -1, value)
            output_box = OutputTextCtrl(self, wx.NewId(),
                value="-", style=wx.ALIGN_CENTER_HORIZONTAL)
            # Save the ID of each of the text boxes for accessing after the
            # output data has been calculated
            self._output_boxes[key] = output_box
            output_sizer.Add(label, (i, 0), (1, 1), wx.LEFT | wx.EXPAND, 15)
            output_sizer.Add(output_box, (i, 2), (1, 1),
                wx.RIGHT | wx.EXPAND, 15)
            i += 1

        outputbox_sizer.Add(output_sizer, wx.TOP, 0)

        vbox.Add(outputbox_sizer, (3, 0), (1, 1),
            wx.LEFT | wx.RIGHT | wx.EXPAND | wx.ADJUST_MINSIZE, 15)

        # Controls
        controlbox = wx.StaticBox(self, -1, "Controls")
        controlbox_sizer = wx.StaticBoxSizer(controlbox, wx.VERTICAL)

        controls_sizer = wx.BoxSizer(wx.VERTICAL)

        extrapolate_btn = wx.Button(self, wx.NewId(), "Extrapolate")
        self._transform_btn = wx.Button(self, wx.NewId(), "Transform")
        self._extract_btn = wx.Button(self, wx.NewId(), "Compute Parameters")
        help_btn = wx.Button(self, -1, "HELP")

        self._transform_btn.Disable()
        self._extract_btn.Disable()

        extrapolate_btn.Bind(wx.EVT_BUTTON, self.compute_extrapolation)
        self._transform_btn.Bind(wx.EVT_BUTTON, self.compute_transform)
        self._extract_btn.Bind(wx.EVT_BUTTON, self.extract_parameters)
        help_btn.Bind(wx.EVT_BUTTON, self.on_help)

        controls_sizer.Add(extrapolate_btn, wx.CENTER | wx.EXPAND)
        controls_sizer.Add(self._transform_btn, wx.CENTER | wx.EXPAND)
        controls_sizer.Add(self._extract_btn, wx.CENTER | wx.EXPAND)
        controls_sizer.Add(help_btn, wx.CENTER | wx.EXPAND)

        controlbox_sizer.Add(controls_sizer, wx.TOP | wx.EXPAND, 0)
        vbox.Add(controlbox_sizer, (4, 0), (1, 1),
            wx.LEFT | wx.RIGHT | wx.EXPAND | wx.ADJUST_MINSIZE, 15)


        self.SetSizer(vbox)

    def _disable_inputs(self):
        """
        Disable all input fields
        """
        self._qmin_input.Disable()
        self._qmax1_input.Disable()
        self._qmax2_input.Disable()
        self._background_input.Disable()

    def _enable_inputs(self):
        """
        Enable all input fields
        """
        self._qmin_input.Enable()
        self._qmax1_input.Enable()
        self._qmax2_input.Enable()
        self._background_input.Enable()

    def _round_sig_figs(self, x, sigfigs):
        """
        Round a number to a given number of significant figures.

        :param x: The value to round
        :param sigfigs: How many significant figures to round to
        :return rounded_str: x rounded to the given number of significant
            figures, as a string
        """
        # Index of first significant digit
        significant_digit = -int(np.floor(np.log10(np.abs(x))))
        # Number of digits required for correct number of sig figs
        digits = significant_digit + (sigfigs - 1)
        rounded = np.round(x, decimals=digits)
        rounded_str = "{1:.{0}f}".format(sigfigs -1  + significant_digit,
            rounded)
        return rounded_str
