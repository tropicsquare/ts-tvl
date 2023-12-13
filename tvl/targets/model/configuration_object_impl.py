# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

# GENERATED ON 2023-07-07 10:57:27.809240
# BY configuration_object_generator.py VERSION 0.2
# INPUT FILE: a86fdee886bdfdb266dcf7bdeecef16ddac749b3a6ddac69f4c82e06fe12928d

from enum import IntEnum
from typing import Optional

from pydantic import StrictInt

from tvl.targets.model.internal.configuration_object import (
    AccessType,
    ConfigObjectField,
    ConfigObjectRegister,
    ConfigurationObject,
    ConfigurationObjectModel,
)


class CfgStartUp(ConfigObjectRegister):
    mbist = ConfigObjectField(0, 1, AccessType.W1C)
    """Execute Memory built-in self-test during start-up sequence. If test
    fails move to Alarm Mode."""
    fw_self_test = ConfigObjectField(1, 1, AccessType.W1C)
    """Execute self-test by a FW on internal CPU during start-up sequence. If
    test fails, move to Alarm Mode."""


class CfgSleepMode(ConfigObjectRegister):
    sleep_mode_en = ConfigObjectField(0, 1, AccessType.W1C)
    """When 1, TROPIC01 moves to Sleep mode upon receiving Sleep_Req L2
    Request Frame."""


class CfgSensors(ConfigObjectRegister):
    positive_glitch = ConfigObjectField(0, 1, AccessType.W1C)
    """TROPIC01 behavior upon detecting Positive Glitch on VDD Supply Voltage
    by Glitch Detector."""
    negative_glitch = ConfigObjectField(1, 1, AccessType.W1C)
    """TROPIC01 behavior upon detecting Negative Glitch on VDD Supply Voltage
    by Glitch Detector."""
    laser_attack = ConfigObjectField(2, 1, AccessType.W1C)
    """TROPIC01 behavior upon detecting Laser Attack by Laser Detector."""
    temperature_high = ConfigObjectField(3, 1, AccessType.W1C)
    """TROPIC01 behavior when it detects Temperature higher than
    $t_{HIGH}$."""
    temperature_low = ConfigObjectField(4, 1, AccessType.W1C)
    """TROPIC01 behavior when it detects Temperature lower than $t_{LOW}$."""
    em_attack = ConfigObjectField(5, 1, AccessType.W1C)
    """TROPIC01 behavior when it detects Electromagnetic Pulse by EM
    Detector."""
    shield_attack = ConfigObjectField(6, 1, AccessType.W1C)
    """TROPIC01 behavior when it detects tampering of its top level metal
    shield."""
    ecc_error = ConfigObjectField(7, 1, AccessType.W1C)
    """TROPIC01 behavior when it detects Error Correction Error during any of
    its calculations."""
    majority_error = ConfigObjectField(8, 1, AccessType.W1C)
    """TROPIC01 behavior when it detects Error on any internal data structure
    protected by Multiple majority encoding."""
    pin_verification_attack = ConfigObjectField(9, 1, AccessType.W1C)
    """TROPIC01 behavior when it detects an attack on execution of Mac-And-
    Destroy sequence by Pin Verification engine."""
    elliptic_curves_attack = ConfigObjectField(10, 1, AccessType.W1C)
    """TROPIC01 behavior when it detects an attack on Elliptic Curve
    Cryptography engine."""
    mcounters_attack = ConfigObjectField(11, 1, AccessType.W1C)
    """TROPIC01 behavior when it detects an attack on Monotonic Counters."""


class CfgAlarmMode(ConfigObjectRegister):
    complain = ConfigObjectField(0, 1, AccessType.W1C)
    """When 1, TROPIC01 responds with CHIP_STATUS[ALARM]=1 in Alarm mode."""


