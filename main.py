#!/bin/python3
# -*- coding: utf-8 -*-

# Script convert JetBrains format xml files to lua file that return table
# with all data needed for deploy

import xml.etree.ElementTree as ET
import os
import json
import sys
from jsontolua import SaveToLua


def extractMappings(deployment_file):
    tree = ET.parse(deployment_file)
    root = tree.getroot()
    deploymentData = {}
    for component in root.findall('component'):
        if component.attrib['name'] == 'PublishConfigData':
            for serverData in component.findall('serverData'):
                for path in serverData.findall('paths'):
                    name = path.attrib['name']
                    deploymentData[name] = dict(mappings=[], excludedPaths=[])
                    for serverdata in path.findall('serverdata'):
                        for mappings in serverdata.findall('mappings'):
                            for mapping in mappings.findall('mapping'):
                                remote = mapping.attrib['deploy']
                                local = mapping.attrib['local'].replace(
                                    '$PROJECT_DIR$/', "")
                                deploymentData[name]['mappings'].append(
                                    dict(remote=remote, local=local))
                        for excludedPaths in serverdata.findall('excludedPaths'):
                            for excludedPath in excludedPaths.findall('excludedPath'):
                                path = excludedPath.attrib['path'].replace(
                                    '$PROJECT_DIR$/', "")
                                deploymentData[name]['excludedPaths'].append(
                                    path)
    return deploymentData


def extractWebServers(webServers_file):
    tree = ET.parse(webServers_file)
    root = tree.getroot()
    webServersData = {}
    for component in root.findall('component'):
        if component.attrib['name'] == 'WebServers':
            for option in component.findall('option'):
                for webServer in option.findall('webServer'):
                    name = webServer.attrib['name']
                    webServersData[name] = dict()
                    for fileTransfer in webServer.findall('fileTransfer'):
                        if 'rootFolder' in fileTransfer.attrib:
                            webServersData[name]['rootFolder'] = fileTransfer.attrib['rootFolder']
                        if 'accessType' in fileTransfer.attrib:
                            webServersData[name]['accessType'] = fileTransfer.attrib['accessType']
                        webServersData[name]['sshConfigId'] = fileTransfer.attrib['sshConfigId']
                        webServersData[name]['sshConfig'] = fileTransfer.attrib['sshConfig']
                        if 'username' in fileTransfer.attrib:
                            webServersData[name]['username'] = fileTransfer.attrib['username']
                        if 'password' in fileTransfer.attrib:
                            webServersData[name]['password'] = fileTransfer.attrib['password']
    return webServersData


def extractSshConfigs(sshConfigs_file):
    tree = ET.parse(sshConfigs_file)
    root = tree.getroot()
    sshConfigsData = {}
    for component in root.findall('component'):
        if component.attrib['name'] == 'SshConfigs':
            for sshConfig in component.findall('configs'):
                for config in sshConfig.findall('sshConfig'):
                    name = config.attrib['id']
                    sshConfigsData[name] = dict()
                    sshConfigsData[name]['host'] = config.attrib['host']
                    sshConfigsData[name]['port'] = config.attrib['port']
                    if 'username' in config.attrib:
                        sshConfigsData[name]['username'] = config.attrib['username']
                    if 'password' in config.attrib:
                        sshConfigsData[name]['password'] = config.attrib['password']
                    if 'authType' in config.attrib:
                        sshConfigsData[name]['authType'] = config.attrib['authType']
                    if 'connectionConfig' in config.attrib:
                        sshConfigsData[name]['connectionConfig'] = config.attrib['connectionConfig']
    return sshConfigsData


def combine(mappings, webServers, sshConfigs):
    data = {}
    for server in webServers:
        if 'sshConfigId' not in webServers[server]:
            print("No sshConfigId for server: " + server)
            continue
        if server not in mappings:
            print("No mappings for server: " + server)
            continue
        sshConfigId = webServers[server]['sshConfigId']
        if sshConfigId not in sshConfigs:
            print("No sshConfigId for server: " + server)
            continue
        data[server] = {}

        if 'username' in webServers[server]:
            data[server]['username'] = webServers[server]['username']
        data[server]['mappings'] = mappings[server]['mappings']
        if 'rootFolder' in webServers[server]:
            rootFolder = webServers[server]['rootFolder']
            data[server]['rootFolder'] = rootFolder  # TODO: remove it
            # add rootFolder to mappings remote paths
            for i in range(len(mappings[server]['mappings'])):
                path = rootFolder + mappings[server]['mappings'][i]['remote']
                # remove slash at the end
                mappings[server]['mappings'][i]['remote'] = path.rstrip('/')

        data[server]['excludedPaths'] = mappings[server]['excludedPaths']
        if sshConfigs[sshConfigId]['host']:
            data[server]['host'] = sshConfigs[sshConfigId]['host']
        else:
            print("No host for server: " + server)
        if sshConfigs[sshConfigId]['port'] != "22":
            data[server]['port'] = sshConfigs[sshConfigId]['port']
        if 'username' in sshConfigs[sshConfigId]:
            data[server]['username'] = sshConfigs[sshConfigId]['username']
    return data


if __name__ == "__main__":
    project_path = sys.argv[1]

    project_path = os.path.expanduser(project_path)
    if project_path[-1] != '/':
        project_path = project_path + '/'

    override_file = project_path + ".nvim/deployment.lua"

    deployment_file = project_path + ".idea/deployment.xml"
    webServers_file = project_path + ".idea/webServers.xml"
    sshConfigs_file = project_path + ".idea/sshConfigs.xml"
    if not os.path.exists(deployment_file):
        print("File not found: " + deployment_file)
        exit(1)
    mappings = extractMappings(deployment_file)
    webServers = extractWebServers(webServers_file)
    sshConfigs = extractSshConfigs(sshConfigs_file)

    combined = combine(mappings, webServers, sshConfigs)

    # jsonStr = json.dumps(combined, indent=2)
    # print(jsonStr)

    if not os.path.exists(os.path.dirname(override_file)):
        os.makedirs(os.path.dirname(override_file))
    SaveToLua(combined, override_file,
              "deployment data parsed from JetBrains format")
