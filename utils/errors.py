
class Error(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

    def __repr__(self):
        return f'{self.__class__.__qualname__}({self.message!r}, payload={self.payload!r}, status_code={self.status_code})'


class NotFromOutboxError(Error):
    pass

class ActivityNotFoundError(Error):
    status_code = 404


class BadActivityError(Error):
    pass


class RecursionLimitExceededError(BadActivityError):
    pass


class UnexpectedActivityTypeError(BadActivityError):
    pass