class CfgUapPairingKeyWrite(ConfigObjectRegister):
    write_pkey_slot_1 = ConfigObjectField(0, 8, AccessType.W1C)
    """Access Privileges of Pairing_Key_Write L3 Command packet to Pairing Key
    Slot 1."""
    write_pkey_slot_2 = ConfigObjectField(8, 8, AccessType.W1C)
    """Access Privileges of Pairing_Key_Write L3 Command packet to Pairing Key
    Slot 2."""
    write_pkey_slot_3 = ConfigObjectField(16, 8, AccessType.W1C)
    """Access Privileges of Pairing_Key_Write L3 Command packet to Pairing Key
    Slot 3."""
    write_pkey_slot_4 = ConfigObjectField(24, 8, AccessType.W1C)
    """Access Privileges of Pairing_Key_Write L3 Command packet to Pairing Key
    Slot 4."""


class CfgUapPairingKeyRead(ConfigObjectRegister):
    read_pkey_slot_1 = ConfigObjectField(0, 8, AccessType.W1C)
    """Access Privileges of Pairing_Key_Read L3 Command packet to Pairing Key
    Slot 1."""
    read_pkey_slot_2 = ConfigObjectField(8, 8, AccessType.W1C)
    """Access Privileges of Pairing_Key_Read L3 Command packet to Pairing Key
    Slot 2."""
    read_pkey_slot_3 = ConfigObjectField(16, 8, AccessType.W1C)
    """Access Privileges of Pairing_Key_Read L3 Command packet to Pairing Key
    Slot 3."""
    read_pkey_slot_4 = ConfigObjectField(24, 8, AccessType.W1C)
    """Access Privileges of Pairing_Key_Read L3 Command packet to Pairing Key
    Slot 4."""


class CfgUapRConfigWrite(ConfigObjectRegister):
    r_config_write_func = ConfigObjectField(0, 8, AccessType.W1C)
    """Access privileges of R_Config_Write L3 Command packet to
    'Functionality' configuration objects. Refer to 'User Access Privileges'
    section in TROPIC01 Datasheet."""
    r_config_write_cfg = ConfigObjectField(8, 8, AccessType.W1C)
    """Access privileges of R_Config_Write L3 Command packet to
    'Configuration' configuration objects. Refer to 'User Access Privileges'
    section in TROPIC01 Datasheet."""


class CfgUapRConfigRead(ConfigObjectRegister):
    r_config_read_func = ConfigObjectField(0, 8, AccessType.W1C)
    """Access privileges of R_Config_Read L3 Command packet to 'Functionality'
    configuration objects. Refer to 'User Access Privileges' section in
    TROPIC01 Datasheet."""
    r_config_read_cfg = ConfigObjectField(8, 8, AccessType.W1C)
    """Access privileges of R_Config_Read L3 Command packet to 'Configuration'
    configuration objects. Refer to 'User Access Privileges' section in
    TROPIC01 Datasheet."""


class CfgUapRConfigErase(ConfigObjectRegister):
    r_config_erase_func = ConfigObjectField(0, 8, AccessType.W1C)
    """Access privileges of R_Config_Erase L3 Command packet to
    'Functionality' configuration objects. Refer to 'User Access Privileges'
    section in TROPIC01 Datasheet."""
    r_config_erase_cfg = ConfigObjectField(8, 8, AccessType.W1C)
    """Access privileges of R_Config_Erase L3 Command packet to
    'Configuration' configuration objects. Refer to 'User Access Privileges'
    section in TROPIC01 Datasheet."""


class CfgUapIConfigWrite(ConfigObjectRegister):
    i_config_write_func = ConfigObjectField(0, 8, AccessType.W1C)
    """Access privileges of I_Config_Write L3 Command packet to
    'Functionality' configuration objects. Refer to 'User Access Privileges'
    section in TROPIC01 Datasheet."""
    i_config_write_cfg = ConfigObjectField(8, 8, AccessType.W1C)
    """Access privileges of I_Config_Write L3 Command packet to
    'Configuration' configuration objects. Refer to 'User Access Privileges'
    section in TROPIC01 Datasheet."""


