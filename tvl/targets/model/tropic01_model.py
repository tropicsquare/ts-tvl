from .tropic01_l2_api_impl import L2APIImplementation
from .tropic01_l3_api_impl import L3APIImplementation


class Tropic01Model(L2APIImplementation, L3APIImplementation):
    """Model of the TROPIC01"""
