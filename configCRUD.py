__author__ = 'DusX'

import ConfigParser
import os

# TODO: add comments to file (localhost IP) etc
# add config comments
# http://stackoverflow.com/questions/6620637/writing-comments-to-files-with-configparser


def createConfig(path):
    """
    Create a config file
    """

    config = ConfigParser.ConfigParser()

    config.add_section("tcpBridge")
    config.set("tcpBridge", "selfLaunch", True)
    config.set("tcpBridge", "host", "127.0.0.1")
    config.set("tcpBridge", "port", "8080")

    with open(path, "wb") as config_file:  # wb or w
        config.write(config_file)

"""
note that the selfLaunch val is boolean... requires new definition
currently uses eval in tcpbridge
see: https://wiki.python.org/moin/ConfigParserExamples
"""

#Config.getboolean("SectionOne", "single")

def readConfig(path, section='tcpBridge', value="host"):
    """ read config and return specific value """

    config = ConfigParser.ConfigParser()
    config.read(path)

    # read some values from the config
    configData = config.get(section, value)
    return configData


#===================================================================================


if __name__ == "__main__":
    path = "settings.ini"
    if not os.path.exists(path):
        createConfig(path)
        print "Default config file created as:", path
        print "tcpBridge host set to", readConfig(path, "tcpBridge", "host")
    else:
        print "Delete the", path, "file and run again to create default", path, "config file."