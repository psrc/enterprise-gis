from arcgis import features
from arcgis import mapping
import arcpy
import sys
from pathlib import Path
from arcpy import metadata as md
import os, shutil 
import xml.dom.minidom as DOM
from arcgis import GIS


elmer_geo_conn_path = r'C:\Users\scoe\Documents\publish_elmer_geo\elmer_geo\elmer_geo_conn.sde'
aprx_path = r'C:\Users\scoe\Documents\publish_elmer_geo\elmer_geo\elmer_geo.aprx'
test_fc = r"ElmerGeo.DBO.tract10centroids2"
outdir = r'C:\Users\scoe\Documents\publish_elmer_geo\service_definitions'

skip_layers = ['ElmerGeo.DBO.bldg_footprints', 'ElmerGeo.DBO.hct_station_areas_dissolve']


def configure_featureserver_capabilities(sddraftPath, capabilities):
    """Function to configure FeatureServer properties"""
    # Read the .sddraft file
    doc = DOM.parse(sddraftPath)

    # Find all elements named TypeName
    # This is where the additional layers and capabilities are defined
    typeNames = doc.getElementsByTagName('TypeName')
    for typeName in typeNames:
        # Get the TypeName to enable
        if typeName.firstChild.data == "FeatureServer":
            extension = typeName.parentNode
            for extElement in extension.childNodes:
                if extElement.tagName == 'Info':
                    for propSet in extElement.childNodes:
                        for prop in propSet.childNodes:
                            for prop1 in prop.childNodes:
                                if prop1.tagName == "Key":
                                    if prop1.firstChild.data == 'WebCapabilities':
                                        if prop1.nextSibling.hasChildNodes():
                                            prop1.nextSibling.firstChild.data = capabilities
                                        else:
                                            txt = doc.createTextNode(capabilities)
                                            prop1.nextSibling.appendChild(txt)
    # Write to the .sddraft file
    f = open(sddraftPath, 'w')
    doc.writexml(f)
    f.close()
def configure_mapserver_capabilities(sddraftPath, capabilities):
    """Function to configure MapServer properties"""
    # Read the .sddraft file
    doc = DOM.parse(sddraftPath)
    key_list = doc.getElementsByTagName('Key')
    value_list = doc.getElementsByTagName('Value')

    
    # Change following to "true" to share
    #PackageUnderMyContent = "false"
    SharetoOrganization = "true"
    SharetoEveryone = "false"
    SharetoGroup = "true"
    # If SharetoGroup is set to "true", uncomment line below and provide group IDs
    #GroupID = "87b588984f8c4ffeae8b835be05c3866"    # GroupID = "f07fab920d71339cb7b1291e3059b7a8, e0fb8fff410b1d7bae1992700567f54a"
    GroupID = "9e2cde6f8318442ab14cd1f421abc46e"

    # Each key has a corresponding value. In all the cases value of key_list[i] is value_list[i]
    for i in range(key_list.length):
        # if key_list[i].firstChild.nodeValue == "PackageUnderMyContent":
        #     value_list[i].firstChild.nodeValue = PackageUnderMyContent
        if key_list[i].firstChild.nodeValue == "PackageUnderMyOrg":
            value_list[i].firstChild.nodeValue = SharetoOrganization
        if key_list[i].firstChild.nodeValue == "PackageIsPublic":
            value_list[i].firstChild.nodeValue = SharetoEveryone
        if key_list[i].firstChild.nodeValue == "PackageShareGroups":
            value_list[i].firstChild.nodeValue = SharetoGroup
        if SharetoGroup == "true" and key_list[i].firstChild.nodeValue == "PackageGroupIDs":
            new_node = doc.createTextNode(GroupID)
            value_list[i].childNodes = [new_node]

    # Find all elements named TypeName
    # This is where the additional layers and capabilities are defined
    typeNames = doc.getElementsByTagName('TypeName')
    for typeName in typeNames:
        # Get the TypeName to enable
        if typeName.firstChild.data == "MapServer":
            extension = typeName.parentNode
            for extElement in extension.childNodes:
                if extElement.tagName == 'Definition':
                    for propArray in extElement.childNodes:
                        if propArray.tagName == 'Info':
                            for propSet in propArray.childNodes:
                                for prop in propSet.childNodes:
                                    for prop1 in prop.childNodes:
                                        if prop1.tagName == "Key":
                                            if prop1.firstChild.data == 'WebCapabilities':
                                                if prop1.nextSibling.hasChildNodes():
                                                    prop1.nextSibling.firstChild.data = capabilities
                                                else:
                                                    txt = doc.createTextNode(capabilities)
                                                    prop1.nextSibling.appendChild(txt)
    # Write to the .sddraft file
    f = open(sddraftPath, 'w')
    doc.writexml(f)
    f.close()
    

