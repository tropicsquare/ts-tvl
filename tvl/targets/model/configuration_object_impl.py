# GENERATED ON 2024-05-09 09:37:02.379797
# BY configuration_object_generator.py VERSION 0.3
# INPUT FILE: 9a53604569b8f7927ee6fc59814a64817b72964c69f6e2818a37ea8a26aed66f
#
# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

from enum import IntEnum
from typing import Optional

from pydantic import StrictInt

from tvl.targets.model.internal.configuration_object import AccessType
from tvl.targets.model.internal.configuration_object import (
    ConfigObjectField,
    ConfigObjectRegister,
    ConfigurationObject,
    ConfigurationObjectModel,
)


class CfgStartUp(ConfigObjectRegister):
    mbist_dis = ConfigObjectField(1, 1, AccessType.W1C)
    """Configuration of the mutable FW test during start-up. If the test
    fails, TROPIC01 enters Alarm Mode."""
    rngtest_dis = ConfigObjectField(2, 1, AccessType.W1C)
    """PTRNG test configuration in Start-up mode."""
    maintenance_ena = ConfigObjectField(3, 1, AccessType.W1C)
    """Configuration of Maintenance restart."""
    cpu_fw_verify_dis = ConfigObjectField(4, 1, AccessType.W1C)
    """Configuration of the CPU mutable FW signature verification during
    start-up. If the test fails, TROPIC01 stays in Startup Mode and does not
    start the mutable FW."""
    spect_fw_verify_dis = ConfigObjectField(5, 1, AccessType.W1C)
    """Configuration of the SPECT mutable FW signature verification during
    start-up. If the test fails, TROPIC01 stays in Startup Mode and does not
    start the mutable FW."""


class CfgSleepMode(ConfigObjectRegister):
    sleep_mode_en = ConfigObjectField(0, 1, AccessType.W1C)
    """When 1, TROPIC01 enters Sleep mode upon receiving a Sleep_Req L2
    Request Frame with SLEEP_KIND=SLEEP_MODE"""
    deep_sleep_mode_en = ConfigObjectField(1, 1, AccessType.W1C)
    """When 1, TROPIC01 enters Deep Sleep mode upon receiving a Sleep_Req L2
    Request Frame."""


class CfgSensors(ConfigObjectRegister):
    ptrng0_test_dis = ConfigObjectField(0, 1, AccessType.W1C)
    """TROPIC01 behavior when TRNG0 detects low entropy or error on internal
    redundancy encodings."""
    ptrng1_test_dis = ConfigObjectField(1, 1, AccessType.W1C)
    """TROPIC01 behavior when TRNG1 detects low entropy or error on internal
    redundancy encodings."""
    oscillator_mon_dis = ConfigObjectField(2, 1, AccessType.W1C)
    """TROPIC01 behavior when its internal oscillator detects too low
    frequency."""
    shield_dis = ConfigObjectField(3, 1, AccessType.W1C)
    """TROPIC01 behavior when its top metal layer active shield detects
    tampering or an error on internal redundancy encdoings."""
    voltage_mon_dis = ConfigObjectField(4, 1, AccessType.W1C)
    """TROPIC01 behavior when its voltage monitor detects overvoltage or
    undervoltage on VCC."""
    glitch_det_dis = ConfigObjectField(5, 1, AccessType.W1C)
    """TROPIC01 behavior when its glitch detector detects a glitch on VCC."""
    temp_sens_dis = ConfigObjectField(6, 1, AccessType.W1C)
    """TROPIC01 behavior when its temperature sensor detects overtemperature
    or undertemperature."""
    laser_det_dis = ConfigObjectField(7, 1, AccessType.W1C)
    """TROPIC01 behavior when its laser detector detects an laser attack."""
    em_pulse_det_dis = ConfigObjectField(8, 1, AccessType.W1C)
    """TROPIC01 behavior when its Electromagnetic Pulse detects an laser
    attack."""
    cpu_alert_dis = ConfigObjectField(9, 1, AccessType.W1C)
    """TROPIC01 behavior when its RISCV CPU detects an attack on its memories,
    register file or instruction pipeline."""
    pin_verif_bit_flip_dis = ConfigObjectField(10, 1, AccessType.W1C)
    """TROPIC01 behavior when its Pin Verification engine detects bit flip on
    its redundancy encoding mechanisms."""
    scb_bit_flip_dis = ConfigObjectField(11, 1, AccessType.W1C)
    """TROPIC01 behavior when its Secure Channel Block detects bit flip on its
    redundancy encoding mechanisms."""
    cpb_bit_flip_dis = ConfigObjectField(12, 1, AccessType.W1C)
    """TROPIC01 behavior when its Command Processing Block detects bit flip on
    its redundancy encoding mechanisms."""
    ecc_bit_flip_dis = ConfigObjectField(13, 1, AccessType.W1C)
    """TROPIC01 behavior when its ECC engine detects bit flip on its
    redundancy encoding mechanisms."""
    r_mem_bit_flip_dis = ConfigObjectField(14, 1, AccessType.W1C)
    """TROPIC01 behavior when its R Memory controller detects bit flip on its
    redundancy encoding mechanisms."""
    ekdb_bit_flip_dis = ConfigObjectField(15, 1, AccessType.W1C)
    """TROPIC01 behavior when its Entropy and Key distribution engine detects
    bit flip on its redundancy encoding mechanisms."""
    i_mem_bit_flip_dis = ConfigObjectField(16, 1, AccessType.W1C)
    """TROPIC01 behavior when its I Memory controller detects bit flip on its
    redundancy encoding mechanisms."""
    platform_bit_flip_dis = ConfigObjectField(17, 1, AccessType.W1C)
    """TROPIC01 behavior when its platform management logic (silicon life-
    cycle and SoC control) detects bit flip on its redundancy encoding
    mechanisms."""