class CfgUapIConfigRead(ConfigObjectRegister):
    i_config_read_func = ConfigObjectField(0, 8, AccessType.W1C)
    """Access privileges of I_Config_Read L3 Command packet to 'Functionality'
    configuration objects. Refer to 'User Access Privileges' section in
    TROPIC01 Datasheet."""
    i_config_read_cfg = ConfigObjectField(8, 8, AccessType.W1C)
    """Access privileges of I_Config_Read L3 Command packet to 'Configuration'
    configuration objects. Refer to 'User Access Privileges' section in
    TROPIC01 Datasheet."""


class CfgUapPing(ConfigObjectRegister):
    ping = ConfigObjectField(0, 8, AccessType.W1C)
    """Access Privileges of Ping L3 Command packet."""


class CfgUapRMemDataWrite(ConfigObjectRegister):
    write_udata_slot_1_128 = ConfigObjectField(0, 8, AccessType.W1C)
    """Access Privileges of R_Mem_Data_Write L3 Command packet to Slots 1 -
    128 of 'User Data' Partition in R-Memory."""
    write_udata_slot_129_256 = ConfigObjectField(8, 8, AccessType.W1C)
    """Access Privileges of R_Mem_Data_Write L3 Command packet to Slots 129 -
    256 of 'User Data' Partition in R-Memory."""
    write_udata_slot_257_384 = ConfigObjectField(16, 8, AccessType.W1C)
    """Access Privileges of R_Mem_Data_Write L3 Command packet to Slots 257 -
    384 of 'User Data' Partition in R-Memory."""
    write_udata_slot_385_512 = ConfigObjectField(24, 8, AccessType.W1C)
    """Access Privileges of R_Mem_Data_Write L3 Command packet to Slots 385 -
    512 of 'User Data' Partition in R-Memory."""


class CfgUapRMemDataRead(ConfigObjectRegister):
    read_udata_slot_1_128 = ConfigObjectField(0, 8, AccessType.W1C)
    """Access Privileges of R_Mem_Data_Read L3 Command packet to Slots 1 - 128
    of 'User Data' Partition in R-Memory."""
    read_udata_slot_129_256 = ConfigObjectField(8, 8, AccessType.W1C)
    """Access Privileges of R_Mem_Data_Read L3 Command packet to Slots 129 -
    256 of 'User Data' Partition in R-Memory."""
    read_udata_slot_257_384 = ConfigObjectField(16, 8, AccessType.W1C)
    """Access Privileges of R_Mem_Data_Read L3 Command packet to Slots 257 -
    384 of 'User Data' Partition in R-Memory."""
    read_udata_slot_385_512 = ConfigObjectField(24, 8, AccessType.W1C)
    """Access Privileges of R_Mem_Data_Read L3 Command packet to Slots 385 -
    512 of 'User Data' Partition in R-Memory."""


class CfgUapRMemDataErase(ConfigObjectRegister):
    erase_udata_slot_1_128 = ConfigObjectField(0, 8, AccessType.W1C)
    """Access Privileges of R_Mem_Data_Erase L3 Command packet to Slots 1 -
    128 of 'User Data' Partition in R-Memory."""
    erase_udata_slot_129_256 = ConfigObjectField(8, 8, AccessType.W1C)
    """Access Privileges of R_Mem_Data_Erase L3 Command packet to Slots 129 -
    256 of 'User Data' Partition in R-Memory."""
    erase_udata_slot_257_384 = ConfigObjectField(16, 8, AccessType.W1C)
    """Access Privileges of R_Mem_Data_Erase L3 Command packet to Slots 257 -
    384 of 'User Data' Partition in R-Memory."""
    erase_udata_slot_385_512 = ConfigObjectField(24, 8, AccessType.W1C)
    """Access Privileges of R_Mem_Data_Erase L3 Command packet to Slots 385 -
    512 of 'User Data' Partition in R-Memory."""


class CfgUapRandomValueGet(ConfigObjectRegister):
    random_value_get = ConfigObjectField(0, 8, AccessType.W1C)
    """Access Privileges of Random_Value_Get L3 Command packet."""


