from PinRobot import PinRobot
from RestfulThreaded import RESTfulThreadedServer
from os.path import join
from ParseXmlRobotConfiguration import ParseXmlRobotConfiguration, RobotConfiguration
from Exception import Error, ConnectionError, InputError, ParseError
import json
import argparse
from Statistics import Statistics


def main():
    _path = "ConfigRest"

    parser = argparse.ArgumentParser(description='PIN Robot Rest API')
    parser.add_argument('-config','-configfile", help="path to entry configuration xml',required=False)
    parser.add_argument('-port','-port", help="port for the http listener',required=False)
    parser.add_argument('-enable_statistics', nargs='?', const=True, default=False, help="enable tracking of the button press.", required=False)
    args = (parser.parse_args())

    if(None is args.config):
        config = join("Assets", "EntryConfiguration.xml")
        port = 8000

    else:
        config = args.config
        port = args.port
        
    enable_statistics=args.enable_statistics

    try:
        ConfigurationList = ParseXmlRobotConfiguration.parseXml(config)
        RobotList = {}

        for key, value in ConfigurationList.items():
             robot = PinRobot(enable_statistics)
             if(False is robot.InitializeTerminal(join(_path, value.Layout))):
                print(value.Layout + ": Initialization failed, skip...")
                continue

             if(False is robot.InitializeConnection(value.IP, int(value.Port))):
                print(value.Layout + ": robot not reachable, skip...")
                continue

             RobotList.update({key:robot})

        if(not RobotList):
            print(" Fatal error, robot list is empty...")
            raise

        server = RESTfulThreadedServer(doPostWork, doGetWork, RobotList, port)
        server.start()
        server.waitForThread()
    except (Error):
        pass
    except:
        pass

def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')
   

def doPostWork(jsonString, robotList):
    j = json.loads(jsonString)
        
    for command in j["commands"]:
        if(True is robotList[j['id']].SendCommand(command)):
            print(j['id'] + ": execution of " + command + " was succesful")
            robotList[j['id']].UpdateTable(j['id'], command)
        else:
            raise InputError
        
def doGetWork(robotList):
    l = list(robotList.keys())
    robot_object = {'id' : l}
    return json.dumps(robot_object)

main()