class CfgDebug(ConfigObjectRegister):
    fw_log_en = ConfigObjectField(0, 1, AccessType.W1C)
    """TROPIC01 FW Logging enable."""


class CfgUapPairingKeyWrite(ConfigObjectRegister):
    write_pkey_slot_0 = ConfigObjectField(0, 8, AccessType.W1C)
    """Access privileges of the Pairing_Key_Write L3 Command packet to Pairing
    Key slot 0."""
    write_pkey_slot_1 = ConfigObjectField(8, 8, AccessType.W1C)
    """Access privileges of the Pairing_Key_Write L3 Command packet to Pairing
    Key slot 1."""
    write_pkey_slot_2 = ConfigObjectField(16, 8, AccessType.W1C)
    """Access privileges of the Pairing_Key_Write L3 Command packet to Pairing
    Key slot 2."""
    write_pkey_slot_3 = ConfigObjectField(24, 8, AccessType.W1C)
    """Access privileges of the Pairing_Key_Write L3 Command packet to Pairing
    Key slot 3."""


class CfgUapPairingKeyRead(ConfigObjectRegister):
    read_pkey_slot_0 = ConfigObjectField(0, 8, AccessType.W1C)
    """Access privileges of the Pairing_Key_Read L3 Command packet to Pairing
    Key slot 0."""
    read_pkey_slot_1 = ConfigObjectField(8, 8, AccessType.W1C)
    """Access privileges of the Pairing_Key_Read L3 Command packet to Pairing
    Key slot 1."""
    read_pkey_slot_2 = ConfigObjectField(16, 8, AccessType.W1C)
    """Access privileges of the Pairing_Key_Read L3 Command packet to Pairing
    Key slot 2."""
    read_pkey_slot_3 = ConfigObjectField(24, 8, AccessType.W1C)
    """Access privileges of the Pairing_Key_Read L3 Command packet to Pairing
    Key slot 3."""


class CfgUapRConfigWrite(ConfigObjectRegister):
    r_config_write_func = ConfigObjectField(0, 8, AccessType.W1C)
    """Access privileges of the R_Config_Write L3 Command packet to the
    Functionality COs. Refer to the 'User Access Privileges' section in the
    TROPIC01 Datasheet."""
    r_config_write_cfg = ConfigObjectField(8, 8, AccessType.W1C)
    """Access privileges of the R_Config_Write L3 Command packet to the
    Configuration COs. Refer to the 'User Access Privileges' section in the
    TROPIC01 Datasheet."""