def publish_to_portal(m, outdir, service_name, tags, categories, metadata):
    sddraft_filename = service_name + ".sddraft"
    sddraft_output_filename = os.path.join(outdir, sddraft_filename)
    sd_filename = service_name + ".sd"
    sd_output_filename = os.path.join(outdir, sd_filename)

    # Create MapImageSharingDraft and set copyDataToServer property to False to reference registered data
    server_type = "FEDERATED_SERVER"
    federated_server_url = "https://gis.psrc.org/server"
    sddraft = m.getWebLayerSharingDraft(server_type, "MAP_IMAGE", service_name)
    sddraft.federatedServerUrl = federated_server_url
    sddraft.copyDataToServer = False
    sddraft.overwriteExistingService = True
    sddraft.categories = categories
    sddraft.credits = metadata.credits
    sddraft.description = metadata.description 
    sddraft.summary = metadata.summary
    sddraft.tags = tags
    sddraft.useLimitations = metadata.accessConstraints
    sddraft.portalFolder = "ElmerGeo"
    sddraft.serverFolder = "ElmerGeo"

    # Create Service Definition Draft file
    sddraft.exportToSDDraft(sddraft_output_filename)

    """Modify the .sddraft file to include a feature layer and set map image layer and feature layer properties"""

    # Modify the .sddraft file to change map image layer properties
    # Defaults are Map,Query,Data
    # Comment out the line below if you do not want to modify map image layer properties
    configure_mapserver_capabilities(sddraft_output_filename, "Map,Data")

    # Modify the .sddraft file to include a feature layer
    # Read the file
    doc = DOM.parse(sddraft_output_filename)

    # Find all elements named TypeName
    # This is where the extensions are defined
    typeNames = doc.getElementsByTagName('TypeName')
    for typeName in typeNames:
        # Get the TypeName to enable
        if typeName.firstChild.data == "FeatureServer":
            extension = typeName.parentNode
            for extElement in extension.childNodes:
                # Include a feature layer
                if extElement.tagName == 'Enabled':
                    extElement.firstChild.data = 'true'

    # Write to new .sddraft file
    sddraft_mod_xml = service_name + '_mod_xml' + '.sddraft'
    sddraft_mod_xml_file = os.path.join(outdir, sddraft_mod_xml)
    f = open(sddraft_mod_xml_file, 'w')
    doc.writexml(f)
    f.close()

    # Modify the .sddraft file to change feature layer properties
    # Defaults are Query,Create,Update,Delete,Uploads,Editing
    # Comment out the line below if you don't want to modify feature layer properties
    configure_featureserver_capabilities(sddraft_mod_xml_file, "Create,Query,Extract")

    # Stage Service
    print("Start Staging")
    #arcpy.server.StageService(sddraft_mod_xml_file, sd_output_filename)
    arcpy.server.StageService(sddraft_mod_xml_file)

    # Share to portal
    print("Start Uploading")
    #arcpy.server.UploadServiceDefinition(sd_output_filename, federated_server_url)
    response = arcpy.server.UploadServiceDefinition(sddraft_mod_xml_file, federated_server_url)
    response
    

    print("Finish Publishing")  


def delete_files_from_folder(folder):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))
    
    
arcpy.env.workspace = elmer_geo_conn_path
aprx = arcpy.mp.ArcGISProject(aprx_path)
map = aprx.listMaps()[0]

# Sign into portal
# portal_url = "https://gis.psrc.org/portal/"
# arcpy.SignInToPortal(portal_url)
#gis = GIS(portal_url, username='SCoe@PSRC.org', password='February17th2023')

####### Testing 
fail_list = []
for layer in map.listLayers():
    map.removeLayer(layer)
dataset = 'ElmerGeo.DBO.test'    
dataset_name = 'test'
centers = r"ElmerGeo.DBO.soundcast_districts_test"
#outdir = r'C:\Users\scoe\Documents\publish_elmer_geo\service_definitions'


centers_path = Path(elmer_geo_conn_path)/dataset/centers
target_item_md = md.Metadata(centers_path)

lyr = map.addDataFromPath(centers_path)
aprx.save()
layer_name = centers.split(".")[2]
tags = f"ElmerGeo, {dataset_name}"
#try:
publish_to_portal(map, outdir, layer_name, tags, dataset_name.capitalize(), target_item_md)
#except:
    #fail_list.append(layer_name)

delete_files_from_folder(outdir)