from .tropic01_l2_api_impl import L2APIImplementation
from .tropic01_l3_api_impl import L3APIImplementation


class Tropic01Model(L3APIImplementation, L2APIImplementation):
    """Model of the TROPIC01"""