class CfgUapRConfigRead(ConfigObjectRegister):
    r_config_read_func = ConfigObjectField(0, 8, AccessType.W1C)
    """Access privileges of the R_Config_Read L3 Command packet to the
    Functionality COs. Refer to the 'User Access Privileges' section in the
    TROPIC01 Datasheet."""
    r_config_read_cfg = ConfigObjectField(8, 8, AccessType.W1C)
    """Access privileges of the R_Config_Read L3 Command packet to the
    Configuration COs. Refer to the 'User Access Privileges' section in the
    TROPIC01 Datasheet."""


class CfgUapRConfigErase(ConfigObjectRegister):
    r_config_erase_func = ConfigObjectField(0, 8, AccessType.W1C)
    """Access privileges of the R_Config_Erase L3 Command packet to the
    Functionality COs. Refer to the 'User Access Privileges' section in the
    TROPIC01 Datasheet."""
    r_config_erase_cfg = ConfigObjectField(8, 8, AccessType.W1C)
    """Access privileges of the R_Config_Erase L3 Command packet to the
    Configuration COs. Refer to the 'User Access Privileges' section in the
    TROPIC01 Datasheet."""


class CfgUapIConfigWrite(ConfigObjectRegister):
    i_config_write_func = ConfigObjectField(0, 8, AccessType.W1C)
    """Access privileges of the I_Config_Write L3 Command packet to the
    Functionality COs. Refer to the 'User Access Privileges' section in the
    TROPIC01 Datasheet."""
    i_config_write_cfg = ConfigObjectField(8, 8, AccessType.W1C)
    """Access privileges of the I_Config_Write L3 Command packet to the
    Configuration COs. Refer to the 'User Access Privileges' section in the
    TROPIC01 Datasheet."""


class CfgUapIConfigRead(ConfigObjectRegister):
    i_config_read_func = ConfigObjectField(0, 8, AccessType.W1C)
    """Access privileges of the I_Config_Read L3 Command packet to the
    Functionality COs. Refer to the 'User Access Privileges' section in the
    TROPIC01 Datasheet."""
    i_config_read_cfg = ConfigObjectField(8, 8, AccessType.W1C)
    """Access privileges of the I_Config_Read L3 Command packet to the
    Configuration COs. Refer to the 'User Access Privileges' section in the
    TROPIC01 Datasheet."""


class CfgUapPing(ConfigObjectRegister):
    ping = ConfigObjectField(0, 8, AccessType.W1C)
    """Access privileges of the Ping L3 Command packet."""


class CfgUapRMemDataWrite(ConfigObjectRegister):
    write_udata_slot_1_128 = ConfigObjectField(0, 8, AccessType.W1C)
    """Access privileges of the R_Mem_Data_Write L3 Command packet to slots 1
    - 128 of the User Data partition in R-Memory."""
    write_udata_slot_129_256 = ConfigObjectField(8, 8, AccessType.W1C)
    """Access privileges of the R_Mem_Data_Write L3 Command packet to slots
    129 - 256 of the User Data partition in R-Memory."""
    write_udata_slot_257_384 = ConfigObjectField(16, 8, AccessType.W1C)
    """Access privileges of the R_Mem_Data_Write L3 Command packet to slots
    257 - 384 of the User Data partition in R-Memory."""
    write_udata_slot_385_512 = ConfigObjectField(24, 8, AccessType.W1C)
    """Access privileges of the R_Mem_Data_Write L3 Command packet to slots
    385 - 512 of the User Data partition in R-Memory."""


