# GENERATED ON 2025-02-20 15:25:12.100946
# BY internal.py VERSION 0.4
# INPUT FILE: 8e0b7d81d7ac0252fdbff9726bbb6ae084d7d9bab49f27cdbda22da3832091d8
#
from typing import Optional

from pydantic import StrictInt

from tvl.targets.model.internal.configuration_object import (
    ConfigObjectField,
    ConfigObjectRegister,
    ConfigurationObject,
    ConfigurationObjectModel,
)
from tvl.typing_utils import HexReprIntEnum


class CfgSleepMode(ConfigObjectRegister):
    sleep_mode_en = ConfigObjectField(0, 1)
    """When 1, TROPIC01 enters Sleep mode upon receiving a Sleep_Req L2
    Request Frame with SLEEP_KIND=SLEEP_MODE"""


class CfgUapPairingKeyWrite(ConfigObjectRegister):
    write_pkey_slot_0 = ConfigObjectField(0, 8)
    """Access privileges of the Pairing_Key_Write L3 Command packet to Pairing
    Key slot 0."""
    write_pkey_slot_1 = ConfigObjectField(8, 8)
    """Access privileges of the Pairing_Key_Write L3 Command packet to Pairing
    Key slot 1."""
    write_pkey_slot_2 = ConfigObjectField(16, 8)
    """Access privileges of the Pairing_Key_Write L3 Command packet to Pairing
    Key slot 2."""
    write_pkey_slot_3 = ConfigObjectField(24, 8)
    """Access privileges of the Pairing_Key_Write L3 Command packet to Pairing
    Key slot 3."""


class CfgUapPairingKeyRead(ConfigObjectRegister):
    read_pkey_slot_0 = ConfigObjectField(0, 8)
    """Access privileges of the Pairing_Key_Read L3 Command packet to Pairing
    Key slot 0."""
    read_pkey_slot_1 = ConfigObjectField(8, 8)
    """Access privileges of the Pairing_Key_Read L3 Command packet to Pairing
    Key slot 1."""
    read_pkey_slot_2 = ConfigObjectField(16, 8)
    """Access privileges of the Pairing_Key_Read L3 Command packet to Pairing
    Key slot 2."""
    read_pkey_slot_3 = ConfigObjectField(24, 8)
    """Access privileges of the Pairing_Key_Read L3 Command packet to Pairing
    Key slot 3."""


class CfgUapPairingKeyInvalidate(ConfigObjectRegister):
    invalidate_pkey_slot_0 = ConfigObjectField(0, 8)
    """Access privileges of the Pairing_Key_Invalidate L3 Command packet to
    Pairing Key slot 0."""
    invalidate_pkey_slot_1 = ConfigObjectField(8, 8)
    """Access privileges of the Pairing_Key_Invalidate L3 Command packet to
    Pairing Key slot 1."""
    invalidate_pkey_slot_2 = ConfigObjectField(16, 8)
    """Access privileges of the Pairing_Key_Invalidate L3 Command packet to
    Pairing Key slot 2."""
    invalidate_pkey_slot_3 = ConfigObjectField(24, 8)
    """Access privileges of the Pairing_Key_Invalidate L3 Command packet to
    Pairing Key slot 3."""


class CfgUapRConfigWriteErase(ConfigObjectRegister):
    r_config_write_erase = ConfigObjectField(0, 8)
    """Access privileges of the R_Config_Write and R_Config_Erase L3 Command
    packets to all COs. Refer to the 'User Access Privileges' section in the
    TROPIC01 Datasheet."""


class CfgUapRConfigRead(ConfigObjectRegister):
    r_config_read_cfg = ConfigObjectField(0, 8)
    """Access privileges of the R_Config_Read L3 Command packet to the
    Configuration COs. Refer to the 'User Access Privileges' section in the
    TROPIC01 Datasheet."""
    r_config_read_func = ConfigObjectField(8, 8)
    """Access privileges of the R_Config_Read L3 Command packet to the
    Functionality COs. Refer to the 'User Access Privileges' section in the
    TROPIC01 Datasheet."""