class CfgUapEccKeyGenerate(ConfigObjectRegister):
    gen_ecckey_slot_1_8 = ConfigObjectField(0, 8, AccessType.W1C)
    """Access Privileges of ECC_Key_Generate L3 Command packet to ECC Key
    Slots 1-8."""
    gen_ecckey_slot_9_16 = ConfigObjectField(8, 8, AccessType.W1C)
    """Access Privileges of ECC_Key_Generate L3 Command packet to ECC Key
    Slots 9-16."""
    gen_ecckey_slot_17_24 = ConfigObjectField(16, 8, AccessType.W1C)
    """Access Privileges of ECC_Key_Generate L3 Command packet to ECC Key
    Slots 17-24."""
    gen_ecckey_slot_25_32 = ConfigObjectField(24, 8, AccessType.W1C)
    """Access Privileges of ECC_Key_Generate L3 Command packet to ECC Key
    Slots 25-32."""


class CfgUapEccKeyStore(ConfigObjectRegister):
    store_ecckey_slot_1_8 = ConfigObjectField(0, 8, AccessType.W1C)
    """Access Privileges of ECC_Key_Store L3 Command packet to ECC Key Slots
    1-8."""
    store_ecckey_slot_9_16 = ConfigObjectField(8, 8, AccessType.W1C)
    """Access Privileges of ECC_Key_Store L3 Command packet to ECC Key Slots
    9-16."""
    store_ecckey_slot_17_24 = ConfigObjectField(16, 8, AccessType.W1C)
    """Access Privileges of ECC_Key_Store L3 Command packet to ECC Key Slots
    17-24."""
    store_ecckey_slot_25_32 = ConfigObjectField(24, 8, AccessType.W1C)
    """Access Privileges of ECC_Key_Store L3 Command packet to ECC Key Slots
    25-32."""


class CfgUapEccKeyRead(ConfigObjectRegister):
    read_ecckey_slot_1_8 = ConfigObjectField(0, 8, AccessType.W1C)
    """Access Privileges of ECC_Key_Read L3 Command packet to ECC Key Slots
    1-8."""
    read_ecckey_slot_9_16 = ConfigObjectField(8, 8, AccessType.W1C)
    """Access Privileges of ECC_Key_Read L3 Command packet to ECC Key Slots
    9-16."""
    read_ecckey_slot_17_24 = ConfigObjectField(16, 8, AccessType.W1C)
    """Access Privileges of ECC_Key_Read L3 Command packet to ECC Key Slots
    17-24."""
    read_ecckey_slot_25_32 = ConfigObjectField(24, 8, AccessType.W1C)
    """Access Privileges of ECC_Key_Read L3 Command packet to ECC Key Slots
    25-32."""


class CfgUapEccKeyErase(ConfigObjectRegister):
    erase_ecckey_slot_1_8 = ConfigObjectField(0, 8, AccessType.W1C)
    """Access Privileges of ECC_Key_Erase L3 Command packet to ECC Key Slots
    1-8."""
    erase_ecckey_slot_9_16 = ConfigObjectField(8, 8, AccessType.W1C)
    """Access Privileges of ECC_Key_Erase L3 Command packet to ECC Key Slots
    9-16."""
    erase_ecckey_slot_17_24 = ConfigObjectField(16, 8, AccessType.W1C)
    """Access Privileges of ECC_Key_Erase L3 Command packet to ECC Key Slots
    17-24."""
    erase_ecckey_slot_25_32 = ConfigObjectField(24, 8, AccessType.W1C)
    """Access Privileges of ECC_Key_Erase L3 Command packet to ECC Key Slots
    25-32."""


class CfgUapEcdsaSign(ConfigObjectRegister):
    ecdsa_ecckey_slot_1_8 = ConfigObjectField(0, 8, AccessType.W1C)
    """Access Privileges of ECDSA_Sign L3 Command packet with Keys from ECC
    Key Slots 1-8."""
    ecdsa_ecckey_slot_9_16 = ConfigObjectField(8, 8, AccessType.W1C)
    """Access Privileges of ECDSA_Sign L3 Command packet with Keys from ECC
    Key Slots 9-16."""
    ecdsa_ecckey_slot_17_24 = ConfigObjectField(16, 8, AccessType.W1C)
    """Access Privileges of ECDSA_Sign L3 Command packet with Keys from ECC
    Key Slots 17-24."""
    ecdsa_ecckey_slot_25_32 = ConfigObjectField(24, 8, AccessType.W1C)
    """Access Privileges of ECDSA_Sign L3 Command packet with Keys from ECC
    Key Slots 25-32."""