class CfgUapRMemDataRead(ConfigObjectRegister):
    read_udata_slot_1_128 = ConfigObjectField(0, 8, AccessType.W1C)
    """Access privileges of the R_Mem_Data_Read L3 Command packet to slots 1 -
    128 of the User Data partition in R-Memory."""
    read_udata_slot_129_256 = ConfigObjectField(8, 8, AccessType.W1C)
    """Access privileges of the R_Mem_Data_Read L3 Command packet to slots 129
    - 256 of the User Data partition in R-Memory."""
    read_udata_slot_257_384 = ConfigObjectField(16, 8, AccessType.W1C)
    """Access privileges of the R_Mem_Data_Read L3 Command packet to slots 257
    - 384 of the User Data partition in R-Memory."""
    read_udata_slot_385_512 = ConfigObjectField(24, 8, AccessType.W1C)
    """Access privileges of the R_Mem_Data_Read L3 Command packet to slots 385
    - 512 of the User Data partition in R-Memory."""


class CfgUapRMemDataErase(ConfigObjectRegister):
    erase_udata_slot_1_128 = ConfigObjectField(0, 8, AccessType.W1C)
    """Access privileges of the R_Mem_Data_Erase L3 Command packet to slots 1
    - 128 of the User Data partition in R-Memory."""
    erase_udata_slot_129_256 = ConfigObjectField(8, 8, AccessType.W1C)
    """Access privileges of the R_Mem_Data_Erase L3 Command packet to slots
    129 - 256 of the User Data partition in R-Memory."""
    erase_udata_slot_257_384 = ConfigObjectField(16, 8, AccessType.W1C)
    """Access privileges of the R_Mem_Data_Erase L3 Command packet to slots
    257 - 384 of the User Data partition in R-Memory."""
    erase_udata_slot_385_512 = ConfigObjectField(24, 8, AccessType.W1C)
    """Access privileges of the R_Mem_Data_Erase L3 Command packet to slots
    385 - 512 of the User Data partition in R-Memory."""


class CfgUapRandomValueGet(ConfigObjectRegister):
    random_value_get = ConfigObjectField(0, 8, AccessType.W1C)
    """Access privileges of the Random_Value_Get L3 Command packet."""


class CfgUapEccKeyGenerate(ConfigObjectRegister):
    gen_ecckey_slot_1_8 = ConfigObjectField(0, 8, AccessType.W1C)
    """Access privileges of the ECC_Key_Generate L3 Command packet to ECC Key
    slots 1-8."""
    gen_ecckey_slot_9_16 = ConfigObjectField(8, 8, AccessType.W1C)
    """Access privileges of the ECC_Key_Generate L3 Command packet to ECC Key
    slots 9-16."""
    gen_ecckey_slot_17_24 = ConfigObjectField(16, 8, AccessType.W1C)
    """Access privileges of the ECC_Key_Generate L3 Command packet to ECC Key
    slots 17-24."""
    gen_ecckey_slot_25_32 = ConfigObjectField(24, 8, AccessType.W1C)
    """Access privileges of the ECC_Key_Generate L3 Command packet to ECC Key
    slots 25-32."""


class CfgUapEccKeyStore(ConfigObjectRegister):
    store_ecckey_slot_1_8 = ConfigObjectField(0, 8, AccessType.W1C)
    """Access privileges of the ECC_Key_Store L3 Command packet to ECC Key
    slots 1-8."""
    store_ecckey_slot_9_16 = ConfigObjectField(8, 8, AccessType.W1C)
    """Access privileges of the ECC_Key_Store L3 Command packet to ECC Key
    slots 9-16."""
    store_ecckey_slot_17_24 = ConfigObjectField(16, 8, AccessType.W1C)
    """Access privileges of the ECC_Key_Store L3 Command packet to ECC Key
    slots 17-24."""
    store_ecckey_slot_25_32 = ConfigObjectField(24, 8, AccessType.W1C)
    """Access privileges of the ECC_Key_Store L3 Command packet to ECC Key
    slots 25-32."""