class CfgUapIConfigWrite(ConfigObjectRegister):
    i_config_write_cfg = ConfigObjectField(0, 8)
    """Access privileges of the I_Config_Write L3 Command packet to the
    Configuration COs. Refer to the 'User Access Privileges' section in the
    TROPIC01 Datasheet."""
    i_config_write_func = ConfigObjectField(8, 8)
    """Access privileges of the I_Config_Write L3 Command packet to the
    Functionality COs. Refer to the 'User Access Privileges' section in the
    TROPIC01 Datasheet."""


class CfgUapIConfigRead(ConfigObjectRegister):
    i_config_read_cfg = ConfigObjectField(0, 8)
    """Access privileges of the I_Config_Read L3 Command packet to the
    Configuration COs. Refer to the 'User Access Privileges' section in the
    TROPIC01 Datasheet."""
    i_config_read_func = ConfigObjectField(8, 8)
    """Access privileges of the I_Config_Read L3 Command packet to the
    Functionality COs. Refer to the 'User Access Privileges' section in the
    TROPIC01 Datasheet."""


class CfgUapPing(ConfigObjectRegister):
    ping = ConfigObjectField(0, 8)
    """Access privileges of the Ping L3 Command packet."""


class CfgUapRMemDataWrite(ConfigObjectRegister):
    write_udata_slot_0_127 = ConfigObjectField(0, 8)
    """Access privileges of the R_Mem_Data_Write L3 Command packet to slots 0
    - 127 of the User Data partition in R-Memory."""
    write_udata_slot_128_255 = ConfigObjectField(8, 8)
    """Access privileges of the R_Mem_Data_Write L3 Command packet to slots
    128 - 255 of the User Data partition in R-Memory."""
    write_udata_slot_256_383 = ConfigObjectField(16, 8)
    """Access privileges of the R_Mem_Data_Write L3 Command packet to slots
    256 - 383 of the User Data partition in R-Memory."""
    write_udata_slot_384_511 = ConfigObjectField(24, 8)
    """Access privileges of the R_Mem_Data_Write L3 Command packet to slots
    384 - 511 of the User Data partition in R-Memory."""


class CfgUapRMemDataRead(ConfigObjectRegister):
    read_udata_slot_0_127 = ConfigObjectField(0, 8)
    """Access privileges of the R_Mem_Data_Read L3 Command packet to slots 0 -
    127 of the User Data partition in R-Memory."""
    read_udata_slot_128_255 = ConfigObjectField(8, 8)
    """Access privileges of the R_Mem_Data_Read L3 Command packet to slots 128
    - 255 of the User Data partition in R-Memory."""
    read_udata_slot_256_383 = ConfigObjectField(16, 8)
    """Access privileges of the R_Mem_Data_Read L3 Command packet to slots 256
    - 383 of the User Data partition in R-Memory."""
    read_udata_slot_384_511 = ConfigObjectField(24, 8)
    """Access privileges of the R_Mem_Data_Read L3 Command packet to slots 385
    - 512 of the User Data partition in R-Memory."""


class CfgUapRMemDataErase(ConfigObjectRegister):
    erase_udata_slot_0_127 = ConfigObjectField(0, 8)
    """Access privileges of the R_Mem_Data_Erase L3 Command packet to slots 0
    - 127 of the User Data partition in R-Memory."""
    erase_udata_slot_128_255 = ConfigObjectField(8, 8)
    """Access privileges of the R_Mem_Data_Erase L3 Command packet to slots
    128 - 255 of the User Data partition in R-Memory."""
    erase_udata_slot_256_383 = ConfigObjectField(16, 8)
    """Access privileges of the R_Mem_Data_Erase L3 Command packet to slots
    256 - 383 of the User Data partition in R-Memory."""
    erase_udata_slot_384_511 = ConfigObjectField(24, 8)
    """Access privileges of the R_Mem_Data_Erase L3 Command packet to slots
    385 - 512 of the User Data partition in R-Memory."""


