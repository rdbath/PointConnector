# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PointConnector
                                 A QGIS plugin
 Creating lines between points following a from-to list.
                              -------------------
        begin                : 2014-07-15
        git sha              : $Format:%H$
        copyright            : (C) 2014 by Peter Ahlstrom
        email                : ahlstrom (dot) peter (at) gmail (dot) com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
# Initialize Qt resources from file resources.py
import resources_rc
# Import the code for the dialog
from point_connector_dialog import PointConnectorDialog
import os.path
import processing
from qgis.utils import *
import time



class PointConnector:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'PointConnector_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = PointConnectorDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Point Connector')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'PointConnector')
        self.toolbar.setObjectName(u'PointConnector')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('PointConnector', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the InaSAFE toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    # def initGui(self):
    #     """Create the menu entries and toolbar icons inside the QGIS GUI."""

    #     icon_path = ':/plugins/PointConnector/icon.png'
    #     self.add_action(
    #         icon_path,
    #         text=self.tr(u'Connect points according to list.'),
    #         callback=self.run,
    #         parent=self.iface.mainWindow())


    # def unload(self):
    #     """Removes the plugin menu item and icon from QGIS GUI."""
    #     for action in self.actions:
    #         self.iface.removePluginMenu(
    #             self.tr(u'&Point Connector'),
    #             action)
    #         self.iface.removeToolBarIcon(action)

    def initGui(self):
      self.action = QAction(QIcon(":/plugins/pointconnector/icon.png"), "PointConnector", self.iface.mainWindow())
      self.action.setWhatsThis("Connect points")
      self.action.setStatusTip("Connect points following a from-to list")

      QObject.connect(self.action, SIGNAL("triggered()"), self.run)

      #if hasattr( self.iface, "addPluginToVectorMenu" ):
      self.iface.addVectorToolBarIcon(self.action)
      self.iface.addPluginToVectorMenu("&PointConnector", self.action)
      #else:
      self.iface.addToolBarIcon(self.action)
      self.iface.addPluginToMenu("&PointConnector", self.action)

      # icon_path = ':/plugins/pointconnector/icon.png'
      # self.add_action(
      #     icon_path,
      #     text=self.tr(u'Connect points according to list.'),
      #     callback=self.run,
      #     parent=self.iface.mainWindow())

    def unload(self):
      if hasattr( self.iface, "addPluginToVectorMenu" ):
        self.iface.removePluginVectorMenu("&PointConnector",self.action)
        self.iface.removeVectorToolBarIcon(self.action)
      else:
        self.iface.removePluginMenu("&PointConnector",self.action)
        self.iface.removeToolBarIcon(self.action)


    def run(self):
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result == 1:
            csvPath = self.dlg.csvFileName
            pointPath = self.dlg.pointFileName 
            point_layer = QgsVectorLayer(pointPath, 'points', 'ogr') #shp-file with attribute field name
            lines_layer = QgsVectorLayer('LineString', 'lines', 'memory') 
            point_name_index = 0
            pr = lines_layer.dataProvider()

            lines_layer.startEditing()
            pr.addAttributes ([ QgsField('id', QVariant.Int), QgsField('from', QVariant.String), QgsField('to', QVariant.String)] )

            #creating point coordinate dict
            points = processing.features(point_layer)
            points_dict = {}
            
            #Progress bar widget 
            progressMessageBar = iface.messageBar().createMessage("Building point database...")
            progress = QProgressBar()
            progress.setMaximum(len(points))
            progress.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
            progressMessageBar.layout().addWidget(progress)
            iface.messageBar().pushWidget(progressMessageBar, iface.messageBar().INFO)

            i = 0
            for p in points:
                geom = p.geometry()
                attrs = p.attributes()
                p = geom.asPoint()
                time.sleep(0.01)
                points_dict[attrs[point_name_index]] = p #attrs[point_name_index] = name field
                i += 1
                progress.setValue(i)
            iface.messageBar().clearWidgets()
            QgsMapLayerRegistry().instance().addMapLayer(point_layer)
            print len(points_dict)
            print 'dict'

            #creating lines list from file
            lines_list = []
            f = open(csvPath, 'r')
            for line in f:
              line = line.split('\n')
              for s in line[:1]:
                s = tuple(s.split(','))
                lines_list.append(s)
            f.close()
            print 'list done'
            print lines_list

            #Progress bar widget
            progressMessageBar = iface.messageBar().createMessage("Drawing lines...")
            progress = QProgressBar()
            progress.setMaximum(len(lines_list))
            progress.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
            progressMessageBar.layout().addWidget(progress)
            iface.messageBar().pushWidget(progressMessageBar, iface.messageBar().INFO)

            #Drawing the lines
            i = 1
            not_processed_list = []
            
            for line in lines_list:
              if (line[0] in points_dict.keys() and line[1] in points_dict.keys()):
                frPoint = points_dict[line[0]]
                toPoint = points_dict[line[1]]
                attrs = [i, line[0], line[1]]
                new_line = QgsGeometry.fromPolyline([QgsPoint(frPoint), QgsPoint(toPoint)])
                feat = QgsFeature()
                feat.setGeometry(new_line)
                feat.setAttributes(attrs)
                (res, outFeats) = pr.addFeatures([feat])
                lines_layer.commitChanges()
                if res != True:
                    pass
                i += 1
                progress.setValue(i)
              else:
                not_processed_list.append(line)
            
                
            iface.messageBar().clearWidgets()

            # add lines layer to canvas
            QgsMapLayerRegistry().instance().addMapLayer(lines_layer)
            
            if not not_processed_list:
                QMessageBox.information(None, 'Success', 'All lines drawn without error')
            else:     
                error_list = []
                for line in not_processed_list:
                    output_line = line[0], 'to', line[1]
                    error_list.append(str(output_line))                    
                QMessageBox.information(None, 'Error', str(len(not_processed_list))+' out of '+str(len(lines_list))+' line(s) not drawn.')