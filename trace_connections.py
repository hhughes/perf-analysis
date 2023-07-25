import collections
import sys
import event_parser
import re
import argparse


def merge(d1, d2):
    # d2 takes preference over d1
    out = {}
    for d in [d1, d2]:
        for k in d:
            out[k] = d[k]
    return out


# Node(endPoint=bb96eb58-c98f-4495-bde1-ce91bc721b30-us-east1.db.astra-test.datastax.com:29042:3e6ee081-e942-4553-bc05-43ae40ffcd8b, hostId=3e6ee081-e942-4553-bc05-43ae40ffcd8b, hashCode=407237c3)
host_id_expr = re.compile(r'hostId=([\w\-]+)')
ip_and_port_expr = re.compile(r' /([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+:[0-9]+)')

class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-limit', action='store', type=int, help='limit number of input lines read')
    parser.add_argument('--log-format', action='store', type=str, help='log formatting: fallout (default), logback, json')
    args, argv = parser.parse_known_args()
    events = []
    for event in event_parser.LogParser(args, sys.stdin).events:
        # unwrap inner event
        if 'message' in event and isinstance(event['message'], dict):
            events.append(merge(event, event['message']))

    hosts = {}
    for event in events:
        for host_id in host_id_expr.findall(event['message']):
            if host_id == "null":
                continue
            if host_id not in hosts:
                hosts[host_id] = {'host_id': host_id, 'ips': []}

    # hostId may be mentioned without keyname in message
    for event in events:
        message_host_ids = set()
        for host_id in hosts:
            if host_id in event['message']:
                message_host_ids.add(host_id)
        if len(message_host_ids) == 1:
            (host_id, ) = message_host_ids
            for ip_and_port in ip_and_port_expr.findall(event['message']):
                hosts[host_id]['ips'].append(ip_and_port)

    print("")

    events_by_host_id = collections.defaultdict(list)
    for event in events:
        for host_id in hosts:
            should_include = False
            host = hosts[host_id]
            if host_id in event['message']:
                should_include = True
            else:
                # else check for IP without hostId
                for ip in host['ips']:
                    if ip in event['message']:
                        should_include = True

            if should_include:
                events_by_host_id[host_id].append(event)

    for host_id in hosts:
        host = hosts[host_id]
        print(f"host id: {color.BOLD}{host_id}{color.END} ({', '.join(host['ips'])})")
        print("---------------------------------------------")
        for event in events_by_host_id[host_id]:
            highlit_message = event["message"].replace(host_id, f"{color.BOLD}{host_id}{color.END}")
            for ip in hosts[host_id]['ips']:
                highlit_message = highlit_message.replace(ip, f"{color.BOLD}{ip}{color.END}")
            print(f'  {color.DARKCYAN}{event["time"]}{color.END} [{event["thread"]}] {color.BLUE}{event["classname"]}{color.END} - {highlit_message}')
        print("")
        print("")