class CfgUapEddsaSign(ConfigObjectRegister):
    eddsa_ecckey_slot_1_8 = ConfigObjectField(0, 8, AccessType.W1C)
    """Access Privileges of EDDSA_Sign L3 Command packet with Keys from ECC
    Key Slots 1-8."""
    eddsa_ecckey_slot_9_16 = ConfigObjectField(8, 8, AccessType.W1C)
    """Access Privileges of EDDSA_Sign L3 Command packet with Keys from ECC
    Key Slots 9-16."""
    eddsa_ecckey_slot_17_24 = ConfigObjectField(16, 8, AccessType.W1C)
    """Access Privileges of EDDSA_Sign L3 Command packet with Keys from ECC
    Key Slots 17-24."""
    eddsa_ecckey_slot_25_32 = ConfigObjectField(24, 8, AccessType.W1C)
    """Access Privileges of EDDSA_Sign L3 Command packet with Keys from ECC
    Key Slots 25-32."""


class CfgUapMcounterInit(ConfigObjectRegister):
    mcounter_init_1_4 = ConfigObjectField(0, 8, AccessType.W1C)
    """Access Privileges of MCounter_Init L3 Command packet on Monotonic
    counters 1-4."""
    mcounter_init_5_8 = ConfigObjectField(8, 8, AccessType.W1C)
    """Access Privileges of MCounter_Init L3 Command packet on Monotonic
    counters 5-8."""
    mcounter_init_9_12 = ConfigObjectField(16, 8, AccessType.W1C)
    """Access Privileges of MCounter_Init L3 Command packet on Monotonic
    counters 9-12."""
    mcounter_init_13_16 = ConfigObjectField(24, 8, AccessType.W1C)
    """Access Privileges of MCounter_Init L3 Command packet on Monotonic
    counters 13-16."""


class CfgUapMcounterGet(ConfigObjectRegister):
    mcounter_get_1_4 = ConfigObjectField(0, 8, AccessType.W1C)
    """Access Privileges of MCounter_Get L3 Command packet on Monotonic
    counters 1-4."""
    mcounter_get_5_8 = ConfigObjectField(8, 8, AccessType.W1C)
    """Access Privileges of MCounter_Get L3 Command packet on Monotonic
    counters 5-8."""
    mcounter_get_9_12 = ConfigObjectField(16, 8, AccessType.W1C)
    """Access Privileges of MCounter_Get L3 Command packet on Monotonic
    counters 9-12."""
    mcounter_get_13_16 = ConfigObjectField(24, 8, AccessType.W1C)
    """Access Privileges of MCounter_Get L3 Command packet on Monotonic
    counters 13-16."""


class CfgUapMcounterUpdate(ConfigObjectRegister):
    mcounter_update_1_4 = ConfigObjectField(0, 8, AccessType.W1C)
    """Access Privileges of MCounter_Update L3 Command packet on Monotonic
    counters 1-4."""
    mcounter_update_5_8 = ConfigObjectField(8, 8, AccessType.W1C)
    """Access Privileges of MCounter_Update L3 Command packet on Monotonic
    counters 5-8."""
    mcounter_update_9_12 = ConfigObjectField(16, 8, AccessType.W1C)
    """Access Privileges of MCounter_Update L3 Command packet on Monotonic
    counters 9-12."""
    mcounter_update_13_16 = ConfigObjectField(24, 8, AccessType.W1C)
    """Access Privileges of MCounter_Update L3 Command packet on Monotonic
    counters 13-16."""


