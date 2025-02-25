from typing import List, Tuple, Type

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
    TsL3PairingKeyInvalidateCommand,
    TsL3PairingKeyInvalidateResult,
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
)
from ...constants import L3ResultFieldEnum
from .exceptions import (
    L3ProcessingError,
    L3ProcessingErrorFail,
    L3ProcessingErrorInvalidCmd,
    L3ProcessingErrorUnauthorized,
)
from .internal.configuration_object import (
    CONFIGURATION_ACCESS_PRIVILEGES,
    FUNCTIONALITY_ACCESS_PRIVILEGES,
    AddressNotAlignedError,
    AddressOutOfRangeError,
    BitIndexOutOfBoundError,
    NoFreeSpaceError,
)
from .internal.ecc_keys import (
    CurveMismatchError,
    ECCKeyDoesNotExistInSlotError,
    ECCKeyExistsInSlotError,
    ECCKeySetupError,
    SignatureFailedError,
)
from .internal.mcounter import (
    MCounterNotInitializedError,
    MCounterUpdateError,
    MCounterWrongInitValueError,
)
from .internal.pairing_keys import (
    BlankSlotError,
    InvalidatedSlotError,
    WrittenSlotError,
)
from .internal.user_data_partition import SlotAlreadyWrittenError


class L3APIImplementation(L3API):
    def ts_l3_ping(self, command: TsL3PingCommand) -> TsL3PingResult:
        self.check_access_privileges("ping", self.config.cfg_uap_ping.ping)
        self.logger.debug("ping: %s", command)

        result = TsL3PingResult(
            result=L3ResultFieldEnum.OK, data_out=command.data_in.value
        )
        self.logger.debug("pong: %s", result)
        return result

    def _check_pairing_key_slot_access_privileges(
        self, address: int, access_privileges_list: List[Tuple[str, int]]
    ) -> None:
        for name, value in access_privileges_list:
            if address == int(name.rsplit("_", maxsplit=1)[-1]):
                self.check_access_privileges(name, value)
                return
        raise RuntimeError(f"Slot index {address=:#06x} out of range.")

    def ts_l3_pairing_key_write(
        self, command: TsL3PairingKeyWriteCommand
    ) -> TsL3PairingKeyWriteResult:
        pkey_slot = command.slot.value
        try:
            pkey_slot = TsL3PairingKeyWriteCommand.SlotEnum(pkey_slot)
        except ValueError:
            raise L3ProcessingErrorUnauthorized(f"Invalid {pkey_slot = }") from None
        self.logger.debug("pkey_slot = %s", pkey_slot)

        config = self.config.cfg_uap_pairing_key_write
        self._check_pairing_key_slot_access_privileges(
            pkey_slot,
            [
                ("write_pkey_slot_0", config.write_pkey_slot_0),
                ("write_pkey_slot_1", config.write_pkey_slot_1),
                ("write_pkey_slot_2", config.write_pkey_slot_2),
                ("write_pkey_slot_3", config.write_pkey_slot_3),
            ],
        )

        s_hipub_bytes = command.s_hipub.to_bytes()
        self.logger.debug("Writing pairing key: %s", s_hipub_bytes)

        try:
            self.i_pairing_keys[pkey_slot].write(s_hipub_bytes)
        except WrittenSlotError as exc:
            self.logger.info(exc)
            raise L3ProcessingErrorFail(exc) from None

        self.logger.debug("Pairing key slot #%d written.", pkey_slot)
        return TsL3PairingKeyWriteResult(result=L3ResultFieldEnum.OK)

    def ts_l3_pairing_key_read(
        self, command: TsL3PairingKeyReadCommand
    ) -> TsL3PairingKeyReadResult:
        pkey_slot = command.slot.value
        try:
            pkey_slot = TsL3PairingKeyReadCommand.SlotEnum(pkey_slot)
        except ValueError:
            raise L3ProcessingErrorUnauthorized(f"Invalid {pkey_slot = }") from None
        self.logger.debug("pkey_slot = %s", pkey_slot)

        config = self.config.cfg_uap_pairing_key_read
        self._check_pairing_key_slot_access_privileges(
            pkey_slot,
            [
                ("read_pkey_slot_0", config.read_pkey_slot_0),
                ("read_pkey_slot_1", config.read_pkey_slot_1),
                ("read_pkey_slot_2", config.read_pkey_slot_2),
                ("read_pkey_slot_3", config.read_pkey_slot_3),
            ],
        )

        try:
            s_hipub_bytes = self.i_pairing_keys[pkey_slot].read()
        except BlankSlotError as exc:
            self.logger.info(exc)
            raise L3ProcessingError(
                exc, result=TsL3PairingKeyReadResult.ResultEnum.PAIRING_KEY_EMPTY
            ) from None
        except InvalidatedSlotError as exc:
            self.logger.info(exc)
            raise L3ProcessingError(
                exc, result=TsL3PairingKeyReadResult.ResultEnum.PAIRING_KEY_INVALID
            ) from None

        self.logger.debug("Read pairing key: %s", s_hipub_bytes)
        return TsL3PairingKeyReadResult(
            result=L3ResultFieldEnum.OK, s_hipub=s_hipub_bytes
        )

    def ts_l3_pairing_key_invalidate(
        self, command: TsL3PairingKeyInvalidateCommand
    ) -> TsL3PairingKeyInvalidateResult:
        pkey_slot = command.slot.value
        try:
            pkey_slot = TsL3PairingKeyInvalidateCommand.SlotEnum(pkey_slot)
        except ValueError:
            raise L3ProcessingErrorUnauthorized(f"Invalid {pkey_slot = }") from None
        self.logger.debug("pkey_slot = %s", pkey_slot)

        config = self.config.cfg_uap_pairing_key_invalidate
        self._check_pairing_key_slot_access_privileges(
            pkey_slot,
            [
                ("invalidate_pkey_slot_0", config.invalidate_pkey_slot_0),
                ("invalidate_pkey_slot_1", config.invalidate_pkey_slot_1),
                ("invalidate_pkey_slot_2", config.invalidate_pkey_slot_2),
                ("invalidate_pkey_slot_3", config.invalidate_pkey_slot_3),
            ],
        )

        try:
            self.i_pairing_keys[pkey_slot].invalidate()
        except BlankSlotError as exc:
            self.logger.info(exc)
            raise L3ProcessingErrorFail(exc) from None

        self.logger.debug("Invalidated pairing key in slot #%d.", pkey_slot)
        return TsL3PairingKeyInvalidateResult(result=L3ResultFieldEnum.OK)

    def _check_config_access_privileges(
        self,
        address: int,
        functionality_access_privileges: Tuple[str, int],
        configuration_access_privileges: Tuple[str, int],
    ) -> None:
        if address in FUNCTIONALITY_ACCESS_PRIVILEGES:
            self.uap_logger.debug("'Functionality' register.")
            self.check_access_privileges(*functionality_access_privileges)
        elif address in CONFIGURATION_ACCESS_PRIVILEGES:
            self.uap_logger.debug("'Configuration' register.")
            self.check_access_privileges(*configuration_access_privileges)
        else:
            self.uap_logger.debug("Not 'functionality' nor 'configuration'.")

    def ts_l3_r_config_write(
        self, command: TsL3RConfigWriteCommand
    ) -> TsL3RConfigWriteResult:
        self.check_access_privileges(
            "r_config_write_erase",
            self.config.cfg_uap_r_config_write_erase.r_config_write_erase,
        )

        address = command.address.value
        self.logger.debug("Register address: %#04x.", address)

        value = command.value.value
        self.logger.debug("Writing value: %#010x.", value)

        try:
            self.r_config.write(address, value)
        except AddressOutOfRangeError as exc:
            raise L3ProcessingErrorUnauthorized(exc) from None
        except (AddressNotAlignedError, NoFreeSpaceError) as exc:
            raise L3ProcessingErrorFail(exc) from None

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

        self.logger.debug("Register address: %#04x.", address)

        try:
            value = self.r_config.read(address)
        except AddressOutOfRangeError as exc:
            raise L3ProcessingErrorUnauthorized(exc) from None
        except AddressNotAlignedError as exc:
            raise L3ProcessingErrorFail(exc) from None

        self.logger.debug("Read value: %#010x.", value)
        return TsL3RConfigReadResult(result=L3ResultFieldEnum.OK, value=value)

    def ts_l3_r_config_erase(
        self, command: TsL3RConfigEraseCommand
    ) -> TsL3RConfigEraseResult:
        self.check_access_privileges(
            "r_config_write_erase",
            self.config.cfg_uap_r_config_write_erase.r_config_write_erase,
        )

        self.r_config.erase()

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

        self.logger.debug("Register address: %#04x.", address)
        bit_index = command.bit_index.value
        self.logger.debug("Bit index: %d.", bit_index)

        try:
            self.i_config.write_bit(address, bit_index)
        except AddressOutOfRangeError as exc:
            raise L3ProcessingErrorUnauthorized(exc) from None
        except (AddressNotAlignedError, BitIndexOutOfBoundError) as exc:
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

        self.logger.debug("Register address: %#04x.", address)

        try:
            value = self.i_config.read(address)
        except AddressOutOfRangeError as exc:
            raise L3ProcessingErrorUnauthorized(exc) from None
        except AddressNotAlignedError as exc:
            raise L3ProcessingErrorFail(exc) from None

        self.logger.debug("Read value: %#010x.", value)
        return TsL3IConfigReadResult(result=L3ResultFieldEnum.OK, value=value)

    def _check_ranged_access_privileges(
        self,
        address: int,
        access_privileges_list: List[Tuple[str, int]],
        *,
        raise_on_failure: Type[Exception] = L3ProcessingErrorFail,
    ) -> None:
        for name, value in access_privileges_list:
            lower, upper = map(int, name.rsplit("_", maxsplit=2)[-2:])
            if lower <= address <= upper:
                self.check_access_privileges(name, value)
                return
        raise raise_on_failure(f"Slot index {address=:#06x} out of range.")

    def ts_l3_r_mem_data_write(
        self, command: TsL3RMemDataWriteCommand
    ) -> TsL3RMemDataWriteResult:
        config = self.config.cfg_uap_r_mem_data_write
        self._check_ranged_access_privileges(
            (address := command.udata_slot.value),
            [
                ("write_udata_slot_0_127", config.write_udata_slot_0_127),
                ("write_udata_slot_128_255", config.write_udata_slot_128_255),
                ("write_udata_slot_256_383", config.write_udata_slot_256_383),
                ("write_udata_slot_384_511", config.write_udata_slot_384_511),
            ],
        )

        self.logger.debug("User data slot address: %#06x.", address)
        data = command.data.to_bytes()
        self.logger.debug("Writing value: %s.", data)
        try:
            self.r_user_data[address].write(data)
        except SlotAlreadyWrittenError as exc:
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
                ("read_udata_slot_0_127", config.read_udata_slot_0_127),
                ("read_udata_slot_128_255", config.read_udata_slot_128_255),
                ("read_udata_slot_256_383", config.read_udata_slot_256_383),
                ("read_udata_slot_384_511", config.read_udata_slot_384_511),
            ],
        )

        self.logger.debug("User data slot address: %#06x.", address)
        data = self.r_user_data[address].read()

        self.logger.debug("Read value: %s.", data)
        return TsL3RMemDataReadResult(result=L3ResultFieldEnum.OK, data=data)

    def ts_l3_r_mem_data_erase(
        self, command: TsL3RMemDataEraseCommand
    ) -> TsL3RMemDataEraseResult:
        config = self.config.cfg_uap_r_mem_data_erase
        self._check_ranged_access_privileges(
            (address := command.udata_slot.value),
            [
                ("erase_udata_slot_0_127", config.erase_udata_slot_0_127),
                ("erase_udata_slot_128_255", config.erase_udata_slot_128_255),
                ("erase_udata_slot_256_383", config.erase_udata_slot_256_383),
                ("erase_udata_slot_384_511", config.erase_udata_slot_384_511),
            ],
        )

        self.logger.debug("User data slot address: %#06x.", address)
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

        n_bytes = command.n_bytes.value
        self.logger.debug("Number of random bytes: %d.", n_bytes)

        random_data = self.trng2.urandom(n_bytes)
        self.logger.debug("Random data: %s.", random_data)
        return TsL3RandomValueGetResult(
            result=L3ResultFieldEnum.OK, random_data=random_data
        )

    def ts_l3_mcounter_init(
        self, command: TsL3McounterInitCommand
    ) -> TsL3McounterInitResult:
        config = self.config.cfg_uap_mcounter_init
        self._check_ranged_access_privileges(
            (index := command.mcounter_index.value),
            [
                ("mcounter_init_0_3", config.mcounter_init_0_3),
                ("mcounter_init_4_7", config.mcounter_init_4_7),
                ("mcounter_init_8_11", config.mcounter_init_8_11),
                ("mcounter_init_12_15", config.mcounter_init_12_15),
            ],
            raise_on_failure=L3ProcessingErrorUnauthorized,
        )

        mcounter_val = command.mcounter_val.value
        self.logger.debug("Mcounter index: %d; value: %#x.", index, mcounter_val)
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
                ("mcounter_update_0_3", config.mcounter_update_0_3),
                ("mcounter_update_4_7", config.mcounter_update_4_7),
                ("mcounter_update_8_11", config.mcounter_update_8_11),
                ("mcounter_update_12_15", config.mcounter_update_12_15),
            ],
            raise_on_failure=L3ProcessingErrorUnauthorized,
        )

        self.logger.debug("MCounter index: %d.", index)
        try:
            self.r_mcounters[index].update()
            self.logger.debug("Updated mcounter index=%d.", index)
        except MCounterNotInitializedError as exc:
            self.logger.info(exc)
            raise L3ProcessingError(
                exc, result=TsL3McounterUpdateResult.ResultEnum.COUNTER_INVALID
            ) from None
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
                ("mcounter_get_0_3", config.mcounter_get_0_3),
                ("mcounter_get_4_7", config.mcounter_get_4_7),
                ("mcounter_get_8_11", config.mcounter_get_8_11),
                ("mcounter_get_12_15", config.mcounter_get_12_15),
            ],
            raise_on_failure=L3ProcessingErrorUnauthorized,
        )

        self.logger.debug("Mcounter index %d.", index)
        try:
            mcounter_val = self.r_mcounters[index].get()
        except MCounterNotInitializedError as exc:
            raise L3ProcessingError(
                exc, result=TsL3McounterUpdateResult.ResultEnum.COUNTER_INVALID
            ) from None

        self.logger.debug("Read value: %#x.", mcounter_val)
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
                ("gen_ecckey_slot_0_7", config.gen_ecckey_slot_0_7),
                ("gen_ecckey_slot_8_15", config.gen_ecckey_slot_8_15),
                ("gen_ecckey_slot_16_23", config.gen_ecckey_slot_16_23),
                ("gen_ecckey_slot_24_31", config.gen_ecckey_slot_24_31),
            ],
        )

        self.logger.debug("ECC key slot: %d.", slot)
        try:
            self.r_ecc_keys.generate(slot, curve, self.trng2)
        except ECCKeyExistsInSlotError as exc:
            raise L3ProcessingErrorFail(exc) from None

        self.logger.debug("Generated ECC key in slot=%d.", slot)
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
                ("store_ecckey_slot_0_7", config.store_ecckey_slot_0_7),
                ("store_ecckey_slot_8_15", config.store_ecckey_slot_8_15),
                ("store_ecckey_slot_16_23", config.store_ecckey_slot_16_23),
                ("store_ecckey_slot_24_31", config.store_ecckey_slot_24_31),
            ],
        )

        self.logger.debug("ECC key slot: %d.", slot)
        try:
            self.r_ecc_keys.store(slot, curve, command.k.to_bytes())
        except (ECCKeyExistsInSlotError, ECCKeySetupError) as exc:
            raise L3ProcessingErrorFail(exc) from None

        self.logger.debug("Stored ECC key in slot=%d.", slot)
        return TsL3EccKeyStoreResult(result=L3ResultFieldEnum.OK)

    def ts_l3_ecc_key_read(
        self, command: TsL3EccKeyReadCommand
    ) -> TsL3EccKeyReadResult:
        config = self.config.cfg_uap_ecc_key_read
        self._check_ranged_access_privileges(
            (slot := command.slot.value),
            [
                ("read_ecckey_slot_0_7", config.read_ecckey_slot_0_7),
                ("read_ecckey_slot_8_15", config.read_ecckey_slot_8_15),
                ("read_ecckey_slot_16_23", config.read_ecckey_slot_16_23),
                ("read_ecckey_slot_24_31", config.read_ecckey_slot_24_31),
            ],
        )

        self.logger.debug("ECC key slot: %d.", slot)
        try:
            curve, pub_key, origin = self.r_ecc_keys.read(slot)
        except ECCKeyDoesNotExistInSlotError as exc:
            raise L3ProcessingError(
                exc, result=TsL3EccKeyReadResult.ResultEnum.INVALID_KEY
            ) from None
        self.logger.debug(
            "Read ECC key from slot=%d: curve=%d; pub_key=%s; randomly generated=%d.",
            slot,
            curve,
            pub_key,
            origin,
        )

        return TsL3EccKeyReadResult(
            result=L3ResultFieldEnum.OK,
            curve=curve,
            origin=origin,
            pub_key=pub_key,
        )

    def ts_l3_ecc_key_erase(
        self, command: TsL3EccKeyEraseCommand
    ) -> TsL3EccKeyEraseResult:
        config = self.config.cfg_uap_ecc_key_erase
        self._check_ranged_access_privileges(
            (slot := command.slot.value),
            [
                ("erase_ecckey_slot_0_7", config.erase_ecckey_slot_0_7),
                ("erase_ecckey_slot_8_15", config.erase_ecckey_slot_8_15),
                ("erase_ecckey_slot_16_23", config.erase_ecckey_slot_16_23),
                ("erase_ecckey_slot_24_31", config.erase_ecckey_slot_24_31),
            ],
        )

        self.logger.debug("ECC key slot: %d.", slot)
        self.r_ecc_keys.erase(slot)

        self.logger.debug("Erased ECC key in slot=%d.", slot)
        return TsL3EccKeyEraseResult(result=L3ResultFieldEnum.OK)

    def ts_l3_ecdsa_sign(self, command: TsL3EcdsaSignCommand) -> TsL3EcdsaSignResult:
        config = self.config.cfg_uap_ecdsa_sign
        self._check_ranged_access_privileges(
            (slot := command.slot.value),
            [
                ("ecdsa_ecckey_slot_0_7", config.ecdsa_ecckey_slot_0_7),
                ("ecdsa_ecckey_slot_8_15", config.ecdsa_ecckey_slot_8_15),
                ("ecdsa_ecckey_slot_16_23", config.ecdsa_ecckey_slot_16_23),
                ("ecdsa_ecckey_slot_24_31", config.ecdsa_ecckey_slot_24_31),
            ],
        )

        msg_hash = command.msg_hash.to_bytes()
        self.logger.debug("Message hash: %s.", msg_hash)
        try:
            r, s = self.r_ecc_keys.ecdsa_sign(
                slot,
                msg_hash,
                self.session.handshake_hash,
                # CMD nonce is incremented right after the L3 command is received but
                # according to the datasheet the nonce has to be incremented
                # after processing an L3 Command packet and encrypting an L3 Result packet.
                # It's not clear why the model holds two NONCEs but the SPECT needs
                # to get the one which is incremented after L3 response is encrypted.
                # SPECT takes the SCN in little-endian form, it will be discussed
                # and probably fixed in SPECT, for now hotfixed in model.
                self.session.nonce_resp.to_bytes(4, byteorder="little"),
            )
        except (ECCKeyDoesNotExistInSlotError, CurveMismatchError) as exc:
            self.logger.info(exc)
            raise L3ProcessingError(
                result=TsL3EcdsaSignResult.ResultEnum.INVALID_KEY
            ) from None
        except SignatureFailedError as exc:
            raise L3ProcessingErrorFail(exc) from None

        self.logger.debug("Signed message hash with ECDSA: r=%s; s=%s.", r, s)
        return TsL3EcdsaSignResult(result=L3ResultFieldEnum.OK, r=r, s=s)

    def ts_l3_eddsa_sign(self, command: TsL3EddsaSignCommand) -> TsL3EddsaSignResult:
        config = self.config.cfg_uap_eddsa_sign
        self._check_ranged_access_privileges(
            (slot := command.slot.value),
            [
                ("eddsa_ecckey_slot_0_7", config.eddsa_ecckey_slot_0_7),
                ("eddsa_ecckey_slot_8_15", config.eddsa_ecckey_slot_8_15),
                ("eddsa_ecckey_slot_16_23", config.eddsa_ecckey_slot_16_23),
                ("eddsa_ecckey_slot_24_31", config.eddsa_ecckey_slot_24_31),
            ],
        )

        msg_bytes = command.msg.to_bytes()
        self.logger.debug("Message: %s.", msg_bytes)
        try:
            r, s = self.r_ecc_keys.eddsa_sign(
                slot,
                msg_bytes,
                self.session.handshake_hash,
                # CMD nonce is incremented right after the L3 command is received but
                # according to the datasheet the nonce has to be incremented
                # after processing an L3 Command packet and encrypting an L3 Result packet.
                # It's not clear why the model holds two NONCEs but the SPECT needs
                # to get the one which is incremented after L3 response is encrypted.
                # SPECT takes the SCN in little-endian form, it will be discussed
                # and probably fixed in SPECT, for now hotfixed in model.
                self.session.nonce_resp.to_bytes(4, byteorder="little"),
            )
        except (ECCKeyDoesNotExistInSlotError, CurveMismatchError) as exc:
            self.logger.info(exc)
            raise L3ProcessingError(
                result=TsL3EcdsaSignResult.ResultEnum.INVALID_KEY
            ) from None

        self.logger.debug("Signed message with EdDSA: r=%s; s=%s.", r, s)
        return TsL3EddsaSignResult(result=L3ResultFieldEnum.OK, r=r, s=s)

    def ts_l3_mac_and_destroy(
        self, command: TsL3MacAndDestroyCommand
    ) -> TsL3MacAndDestroyResult:
        raise L3ProcessingErrorInvalidCmd("Mac-and-Destroy not yet available.")