class CfgUapEccKeyRead(ConfigObjectRegister):
    read_ecckey_slot_1_8 = ConfigObjectField(0, 8, AccessType.W1C)
    """Access privileges of the ECC_Key_Read L3 Command packet to ECC Key
    slots 1-8."""
    read_ecckey_slot_9_16 = ConfigObjectField(8, 8, AccessType.W1C)
    """Access privileges of the ECC_Key_Read L3 Command packet to ECC Key
    slots 9-16."""
    read_ecckey_slot_17_24 = ConfigObjectField(16, 8, AccessType.W1C)
    """Access privileges of the ECC_Key_Read L3 Command packet to ECC Key
    slots 17-24."""
    read_ecckey_slot_25_32 = ConfigObjectField(24, 8, AccessType.W1C)
    """Access privileges of the ECC_Key_Read L3 Command packet to ECC Key
    slots 25-32."""


class CfgUapEccKeyErase(ConfigObjectRegister):
    erase_ecckey_slot_1_8 = ConfigObjectField(0, 8, AccessType.W1C)
    """Access privileges of the ECC_Key_Erase L3 Command packet to ECC Key
    slots 1-8."""
    erase_ecckey_slot_9_16 = ConfigObjectField(8, 8, AccessType.W1C)
    """Access privileges of the ECC_Key_Erase L3 Command packet to ECC Key
    slots 9-16."""
    erase_ecckey_slot_17_24 = ConfigObjectField(16, 8, AccessType.W1C)
    """Access privileges of the ECC_Key_Erase L3 Command packet to ECC Key
    slots 17-24."""
    erase_ecckey_slot_25_32 = ConfigObjectField(24, 8, AccessType.W1C)
    """Access privileges of the ECC_Key_Erase L3 Command packet to ECC Key
    slots 25-32."""


class CfgUapEcdsaSign(ConfigObjectRegister):
    ecdsa_ecckey_slot_1_8 = ConfigObjectField(0, 8, AccessType.W1C)
    """Access privileges of the ECDSA_Sign L3 Command packet to keys from ECC
    Key slots 1-8."""
    ecdsa_ecckey_slot_9_16 = ConfigObjectField(8, 8, AccessType.W1C)
    """Access privileges of the ECDSA_Sign L3 Command packet to keys from ECC
    Key slots 9-16."""
    ecdsa_ecckey_slot_17_24 = ConfigObjectField(16, 8, AccessType.W1C)
    """Access privileges of the ECDSA_Sign L3 Command packet to keys from ECC
    Key slots 17-24."""
    ecdsa_ecckey_slot_25_32 = ConfigObjectField(24, 8, AccessType.W1C)
    """Access privileges of the ECDSA_Sign L3 Command packet to keys from ECC
    Key slots 25-32."""


class CfgUapEddsaSign(ConfigObjectRegister):
    eddsa_ecckey_slot_1_8 = ConfigObjectField(0, 8, AccessType.W1C)
    """Access privileges of the EDDSA_Sign L3 Command packet to keys from ECC
    Key slots 1-8."""
    eddsa_ecckey_slot_9_16 = ConfigObjectField(8, 8, AccessType.W1C)
    """Access privileges of the EDDSA_Sign L3 Command packet to keys from ECC
    Key slots 9-16."""
    eddsa_ecckey_slot_17_24 = ConfigObjectField(16, 8, AccessType.W1C)
    """Access privileges of the EDDSA_Sign L3 Command packet to keys from ECC
    Key slots 17-24."""
    eddsa_ecckey_slot_25_32 = ConfigObjectField(24, 8, AccessType.W1C)
    """Access privileges of the EDDSA_Sign L3 Command packet to keys from ECC
    Key slots 25-32."""


class CfgUapMcounterInit(ConfigObjectRegister):
    mcounter_init_1_4 = ConfigObjectField(0, 8, AccessType.W1C)
    """Access privileges of the MCounter_Init L3 Command packet to Monotonic
    counters 1-4."""
    mcounter_init_5_8 = ConfigObjectField(8, 8, AccessType.W1C)
    """Access privileges of the MCounter_Init L3 Command packet to Monotonic
    counters 5-8."""
    mcounter_init_9_12 = ConfigObjectField(16, 8, AccessType.W1C)
    """Access privileges of the MCounter_Init L3 Command packet to Monotonic
    counters 9-12."""
    mcounter_init_13_16 = ConfigObjectField(24, 8, AccessType.W1C)
    """Access privileges of the MCounter_Init L3 Command packet to Monotonic
    counters 13-16."""


