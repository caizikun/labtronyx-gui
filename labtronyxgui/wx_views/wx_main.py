import wx
import wx.gizmos

from labtronyx.common import events
from . import FrameViewBase

def main(controller):
    app = LabtronyxApp()
    view = MainView(controller)

    app.SetTopWindow(view)
    app.MainLoop()


class LabtronyxApp(wx.App):

    def OnInit(self):
        return True


class MainView(FrameViewBase):
    """
    Labtronyx Top-Level Window
    """

    def __init__(self, controller):
        super(MainView, self).__init__(None, controller,
            id=-1, title="Labtronyx", size=(640, 480), style=wx.DEFAULT_FRAME_STYLE)

        # self.sizer = wx.BoxSizer(wx.VERTICAL)
        # self.frame.SetSizer(self.sizer)

        # Build Menu
        self.buildMenubar()

        # Build Tree
        self.treePanel = wx.Panel(parent=self, id=wx.ID_ANY, style=wx.WANTS_CHARS)
        self.tree = wx.gizmos.TreeListCtrl(parent=self.treePanel, id=wx.ID_ANY,
                                pos=wx.DefaultPosition, size=wx.DefaultSize,
                                style=wx.TR_HAS_BUTTONS|wx.TR_HIDE_ROOT)
        self.buildTree()
        self.treePanel.Bind(wx.EVT_SIZE, self.e_OnSize)
        self.tree.GetMainWindow().Bind(wx.EVT_RIGHT_UP, self.e_OnRightClick)
        # self.tree.Bind(wx.EVT_KEY_UP, self.e_OnKeyEvent)

        # Event bindings
        self.Bind(wx.EVT_CLOSE, self.e_OnWindowClose)

        # self.tree.Expand(self.node_root)

        self.Show(True)

        self.SetSize((640, 480))
        # self.Fit()

        # Run updates
        wx.CallAfter(self.update_tree)

    def buildMenubar(self):
        self.menubar = wx.MenuBar()

        # File
        self.menu_file = wx.Menu()
        item = self.menu_file.Append(-1, "E&xit\tCtrl-Q", "Exit")
        self.Bind(wx.EVT_MENU, self.e_MenuExit, item)

        self.menubar.Append(self.menu_file, "&File")

        # Set frame menubar
        self.SetMenuBar(self.menubar)

    def buildTree(self):
        self.tree.AddColumn('')
        self.tree.AddColumn('Type')
        self.tree.AddColumn('Vendor')
        self.tree.AddColumn('Model')
        self.tree.AddColumn('Serial')
        self.tree.SetMainColumn(0)
        self.tree.SetColumnWidth(0, 175)
        self.node_root = self.tree.AddRoot("Labtronyx") # Add hidden root item
        self.tree.SetPyData(self.node_root, None)
        self.nodes_hosts = {}
        self.nodes_resources = {}

        # Build image list
        isz = (16, 16)
        self.il = wx.ImageList(*isz)
        self.art_host = self.il.Add(wx.ArtProvider_GetBitmap(wx.ART_REMOVABLE, wx.ART_OTHER, isz))

        self.tree.SetImageList(self.il)

    def update_tree(self):
        # Hosts
        for ip_address, host_controller in self._controller.hosts.items():
            # Add new hosts
            if ip_address not in self.nodes_hosts:
                hostname = self._controller.networkHostname(ip_address)

                child = self.tree.AppendItem(self.node_root, hostname)
                self.tree.SetPyData(child, ip_address)
                self.tree.SetItemImage(child, self.art_host)
                self.tree.Expand(child)

                self.nodes_hosts[ip_address] = child

            host_node = self.nodes_hosts.get(ip_address)

            # Resources
            for res_uuid, res_controller in host_controller.resources.items():
                # Add new resources
                if res_uuid not in self.nodes_resources:
                    res_prop = res_controller.properties

                    # Resource Name
                    node_name = res_prop.get('resourceID')

                    child = self.tree.AppendItem(host_node, node_name)
                    self.tree.SetPyData(child, res_uuid)
                    self.nodes_resources[res_uuid] = child

        self.update_tree_columns()

    def update_tree_columns(self):
        for res_uuid, res_node in self.nodes_resources.items():
            res_con = self.controller.get_resource(res_uuid)

            if res_con is not None:
                res_props = res_con.properties
                self.tree.SetItemText(res_node, res_props.get('deviceType', ''), 1)
                self.tree.SetItemText(res_node, res_props.get('deviceVendor', ''), 2)
                self.tree.SetItemText(res_node, res_props.get('deviceModel', ''), 3)
                self.tree.SetItemText(res_node, res_props.get('deviceSerial', ''), 4)

    # wx Events

    def e_OnRightClick(self, event):
        pos = event.GetPosition()
        item, flags, col = self.tree.HitTest(pos)

        if item:
            node_data = self.tree.GetPyData(item)

            if node_data in self.controller.hosts:
                # Host
                pass

            elif self.controller.get_resource(node_data) is not None:
                # Resource
                menu = wx.Menu()
                ctx_control = menu.Append(-1, "&Control", "Control")
                self.Bind(wx.EVT_MENU, lambda event: self.e_ResourceContextControl(event, node_data), ctx_control)
                menu.AppendSeparator()
                ctx_properties = menu.Append(-1, "&Properties", "Properties")
                self.Bind(wx.EVT_MENU, lambda event: self.e_ResourceContextProperties(event, node_data), ctx_properties)

                self.PopupMenu(menu, event.GetPosition())

    def e_ResourceContextControl(self, event, uuid):
        from .wx_resources import ResourceControlView

        # Get the resource controller
        res_controller = self.controller.get_resource(uuid)

        # Instantiate and show the window
        win = ResourceControlView(self, res_controller)
        win.Show()

    def e_ResourceContextProperties(self, event, uuid):
        from .wx_resources import ResourcePropertiesView

        # Get the resource controller
        res_controller = self.controller.get_resource(uuid)

        # Instantiate and show the window
        win = ResourcePropertiesView(self, res_controller)
        win.Show()

    def e_OnKeyEvent(self, event):
        keycode = event.GetKeyCode()
        pass

    def e_OnSize(self, event):
        w,h = self.GetClientSizeTuple()
        self.tree.SetDimensions(0, 0, w, h)

    def e_MenuExit(self, event):
        self.Close(True)

    def e_OnWindowClose(self, event):
        self.Destroy()

    # Controller Events

    def _handleEvent(self, event):
        if event.event == events.EventCodes.manager.heartbeat:
            self.handleEvent_heartbeat(event)

        elif event.event in [events.EventCodes.resource.created, events.EventCodes.resource.destroyed]:
            self.update_tree()

        elif event.event in [events.EventCodes.resource.changed, events.EventCodes.resource.driver_loaded,
                             events.EventCodes.resource.driver_unloaded]:
            self.update_tree_columns()

    def handleEvent_heartbeat(self, event):
        # dlg = wx.MessageDialog(self, 'Heartbeat', 'Heartbeat', wx.OK|wx.ICON_INFORMATION)
        # dlg.ShowModal()
        # dlg.Destroy()
        pass