class CfgUapMacAndDestroy(ConfigObjectRegister):
    macandd_1_32 = ConfigObjectField(0, 8, AccessType.W1C)
    """Access Privileges of MAC_And_Destroy L3 Command packet when executing
    MAC-and-Destroy sequence to Slots 1-32 of Mac-And-Destroy Partition of
    R-Memory."""
    macandd_33_64 = ConfigObjectField(8, 8, AccessType.W1C)
    """Access Privileges of MAC_And_Destroy L3 Command packet when executing
    MAC-and-Destroy sequence to Slots 33-64 of Mac-And-Destroy Partition of
    R-Memory."""
    macandd_65_96 = ConfigObjectField(16, 8, AccessType.W1C)
    """Access Privileges of MAC_And_Destroy L3 Command packet when executing
    MAC-and-Destroy sequence to Slots 65-96 of Mac-And-Destroy Partition of
    R-Memory."""
    macandd_97_128 = ConfigObjectField(24, 8, AccessType.W1C)
    """Access Privileges of MAC_And_Destroy L3 Command packet when executing
    MAC-and-Destroy sequence to Slots 97-128 of Mac-And-Destroy Partition of
    R-Memory."""


class CfgUapSerialCodeGet(ConfigObjectRegister):
    serial_code = ConfigObjectField(0, 8, AccessType.W1C)
    """Access Privileges of Serial_Code_Get L3 Command packet."""


class ConfigObjectRegisterAddressEnum(IntEnum):
    CFG_START_UP = 0x00
    CFG_SLEEP_MODE = 0x04
    CFG_SENSORS = 0x08
    CFG_ALARM_MODE = 0x0C
    CFG_UAP_PAIRING_KEY_WRITE = 0x20
    CFG_UAP_PAIRING_KEY_READ = 0x24
    CFG_UAP_R_CONFIG_WRITE = 0x30
    CFG_UAP_R_CONFIG_READ = 0x34
    CFG_UAP_R_CONFIG_ERASE = 0x38
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
    CFG_UAP_SERIAL_CODE_GET = 0x170


