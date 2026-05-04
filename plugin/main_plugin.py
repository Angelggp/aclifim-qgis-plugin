from qgis.PyQt.QtWidgets import QAction
from .ui.main_dialog import MainDialog
from .modules.layer_migration import check_and_migrate_if_needed


class ACLIFIMPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.action = None
        self.dialog = None
        self.migration_checked = False  # Flag para verificar migración solo una vez

    def initGui(self):
        self.action = QAction("ACLIFIM Plugin", self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)

    def unload(self):
        self.iface.removeToolBarIcon(self.action)

    def run(self):
        # Verificar si hay capas que necesitan migración (solo la primera vez)
        if not self.migration_checked:
            print("[PLUGIN] Verificando si hay capas para migrar...")
            check_and_migrate_if_needed(self.iface)
            self.migration_checked = True
        
        if not self.dialog:
            self.dialog = MainDialog(self.iface)

        self.dialog.show()