# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Fixed

- Tests: `test_server/test_configuration.py` expected `pydantic.ValidationError`, but
  since the pydantic v2 migration (#15) the configuration models raise
  `pydantic.v1.ValidationError`; two tests failed deterministically
- Configuration object generator template imported `StrictInt` from `pydantic`
  instead of `pydantic.v1`, so regenerating `configuration_object_impl.py` would
  mix v1 models with a v2 type

## [2.5]

### Changed

- Target ts-tr01-app FW version 2.1.0
- Target SPECT FW version 1.3.0
- `--configuration-out` CLI argument is now optional. When omitted, the model
  server no longer writes `./.model_config_save.yaml` — the save callback becomes
  a no-op and nothing is written to disk (ETR01SV-100)
- SPI FSM: busy emulation (`READY=0` / `NO_RESP`) now fires *before* the response
  chunk is sent while a response is still pending, rather than only after the
  buffer is drained — tightening the "busy chip" emulation added in 2.4

### Added

- `r_ecc_keys` slots can now load a signing key directly from a PEM/DER file via
  `private_key`; the `s`/`prefix`/`a` (Ed25519) or `d`/`w`/`a` (P-256) components
  are derived automatically (clamping and EdDSA prefix handled correctly),
  removing the need to compute and clamp them by hand. Mirrors how
  `s_t_priv`/`s_t_pub` already load. Includes example config and docs on the
  common EdDSA prefix pitfall (prefix is `sha512(seed)[32:]`, not `sha512(s)[:32]`)

### Fixed

- Model: partition slot keys are now serialized as plain `int` in
  `GenericPartition.to_dict()`, preventing enum-typed keys from leaking into the
  dumped config

## [2.4]

### Changed

- Changed method of deriving seed from TRNG for ephemeral X25519 keys for secure channel and EdDSA keys
- Regenerated L2 and L3 API from updated datasheet XML — renamed result enums (`PAIRING_KEY_EMPTY` → `SLOT_EMPTY`, `PAIRING_KEY_INVALID` → `SLOT_INVALID`, `WRITE_FAIL` → `SLOT_NOT_EMPTY`), added `HARDWARE_FAIL` result to PairingKeyWrite, PairingKeyInvalidate, RConfigWrite, IConfigWrite, and RMemDataWrite commands, updated docstrings
- Updated chip status constant — added `BOOT_HOLD` flag to `L1ChipStatusFlag`
- Target SPECT FW version 1.2.0
- Updated model Configuration Object registers and addresses
- CO generator now accepts separate bootloader and application XML inputs; overlapping registers between the two are validated for consistency
- Firmware version is now configurable via config file (`riscv_fw_version`, `spect_fw_version`). Default values always represent the concrete firmware versions available at the time of the model release (see [Firmware version defaults](tvl/targets/model/README.md#firmware-version-defaults))
- SPI FSM: busy emulation now only fires while a response is still pending, not after the buffer is drained

### Added

- Firmware version encoding matching the format used by the firmware build system
- Bootloader CO registers to model configuration object (`CfgStartUp`, `CfgSensors`, `CfgDebug`, `CfgGpo`)
- `TCPTropicProtocol` client class for communicating with a model TCP server
- Python 3.14 compatibility (annotation processing rewrite)
- TCP transport smoke tests

### Fixed

- Model responds with L2 GEN_ERR on L3 size mismatch and invalidates session (ETR01SV-79)
- Defer TCP listen until model is ready — fix startup race (TR01SV-98)
- SPI FSM: chip status byte on command acceptance (`READY` flag now set correctly) (ETR01SV-126)
- Restore `latest_response` on aborted SPI transaction
- Re-queue odata on CSN high to prevent stale buffer crash
- Endianity in ECC key and ETPriv generation
- Pin cffi >=2.0 for Python 3.9+ to support Python 3.14
- Widen cryptography version constraint to >43

## [2.3]

### Changed
- Updated L3 API to support UDATA slot size of 475 bytes

### Added

### Fixed
- Fixed UDATA slot size configuration in L3 model

## [2.2]

### Changed
- Update API to allowe EdDSA sing command with empty message

### Added

### Fixed

## [2.1]

### Fixed
- Expected result value in some L3 tests from `L3ResultFieldEnum.FAIL` to `L3ResultFieldEnum.UNAUTHORIZED`
- Exception raising in some L3 test

## [2.0]

### Changed
- `model_server`: model state is now saved upon termination of the tcp server

### Added
- Added support for irq_state in low-level functions

## [1.8]

### Added
- Added install job