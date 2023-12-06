import contextlib
from typing import List, Tuple

from ...api.l3_api import (
    L3API,
    TsL3EccKeyEraseCommand,
    TsL3EccKeyEraseResult,
    TsL3EccKeyGenerateCommand,
    TsL3EccKeyGenerateResult,
    TsL3EccKeyReadCommand,
    TsL3EccKeyReadResult,
    TsL3EccKeyStoreCommand,
    TsL3EccKeyStoreResult,
    TsL3EcdsaSignCommand,
    TsL3EcdsaSignResult,
    TsL3EddsaSignCommand,
    TsL3EddsaSignResult,
    TsL3IConfigReadCommand,
    TsL3IConfigReadResult,
    TsL3IConfigWriteCommand,
    TsL3IConfigWriteResult,
    TsL3MacAndDestroyCommand,
    TsL3MacAndDestroyResult,
    TsL3McounterGetCommand,
    TsL3McounterGetResult,
    TsL3McounterInitCommand,
    TsL3McounterInitResult,
    TsL3McounterUpdateCommand,
    TsL3McounterUpdateResult,
    TsL3PairingKeyReadCommand,
    TsL3PairingKeyReadResult,
    TsL3PairingKeyWriteCommand,
    TsL3PairingKeyWriteResult,
    TsL3PingCommand,
    TsL3PingResult,
    TsL3RandomValueGetCommand,
    TsL3RandomValueGetResult,
    TsL3RConfigEraseCommand,
    TsL3RConfigEraseResult,
    TsL3RConfigReadCommand,
    TsL3RConfigReadResult,
    TsL3RConfigWriteCommand,
    TsL3RConfigWriteResult,
    TsL3RMemDataEraseCommand,
    TsL3RMemDataEraseResult,
    TsL3RMemDataReadCommand,
    TsL3RMemDataReadResult,
    TsL3RMemDataWriteCommand,
    TsL3RMemDataWriteResult,
    TsL3SerialCodeGetCommand,
    TsL3SerialCodeGetResult,
)
from ...constants import L3ResultFieldEnum
from .configuration_object_impl import ConfigObjectRegisterAddressEnum
from .exceptions import (
    L3ProcessingError,
    L3ProcessingErrorFail,
    L3ProcessingErrorInvalidCmd,
)
from .internal.ecc_keys import (
    KEY_SIZE,
    CurveMismatchError,
    ECCKeyDoesNotExistInSlotError,
    ECCKeyExistsInSlotError,
    Origins,
    SignatureFailedError,
)
from .internal.mcounter import (
    MCounterNotInitializedError,
    MCounterUpdateError,
    MCounterWrongInitValueError,
)
from .internal.pairing_keys import InvalidatedSlotError
from .internal.user_data_partition import DataLengthOverflow, SlotAlreadyWrittenError

FUNCTIONALITY_ACCESS_PRIVILEGES = [
    ConfigObjectRegisterAddressEnum.CFG_UAP_R_MEM_DATA_WRITE,
    ConfigObjectRegisterAddressEnum.CFG_UAP_R_MEM_DATA_READ,
    ConfigObjectRegisterAddressEnum.CFG_UAP_R_MEM_DATA_ERASE,
    ConfigObjectRegisterAddressEnum.CFG_UAP_RANDOM_VALUE_GET,
    ConfigObjectRegisterAddressEnum.CFG_UAP_ECC_KEY_GENERATE,
    ConfigObjectRegisterAddressEnum.CFG_UAP_ECC_KEY_STORE,
    ConfigObjectRegisterAddressEnum.CFG_UAP_ECC_KEY_READ,
    ConfigObjectRegisterAddressEnum.CFG_UAP_ECC_KEY_ERASE,
    ConfigObjectRegisterAddressEnum.CFG_UAP_ECDSA_SIGN,
    ConfigObjectRegisterAddressEnum.CFG_UAP_EDDSA_SIGN,
    ConfigObjectRegisterAddressEnum.CFG_UAP_MCOUNTER_INIT,
    ConfigObjectRegisterAddressEnum.CFG_UAP_MCOUNTER_GET,
    ConfigObjectRegisterAddressEnum.CFG_UAP_MCOUNTER_UPDATE,
    ConfigObjectRegisterAddressEnum.CFG_UAP_MAC_AND_DESTROY,
    ConfigObjectRegisterAddressEnum.CFG_UAP_PING,
    ConfigObjectRegisterAddressEnum.CFG_UAP_SERIAL_CODE_GET,
]


