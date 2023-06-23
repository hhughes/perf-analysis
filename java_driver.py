import sys
import re
import json
from collections import Counter
import argparse

DEBUG_ON = False


def debug(msg):
    global DEBUG_ON
    if not DEBUG_ON:
        return
    if isinstance(msg, list) or isinstance(msg, dict):
        print(f'DEBUG: {json.dumps(msg, indent=2)}')
    else:
        print(f'DEBUG: {msg}')


KDATE = 'date'
KNAME = 'name'
KPROC = 'proc'
KLEVEL = 'level'
KNODE = 'node'
KMESSAGE = 'message'

# 2023-06-16 18:51:08,773 [CmdOut:208468]
date_exp = rf'(?P<{KDATE}>\d{{4}}-\d{{2}}-\d{{2}} \d{{2}}:\d{{2}}:\d{{2}},\d{{3}})'
proc_exp = rf'\[(?P<{KNAME}>\w+):(?P<pid>\d+)\]'
level_exp = rf'(?P<{KLEVEL}>[A-Z]+)'
node_exp = rf'(?P<{KNODE}>[\w\-]+)'
message_exp = rf'(?P<{KMESSAGE}>.*)'

line_pattern = re.compile(rf'^{date_exp}\s+{proc_exp}\s+{level_exp}\s+{node_exp}\s+-\s+{message_exp}$')

# examples
# STDOUT: [INFO] ------------------------------------------------------------------------
maven_line_pattern = re.compile(rf'^STDOUT:\s+\[{level_exp}\]\s+{message_exp}$')

# examples
# STDOUT: INFO  [2023-06-16 18:55:56,123] [com.datastax.durationtest.core.DurationTest.main()] c.d.durationtest.core.DurationTest - Beginning Duration Test...
# STDOUT: INFO  [2023-06-16 19:23:23,506] [duration-test-executorService-4] c.d.durationtest.core.DurationTest - Completed 874000 suite tests...
logback_line_pattern = re.compile(rf'^STDOUT:\s+{level_exp}\s+\[{date_exp}\]\s+\[(?P<thread>[\w\-().]+)\s*\]\s+(?P<classname>[\w\-.]+)\s+-\s+{message_exp}$')

stdout_line_pattern = re.compile(rf'^STDOUT: {message_exp}$')


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


def parse_line(line):
    return line_pattern.match(line)


def parse_maven_line(line):
    return maven_line_pattern.match(line)


def parse_logback_line(line):
    return logback_line_pattern.match(line)


ip_address_pattern = re.compile(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(:[0-9]{2,})?')
uuid_pattern = re.compile(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}')
hex_pattern = re.compile(r'[0-9a-f]{8,}')
java_line_pattern = re.compile(f'\.java:[0-9]+')
jar_pattern = re.compile(r'[\w\-.]+.jar:[\w\-.]+')
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


def parse_events(args, file):
    events = []
    with file:
        for line in file:
            m = parse_line(apply_substitutions(args, line))
            if m is not None:
                if args.input_limit and len(events) >= int(args.input_limit):
                    debug(f'reached requested limit if {args.input_limit} events')
                    break
                events.append(m.groupdict())
            elif len(events):
                events[-1][KMESSAGE] += f'{line}'
    consolidated = []
    for event in events:
        maven_match = parse_maven_line(event['message'])
        logback_match = parse_logback_line(event['message'])
        if maven_match is not None:
            event[KMESSAGE] = maven_match.groupdict()
            event[KMESSAGE]['type'] = 'maven'
            consolidated.append(event)
        elif logback_match is not None:
            event[KMESSAGE] = logback_match.groupdict()
            event[KMESSAGE]['type'] = 'logback'
            consolidated.append(event)
        elif len(consolidated) and consolidated[-1][KMESSAGE]['type'] != 'toplevel':
            line = event[KMESSAGE]
            stdout_match = stdout_line_pattern.match(line)
            if stdout_match:
                line = stdout_match.group(KMESSAGE)
            consolidated[-1][KMESSAGE][KMESSAGE] += f'\n{line}'
        else:
            event[KMESSAGE] = {
                'type': 'toplevel',
                KMESSAGE: event[KMESSAGE]
            }
            consolidated.append(event)
    return consolidated


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

    results = parse_events(args, file)
    baseline = None
    if args.compare_to:
        baseline = parse_events(args, open(args.compare_to, 'r'))

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