class CfgUapRandomValueGet(ConfigObjectRegister):
    random_value_get = ConfigObjectField(0, 8)
    """Access privileges of the Random_Value_Get L3 Command packet."""


class CfgUapEccKeyGenerate(ConfigObjectRegister):
    gen_ecckey_slot_0_7 = ConfigObjectField(0, 8)
    """Access privileges of the ECC_Key_Generate L3 Command packet to ECC Key
    slots 0-7."""
    gen_ecckey_slot_8_15 = ConfigObjectField(8, 8)
    """Access privileges of the ECC_Key_Generate L3 Command packet to ECC Key
    slots 8-15."""
    gen_ecckey_slot_16_23 = ConfigObjectField(16, 8)
    """Access privileges of the ECC_Key_Generate L3 Command packet to ECC Key
    slots 16-23."""
    gen_ecckey_slot_24_31 = ConfigObjectField(24, 8)
    """Access privileges of the ECC_Key_Generate L3 Command packet to ECC Key
    slots 24-31."""


class CfgUapEccKeyStore(ConfigObjectRegister):
    store_ecckey_slot_0_7 = ConfigObjectField(0, 8)
    """Access privileges of the ECC_Key_Store L3 Command packet to ECC Key
    slots 0-7."""
    store_ecckey_slot_8_15 = ConfigObjectField(8, 8)
    """Access privileges of the ECC_Key_Store L3 Command packet to ECC Key
    slots 8-15."""
    store_ecckey_slot_16_23 = ConfigObjectField(16, 8)
    """Access privileges of the ECC_Key_Store L3 Command packet to ECC Key
    slots 16-23."""
    store_ecckey_slot_24_31 = ConfigObjectField(24, 8)
    """Access privileges of the ECC_Key_Store L3 Command packet to ECC Key
    slots 24-31."""


class CfgUapEccKeyRead(ConfigObjectRegister):
    read_ecckey_slot_0_7 = ConfigObjectField(0, 8)
    """Access privileges of the ECC_Key_Read L3 Command packet to ECC Key
    slots 0-7."""
    read_ecckey_slot_8_15 = ConfigObjectField(8, 8)
    """Access privileges of the ECC_Key_Read L3 Command packet to ECC Key
    slots 8-15."""
    read_ecckey_slot_16_23 = ConfigObjectField(16, 8)
    """Access privileges of the ECC_Key_Read L3 Command packet to ECC Key
    slots 16-23."""
    read_ecckey_slot_24_31 = ConfigObjectField(24, 8)
    """Access privileges of the ECC_Key_Read L3 Command packet to ECC Key
    slots 24-31."""


class CfgUapEccKeyErase(ConfigObjectRegister):
    erase_ecckey_slot_0_7 = ConfigObjectField(0, 8)
    """Access privileges of the ECC_Key_Erase L3 Command packet to ECC Key
    slots 0-7."""
    erase_ecckey_slot_8_15 = ConfigObjectField(8, 8)
    """Access privileges of the ECC_Key_Erase L3 Command packet to ECC Key
    slots 8-15."""
    erase_ecckey_slot_16_23 = ConfigObjectField(16, 8)
    """Access privileges of the ECC_Key_Erase L3 Command packet to ECC Key
    slots 16-23."""
    erase_ecckey_slot_24_31 = ConfigObjectField(24, 8)
    """Access privileges of the ECC_Key_Erase L3 Command packet to ECC Key
    slots 24-31."""


class CfgUapEcdsaSign(ConfigObjectRegister):
    ecdsa_ecckey_slot_0_7 = ConfigObjectField(0, 8)
    """Access privileges of the ECDSA_Sign L3 Command packet to keys from ECC
    Key slots 0-7."""
    ecdsa_ecckey_slot_8_15 = ConfigObjectField(8, 8)
    """Access privileges of the ECDSA_Sign L3 Command packet to keys from ECC
    Key slots 8-15."""
    ecdsa_ecckey_slot_16_23 = ConfigObjectField(16, 8)
    """Access privileges of the ECDSA_Sign L3 Command packet to keys from ECC
    Key slots 16-23."""
    ecdsa_ecckey_slot_24_31 = ConfigObjectField(24, 8)
    """Access privileges of the ECDSA_Sign L3 Command packet to keys from ECC
    Key slots 24-31."""