CONFIGURATION_ACCESS_PRIVILEGES = [
    ConfigObjectRegisterAddressEnum.CFG_UAP_I_CONFIG_WRITE,
    ConfigObjectRegisterAddressEnum.CFG_UAP_I_CONFIG_READ,
    ConfigObjectRegisterAddressEnum.CFG_UAP_R_CONFIG_WRITE,
    ConfigObjectRegisterAddressEnum.CFG_UAP_R_CONFIG_READ,
    ConfigObjectRegisterAddressEnum.CFG_UAP_R_CONFIG_ERASE,
    ConfigObjectRegisterAddressEnum.CFG_UAP_PAIRING_KEY_WRITE,
    ConfigObjectRegisterAddressEnum.CFG_UAP_PAIRING_KEY_READ,
]


class L3APIImplementation(L3API):
    def ts_l3_ping(self, command: TsL3PingCommand) -> TsL3PingResult:
        self.check_access_privileges("ping", self.config.cfg_uap_ping.ping)
        self.logger.debug(f"ping: {command}")

        result = TsL3PingResult(
            result=L3ResultFieldEnum.OK, data_out=command.data_in.value
        )
        self.logger.debug(f"pong: {result}")
        return result

    def _check_slot_access_privileges(
        self, address: int, access_privileges_list: List[Tuple[str, int]]
    ) -> None:
        for access_privileges in access_privileges_list:
            value = int(access_privileges[0].split("_")[-1])
            if address == value:
                self.check_access_privileges(*access_privileges)
                return
        raise L3ProcessingErrorFail(f"Slot index {address=:#06x} out of range.")

    def ts_l3_pairing_key_write(
        self, command: TsL3PairingKeyWriteCommand
    ) -> TsL3PairingKeyWriteResult:
        config = self.config.cfg_uap_pairing_key_write
        self._check_slot_access_privileges(
            (pkey_slot := command.slot.value),
            [
                ("write_pkey_slot_1", config.write_pkey_slot_1),
                ("write_pkey_slot_2", config.write_pkey_slot_2),
                ("write_pkey_slot_3", config.write_pkey_slot_3),
                ("write_pkey_slot_4", config.write_pkey_slot_4),
            ],
        )

        self.logger.info(f"Writing pairing key to slot #{pkey_slot}.")
        s_hipub_bytes = command.s_hipub.to_bytes()
        self.logger.debug(f"Writing pairing key: {s_hipub_bytes}")
        try:
            self.i_pairing_keys[pkey_slot].write(s_hipub_bytes)
        except InvalidatedSlotError as exc:
            self.logger.info(exc)
            raise L3ProcessingErrorFail(
                f"Pairing key slot #{pkey_slot} is invalidated"
            ) from None

        self.logger.debug(f"Pairing key slot #{pkey_slot} written.")
        return TsL3PairingKeyWriteResult(result=L3ResultFieldEnum.OK)

    def ts_l3_pairing_key_read(
        self, command: TsL3PairingKeyReadCommand
    ) -> TsL3PairingKeyReadResult:
        config = self.config.cfg_uap_pairing_key_read
        self._check_slot_access_privileges(
            (pkey_slot := command.slot.value),
            [
                ("read_pkey_slot_1", config.read_pkey_slot_1),
                ("read_pkey_slot_2", config.read_pkey_slot_2),
                ("read_pkey_slot_3", config.read_pkey_slot_3),
                ("read_pkey_slot_4", config.read_pkey_slot_4),
            ],
        )

        self.logger.info(f"Reading pairing key from slot #{pkey_slot}.")
        s_hipub_bytes = self.i_pairing_keys[pkey_slot].read()

        self.logger.debug(f"Read pairing key: {s_hipub_bytes}")
        return TsL3PairingKeyReadResult(
            result=L3ResultFieldEnum.OK, s_hipub=s_hipub_bytes
        )

    def _check_config_access_privileges(
        self,
        address: int,
        functionality_access_privileges: Tuple[str, int],
        configuration_access_privileges: Tuple[str, int],
    ) -> None:
        try:
            address_enum = ConfigObjectRegisterAddressEnum(address)
        except ValueError:
            raise L3ProcessingErrorFail(
                f"No configuration register at {address=:#04x}."
            ) from None
        if address_enum in FUNCTIONALITY_ACCESS_PRIVILEGES:
            self.logger.debug("'Functionality' register.")
            self.check_access_privileges(*functionality_access_privileges)
        elif address_enum in CONFIGURATION_ACCESS_PRIVILEGES:
            self.logger.debug("'Configuration' register.")
            self.check_access_privileges(*configuration_access_privileges)
        else:
            self.logger.debug("Not 'functionality' nor 'configuration'.")

    def ts_l3_r_config_write(
        self, command: TsL3RConfigWriteCommand
    ) -> TsL3RConfigWriteResult:
        config = self.config.cfg_uap_r_config_write
        self._check_config_access_privileges(
            (address := command.address.value),
            ("r_config_write_func", config.r_config_write_func),
            ("r_config_write_cfg", config.r_config_write_cfg),
        )

        self.logger.info("Writing r_config register.")
        self.logger.debug(f"Register address: {address:#04x}.")
        value = command.value.value
        self.logger.debug(f"Writing value: {value:#010x}.")
        self.r_config[address].value = value

        self.logger.debug("R_config register written.")
        return TsL3RConfigWriteResult(result=L3ResultFieldEnum.OK)

    def ts_l3_r_config_read(
        self, command: TsL3RConfigReadCommand
    ) -> TsL3RConfigReadResult:
        config = self.config.cfg_uap_r_config_read
        self._check_config_access_privileges(
            (address := command.address.value),
            ("r_config_read_func", config.r_config_read_func),
            ("r_config_read_cfg", config.r_config_read_cfg),
        )

        self.logger.info("Reading r_config register.")
        self.logger.debug(f"Register address: {address:#04x}.")
        value = self.r_config[address].value

        self.logger.debug(f"Read value: {value:#010x}.")
        return TsL3RConfigReadResult(result=L3ResultFieldEnum.OK, value=value)

    def ts_l3_r_config_erase(
        self, command: TsL3RConfigEraseCommand
    ) -> TsL3RConfigEraseResult:
        config = self.config.cfg_uap_r_config_erase

        self.logger.info("Erasing r_config configuration object.")
        with contextlib.suppress(Exception):
            self.check_access_privileges(
                "r_config_erase_func", config.r_config_erase_func
            )
            self.logger.info("Erasing 'functionality' registers.")
            for address in FUNCTIONALITY_ACCESS_PRIVILEGES:
                self.logger.debug(f"{address!s}.")
                self.r_config[address].reset()

        with contextlib.suppress(Exception):
            self.check_access_privileges(
                "r_config_erase_cfg", config.r_config_erase_cfg
            )
            self.logger.info("Erasing 'configuration' registers.")
            for address in CONFIGURATION_ACCESS_PRIVILEGES:
                self.logger.debug(f"{address!s}.")
                self.r_config[address].reset()

        self.logger.debug("R_config configuration object erased.")
        return TsL3RConfigEraseResult(result=L3ResultFieldEnum.OK)

    def ts_l3_i_config_write(
        self, command: TsL3IConfigWriteCommand
    ) -> TsL3IConfigWriteResult:
        config = self.config.cfg_uap_i_config_write
        self._check_config_access_privileges(
            (address := command.address.value),
            ("i_config_write_func", config.i_config_write_func),
            ("i_config_write_cfg", config.i_config_write_cfg),
        )

        self.logger.info("Writing i_config register.")
        self.logger.debug(f"Register address: {address:#04x}.")
        bit_index = command.bit_index.value
        self.logger.debug(f"Bit index: {bit_index}.")

        try:
            self.i_config[address].write_bit(bit_index)
        except ValueError as exc:
            raise L3ProcessingErrorFail(exc) from None

        self.logger.debug("I_config register written.")
        return TsL3IConfigWriteResult(result=L3ResultFieldEnum.OK)

    def ts_l3_i_config_read(
        self, command: TsL3IConfigReadCommand
    ) -> TsL3IConfigReadResult:
        config = self.config.cfg_uap_i_config_read
        self._check_config_access_privileges(
            (address := command.address.value),
            ("i_config_read_func", config.i_config_read_func),
            ("i_config_read_cfg", config.i_config_read_cfg),
        )

        self.logger.info("Reading i_config register.")
        self.logger.debug(f"Register address: {address:#04x}.")
        value = self.i_config[address].value

        self.logger.debug(f"Read value: {value:#010x}.")
        return TsL3IConfigReadResult(result=L3ResultFieldEnum.OK, value=value)

    def _check_ranged_access_privileges(
        self, address: int, access_privileges_list: List[Tuple[str, int]]
    ) -> None:
        for access_privileges in access_privileges_list:
            lower, upper = map(int, access_privileges[0].split("_")[-2:])
            if lower <= address <= upper:
                self.check_access_privileges(*access_privileges)
                return
        raise L3ProcessingErrorFail(f"Slot index {address=:#06x} out of range.")

    def ts_l3_r_mem_data_write(
        self, command: TsL3RMemDataWriteCommand
    ) -> TsL3RMemDataWriteResult:
        config = self.config.cfg_uap_r_mem_data_write
        self._check_ranged_access_privileges(
            (address := command.udata_slot.value),
            [
                ("write_udata_slot_1_128", config.write_udata_slot_1_128),
                ("write_udata_slot_129_256", config.write_udata_slot_129_256),
                ("write_udata_slot_257_384", config.write_udata_slot_257_384),
                ("write_udata_slot_385_512", config.write_udata_slot_385_512),
            ],
        )

        self.logger.info("Writing user data slot.")
        self.logger.debug(f"User data slot address: {address:#06x}.")
        data = command.data.to_bytes()
        self.logger.debug(f"Writing value: {data}.")
        try:
            self.r_user_data[address].write(data)
        except (SlotAlreadyWrittenError, DataLengthOverflow) as exc:
            self.logger.info(exc)
            raise L3ProcessingError(
                result=TsL3RMemDataWriteResult.ResultEnum.WRITE_FAIL
            ) from None

        self.logger.debug("User data slot written.")
        return TsL3RMemDataWriteResult(result=L3ResultFieldEnum.OK)

    def ts_l3_r_mem_data_read(
        self, command: TsL3RMemDataReadCommand
    ) -> TsL3RMemDataReadResult:
        config = self.config.cfg_uap_r_mem_data_read
        self._check_ranged_access_privileges(
            (address := command.udata_slot.value),
            [
                ("read_udata_slot_1_128", config.read_udata_slot_1_128),
                ("read_udata_slot_129_256", config.read_udata_slot_129_256),
                ("read_udata_slot_257_384", config.read_udata_slot_257_384),
                ("read_udata_slot_385_512", config.read_udata_slot_385_512),
            ],
        )

        self.logger.info("Reading user data slot.")
        self.logger.debug(f"User data slot address: {address:#06x}.")
        data = self.r_user_data[address].read()

        self.logger.debug(f"Read value: {data}.")
        return TsL3RMemDataReadResult(result=L3ResultFieldEnum.OK, data=data)

    def ts_l3_r_mem_data_erase(
        self, command: TsL3RMemDataEraseCommand
    ) -> TsL3RMemDataEraseResult:
        config = self.config.cfg_uap_r_mem_data_erase
        self._check_ranged_access_privileges(
            (address := command.udata_slot.value),
            [
                ("erase_udata_slot_1_128", config.erase_udata_slot_1_128),
                ("erase_udata_slot_129_256", config.erase_udata_slot_129_256),
                ("erase_udata_slot_257_384", config.erase_udata_slot_257_384),
                ("erase_udata_slot_385_512", config.erase_udata_slot_385_512),
            ],
        )

        self.logger.info("Erasing user data slot.")
        self.logger.debug(f"User data slot address: {address:#06x}.")
        self.r_user_data[address].erase()

        self.logger.debug("User data slot erased.")
        return TsL3RMemDataEraseResult(result=L3ResultFieldEnum.OK)

    def ts_l3_random_value_get(
        self, command: TsL3RandomValueGetCommand
    ) -> TsL3RandomValueGetResult:
        self.check_access_privileges(
            "random_value_get",
            self.config.cfg_uap_random_value_get.random_value_get,
        )

        self.logger.info("Get random number from TRNG2.")
        n_bytes = command.n_bytes.value
        self.logger.debug(f"Number of random bytes: {n_bytes}.")

        random_data = self.trng2.get_random_bytes(n_bytes)
        self.logger.debug(f"Random data: {random_data}.")
        return TsL3RandomValueGetResult(
            result=L3ResultFieldEnum.OK, random_data=random_data
        )

    def ts_l3_serial_code_get(
        self, command: TsL3SerialCodeGetCommand
    ) -> TsL3SerialCodeGetResult:
        self.check_access_privileges(
            "serial_code", self.config.cfg_uap_serial_code_get.serial_code
        )
        self.logger.info("Get chip unique serial code.")
        self.logger.debug(f"Serial code: {self.serial_code}.")
        return TsL3SerialCodeGetResult(
            result=L3ResultFieldEnum.OK, serial_code=self.serial_code
        )

    def ts_l3_mcounter_init(
        self, command: TsL3McounterInitCommand
    ) -> TsL3McounterInitResult:
        config = self.config.cfg_uap_mcounter_init
        self._check_ranged_access_privileges(
            (index := command.mcounter_index.value),
            [
                ("mcounter_init_1_4", config.mcounter_init_1_4),
                ("mcounter_init_5_8", config.mcounter_init_5_8),
                ("mcounter_init_9_12", config.mcounter_init_9_12),
                ("mcounter_init_13_16", config.mcounter_init_13_16),
            ],
        )

        mcounter_val = command.mcounter_val.value
        self.logger.info("Initializing mcounter.")
        self.logger.debug(f"Mcounter index: {index}; value: {mcounter_val}.")
        try:
            self.r_mcounters[index].init(mcounter_val)
        except MCounterWrongInitValueError as exc:
            raise L3ProcessingErrorFail(exc) from None

        self.logger.debug("Initialized mcounter.")
        return TsL3McounterInitResult(result=L3ResultFieldEnum.OK)

    def ts_l3_mcounter_update(
        self, command: TsL3McounterUpdateCommand
    ) -> TsL3McounterUpdateResult:
        config = self.config.cfg_uap_mcounter_update
        self._check_ranged_access_privileges(
            (index := command.mcounter_index.value),
            [
                ("mcounter_update_1_4", config.mcounter_update_1_4),
                ("mcounter_update_5_8", config.mcounter_update_5_8),
                ("mcounter_update_9_12", config.mcounter_update_9_12),
                ("mcounter_update_13_16", config.mcounter_update_13_16),
            ],
        )

        self.logger.info("Updating mcounter.")
        self.logger.debug(f"MCounter index: {index}.")
        try:
            self.r_mcounters[index].update()
            self.logger.debug(f"Updated mcounter {index=}.")
        except MCounterNotInitializedError as exc:
            raise L3ProcessingErrorFail(exc) from None
        except MCounterUpdateError as exc:
            self.logger.info(exc)
            raise L3ProcessingError(
                result=TsL3McounterUpdateResult.ResultEnum.UPDATE_ERR
            ) from None

        return TsL3McounterUpdateResult(result=L3ResultFieldEnum.OK)

    def ts_l3_mcounter_get(
        self, command: TsL3McounterGetCommand
    ) -> TsL3McounterGetResult:
        config = self.config.cfg_uap_mcounter_get
        self._check_ranged_access_privileges(
            (index := command.mcounter_index.value),
            [
                ("mcounter_get_1_4", config.mcounter_get_1_4),
                ("mcounter_get_5_8", config.mcounter_get_5_8),
                ("mcounter_get_9_12", config.mcounter_get_9_12),
                ("mcounter_get_13_16", config.mcounter_get_13_16),
            ],
        )

        self.logger.info("Getting value of mcounter.")
        self.logger.debug(f"Mcounter index {index}.")
        try:
            mcounter_val = self.r_mcounters[index].get()
        except MCounterNotInitializedError as exc:
            raise L3ProcessingErrorFail(exc) from None

        self.logger.debug(f"Read value: {mcounter_val}.")
        return TsL3McounterGetResult(
            result=L3ResultFieldEnum.OK, mcounter_val=mcounter_val
        )

    def ts_l3_ecc_key_generate(
        self, command: TsL3EccKeyGenerateCommand
    ) -> TsL3EccKeyGenerateResult:
        try:
            curve = TsL3EccKeyGenerateCommand.CurveEnum(command.curve.value)
        except ValueError as exc:
            raise L3ProcessingErrorFail(exc) from None

        config = self.config.cfg_uap_ecc_key_generate
        self._check_ranged_access_privileges(
            (slot := command.slot.value),
            [
                ("gen_ecckey_slot_1_8", config.gen_ecckey_slot_1_8),
                ("gen_ecckey_slot_9_16", config.gen_ecckey_slot_9_16),
                ("gen_ecckey_slot_17_24", config.gen_ecckey_slot_17_24),
                ("gen_ecckey_slot_25_32", config.gen_ecckey_slot_25_32),
            ],
        )

        self.logger.info("Generating ECC key.")
        self.logger.debug(f"ECC key slot: {slot}.")
        try:
            self.r_ecc_keys.store(
                slot,
                curve,
                self.trng2.get_random_bytes(KEY_SIZE),
                Origins.Ecc_Key_Generate,
            )
        except ECCKeyExistsInSlotError as exc:
            raise L3ProcessingErrorFail(exc) from None

        self.logger.debug(f"Generated ECC key in {slot=}.")
        return TsL3EccKeyGenerateResult(result=L3ResultFieldEnum.OK)

    def ts_l3_ecc_key_store(
        self, command: TsL3EccKeyStoreCommand
    ) -> TsL3EccKeyStoreResult:
        try:
            curve = TsL3EccKeyStoreCommand.CurveEnum(command.curve.value)
        except ValueError as exc:
            raise L3ProcessingErrorFail(exc) from None

        config = self.config.cfg_uap_ecc_key_store
        self._check_ranged_access_privileges(
            (slot := command.slot.value),
            [
                ("store_ecckey_slot_1_8", config.store_ecckey_slot_1_8),
                ("store_ecckey_slot_9_16", config.store_ecckey_slot_9_16),
                ("store_ecckey_slot_17_24", config.store_ecckey_slot_17_24),
                ("store_ecckey_slot_25_32", config.store_ecckey_slot_25_32),
            ],
        )

        self.logger.info("Storing ECC key.")
        self.logger.debug(f"ECC key slot: {slot}.")
        try:
            self.r_ecc_keys.store(
                slot, curve, command.k.to_bytes(), Origins.Ecc_Key_Store
            )
        except ECCKeyExistsInSlotError as exc:
            raise L3ProcessingErrorFail(exc) from None

        self.logger.debug(f"Stored ECC key in {slot=}.")
        return TsL3EccKeyStoreResult(result=L3ResultFieldEnum.OK)

    def ts_l3_ecc_key_read(
        self, command: TsL3EccKeyReadCommand
    ) -> TsL3EccKeyReadResult:
        config = self.config.cfg_uap_ecc_key_read
        self._check_ranged_access_privileges(
            (slot := command.slot.value),
            [
                ("read_ecckey_slot_1_8", config.read_ecckey_slot_1_8),
                ("read_ecckey_slot_9_16", config.read_ecckey_slot_9_16),
                ("read_ecckey_slot_17_24", config.read_ecckey_slot_17_24),
                ("read_ecckey_slot_25_32", config.read_ecckey_slot_25_32),
            ],
        )

        self.logger.info("Reading ECC Key.")
        self.logger.debug(f"ECC key slot: {slot}.")
        try:
            curve, pub_key, origin = self.r_ecc_keys.read(slot)
        except ECCKeyDoesNotExistInSlotError as exc:
            raise L3ProcessingErrorFail(exc) from None
        self.logger.debug(
            f"Read ECC key from {slot=}: {curve=}; {pub_key=}; "
            f"randomly generated={origin}."
        )

        return TsL3EccKeyReadResult(
            result=L3ResultFieldEnum.OK,
            curve=curve,
            origin=origin,
            padding=[],
            pub_key=pub_key,
        )

    def ts_l3_ecc_key_erase(
        self, command: TsL3EccKeyEraseCommand
    ) -> TsL3EccKeyEraseResult:
        config = self.config.cfg_uap_ecc_key_erase
        self._check_ranged_access_privileges(
            (slot := command.slot.value),
            [
                ("erase_ecckey_slot_1_8", config.erase_ecckey_slot_1_8),
                ("erase_ecckey_slot_9_16", config.erase_ecckey_slot_9_16),
                ("erase_ecckey_slot_17_24", config.erase_ecckey_slot_17_24),
                ("erase_ecckey_slot_25_32", config.erase_ecckey_slot_25_32),
            ],
        )

        self.logger.info("Erasing ECC Key.")
        self.logger.debug(f"ECC key slot: {slot}.")
        try:
            self.r_ecc_keys.erase(slot)
        except ECCKeyDoesNotExistInSlotError as exc:
            raise L3ProcessingErrorFail(exc) from None

        self.logger.debug(f"Erased ECC key in {slot=}.")
        return TsL3EccKeyEraseResult(result=L3ResultFieldEnum.OK)

    def ts_l3_ecdsa_sign(self, command: TsL3EcdsaSignCommand) -> TsL3EcdsaSignResult:
        config = self.config.cfg_uap_ecdsa_sign
        self._check_ranged_access_privileges(
            (slot := command.slot.value),
            [
                ("ecdsa_ecckey_slot_1_8", config.ecdsa_ecckey_slot_1_8),
                ("ecdsa_ecckey_slot_9_16", config.ecdsa_ecckey_slot_9_16),
                ("ecdsa_ecckey_slot_17_24", config.ecdsa_ecckey_slot_17_24),
                ("ecdsa_ecckey_slot_25_32", config.ecdsa_ecckey_slot_25_32),
            ],
        )

        self.logger.info("Signing message hash with ECDSA.")
        msg_hash = command.msg_hash.to_bytes()
        self.logger.debug(f"Message hash: {msg_hash}.")
        try:
            r, s = self.r_ecc_keys.ecdsa_sign(
                slot,
                msg_hash,
                self.session.handshake_hash,
                self.session.nonce_cmd.to_bytes(4, byteorder="big"),
            )
        except (ECCKeyDoesNotExistInSlotError, CurveMismatchError) as exc:
            self.logger.info(exc)
            raise L3ProcessingError(
                result=TsL3EcdsaSignResult.ResultEnum.INVALID_KEY
            ) from None
        except SignatureFailedError as exc:
            raise L3ProcessingErrorFail(exc) from None

        self.logger.debug(f"Signed message hash with ECDSA: {r=}; {s=}.")
        return TsL3EcdsaSignResult(result=L3ResultFieldEnum.OK, padding=[], r=r, s=s)

    def ts_l3_eddsa_sign(self, command: TsL3EddsaSignCommand) -> TsL3EddsaSignResult:
        config = self.config.cfg_uap_eddsa_sign
        self._check_ranged_access_privileges(
            (slot := command.slot.value),
            [
                ("eddsa_ecckey_slot_1_8", config.eddsa_ecckey_slot_1_8),
                ("eddsa_ecckey_slot_9_16", config.eddsa_ecckey_slot_9_16),
                ("eddsa_ecckey_slot_17_24", config.eddsa_ecckey_slot_17_24),
                ("eddsa_ecckey_slot_25_32", config.eddsa_ecckey_slot_25_32),
            ],
        )

        self.logger.info("Signing message with EdDSA.")
        msg_bytes = command.msg.to_bytes()
        self.logger.debug(f"Message: {msg_bytes}.")
        try:
            r, s = self.r_ecc_keys.eddsa_sign(
                slot,
                msg_bytes,
                self.session.handshake_hash,
                self.session.nonce_cmd.to_bytes(4, byteorder="big"),
            )
        except (ECCKeyDoesNotExistInSlotError, CurveMismatchError) as exc:
            self.logger.info(exc)
            raise L3ProcessingError(
                result=TsL3EcdsaSignResult.ResultEnum.INVALID_KEY
            ) from None

        self.logger.debug(f"Signed message with EdDSA: {r=}; {s=}.")
        return TsL3EddsaSignResult(result=L3ResultFieldEnum.OK, padding=[], r=r, s=s)

    def ts_l3_mac_and_destroy(
        self, command: TsL3MacAndDestroyCommand
    ) -> TsL3MacAndDestroyResult:
        raise L3ProcessingErrorInvalidCmd("Mac-and-Destroy not yet available.")
