#!./venv/bin/python

"""
Api for metrics page
"""

import logging
import subprocess
import json
import psutil

from fastapi import APIRouter
from libs import mailer_calls

metrics_router = APIRouter()

logger = logging.getLogger(__name__)

@metrics_router.get("/sensor_temp", tags=["metrics"])
async def sensors_temp():
    """
    Return sensor temps

    Returns:
        [type]: [description]
    """

    ff_command = ["sensors", "-u"]

    output, error = subprocess.Popen(
        ff_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    ).communicate()

    if not error:
        return output.decode().strip()

    logger.error(error.decode().replace("\n", " "))
    return {}

@metrics_router.get("/temp", tags=["metrics"])
async def temp():
    """
    Psutil temps

    Returns:

        coretemp-isa-0000\n
        Adapter: ISA adapter\n
        Package id 0:  +49.0°C  (high = +86.0°C, crit = +100.0°C)\n
        Core 0:        +32.0°C  (high = +86.0°C, crit = +100.0°C)\n
        Core 1:        +33.0°C  (high = +86.0°C, crit = +100.0°C)\n
        Core 2:        +33.0°C  (high = +86.0°C, crit = +100.0°C)\n
        Core 3:        +32.0°C  (high = +86.0°C, crit = +100.0°C)\n
        Core 4:        +37.0°C  (high = +86.0°C, crit = +100.0°C)\n
        Core 5:        +37.0°C  (high = +86.0°C, crit = +100.0°C)\n
        Core 6:        +49.0°C  (high = +86.0°C, crit = +100.0°C)\n
        Core 7:        +33.0°C  (high = +86.0°C, crit = +100.0°C)\n

        acpitz-acpi-0\n
        Adapter: ACPI interface\n
        temp1:        +27.8°C  (crit = +119.0°C)\n

        nouveau-pci-0100\n
        Adapter: PCI adapter\n
        fan1:           0 RPM\n
        temp1:        +49.0°C  (high = +95.0°C, hyst =  +3.0°C)\n
                            (crit = +105.0°C, hyst =  +5.0°C)\n
                            (emerg = +135.0°C, hyst =  +5.0°C)\n

        pch_cannonlake-virtual-0\n
        Adapter: Virtual device\n
        temp1:        +40.0°C\n
    """

    temps = psutil.sensors_temperatures()

    try:
        if temps["acpitz"][0][1] >= temps["acpitz"][0][2]:
           mailer_calls.mailer("High acpitz temp!", json.dumps(temps["acpitz"], indent=2))
    except Exception as exp:
        logger.exception(exp)
        return str(exp)
    try:
        if temps["pch_cannonlake"][0][1] >= 75:
            mailer_calls.mailer("High pch temp!", json.dumps(temps["pch_cannonlake"], indent=2))
    except Exception as exp:
        logger.exception(exp)
        return str(exp)
    try:
        if True in [ True for core in temps["coretemp"] if core[1] >= core[2] ]:
            mailer_calls.mailer("High CPU temp!", json.dumps(temps["coretemp"], indent=2))
    except Exception as exp:
        logger.exception(exp)
        return str(exp)
    try:
        if temps["nouveau"][0][1] >= temps["nouveau"][0][2]:
            mailer_calls.mailer("High GPU temp!", json.dumps(temps["nouveau"], indent=2))
    except Exception as exp:
        logger.exception(exp)
        return str(exp)

    return temps
