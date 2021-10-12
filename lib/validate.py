# SPDX-FileCopyrightText: 2021 Aaron Dewes <aaron.dewes@protonmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-only

import os
import yaml
from jsonschema import validate
import json


# Validates app data
# Returns true if valid, false otherwise
appDir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")

def validateApp(app: dict):
    with open(os.path.join(appDir, 'app-standard-v1.json'), 'r') as f:
        schema = json.loads(f.read())

    try:
        validate(app, schema)
        return True
    # Catch and log any errors, and return false
    except Exception as e:
        print(e)
        return False

# Lists all folders in a directory and checks if they are valid
# A folder is valid if it contains an app.yml file
# A folder is invalid if it doesn't contain an app.yml file
def findAndValidateApps(dir: str):
    apps = []
    app_data = {}
    for root, dirs, files in os.walk(dir, topdown=False):
        for name in dirs:
            app_dir = os.path.join(root, name)
            if os.path.isfile(os.path.join(app_dir, "app.yml")):
                apps.append(name)
                # Read the app.yml and append it to app_data
                with open(os.path.join(app_dir, "app.yml"), 'r') as f:
                    app_data[name] = yaml.safe_load(f)
    # Now validate all the apps using the validateApp function by passing the app.yml as an argument to it, if an app is invalid, remove it from the list
    for app in apps:
        appyml = app_data[app]
        if not validateApp(appyml):
            apps.remove(app)
            print("Warning: App {} is invalid".format(app))
            # Skip to the next iteration of the loop
            continue
        # More security validation
        should_continue=True
        if appyml['metadata']['dependencies']:
            for dependency in appyml['metadata']['dependencies']:
                if dependency not in apps and dependency not in ["bitcoind", "lnd", "electrum"]:
                    print("WARNING: App '{}' has unknown dependency '{}'".format(app, dependency))
                    apps.remove(app)
                    should_continue=False
                if dependency == app:
                    print("WARNING: App '{}' depends on itself".format(app))
                    apps.remove(app)
                    should_continue=False
        if not should_continue:
            continue
        for container in appyml['containers']:
            if 'permissions' in container:
                for permission in container['permissions']:
                    if permission not in appyml['metadata']['dependencies'] and permission not in ["root", "hw"]:
                        print("WARNING: App {}'s container '{}' requires the '{}' permission, but the app doesn't list it in it's dependencies".format(app, container['name'], permission))
                        apps.remove(app)
                        # Skip to the next iteration of the loop
                        continue
    return apps