class CfgUapEddsaSign(ConfigObjectRegister):
    eddsa_ecckey_slot_0_7 = ConfigObjectField(0, 8)
    """Access privileges of the EDDSA_Sign L3 Command packet to keys from ECC
    Key slots 0-7."""
    eddsa_ecckey_slot_8_15 = ConfigObjectField(8, 8)
    """Access privileges of the EDDSA_Sign L3 Command packet to keys from ECC
    Key slots 8-15."""
    eddsa_ecckey_slot_16_23 = ConfigObjectField(16, 8)
    """Access privileges of the EDDSA_Sign L3 Command packet to keys from ECC
    Key slots 16-23."""
    eddsa_ecckey_slot_24_31 = ConfigObjectField(24, 8)
    """Access privileges of the EDDSA_Sign L3 Command packet to keys from ECC
    Key slots 24-31."""


class CfgUapMcounterInit(ConfigObjectRegister):
    mcounter_init_0_3 = ConfigObjectField(0, 8)
    """Access privileges of the MCounter_Init L3 Command packet to Monotonic
    counters 0-3."""
    mcounter_init_4_7 = ConfigObjectField(8, 8)
    """Access privileges of the MCounter_Init L3 Command packet to Monotonic
    counters 4-7."""
    mcounter_init_8_11 = ConfigObjectField(16, 8)
    """Access privileges of the MCounter_Init L3 Command packet to Monotonic
    counters 8-11."""
    mcounter_init_12_15 = ConfigObjectField(24, 8)
    """Access privileges of the MCounter_Init L3 Command packet to Monotonic
    counters 12-15."""


class CfgUapMcounterGet(ConfigObjectRegister):
    mcounter_get_0_3 = ConfigObjectField(0, 8)
    """Access privileges of the MCounter_Get L3 Command packet to Monotonic
    counters 0-3."""
    mcounter_get_4_7 = ConfigObjectField(8, 8)
    """Access privileges of the MCounter_Get L3 Command packet to Monotonic
    counters 4-7."""
    mcounter_get_8_11 = ConfigObjectField(16, 8)
    """Access privileges of the MCounter_Get L3 Command packet to Monotonic
    counters 8-11."""
    mcounter_get_12_15 = ConfigObjectField(24, 8)
    """Access privileges of the MCounter_Get L3 Command packet to Monotonic
    counters 12-15."""


class CfgUapMcounterUpdate(ConfigObjectRegister):
    mcounter_update_0_3 = ConfigObjectField(0, 8)
    """Access privileges of the MCounter_Update L3 Command packet to Monotonic
    counters 0-3."""
    mcounter_update_4_7 = ConfigObjectField(8, 8)
    """Access privileges of the MCounter_Update L3 Command packet to Monotonic
    counters 4-7."""
    mcounter_update_8_11 = ConfigObjectField(16, 8)
    """Access privileges of the MCounter_Update L3 Command packet to Monotonic
    counters 8-11."""
    mcounter_update_12_15 = ConfigObjectField(24, 8)
    """Access privileges of the MCounter_Update L3 Command packet to Monotonic
    counters 12-15."""


class CfgUapMacAndDestroy(ConfigObjectRegister):
    macandd_0_31 = ConfigObjectField(0, 8)
    """Access privileges of the MAC_And_Destroy L3 Command packet (when
    executing a MAC-and-Destroy sequence) to slots 0-31 of the MAC-and-Destroy
    Partition of R-Memory."""
    macandd_32_63 = ConfigObjectField(8, 8)
    """Access privileges of the MAC_And_Destroy L3 Command packet (when
    executing a MAC-and-Destroy sequence) to slots 32-63 of the MAC-and-
    Destroy Partition of R-Memory."""
    macandd_64_95 = ConfigObjectField(16, 8)
    """Access privileges of the MAC_And_Destroy L3 Command packet (when
    executing a MAC-and-Destroy sequence) to slots 64-95 of the MAC-and-
    Destroy Partition of R-Memory."""
    macandd_96_127 = ConfigObjectField(24, 8)
    """Access privileges of the MAC_And_Destroy L3 Command packet (when
    executing a MAC-and-Destroy sequence) to slots 96-127 of the MAC-and-
    Destroy Partition of R-Memory."""


