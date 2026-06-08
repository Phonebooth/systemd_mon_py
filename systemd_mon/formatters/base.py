class Base(object):
    def __init__(self, unit):
        self.unit = unit

    def as_html(self):
        raise NotImplementedError(
            "The formatter {0} does not provide an html formatted string".format(
                type(self).__name__))

    def as_text(self):
        raise NotImplementedError(
            "The formatter {0} does not provide a plain text string".format(
                type(self).__name__))
