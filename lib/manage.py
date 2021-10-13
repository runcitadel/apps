#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2021 Aaron Dewes <aaron.dewes@protonmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-only

import os
import json

from lib.validate import findAndValidateApps
from lib.metadata import getSimpleAppRegistry

appsDir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "apps")

def update():
    apps = findAndValidateApps(appsDir)
    simpleRegistry = getSimpleAppRegistry(apps, appsDir)
    with open(os.path.join(appsDir, "..", "apps.json"), "w") as f:
        json.dump(simpleRegistry, f, indent=4, sort_keys=True)
    with open(os.path.join(appsDir, "apps.json"), "w") as f:
        json.dump(simpleRegistry, f, indent=4, sort_keys=True)
    print("Wrote information to apps.json")