class ConfigObjectRegisterAddressEnum(HexReprIntEnum):
    CFG_SLEEP_MODE = 0x14
    CFG_UAP_PAIRING_KEY_WRITE = 0x20
    CFG_UAP_PAIRING_KEY_READ = 0x24
    CFG_UAP_PAIRING_KEY_INVALIDATE = 0x28
    CFG_UAP_R_CONFIG_WRITE_ERASE = 0x30
    CFG_UAP_R_CONFIG_READ = 0x34
    CFG_UAP_I_CONFIG_WRITE = 0x40
    CFG_UAP_I_CONFIG_READ = 0x44
    CFG_UAP_PING = 0x100
    CFG_UAP_R_MEM_DATA_WRITE = 0x110
    CFG_UAP_R_MEM_DATA_READ = 0x114
    CFG_UAP_R_MEM_DATA_ERASE = 0x118
    CFG_UAP_RANDOM_VALUE_GET = 0x120
    CFG_UAP_ECC_KEY_GENERATE = 0x130
    CFG_UAP_ECC_KEY_STORE = 0x134
    CFG_UAP_ECC_KEY_READ = 0x138
    CFG_UAP_ECC_KEY_ERASE = 0x13C
    CFG_UAP_ECDSA_SIGN = 0x140
    CFG_UAP_EDDSA_SIGN = 0x144
    CFG_UAP_MCOUNTER_INIT = 0x150
    CFG_UAP_MCOUNTER_GET = 0x154
    CFG_UAP_MCOUNTER_UPDATE = 0x158
    CFG_UAP_MAC_AND_DESTROY = 0x160


