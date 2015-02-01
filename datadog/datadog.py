''' Log parser that can process multiline log messages. Extracts
    counts of log lines by severity, tagging error lines by
    the exception type.
'''
import re
import datetime as dt
from datetime import datetime
import calendar


first_line = re.compile(r'^(?P<timestamp>\d{2}:\d{2}:\d{2}.\d{3}) \[(?P<severity>[^ ]*)\] (?P<logger>[^ ]*) (?P<message>.*)$')
stack_trace_end = re.compile(r'^(?P<exception>[a-zA-Z]\w*)(:.*)?$')

def parse_date(date):
    today = dt.date.today()
    time = datetime.strptime(date, '%H:%M:%S.%f').time()
    return datetime.combine(today, time)

class MultilineParser(object):
    ''' Possible parser state transitions:

    looking_for_start -> looking_for_start:
      * Line doesn't start with a timestamp
      * Line starts with a timestamp and isn't severity ERROR (emits point)

    looking_for_start -> find_stack_trace_start:
      * Line starts with a timestamp and is severity ERROR

    find_stack_trace_start -> find_stack_trace_start
      * Line doesn't start with "Traceback"
      * Line starts with a timestamp (resets state data)

    find_stack_trace_start -> find_stack_trace_end
      * Line starts with "Traceback"

    find_stack_trace_end -> find_stack_trace_start
      * Line starts with a timestamp (resets state data)

    find_stack_trace_end -> looking_for_start
      * Line looks like end of the stack trace (emits point, resets state)
    '''

    def __init__(self, *args, **kwargs):
        self.state = self.looking_for_start
        self.data = {}

    def parse_line(self, line):
        'Entry point to the log parser'
        return self.state(line)

    def looking_for_start(self, line):
        ''' Initial state of the parser. Will match lines starting with
            a timestamp. If it sees that the log message was of ERROR
            severity, transition to the `find_stack_trace_start` state,
            otherwise, return a metric point for the line.
        '''
        global first_line
        match = first_line.match(line)
        if match:
            data = match.groupdict()
            severity = data.get('severity')
            if severity == 'ERROR':
                self.data = match.groupdict()
                self.state = self.find_stack_trace_start
            elif severity is not None:
                return (
                    'logs.%s.%s' % (data.get('logger'), severity.lower()),
                    parse_date(data.get('timestamp')),
                    1,
                    self.data.get('message'),
                    {'metric_type': 'counter'}
                )

    def find_stack_trace_start(self, line):
        ''' Find the start of the stack trace. If found, transition to
            `find_stack_trace_end`. If a line beginning with a timestamp
            is found first, then reset the state machine.
        '''
        if line.startswith('Traceback'):
            self.state = self.find_stack_trace_end
        else:
            self.looking_for_start(line)

    def find_stack_trace_end(self, line):
        ''' Find the end of the stack trace. If found, return a metric point
            tagged with the type of exception and transition to the
            `looking_for_start` state again. If a line beginning with a
            timestamp is found first, then reset the state machine.
        '''
        global stack_trace_end
        match = stack_trace_end.match(line)
        if match:
            exception = match.group('exception')
            output = (
                'logs.%s.%s' % (self.data.get('logger'), self.data.get('severity').lower()),
                parse_date(self.data.get('timestamp')),
                1,
                self.data.get('message'),
                {'metric_type': 'counter',
                 'tags': ['exception:%s' % exception]}
            )
            self.data = {}
            self.state = self.looking_for_start
            return output
        else:
            self.looking_for_start(line)