class CfgUapMcounterGet(ConfigObjectRegister):
    mcounter_get_1_4 = ConfigObjectField(0, 8, AccessType.W1C)
    """Access privileges of the MCounter_Get L3 Command packet to Monotonic
    counters 1-4."""
    mcounter_get_5_8 = ConfigObjectField(8, 8, AccessType.W1C)
    """Access privileges of the MCounter_Get L3 Command packet to Monotonic
    counters 5-8."""
    mcounter_get_9_12 = ConfigObjectField(16, 8, AccessType.W1C)
    """Access privileges of the MCounter_Get L3 Command packet to Monotonic
    counters 9-12."""
    mcounter_get_13_16 = ConfigObjectField(24, 8, AccessType.W1C)
    """Access privileges of the MCounter_Get L3 Command packet to Monotonic
    counters 13-16."""


class CfgUapMcounterUpdate(ConfigObjectRegister):
    mcounter_update_1_4 = ConfigObjectField(0, 8, AccessType.W1C)
    """Access privileges of the MCounter_Update L3 Command packet to Monotonic
    counters 1-4."""
    mcounter_update_5_8 = ConfigObjectField(8, 8, AccessType.W1C)
    """Access privileges of the MCounter_Update L3 Command packet to Monotonic
    counters 5-8."""
    mcounter_update_9_12 = ConfigObjectField(16, 8, AccessType.W1C)
    """Access privileges of the MCounter_Update L3 Command packet to Monotonic
    counters 9-12."""
    mcounter_update_13_16 = ConfigObjectField(24, 8, AccessType.W1C)
    """Access privileges of the MCounter_Update L3 Command packet to Monotonic
    counters 13-16."""


class CfgUapMacAndDestroy(ConfigObjectRegister):
    macandd_1_32 = ConfigObjectField(0, 8, AccessType.W1C)
    """Access privileges of the MAC_And_Destroy L3 Command packet (when
    executing a MAC-and-Destroy sequence) to slots 1-32 of the MAC-and-Destroy
    Partition of R-Memory."""
    macandd_33_64 = ConfigObjectField(8, 8, AccessType.W1C)
    """Access privileges of the MAC_And_Destroy L3 Command packet (when
    executing a MAC-and-Destroy sequence) to slots 33-64 of the MAC-and-
    Destroy Partition of R-Memory."""
    macandd_65_96 = ConfigObjectField(16, 8, AccessType.W1C)
    """Access privileges of the MAC_And_Destroy L3 Command packet (when
    executing a MAC-and-Destroy sequence) to slots 65-96 of the MAC-and-
    Destroy Partition of R-Memory."""
    macandd_97_128 = ConfigObjectField(24, 8, AccessType.W1C)
    """Access privileges of the MAC_And_Destroy L3 Command packet (when
    executing a MAC-and-Destroy sequence) to slots 97-128 of the MAC-and-
    Destroy Partition of R-Memory."""


class CfgUapSerialCodeGet(ConfigObjectRegister):
    serial_code = ConfigObjectField(0, 8, AccessType.W1C)
    """Access privileges of the Serial_Code_Get L3 Command packet."""


class ConfigObjectRegisterAddressEnum(IntEnum):
    CFG_START_UP = 0x00
    CFG_SLEEP_MODE = 0x04
    CFG_SENSORS = 0x08
    CFG_DEBUG = 0x10
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
        self.cfg_start_up = CfgStartUp(ConfigObjectRegisterAddressEnum.CFG_START_UP, 0x0000003E)
        self.cfg_sleep_mode = CfgSleepMode(ConfigObjectRegisterAddressEnum.CFG_SLEEP_MODE, 0x00000003)
        self.cfg_sensors = CfgSensors(ConfigObjectRegisterAddressEnum.CFG_SENSORS, 0x0003FFFF)
        self.cfg_debug = CfgDebug(ConfigObjectRegisterAddressEnum.CFG_DEBUG, 0x00000001)
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
    cfg_debug: Optional[StrictInt]
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
