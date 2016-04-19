from html.parser import HTMLParser


class AbsenceRecord:
    """
    Store information about absence
    """
    def __init__(self, date, hours):
        """
        :param date: day when absence have place
        :type date: datetime.data
        :param hours: which hours have been skipped (increasing order)
        :type hours: [int]
        """
        self.date = date
        self.hours = hours


class HTMLStatefulParser(HTMLParser):
    #todo: docs
    def __init__(self):
        self.state = 'start'
        super().__init__()

    def handle_starttag(self, tag, attrs):
        try:
            handler = getattr(self, 'handle_starttag_state_' + self.state)
            handler(self, tag, attrs)
        except AttributeError:
            pass

    def handle_endtag(self, tag):
        try:
            handler = getattr(self, 'handle_endtag_state_' + self.state)
            handler(self, tag)
        except AttributeError:
            pass

    def handle_data(self, data):
        try:
            handler = getattr(self, 'handle_data_state_' + self.state)
            handler(self, data)
        except AttributeError:
            pass


class LibrusParser(HTMLStatefulParser):
    def __init__(self):
        self.results = []
        super().__init__()

    def handle_starttag_state_start(self, tag, attrs):
        if len(attrs) != 1:
            return None
        if tag == 'tr':
            if attrs[0] in [('class', 'line0'), ('class', 'line1')]:
                self.state = 'date'

    def handle_starttag_state_date(self, tag, attrs):
        if tag != 'td' or len(attrs) != 0:
            self.state = 'start'
            return None

    def handle_data_state_date(self, data):
        # todo: implement
        # on success should switch to state premain
        pass

    def handle_endtag_state_date(self, tag):
        # this function should never by called when processing correct data
        self.state = 'start'

    def handle_starttag_state_premain(self, tag, attrs):
        if tag == 'td':
            self.state = 'main'
        else
            self.state = 'start'

    def handle_endtag_state_premain(self, tag):
        self.state = 'start'

    def handle_starttag_state_main(self, tag, attrs):
        if tag == 'p':
            self.state = 'box'
            return None
        if tag == 'a':
            return None
        self.state = 'start'

    def handle_endtag_state_main(self, tag):
        if tag != 'td':
            self.state = 'start'
            return None
        self.results.append(AbsenceRecord(self.date, self.hours))
        self.state = 'start'

    def handle_starttag_state_box(self, tag, attrs):




