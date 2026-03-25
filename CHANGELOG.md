# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Changed

- Changed method of deriving seed from TRNG for ephemeral X25519 keys for secure channel and EdDSA keys.

### Added

### Fixed

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