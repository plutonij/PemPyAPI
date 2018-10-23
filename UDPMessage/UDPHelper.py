#!/usr/bin/python3

from UDPMessage.AxUDPCommand import AxUDPCommand;
import socket;
import sys;
from UDPMessage.AxUDPMessage import AxUDPMessage;
from AxHw.Interfaces import Interfaces;
from AxHw.InfoMessage import InfoMessage;
import logging;
import traceback;

class UDPHelper(object):
    """udp class for sending/receiving data"""
    
    PORT = 8005;
    TIMEOUT = 2.0;

    target_ip = "";
    iface = "";
    sock = None;

    def __init__(self, target, iface, magic):
        self.target_ip = target
        self.iface = iface
        self.magic = magic

    def create_udp_client(self, ip_address):
        #so = socket.socket(socket.AF_INET, socket.SOCK_DGRAM);
        #so.bind(self.target_ip);
        #return so;
        pass;

    def send_message(self, message):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.bind((Interfaces.get_local_ip_from_interface(self.iface), 0));
                sock.sendto(message, self.target_ip);
                sock.settimeout(UDPHelper.TIMEOUT);
                (data, server) = sock.recvfrom(10100);

        except socket.timeout:
            logging.warning('no answer received from the endpoint {}'.format(self.target_ip));
            pass;
        except Exception as e :
            logging.warning('got an exception in the discovery mechanism...');
            traceback.print_exc()
            pass;

        return AxUDPMessage.parse(self.magic, data);

    def receive(self):
        #TODO
        data, server = sock.recvfrom(UDPHelper.TIMEOUT);

    @staticmethod
    def fill_devices(magic):
        return UDPHelper.send_broadcast(magic);

    @staticmethod
    def get_info_message_by_broadcast(mac_address, magic):
        info_messages = UDPHelper.send_broadcast(magic);

        for message in info_messages:
            if(bytearray(message.MacAddress) == mac_address):
                return message;
        return None;

    @staticmethod
    def __parse_message(iface, magic, responses, buffer, address):
        msg = AxUDPMessage.parse(magic, buffer);
        info = InfoMessage();
        info.MacAddress = msg.data[2:8];
        info.RemoteIpAddress = address;
        info.Major = msg.data[0];
        info.Minor = msg.data[1];
        info.iface = iface;
        info.magic = magic;
        logging.debug('received IP:{} with Mac:[{}]'.format(info.RemoteIpAddress, ', '.join(hex(x) for x in info.MacAddress)));
        responses.append(info);

    @staticmethod
    def __transmit_message(s, bytes_array, dest, iface, magic, responses):
        try:
            s.bind((Interfaces.get_local_ip_from_interface(iface), 0));
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1);
            logging.debug('sending discovery to {}'.format(dest));
            s.sendto(bytes_array, dest);
            
            s.settimeout(UDPHelper.TIMEOUT);
            while True:
                (buf, addr) = s.recvfrom(10100)
                if(len(buf)):
                    UDPHelper.__parse_message(iface, magic, responses, buf, addr);

        except socket.timeout:
            logging.info('no answer received from any endpoint');
        except TimeoutError:
            logging.debug('no answer received');
            pass;
        except Exception as e :
            logging.warning('got an exception in the discovery mechanism...');
            traceback.print_exc()
            pass;

    @staticmethod
    def send_broadcast(magic):
        responses = [];
        udp_message = AxUDPMessage(magic);
        udp_message.command = int(AxUDPCommand.INFO);
        bytes_array = udp_message.get_bytes();
        
        for iface in Interfaces.get_all_network_interfaces_with_broadcast():
            destIP = Interfaces.get_broadcast_address(iface);

            if(destIP is None):
                continue;

            dest = (destIP, UDPHelper.PORT);
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                UDPHelper.__transmit_message(s, bytes_array, dest, iface, magic, responses);
            
        return responses;

#a = UDPHelper("10.30.10.88");
#UDPHelper.send_broadcast();