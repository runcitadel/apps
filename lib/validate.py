# SPDX-FileCopyrightText: 2021 Aaron Dewes <aaron.dewes@protonmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-only

import os

# Validates app data
# Returns true if valid, false otherwise
appDir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")


# Lists all folders in a directory and checks if they are valid
# A folder is valid if it contains an app.yml file
# A folder is invalid if it doesn't contain an app.yml file
def findAndValidateApps(dir: str):
    apps = []
    for root, dirs, files in os.walk(dir, topdown=False):
        for name in dirs:
            app_dir = os.path.join(root, name)
            if os.path.isfile(os.path.join(app_dir, "app.yml")):
                apps.append(name)
    return apps
