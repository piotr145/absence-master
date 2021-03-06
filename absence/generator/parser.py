from html.parser import HTMLParser
import re
import datetime


class AbsenceRecord:
    """
    Store information about absence
    """
    def __init__(self, date, hours):
        """
        :param date: day when absence have place
        :type date: datetime.date
        :param hours: which hours have been skipped (increasing order)
        :type hours: [int]
        """
        self.date = date
        self.hours = hours

    def __lt__(self, other):
        return self.date < other.date

    def __repr__(self):
        return self.date.isoformat() + ' ' + self.hours.__repr__()


class HTMLStatefulParser(HTMLParser):
    """
    Use simple state machine to handle different stages of parsing
    """
    def __init__(self):
        super().__init__()
        self.state = 'start'

    def handle_starttag(self, tag, attrs):
        try:
            handler = getattr(self, 'handle_starttag_state_' + self.state)
            handler(tag, attrs)
        except AttributeError:
            pass

    def handle_endtag(self, tag):
        try:
            handler = getattr(self, 'handle_endtag_state_' + self.state)
            handler(tag)
        except AttributeError:
            pass

    def handle_data(self, data):
        try:
            handler = getattr(self, 'handle_data_state_' + self.state)
            handler(data)
        except AttributeError:
            pass


class LibrusParser(HTMLStatefulParser):
    """
    Parse HTMLs from Librus Synergia
    """
    date_re = re.compile(r'([0-9]{4})-([0-9]{2})-([0-9]{2}) .*')
    nb_type_re = re.compile(r'Rodzaj: nieobecność\<')
    nb_hour_re = re.compile(r'.*Godzina lekcyjna: ([0-9]+)\<')

    def __init__(self):
        super().__init__()
        self.results = []
        self.hours = []
        self.date = None

    def handle_starttag_state_start(self, tag, attrs):
        self.hours = []
        if tag == 'tr' and len(attrs) == 1:
            if attrs[0] in [('class', 'line0'), ('class', 'line1')]:
                self.state = 'date'

    def handle_data_state_date(self, data):
        match = self.date_re.match(data)
        if match is None:
            return None
        args = [int(match.group(x)) for x in range(1, 4)]
        try:
            self.date = datetime.date(*args)
        except ValueError:
            return None
        self.state = 'main'

    def handle_endtag_state_date(self, tag):
        if tag == 'tr':
            self.state = 'start'

    def handle_starttag_state_main(self, tag, attrs):
        if tag == 'p':
            self.state = 'box'

    def handle_endtag_state_main(self, tag):
        if tag == 'tr':
            if len(self.hours) > 0:
                self.results.append(AbsenceRecord(self.date, self.hours))
            self.state = 'start'

    def handle_starttag_state_box(self, tag, attrs):
        if tag == 'a':
            for (key, value) in attrs:
                if key == 'title':
                    self.parse_box(value)

    def handle_endtag_state_box(self, tag):
        if tag == 'tr':
            self.state = 'start'
            return None
        if tag == 'p':
            self.state = 'main'

    def parse_box(self, data):
        if self.nb_type_re.match(data) is None:
            return None
        match = self.nb_hour_re.match(data)
        try:
            self.hours.append(int(match.group(1)))
        except AttributeError:
            pass
