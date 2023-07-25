import json
import re

DEBUG_ON = True

KTIME = 'time'
KDATE = 'date'
KNAME = 'name'
KPROC = 'proc'
KLEVEL = 'level'
KNODE = 'node'
KMESSAGE = 'message'

# 2023-06-16 18:51:08,773 [CmdOut:208468]
time_exp = rf'(?P<{KTIME}>\d{{2}}:\d{{2}}:\d{{2}}\.\d{{3}})'
date_exp = rf'(?P<{KDATE}>\d{{4}}-\d{{2}}-\d{{2}} \d{{2}}:\d{{2}}:\d{{2}},\d{{3}})'
proc_exp = rf'\[(?P<{KNAME}>\w+):(?P<pid>\d+)\]'
level_exp = rf'(?P<{KLEVEL}>[A-Z]+)'
node_exp = rf'(?P<{KNODE}>[\w\-]+)'
message_exp = rf'(?P<{KMESSAGE}>.*)'

class LogParser:
    line_pattern = re.compile(rf'^{date_exp}\s+{proc_exp}\s+{level_exp}\s+{node_exp}\s+-\s+{message_exp}$')

    # examples
    # STDOUT: [INFO] ------------------------------------------------------------------------
    maven_line_pattern = re.compile(rf'^STDOUT:\s+\[{level_exp}\]\s+{message_exp}$')

    # examples
    # STDOUT: INFO  [2023-06-16 18:55:56,123] [com.datastax.durationtest.core.DurationTest.main()] c.d.durationtest.core.DurationTest - Beginning Duration Test...
    # STDOUT: INFO  [2023-06-16 19:23:23,506] [duration-test-executorService-4] c.d.durationtest.core.DurationTest - Completed 874000 suite tests...
    logback_line_pattern = re.compile(
        rf'^STDOUT:\s+{level_exp}\s+\[{date_exp}\]\s+\[(?P<thread>[\w\-().]+)\s*\]\s+(?P<classname>[\w\-.]+)\s+-\s+{message_exp}$')

    stdout_line_pattern = re.compile(rf'^STDOUT: {message_exp}$')

    # STDOUT: 00:36:05.862 [s0-admin-1] DEBUG c.d.o.d.i.c.m.NodeStateManager - [s0] Processing ChannelEvent(CLOSED, Node(endPoint=bb96eb58-c98f-4495-bde1-ce91bc721b30-us-east1.db.astra-test.datastax.com:29042:441c04f2-1c6d-4a26-b721-2d4ba0895cdb, hostId=441c04f2-1c6d-4a26-b721-2d4ba0895cdb, hashCode=3dcde56d))
    demo_line_pattern = re.compile(
        rf'^(STDOUT:\s+)?{time_exp}\s+\[(?P<thread>[\w\-().]+)\s*\]\s+{level_exp}\s+(?P<classname>[\w\-.]+)\s+-\s+{message_exp}$')

    def __init__(self, args, file):
        self.events = self.parse_events(args, file)

    def debug(self, msg):
        global DEBUG_ON
        if not DEBUG_ON:
            return
        if isinstance(msg, list) or isinstance(msg, dict):
            print(f'DEBUG: {json.dumps(msg, indent=2)}')
        else:
            print(f'DEBUG: {msg}')

    def parse_line(self, line):
        return self.line_pattern.match(line)

    def parse_maven_line(self, line):
        return self.maven_line_pattern.match(line)

    def parse_logback_line(self, line):
        return self.logback_line_pattern.match(line)

    def parse_demo_line(self, line):
        return self.demo_line_pattern.match(line)

    def parse_events(self, args, file):
        events = []
        with file:
            for line in file:
                m_fallout = self.parse_line(line)
                m_demo = self.parse_demo_line(line)
                if m_fallout is not None:
                    if args.input_limit and len(events) >= int(args.input_limit):
                        self.debug(f'reached requested limit if {args.input_limit} events')
                        break
                    events.append(m_fallout.groupdict())
                elif m_demo is not None:
                    events.append(m_demo.groupdict())
                elif len(events):
                    events[-1][KMESSAGE] += f'{line}'
        consolidated = []
        for event in events:
            maven_match = self.parse_maven_line(event['message'])
            logback_match = self.parse_logback_line(event['message'])
            demo_match = self.parse_demo_line(event['message'])
            if maven_match is not None:
                event[KMESSAGE] = maven_match.groupdict()
                event[KMESSAGE]['type'] = 'maven'
                consolidated.append(event)
            elif logback_match is not None:
                event[KMESSAGE] = logback_match.groupdict()
                event[KMESSAGE]['type'] = 'logback'
                consolidated.append(event)
            elif demo_match is not None:
                event[KMESSAGE] = demo_match.groupdict()
                event[KMESSAGE]['type'] = 'demo'
                consolidated.append(event)
            elif len(consolidated) and consolidated[-1][KMESSAGE]['type'] != 'toplevel':
                line = event[KMESSAGE]
                stdout_match = self.stdout_line_pattern.match(line)
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
