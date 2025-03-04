class MessageError(Exception):
    """Generic error during message handling"""


class UnauthorizedInstantiationError(MessageError):
    """Instantiation of class is not authorized."""


class NegativeLengthError(MessageError):
    """Data field length is negative"""


class ListTooLongError(MessageError):
    """List is longer than expected."""


class TypeNotSupportedError(MessageError):
    """Input value type cannot be processed."""


class FieldAlreadyExistsError(MessageError):
    """Field is already instantiated in base class."""


class UnsupportedFieldTypeError(MessageError):
    """Type of field is not supported"""


class InsuficientDataLengthError(MessageError):
    """Field does not have enough bytes to be deserialized."""


class ReservedFieldNameError(MessageError):
    """Field name is reserved and shall not be used."""


class SubclassNotFoundError(MessageError):
    """Could not find subclass of current class."""


class NoValidSubclassError(MessageError):
    """Found subclass of current class but deserialization impossible."""


class DataValueError(MessageError):
    """Value out of bounds or format error"""
