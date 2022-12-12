class ReportError(Exception):
    def __init__(self, msg):
        super(ReportError, self).__init__(msg)
        self.msg = msg

    def __str__(self):
        return self.msg
