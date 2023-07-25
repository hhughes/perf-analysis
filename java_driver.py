import sys
import re
import json
from collections import Counter
import argparse
import event_parser

DEBUG_ON = True


def debug(msg):
    global DEBUG_ON
    if not DEBUG_ON:
        return
    if isinstance(msg, list) or isinstance(msg, dict):
        print(f'DEBUG: {json.dumps(msg, indent=2)}')
    else:
        print(f'DEBUG: {msg}')


KTIME = 'time'
KDATE = 'date'
KNAME = 'name'
KPROC = 'proc'
KLEVEL = 'level'
KNODE = 'node'
KMESSAGE = 'message'


def event_summary(events):
    summary = {}
    for ev in events:
        inner = ev['message']
        type = inner['type']
        level = ev[KLEVEL]
        if KLEVEL in inner:
            level = inner[KLEVEL]
        msg = inner[KMESSAGE]
        if type not in summary:
            summary[type] = {}
        if level not in summary[type]:
            summary[type][level] = {'count': 0, 'messages': Counter()}
        summary[type][level]['count'] += 1
        summary[type][level]['messages'][msg] += 1
    return summary


def summarize(args, events, baseline):
    summary = event_summary(events)
    baseline_summary = None
    if baseline:
        baseline_summary = event_summary(baseline)

    for type in summary:
        if args.types and type not in args.types.split(','):
            continue

        print(f'**** {type} messages ****')
        print('--------------------------------------------------------------------------------')
        for level in summary[type]:
            if args.levels and level not in args.levels.split(','):
                continue

            if baseline_summary:
                print(f'  {level} - total: {summary[type][level]["count"]} (baseline: {baseline_summary[type][level]["count"]})')
            else:
                print(f'  {level} - total: {summary[type][level]["count"]}')

            messages_first = True
            common_msgs = set()
            for (m, c) in summary[type][level]["messages"].most_common(args.output_limit):
                if messages_first:
                    print(f'  top messages:')
                    messages_first = False
                if baseline_summary:
                    print(f'   * {c} (baseline: {baseline_summary[type][level]["messages"][m]}): {m}')
                    common_msgs.add(m)
                else:
                    print(f'   * {c}: {m}')
            if baseline_summary:
                additional_first = True
                for (m, c) in baseline_summary[type][level]["messages"].most_common(args.output_limit):
                    if m not in common_msgs:
                        if additional_first:
                            print(f'  additional baseline top messages:')
                            additional_first = False
                        print(f'   {c}: {m}')
            print('--------------------------------------------------------------------------------')


ip_address_pattern = re.compile(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(:[0-9]{2,})?')
uuid_pattern = re.compile(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}')
hex_pattern = re.compile(r'[0-9a-f]{8,}')
java_line_pattern = re.compile(f'\.java:[0-9]+')
jar_pattern = re.compile(r'[\w\-.]+.jar:[\w\-_.]+')
inflight_pattern = re.compile(r'inFlight=[0-9]+')

sub_patterns = {
    'ip': {'pattern': ip_address_pattern, 'token': '$IP_ADDRESS'},
    'uuid': {'pattern': uuid_pattern, 'token': '$UUID'},
    'hex': {'pattern': hex_pattern, 'token': '$HEX'},
    'java_line': {'pattern': java_line_pattern, 'token': '.java:$LINE'},
    'jar': {'pattern': jar_pattern, 'token': '$JAR:?'},
    'inflight': {'pattern': inflight_pattern, 'token': '$INFLIGHT=?'},
}


def apply_substitutions(args, line):
    if not args.substitutions:
        return line
    for sub in args.substitutions.split(','):
        if sub not in sub_patterns:
            debug(f'unrecognized substitution {sub}')
            continue
        line = sub_patterns[sub]['pattern'].sub(sub_patterns[sub]['token'], line)

    return line


def main(args, argv):
    global DEBUG_ON
    if args.debug:
        DEBUG_ON = True
    file = None
    if args.use_stdin:
        debug('reading from stdin')
        file = sys.stdin
    else:
        debug(f'opening {argv[0]}')
        file = open(argv[0], 'r')

    results = event_parser.LogParser(args, file).events
    print(results[-1])
    baseline = None
    if args.compare_to:
        baseline = event_parser.LogParser(args, open(args.compare_to, 'r')).events
        for event in baseline:
            event['message']['message'] = apply_substitutions(args, event['message']['message'])

    for event in results:
        event['message']['message'] = apply_substitutions(args, event['message']['message'])

    summarize(args, results, baseline)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true', help='print debug logs')
    parser.add_argument('--use-stdin', action='store_true', help='parse log text from stdin')
    parser.add_argument('--input-limit', action='store', type=int, help='limit number of input lines read')
    parser.add_argument('--output-limit', action='store', default=10, type=int, help='limit number of input lines read')
    parser.add_argument('--compare-to', action='store', help='file to compare against')
    parser.add_argument('--types', action='store', help='type of events to print (top-level, maven, logback)')
    parser.add_argument('--levels', action='store', help='level of events to print (TRACE, DEBUG, WARN, ERROR, FATAL)')
    parser.add_argument('--substitutions', action='store', help='comma separated list of substitutions to apply to help with similarity matching (ip, uuid, hex, java_line, jar, inflight)')
    args, argv = parser.parse_known_args()
    main(args, argv)