class ConfigurationObjectImpl(ConfigurationObject):
    def __init__(self, **kwargs: int) -> None:
        self.cfg_start_up = CfgStartUp(ConfigObjectRegisterAddressEnum.CFG_START_UP, 0x00000003)
        self.cfg_sleep_mode = CfgSleepMode(ConfigObjectRegisterAddressEnum.CFG_SLEEP_MODE, 0x00000001)
        self.cfg_sensors = CfgSensors(ConfigObjectRegisterAddressEnum.CFG_SENSORS, 0x00000FFF)
        self.cfg_alarm_mode = CfgAlarmMode(ConfigObjectRegisterAddressEnum.CFG_ALARM_MODE, 0x00000001)
        self.cfg_uap_pairing_key_write = CfgUapPairingKeyWrite(ConfigObjectRegisterAddressEnum.CFG_UAP_PAIRING_KEY_WRITE, 0xFFFFFFFF)
        self.cfg_uap_pairing_key_read = CfgUapPairingKeyRead(ConfigObjectRegisterAddressEnum.CFG_UAP_PAIRING_KEY_READ, 0xFFFFFFFF)
        self.cfg_uap_r_config_write = CfgUapRConfigWrite(ConfigObjectRegisterAddressEnum.CFG_UAP_R_CONFIG_WRITE, 0x0000FFFF)
        self.cfg_uap_r_config_read = CfgUapRConfigRead(ConfigObjectRegisterAddressEnum.CFG_UAP_R_CONFIG_READ, 0x0000FFFF)
        self.cfg_uap_r_config_erase = CfgUapRConfigErase(ConfigObjectRegisterAddressEnum.CFG_UAP_R_CONFIG_ERASE, 0x0000FFFF)
        self.cfg_uap_i_config_write = CfgUapIConfigWrite(ConfigObjectRegisterAddressEnum.CFG_UAP_I_CONFIG_WRITE, 0x0000FFFF)
        self.cfg_uap_i_config_read = CfgUapIConfigRead(ConfigObjectRegisterAddressEnum.CFG_UAP_I_CONFIG_READ, 0x0000FFFF)
        self.cfg_uap_ping = CfgUapPing(ConfigObjectRegisterAddressEnum.CFG_UAP_PING, 0x000000FF)
        self.cfg_uap_r_mem_data_write = CfgUapRMemDataWrite(ConfigObjectRegisterAddressEnum.CFG_UAP_R_MEM_DATA_WRITE, 0xFFFFFFFF)
        self.cfg_uap_r_mem_data_read = CfgUapRMemDataRead(ConfigObjectRegisterAddressEnum.CFG_UAP_R_MEM_DATA_READ, 0xFFFFFFFF)
        self.cfg_uap_r_mem_data_erase = CfgUapRMemDataErase(ConfigObjectRegisterAddressEnum.CFG_UAP_R_MEM_DATA_ERASE, 0xFFFFFFFF)
        self.cfg_uap_random_value_get = CfgUapRandomValueGet(ConfigObjectRegisterAddressEnum.CFG_UAP_RANDOM_VALUE_GET, 0x000000FF)
        self.cfg_uap_ecc_key_generate = CfgUapEccKeyGenerate(ConfigObjectRegisterAddressEnum.CFG_UAP_ECC_KEY_GENERATE, 0xFFFFFFFF)
        self.cfg_uap_ecc_key_store = CfgUapEccKeyStore(ConfigObjectRegisterAddressEnum.CFG_UAP_ECC_KEY_STORE, 0xFFFFFFFF)
        self.cfg_uap_ecc_key_read = CfgUapEccKeyRead(ConfigObjectRegisterAddressEnum.CFG_UAP_ECC_KEY_READ, 0xFFFFFFFF)
        self.cfg_uap_ecc_key_erase = CfgUapEccKeyErase(ConfigObjectRegisterAddressEnum.CFG_UAP_ECC_KEY_ERASE, 0xFFFFFFFF)
        self.cfg_uap_ecdsa_sign = CfgUapEcdsaSign(ConfigObjectRegisterAddressEnum.CFG_UAP_ECDSA_SIGN, 0xFFFFFFFF)
        self.cfg_uap_eddsa_sign = CfgUapEddsaSign(ConfigObjectRegisterAddressEnum.CFG_UAP_EDDSA_SIGN, 0xFFFFFFFF)
        self.cfg_uap_mcounter_init = CfgUapMcounterInit(ConfigObjectRegisterAddressEnum.CFG_UAP_MCOUNTER_INIT, 0xFFFFFFFF)
        self.cfg_uap_mcounter_get = CfgUapMcounterGet(ConfigObjectRegisterAddressEnum.CFG_UAP_MCOUNTER_GET, 0xFFFFFFFF)
        self.cfg_uap_mcounter_update = CfgUapMcounterUpdate(ConfigObjectRegisterAddressEnum.CFG_UAP_MCOUNTER_UPDATE, 0xFFFFFFFF)
        self.cfg_uap_mac_and_destroy = CfgUapMacAndDestroy(ConfigObjectRegisterAddressEnum.CFG_UAP_MAC_AND_DESTROY, 0xFFFFFFFF)
        self.cfg_uap_serial_code_get = CfgUapSerialCodeGet(ConfigObjectRegisterAddressEnum.CFG_UAP_SERIAL_CODE_GET, 0x000000FF)
        super().__init__(**kwargs)


class ConfigurationObjectImplModel(ConfigurationObjectModel):
    cfg_start_up: Optional[StrictInt]
    cfg_sleep_mode: Optional[StrictInt]
    cfg_sensors: Optional[StrictInt]
    cfg_alarm_mode: Optional[StrictInt]
    cfg_uap_pairing_key_write: Optional[StrictInt]
    cfg_uap_pairing_key_read: Optional[StrictInt]
    cfg_uap_r_config_write: Optional[StrictInt]
    cfg_uap_r_config_read: Optional[StrictInt]
    cfg_uap_r_config_erase: Optional[StrictInt]
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
    cfg_uap_serial_code_get: Optional[StrictInt]
