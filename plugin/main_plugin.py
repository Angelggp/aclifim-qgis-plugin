import os

from qgis.PyQt.QtWidgets import QAction
from qgis.PyQt.QtGui import QIcon
from .ui.main_dialog import MainDialog
from .modules.layer_migration import check_and_migrate_if_needed


class ACLIFIMPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.action = None
        self.dialog = None
        self.migration_checked = False  # Flag para verificar migración solo una vez

    def initGui(self):
        icon_path = os.path.join(os.path.dirname(__file__), "resources", "aclifim_icon.svg")

        # Si existe icono, mostrar boton con imagen; si no, usar texto como respaldo.
        if os.path.exists(icon_path):
            self.action = QAction(QIcon(icon_path), "", self.iface.mainWindow())
        else:
            self.action = QAction("ACLIFIM", self.iface.mainWindow())

        self.action.setToolTip("ACLIFIM Plugin")
        self.action.setStatusTip("Abrir ACLIFIM Plugin")
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