def test():
    sample_log = """2013-05-07 10:44:22,920 | ERROR | dd.collector | checks.batman(__init__.py:453) | Check 'batman' instance #0 failed
Traceback (most recent call last):
  File "/Users/carlo/Projects/datadog/dd-agent/checks/__init__.py", line 444, in run
    self.check(instance)
  File "/Users/carlo/Projects/datadog/dd-agent/checks.d/batman.py", line 55, in check
    self.gauge('dd.batman.top', y)
UnboundLocalError: local variable 'y' referenced before assignment
2013-05-07 10:44:22,920 | DEBUG | dd.collector | aggregator(aggregator.py:377) | received 0 payloads since last flush
2013-05-07 10:44:22,921 | DEBUG | dd.collector | aggregator(aggregator.py:377) | received 0 payloads since last flush
2013-05-07 10:44:22,921 | DEBUG | dd.collector | checks.mcache(mcache.py:89) | Connecting to localhost:11211 tags:['instance:localhost_11211']
2013-05-07 10:44:22,922 | ERROR | dd.collector | checks.mcache(__init__.py:453) | Check 'mcache' instance #0 failed
Traceback (most recent call last):
  File "/Users/carlo/Projects/datadog/dd-agent/checks/__init__.py", line 444, in run
    self.check(instance)
  File "/Users/carlo/Projects/datadog/dd-agent/checks.d/mcache.py", line 165, in check
    self._get_metrics(server, port, tags, memcache)
  File "/Users/carlo/Projects/datadog/dd-agent/checks.d/mcache.py", line 138, in _get_metrics
    raise Exception("Unable to retrieve stats from memcache instance: " + server + ":" + str(port) + ". Please check your configuration")
Exception: Unable to retrieve stats from memcache instance: localhost:11211. Please check your configuration
2013-05-07 10:44:22,922 | DEBUG | dd.collector | aggregator(aggregator.py:377) | received 0 payloads since last flush
2013-05-07 10:44:22,923 | DEBUG | dd.collector | aggregator(aggregator.py:377) | received 0 payloads since last flush
2013-05-07 10:44:22,924 | DEBUG | dd.collector | checks.http_check(http_check.py:25) | Connecting to http://localhost:5000
2013-05-07 10:44:22,924 | DEBUG | dd.collector | checks.http_check(http_check.py:25) | Connecting to https://app.datadoghq.com
2013-05-07 10:44:22,925 | ERROR | dd.collector | checks.mysql(__init__.py:453) | Check 'mysql' instance #0 failed
Traceback (most recent call last):
  File "/Users/carlo/Projects/datadog/dd-agent/checks/__init__.py", line 444, in run
    self.check(instance)
  File "/Users/carlo/Projects/datadog/dd-agent/checks.d/mysql.py", line 52, in check
    db = self._connect(host, mysql_sock, user, password)
  File "/Users/carlo/Projects/datadog/dd-agent/checks.d/mysql.py", line 225, in _connect
    passwd=password)
  File "/Users/carlo/Projects/datadog/python/lib/python2.6/site-packages/MySQL_python-1.2.4b4-py2.6-macosx-10.6-universal.egg/MySQLdb/__init__.py", line 81, in Connect
    return Connection(*args, **kwargs)
  File "/Users/carlo/Projects/datadog/python/lib/python2.6/site-packages/MySQL_python-1.2.4b4-py2.6-macosx-10.6-universal.egg/MySQLdb/connections.py", line 187, in __init__
    super(Connection, self).__init__(*args, **kwargs2)
OperationalError: (2002, "Can't connect to local MySQL server through socket '/tmp/mysql.sock' (2)")
2013-05-07 10:44:22,926 | DEBUG | dd.collector | aggregator(aggregator.py:377) | received 0 payloads since last flush
2013-05-07 10:44:22,926 | DEBUG | dd.collector | checks.nagios(log_parser.py:35) | Starting parse for file /tmp/service-perfdata
2013-05-07 10:44:22,927 | WARNING | dd.collector | checks.nagios(log_parser.py:41) | Can't tail /tmp/service-perfdata file
2013-05-07 10:44:22,927 | ERROR | dd.collector | checks.nagios(__init__.py:453) | Check 'nagios' instance #0 failed
Traceback (most recent call last):
  File "/Users/carlo/Projects/datadog/dd-agent/checks/__init__.py", line 444, in run
    self.check(instance)
  File "/Users/carlo/Projects/datadog/dd-agent/checks.d/nagios.py", line 77, in check
    parser.parse_file()
  File "/Users/carlo/Projects/datadog/dd-agent/checks/log_parser.py", line 37, in parse_file
    self.gen.next()
StopIteration
"""
    sample_log = """
00:47:12.681 [DEBUG] c.o.s.TimeoutActor - received handled message Kill(Paste(7961,Some(/***
scalaVersion := "2.11.4"
),Some(Processing...),Some(Co2h5rT8x5IMgUO1eunk0tfjRtO24r),None))
01:28:43.756 [DEBUG] c.o.s.PastesActor - received handled message GetPaste(2402)
02:02:44.763 [DEBUG] c.o.s.PastesActor - received handled message GetPaste(3626)
02:03:20.288 [DEBUG] c.o.s.PastesActor - received handled message GetPaste(2725)
02:26:05.017 [DEBUG] c.o.s.PastesActor - received handled message GetPaste(2691)
02:28:21.195 [DEBUG] c.o.s.PastesActor - received handled message GetPaste(1648)
02:40:48.442 [DEBUG] c.o.s.PastesActor - received handled message GetPaste(781)
    """
    import logging
    logging.basicConfig()
    parser = MultilineParser()
    for line in sample_log.split("\n"):
        print parser.parse_line(line)


if __name__ == '__main__':
    test()