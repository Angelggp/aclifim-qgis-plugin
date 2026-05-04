def classFactory(iface):
    from .main_plugin import ACLIFIMPlugin
    return ACLIFIMPlugin(iface)