class ConfigurationObjectImpl(ConfigurationObject):
    def __init__(self, **kwargs: int) -> None:
        self.cfg_sleep_mode = CfgSleepMode(self, ConfigObjectRegisterAddressEnum.CFG_SLEEP_MODE)
        self.cfg_uap_pairing_key_write = CfgUapPairingKeyWrite(self, ConfigObjectRegisterAddressEnum.CFG_UAP_PAIRING_KEY_WRITE)
        self.cfg_uap_pairing_key_read = CfgUapPairingKeyRead(self, ConfigObjectRegisterAddressEnum.CFG_UAP_PAIRING_KEY_READ)
        self.cfg_uap_pairing_key_invalidate = CfgUapPairingKeyInvalidate(self, ConfigObjectRegisterAddressEnum.CFG_UAP_PAIRING_KEY_INVALIDATE)
        self.cfg_uap_r_config_write_erase = CfgUapRConfigWriteErase(self, ConfigObjectRegisterAddressEnum.CFG_UAP_R_CONFIG_WRITE_ERASE)
        self.cfg_uap_r_config_read = CfgUapRConfigRead(self, ConfigObjectRegisterAddressEnum.CFG_UAP_R_CONFIG_READ)
        self.cfg_uap_i_config_write = CfgUapIConfigWrite(self, ConfigObjectRegisterAddressEnum.CFG_UAP_I_CONFIG_WRITE)
        self.cfg_uap_i_config_read = CfgUapIConfigRead(self, ConfigObjectRegisterAddressEnum.CFG_UAP_I_CONFIG_READ)
        self.cfg_uap_ping = CfgUapPing(self, ConfigObjectRegisterAddressEnum.CFG_UAP_PING)
        self.cfg_uap_r_mem_data_write = CfgUapRMemDataWrite(self, ConfigObjectRegisterAddressEnum.CFG_UAP_R_MEM_DATA_WRITE)
        self.cfg_uap_r_mem_data_read = CfgUapRMemDataRead(self, ConfigObjectRegisterAddressEnum.CFG_UAP_R_MEM_DATA_READ)
        self.cfg_uap_r_mem_data_erase = CfgUapRMemDataErase(self, ConfigObjectRegisterAddressEnum.CFG_UAP_R_MEM_DATA_ERASE)
        self.cfg_uap_random_value_get = CfgUapRandomValueGet(self, ConfigObjectRegisterAddressEnum.CFG_UAP_RANDOM_VALUE_GET)
        self.cfg_uap_ecc_key_generate = CfgUapEccKeyGenerate(self, ConfigObjectRegisterAddressEnum.CFG_UAP_ECC_KEY_GENERATE)
        self.cfg_uap_ecc_key_store = CfgUapEccKeyStore(self, ConfigObjectRegisterAddressEnum.CFG_UAP_ECC_KEY_STORE)
        self.cfg_uap_ecc_key_read = CfgUapEccKeyRead(self, ConfigObjectRegisterAddressEnum.CFG_UAP_ECC_KEY_READ)
        self.cfg_uap_ecc_key_erase = CfgUapEccKeyErase(self, ConfigObjectRegisterAddressEnum.CFG_UAP_ECC_KEY_ERASE)
        self.cfg_uap_ecdsa_sign = CfgUapEcdsaSign(self, ConfigObjectRegisterAddressEnum.CFG_UAP_ECDSA_SIGN)
        self.cfg_uap_eddsa_sign = CfgUapEddsaSign(self, ConfigObjectRegisterAddressEnum.CFG_UAP_EDDSA_SIGN)
        self.cfg_uap_mcounter_init = CfgUapMcounterInit(self, ConfigObjectRegisterAddressEnum.CFG_UAP_MCOUNTER_INIT)
        self.cfg_uap_mcounter_get = CfgUapMcounterGet(self, ConfigObjectRegisterAddressEnum.CFG_UAP_MCOUNTER_GET)
        self.cfg_uap_mcounter_update = CfgUapMcounterUpdate(self, ConfigObjectRegisterAddressEnum.CFG_UAP_MCOUNTER_UPDATE)
        self.cfg_uap_mac_and_destroy = CfgUapMacAndDestroy(self, ConfigObjectRegisterAddressEnum.CFG_UAP_MAC_AND_DESTROY)
        super().__init__(**kwargs)


class ConfigurationObjectImplModel(ConfigurationObjectModel):
    cfg_sleep_mode: Optional[StrictInt]
    cfg_uap_pairing_key_write: Optional[StrictInt]
    cfg_uap_pairing_key_read: Optional[StrictInt]
    cfg_uap_pairing_key_invalidate: Optional[StrictInt]
    cfg_uap_r_config_write_erase: Optional[StrictInt]
    cfg_uap_r_config_read: Optional[StrictInt]
    cfg_uap_i_config_write: Optional[StrictInt]
    cfg_uap_i_config_read: Optional[StrictInt]
    cfg_uap_ping: Optional[StrictInt]
    cfg_uap_r_mem_data_write: Optional[StrictInt]
    cfg_uap_r_mem_data_read: Optional[StrictInt]
    cfg_uap_r_mem_data_erase: Optional[StrictInt]
    cfg_uap_random_value_get: Optional[StrictInt]
    cfg_uap_ecc_key_generate: Optional[StrictInt]
    cfg_uap_ecc_key_store: Optional[StrictInt]
    cfg_uap_ecc_key_read: Optional[StrictInt]
    cfg_uap_ecc_key_erase: Optional[StrictInt]
    cfg_uap_ecdsa_sign: Optional[StrictInt]
    cfg_uap_eddsa_sign: Optional[StrictInt]
    cfg_uap_mcounter_init: Optional[StrictInt]
    cfg_uap_mcounter_get: Optional[StrictInt]
    cfg_uap_mcounter_update: Optional[StrictInt]
    cfg_uap_mac_and_destroy: Optional[StrictInt]
