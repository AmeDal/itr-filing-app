from enum import Enum

class DocumentType(str, Enum):
    AS26 = "AS26"
    AIS = "AIS"
    TIS = "TIS"
    FORM_16 = "FORM_16"
    TRADING_REPORT = "TRADING_REPORT"
    BANK_STATEMENT = "BANK_STATEMENT"
    OTHER = "OTHER"

class ITRType(str, Enum):
    ITR1 = "ITR-1"
    ITR2 = "ITR-2"
    ITR3 = "ITR-3"
    ITR4 = "ITR-4"
