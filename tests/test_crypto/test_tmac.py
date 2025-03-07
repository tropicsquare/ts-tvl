from binascii import unhexlify
from typing import Optional

import pytest

from tvl.crypto.tmac import tmac

# Test vectors are from the repository `ts-crypto-blocks` commit `9c93898``
# How to run:
# ts_sim_run.py tb_tmac_rtl tmac_test --add-sim-options "+DEBUG" --seed <seed>


def __sv_str_to_py_bytes(x: str) -> bytes:
    t = x.replace("'{", "").replace("}", "").replace("'h", "").split(", ")
    t = "".join(x.zfill(2) for x in t)
    return unhexlify(t.encode())


def __int_to_bytes(x: int, *, length: Optional[int] = None) -> bytes:
    if length is None:
        length = (x.bit_length() + 7) // 8
    return x.to_bytes(length, byteorder="big")


@pytest.mark.parametrize(
    "nonce, key, input_data, expected_data",
    [
        pytest.param(
            0x6B,
            0x4AFB04B3F4D18C4F6458C910FCC2BA71A9899DFAA49B29CE4AF534E0F695A072,
            "'{'hce, 'he8, 'hd2, 'h61, 'h87, 'h1, 'h25, 'h1c, 'ha9, 'h38, 'h6a, 'hc1, 'h81, 'hb1, 'h5c, 'h75, 'h46, 'h73, 'hba, 'h52, 'hae, 'h38, 'h0, 'he9, 'h95, 'ha7, 'hae, 'h2f, 'h99, 'h4c, 'hb0, 'hdb, 'h85, 'h99, 'h7e, 'hf1, 'h32, 'hb4, 'h8d, 'h5e, 'hc7, 'h11, 'h94, 'hbb, 'h92, 'hf3, 'h8b, 'h3, 'h48, 'h6d, 'h6b, 'had, 'hb, 'hce, 'h73, 'h64, 'h36, 'h11, 'hb4, 'h1d, 'h3d, 'h6f, 'h85, 'h16, 'he6, 'h6, 'had, 'h42, 'h73, 'ha8, 'hc6, 'hb4, 'h7a, 'hb7, 'he4, 'h44, 'h3f, 'h69, 'hb4, 'h61, 'h5d, 'h75, 'h9e, 'h71, 'h97, 'h6, 'h18, 'h80, 'h95, 'hb7, 'h9e, 'h2c, 'hf5, 'h31, 'h6a, 'hf8, 'h8b, 'hbb, 'h54, 'h21, 'hae, 'h35, 'ha4, 'h97, 'hc8, 'h96, 'h88, 'hc0, 'h87, 'hb6, 'he, 'h25, 'h30, 'hb, 'h10, 'h79, 'h6d, 'hb5, 'hdb, 'h2, 'h1d, 'h9a, 'h46, 'h43, 'h78, 'hb4, 'h8e, 'h2d, 'hdb, 'hf4, 'h77, 'h6b, 'h68, 'h3, 'h31, 'h2b, 'h39, 'he7, 'hc8, 'hb3, 'hdd, 'h74, 'h84, 'h97, 'hc3, 'h9d, 'h6b, 'h5, 'hae, 'hf5, 'ha3, 'hc4, 'h3a, 'h1f, 'h8a, 'hf8, 'hf8, 'h98, 'h2f, 'hf5, 'h6, 'he2, 'hf6, 'h51, 'h2c, 'hf1, 'hef, 'h26, 'h9f, 'h1b, 'h45, 'h3c, 'h48, 'h43, 'h3e, 'h43, 'hf5, 'h30, 'hd4, 'h12, 'h9e, 'h1, 'h4, 'h11, 'h63, 'h1, 'h65, 'h87, 'h12, 'hd8, 'h4e, 'h32, 'hdf, 'h1e, 'ha4, 'he0, 'h76, 'he0, 'hba, 'h35, 'ha9, 'h96, 'ha7, 'h7f, 'h2d, 'hd, 'h7, 'heb, 'h7b, 'h56, 'h48, 'h58, 'h84, 'h28, 'h62, 'h59, 'h7a, 'h61, 'h6, 'h19, 'h3a, 'hc2, 'h26, 'hb8, 'h44, 'hef, 'ha9, 'h95, 'h59, 'hdc, 'h15, 'h99, 'h1b, 'hfb, 'hee, 'hd8, 'h81, 'had, 'he1, 'h1, 'h98, 'hfa, 'h6e, 'h77, 'h7e, 'hbe, 'hd4, 'h52, 'hbd, 'h2e, 'hc0, 'h17, 'h83, 'h40, 'h93, 'hf4, 'h9a, 'h90, 'h20, 'h2, 'haa, 'h45, 'h5d, 'had, 'h5a, 'h91, 'hb8, 'ha2, 'h97, 'h6b, 'h17, 'hfd, 'h3, 'hd6, 'h43, 'h6c, 'h87, 'h3a, 'h16, 'hfe, 'ha0, 'h15, 'h59, 'ha4, 'had, 'h9a, 'h7f, 'h2a, 'hd6, 'h51, 'h8b, 'hc3, 'h8f, 'h20, 'h63, 'h94, 'h8d, 'he7, 'haa, 'h6, 'hfe, 'h95, 'h72, 'h37, 'h18, 'h5e, 'ha5, 'h6, 'hba, 'hcd, 'he6, 'h9, 'h73, 'hd7, 'hcb, 'h74, 'h63, 'h17, 'hae, 'h66, 'h84, 'hbc, 'h22, 'hfa, 'hea, 'h74, 'h6e, 'hac, 'hc3, 'hcb, 'hbb, 'h39, 'hc9, 'hf0, 'h24, 'h7b, 'h1f, 'h56, 'hba, 'hd3, 'h1a, 'he0, 'h69, 'h10, 'h87, 'hb8, 'h44, 'hdc, 'h6a, 'h1a, 'h19, 'h24, 'he3, 'hff, 'h56, 'h2e, 'he, 'h28, 'h87, 'h2f, 'h1a, 'h50, 'hbc, 'ha8, 'h3b, 'ha9, 'h86, 'h19, 'h25, 'hbb, 'h20, 'h83, 'hb9, 'h5a, 'h3e, 'h5f, 'h9f, 'h73, 'hd0, 'h1d, 'hde, 'hbc, 'hb1, 'hf7}",
            0xBEF5B7305200EF0E90968B7C2873B7647A20BC2ABBA746699406FBFCAAFA0335,
            id="seed=0",
        ),
        pytest.param(
            0xD1,
            0x89DC851A6DDB42C479DA0237C394F76E9F8EC0F025EA39F44E230C914DAFF494,
            "'{'h30, 'hbf, 'h93, 'h18, 'heb, 'hd5, 'hf, 'h56, 'h37, 'h5b, 'h9e, 'h9e, 'h9, 'hbb, 'hfc, 'ha9, 'h23, 'hd0, 'hfe, 'h28, 'ha, 'h7a, 'hea, 'hd0, 'he5, 'ha2, 'h2c, 'h62, 'hc7, 'h7a, 'h67, 'hea, 'h8a, 'hd9, 'hb7, 'hf6, 'h4d, 'hec, 'hb7, 'hc, 'h30, 'h11, 'h75, 'hc9, 'h71, 'h13, 'h41, 'hb6, 'h4d, 'hc8, 'ha9, 'hd3, 'h79, 'hd, 'h53, 'hce, 'he3, 'h65, 'h58, 'hba, 'ha1, 'h61, 'h37, 'h5e, 'hd7, 'ha1, 'h21, 'hdf, 'he8, 'h10, 'h4c, 'h4b, 'hc7, 'hd5, 'h1c, 'h5a, 'h6a, 'h80, 'hb0, 'h53, 'heb, 'hed, 'h7b, 'h63, 'hf4, 'h44, 'h2e, 'hd1, 'h51, 'he1, 'h26, 'h8e, 'h2, 'h84, 'hcc, 'h43, 'h49, 'h67, 'ha1, 'heb, 'h1a, 'h3a, 'h38, 'h10, 'hed, 'h90, 'h6b, 'hea, 'haf, 'h5f, 'h42, 'hd3, 'hd5, 'h25, 'hac, 'h30, 'h89, 'haa, 'h9f, 'hbc, 'hd, 'hed, 'h8d, 'h23, 'hf3, 'h63, 'h7c, 'h8, 'hdd, 'h9f, 'h97, 'ha2, 'h24, 'h1e, 'h1c, 'hb7, 'h43, 'h69, 'h86, 'hc3, 'h8b, 'h23, 'h7d, 'hd6, 'h89, 'hc, 'hae, 'h6, 'h7c, 'hf6, 'hed, 'hc7, 'h21, 'he4, 'hcd, 'hdb, 'h4a, 'hf7, 'h8e, 'h99, 'h3, 'h2e, 'he0, 'h21, 'hbf, 'hf, 'h82, 'h5b, 'he3, 'h4b, 'hb, 'h4b, 'hfc, 'h26, 'hbf, 'h8f, 'h6b, 'h9a, 'hec, 'h4f, 'h1d, 'h2e, 'h42, 'h82, 'h49, 'h21, 'ha1, 'h46, 'ha1, 'hf3, 'h83, 'h44, 'h78, 'h0, 'h5a, 'hef, 'h1e, 'hf8, 'h5d, 'h2e, 'hc4, 'h92, 'hfa, 'h6c, 'h85, 'hf3, 'hf3, 'h2c, 'h89, 'h53, 'h96, 'hf1, 'ha6, 'h1a, 'h95, 'h2e, 'h54, 'hdd, 'hee, 'h5b, 'hf0, 'hdd, 'h95, 'h7, 'h95, 'h96, 'h7d, 'h3e, 'h2f, 'hef, 'hfb, 'hb5, 'h90, 'h3f, 'h99, 'hc0, 'h8f, 'h3d, 'hf2, 'hf7, 'hcb, 'hf, 'h5, 'h13, 'h38, 'h2c, 'h36, 'h8c, 'h55, 'h9a, 'hef, 'h13, 'h8c, 'hd5, 'h7a, 'hae, 'h86, 'h17, 'h1, 'h2, 'hcf, 'ha5, 'hb5, 'heb, 'hf1, 'hae, 'h29, 'hc5, 'h7f, 'hd8, 'h4a, 'h65, 'hd2, 'he2, 'h70, 'hc7, 'h61, 'hc4, 'h25, 'h7a, 'h8d, 'hac, 'h32, 'hf3, 'hef, 'h71, 'h7c, 'h7c, 'hee, 'h17, 'hab, 'h49, 'he4, 'hc, 'hb5, 'h3f, 'h52, 'h96, 'hbb, 'hc9, 'h6e, 'h3e, 'h33, 'h87, 'hdc, 'h92, 'hba, 'hfa, 'he, 'hb8, 'h39, 'ha1, 'h61, 'he3, 'h58, 'h9e, 'h92, 'hd6, 'he9, 'hd5, 'he0, 'h5f, 'hbe, 'h7b, 'hc3, 'h99, 'h97, 'hc4, 'h2b, 'h6, 'h22, 'hc5, 'hec, 'h84, 'h5f, 'h2e, 'h32, 'h81, 'h4c, 'h3b, 'hfd, 'he9, 'hc7, 'h67, 'h6c, 'h6a, 'h72, 'h78, 'h87, 'heb, 'he1, 'h10, 'hdb, 'h23, 'hec, 'h32, 'hb3, 'h75, 'h2b, 'hdb, 'h7f, 'h9a, 'hcf, 'ha8, 'h65, 'h1a, 'hdb, 'h8f, 'h8e, 'hdb, 'hc4, 'hd, 'h89, 'h99, 'h1, 'hb0, 'h6e, 'hfa, 'h23, 'h2b, 'h30, 'h3d, 'hc5, 'hcd, 'h8d, 'hfe, 'h31, 'h4f, 'h1a, 'h49, 'h3f, 'h8f, 'haa, 'h56, 'h1a, 'he1, 'hf3, 'h90, 'h5a, 'ha6, 'h20, 'h9, 'h30, 'hda, 'h9e, 'h7, 'hc9, 'hd0, 'h69, 'h2c, 'hd3, 'h9, 'h47, 'hd1, 'hdd, 'h2e, 'h2f, 'h44, 'h9d, 'h9, 'h7e, 'hc1, 'h43, 'h88, 'hd5, 'hea, 'h61, 'h6c, 'h69, 'h38, 'h9b, 'hbb, 'hf4, 'h9d, 'hce, 'he5, 'h7e, 'h2a, 'h38, 'hab, 'h4c, 'hb2, 'had, 'hff, 'h63, 'h6c, 'h9, 'ha9, 'h10, 'h82, 'h1c, 'he8, 'h20, 'hd1, 'h1d, 'hdc, 'hf7, 'h80, 'ha8, 'h21, 'he7, 'h1e, 'h51, 'h1d, 'hdc, 'hc7, 'h58, 'hef, 'h6b, 'hc0, 'hc7, 'h5a, 'hc6, 'h6a, 'h89, 'h75, 'hc4, 'h7d, 'hbe, 'hb1, 'hc6, 'h18, 'hee, 'hf0, 'h35, 'hdb, 'hec, 'h4f, 'h68, 'h31, 'hbc, 'h3f, 'h8c, 'haf, 'hb8, 'h78, 'h60, 'hd9, 'ha8, 'h4b, 'h33, 'hd2, 'h27, 'h17, 'had, 'h55, 'h6f, 'hea, 'h44, 'haf, 'hdd, 'h61, 'h3d, 'h6e, 'h73, 'h2a, 'hd1, 'hb2, 'h4c, 'h78, 'hea, 'h9f, 'hb8, 'h4d, 'h80, 'h9f, 'h70, 'h42, 'h28, 'hfb, 'h22, 'h63, 'he5, 'he8, 'h72, 'h2b, 'hd5, 'hd7, 'h65, 'h8a, 'h44, 'hcc, 'h98, 'h9d, 'h15, 'hc3, 'haf, 'ha3, 'h4b, 'h96, 'hd3, 'hac, 'h5f, 'h57, 'h9e, 'h59, 'hbc, 'hf4, 'hac, 'hbf, 'h52, 'hac, 'hcf, 'h46, 'he, 'h24, 'hac, 'h5e, 'hc2, 'h35, 'h63, 'hfe, 'h1b, 'had, 'h36, 'hd2, 'h5e, 'h34, 'h3b, 'h76, 'he, 'hb7, 'hfb, 'h7d, 'h76, 'h7b, 'h53, 'hf7, 'h90, 'h5c, 'h92, 'ha3, 'h12, 'h65, 'h4d, 'h80, 'hf4, 'hdb, 'h5c, 'h32, 'hb0, 'h4f, 'haf, 'h7b, 'hc6, 'ha5, 'h20, 'h4d, 'h67, 'he9, 'h41, 'h7e, 'hb3, 'he5, 'hee, 'h8c, 'h58, 'h75, 'h97, 'h7d, 'hef, 'hcf, 'hda, 'h8b, 'h7e, 'he1, 'h37, 'h58, 'h57, 'heb, 'h91, 'hb1, 'hd4, 'h22, 'h71, 'h7a, 'h18, 'hd2, 'h4e, 'h89, 'h69, 'hf6, 'h84, 'hd1, 'h25, 'h3, 'h64, 'haa, 'h6f, 'he8, 'h23, 'ha8, 'hbf, 'h44, 'hb8, 'hf5, 'hb6, 'h78, 'hde, 'hcf, 'hfe, 'h6b, 'h91, 'h1, 'h3a, 'h18, 'h2e, 'h68, 'hd1, 'h7b, 'h5e, 'h1e, 'hf6, 'hc4, 'hd8, 'h2f, 'h53, 'hf8, 'heb, 'h8c, 'h94, 'h72, 'ha3, 'h25, 'hed, 'h2d, 'hef, 'h49, 'h91, 'h4d, 'h8c, 'h8a, 'h6e, 'h1f, 'h7a, 'h37, 'h7b, 'h74, 'he4, 'hee, 'h2b, 'h8, 'h1b, 'h7, 'hcd, 'h93, 'h21, 'h99, 'hd3, 'hc1, 'hc4, 'h11, 'h4, 'h7d, 'hd3, 'h1e, 'h18, 'hf4, 'h98, 'h9, 'hcf, 'h69, 'h6d, 'h1e, 'h98, 'hb, 'h6e, 'h1f, 'hb8, 'h27, 'h7c, 'hc2, 'h4d, 'h86, 'hcc, 'h6b, 'hb0, 'h11, 'h5f, 'hb, 'hde, 'hc0, 'hce, 'ha6, 'h44, 'h8f, 'he, 'h77, 'h93, 'h25, 'h2a, 'hb9, 'hb5, 'h12, 'hf8, 'h27, 'h3f, 'h21, 'hbe, 'hb5, 'h3e, 'h16, 'hb6, 'hca, 'h69, 'h5b, 'h7b, 'ha0, 'ha1, 'h46, 'h54, 'hdd, 'h92, 'h8b, 'h20, 'hbb, 'h1, 'h26, 'heb, 'h6e, 'h12, 'h17, 'h4a, 'h2a, 'h72, 'h2c, 'h95, 'h46, 'h8a, 'hae, 'h91, 'hd2, 'hb5, 'h93, 'ha3, 'hc5, 'haf, 'h85, 'h55, 'hba, 'hb4, 'he0, 'h81, 'he3, 'h7b, 'hf1, 'h8b, 'h17, 'h6d, 'h26, 'h12, 'h9a, 'h84, 'h0, 'h9f, 'h69, 'h14, 'h69, 'h4a, 'h59, 'h2f, 'hf5, 'h70, 'h43, 'h95, 'h5b, 'h63, 'hd5, 'h89, 'h83, 'hfe, 'hdc, 'h6, 'he6, 'h6d, 'h45, 'h39, 'hd4, 'h8e, 'hd9, 'hc2, 'h55, 'hda, 'hc6, 'h72, 'h9d, 'h46, 'h6a, 'hd4, 'h88, 'hcb, 'h82, 'hc5, 'hc8, 'h70, 'hd5, 'h29, 'hae, 'h78, 'h5c, 'h67, 'hc, 'hd5, 'h46, 'he5, 'hb8, 'h0, 'h50, 'h30, 'h57, 'h59, 'h18, 'h96, 'h24, 'h4f, 'h96, 'h50, 'h70, 'hcb, 'h4a, 'h2a, 'h65, 'hf2, 'h49, 'h72, 'h3a, 'h32, 'hd7, 'h42, 'h68, 'hdb, 'h69, 'h74, 'h9e, 'h83, 'h6c, 'hbb, 'hc7, 'h56, 'hcb, 'h88, 'hab, 'h67, 'h37, 'hf1, 'h1c, 'hb2, 'h9c, 'hcc, 'ha6, 'ha, 'h63, 'hff, 'h9f, 'h42, 'h3f, 'h78, 'hf2, 'hf9, 'h59, 'hb4, 'h32, 'h15, 'hb4, 'h94, 'h49, 'h5, 'hfb, 'h7b, 'hb5, 'h83, 'hd4, 'h31, 'hcb, 'h96, 'h6b, 'hc6, 'h95, 'h53, 'h6c, 'h71, 'h52, 'h93, 'hf8, 'h83, 'haa, 'h24, 'hda, 'hfd, 'h61, 'h34, 'h2b, 'h15}",
            0x858D583D287377817359BA8C850F51BD4DBDD5C5D5692BA766F0132B1C55AEC2,
            id="seed=438560",
        ),
        pytest.param(
            0x88,
            0x25F52F10E3C4A3B542CF7D4A4963C88A5659762777FBEDA9E6C27485600727D7,
            "'{'hf5, 'h8a, 'he, 'h6, 'h1, 'h5f, 'h2a, 'hcf, 'h88, 'h42, 'hcf, 'h9c, 'h49, 'h2c, 'h4f, 'h93, 'h8d, 'h6f, 'h9c, 'hcd, 'h6d, 'h72, 'he3, 'h6b, 'h33, 'he3, 'h48, 'hc8, 'h86, 'hbf, 'hcd, 'h57, 'hd2, 'he4, 'h18, 'h88, 'h55, 'hb5, 'hea, 'hed, 'h48, 'h40, 'hbb, 'h30, 'h93, 'h0, 'hca, 'h25, 'hf0, 'hb5, 'h97, 'h61, 'h49, 'hf3, 'h46, 'he4, 'h7a, 'hdc, 'h2, 'h1b, 'hac, 'hed, 'h9f, 'h0, 'h87, 'hcb, 'hf3, 'hd8, 'h9b, 'hd1, 'ha7, 'hfc, 'h36, 'h50, 'h98, 'h1b, 'h10, 'h0, 'h83, 'h98, 'h8b, 'hed, 'h1b, 'hf5, 'h66, 'h9b, 'h8f, 'hb3, 'h20, 'hdc, 'hca, 'h7e, 'h4, 'h99, 'ha8, 'ha, 'h2d, 'h49, 'h7e, 'hd3, 'h7d, 'h47, 'he4, 'h4f, 'h90, 'hd8, 'h3e, 'h62, 'h45, 'had, 'h91, 'hb8, 'hc0, 'hfa, 'hba, 'h4a, 'hde, 'ha9, 'h16, 'h4e, 'had, 'h47, 'h35, 'h32, 'h52, 'h24, 'hef, 'h47, 'h2c, 'h8b, 'hdc, 'he4, 'ha8, 'hed, 'h7c, 'hb, 'had, 'hd, 'h64, 'h8e, 'h76, 'h29, 'h6d, 'hd9, 'hec, 'h40, 'hf3, 'hf5, 'h2b, 'h9a, 'h8e, 'he5, 'he5, 'hb2, 'h56, 'h97, 'hc1, 'h76, 'h7f, 'hef, 'hed, 'he8, 'hcd, 'h6a, 'hcd, 'he2, 'h29, 'h4e, 'h55, 'h86, 'hbd, 'h21, 'hfc, 'he, 'h12, 'h37, 'h6e, 'h73, 'he9, 'h7f, 'h0, 'ha1, 'h25, 'hb6, 'h6, 'h39, 'h94, 'hc9, 'hfd, 'hab, 'h9, 'h6, 'hd7, 'h8, 'h76, 'hb3, 'h11, 'h3f, 'hd4, 'h96, 'h3d, 'h3, 'h78, 'he5, 'hf8, 'h4b, 'h59, 'hbc, 'hf5, 'h3e, 'hcf, 'hc0, 'had, 'h67, 'h37, 'hfc, 'h4a, 'h21, 'hfc, 'he5, 'h51, 'h19, 'hac, 'h12, 'hde, 'h54, 'h72, 'h5b, 'hab, 'h86, 'h8, 'he8, 'h88, 'hbf, 'hfd, 'hd7, 'h35, 'h1c, 'hc5, 'h7c, 'hf9, 'h50, 'h49, 'h1e, 'he, 'h17, 'h4a, 'he9, 'hdd, 'ha9, 'h22, 'h88, 'hac, 'hf0, 'hef, 'hf6, 'hb4, 'h8, 'ha4, 'ha7, 'hfd, 'he5, 'h32, 'h49, 'h9d, 'hd3, 'h7d, 'hf2, 'hed, 'he1, 'h47, 'h75, 'hec, 'h7, 'hdf, 'h14, 'h93, 'h52, 'ha0, 'h1b, 'h5c, 'haa, 'h5f, 'hcf, 'h38, 'h86, 'hdf, 'h6b, 'h1d, 'hc5, 'hd2, 'h21, 'h2f, 'h82, 'h9f, 'h1e, 'h4a, 'h41, 'haa, 'h26, 'hf, 'hb1, 'h64, 'h4f, 'h7c, 'he2, 'hfc, 'h21, 'h6e, 'h94, 'hd1, 'hc0, 'ha4, 'h2b, 'h1f, 'hbc, 'hab, 'haf, 'hba, 'h27, 'hd2, 'hcc, 'hd4, 'h34, 'hac, 'h54, 'h63, 'h3, 'ha0, 'h81, 'h7d, 'h44, 'h33, 'hd5, 'h78, 'h88, 'h72, 'h32, 'h9f, 'hf5, 'h85, 'h1a, 'h99, 'h67, 'h27, 'h5, 'he1, 'hbb, 'he6, 'h76, 'h38, 'h37, 'h88, 'h23, 'h1a, 'h6, 'h97, 'h8, 'he4, 'h87, 'h90, 'ha4, 'h9b, 'hc, 'h9a, 'h45, 'h8, 'h6a, 'hf5, 'h96, 'h59, 'h30, 'hf4, 'h4b, 'h15, 'h46, 'h41, 'h1e, 'hbb, 'ha9, 'h5, 'hde, 'h7, 'h5e, 'ha0, 'h56, 'hcf, 'hb2, 'h1, 'h24, 'hd9, 'h50, 'h96, 'h40, 'h71, 'h22, 'h10, 'h99, 'h98, 'hcf, 'h34, 'hb8, 'ha0, 'h31, 'h83, 'h87, 'hf4, 'h53, 'h82, 'hb, 'h75, 'h8, 'he4, 'hdd, 'haf, 'h1a, 'h8b, 'hb0, 'h5d, 'haa, 'h68, 'he0, 'h34, 'h66, 'he4, 'hcc, 'hf8, 'had, 'h58, 'ha9, 'h56, 'h2a, 'heb, 'h4e, 'hc5, 'hf8, 'hfa, 'h95, 'h82, 'h9d, 'hd3, 'h43, 'h49, 'h93, 'h1b, 'h1e, 'h14, 'h4a, 'h1b, 'h9a, 'haa, 'h26, 'hf3, 'hc7, 'hae, 'h60, 'h67, 'h5, 'h67, 'h71, 'hba, 'hec, 'h8c, 'h96, 'hda, 'h4d, 'hdb, 'h5, 'hcb, 'hd5, 'hea, 'h9a, 'h3e, 'h8f, 'he9, 'h13, 'hd2, 'h68, 'hc6, 'hb4, 'hf6, 'h81, 'h27, 'hf8, 'h40, 'hb2, 'h21, 'h97, 'hfc, 'h27, 'hdb, 'h4, 'h62, 'h3f, 'h5f, 'h43, 'h9a, 'h6, 'h2a, 'he, 'hb1, 'h14, 'h36, 'h44, 'hd3, 'hba, 'hbc, 'h6d, 'h73, 'ha0, 'hfb, 'h38, 'h17, 'h42, 'ha6, 'hf7, 'hb2, 'hf0, 'h85, 'hfd, 'h3a, 'h51, 'hf2, 'h1e, 'h84, 'h72, 'h5c, 'h85, 'h2b, 'hb8, 'h54, 'h6d, 'h0, 'heb, 'h8b, 'h4, 'h6e, 'hb6, 'h4c, 'h5b, 'hea, 'h60, 'h23, 'h50, 'hd0, 'heb, 'h33, 'h29, 'ha5, 'hf1, 'h51, 'h0, 'h5a, 'hb0, 'h24, 'h91, 'h85, 'h86, 'he8, 'ha6, 'h19, 'hd6, 'ha1, 'h5f, 'h98, 'h0, 'he4, 'ha4, 'h5b, 'haa, 'h28, 'hca, 'h57, 'hdc, 'h13, 'h6b, 'h12, 'h5c, 'h20, 'h69, 'h32, 'h96, 'hb8, 'he, 'h40, 'h7, 'h28, 'h71, 'hf9, 'ha7, 'h27, 'h8f, 'h18, 'h3, 'h8, 'hc, 'h91, 'hc3, 'ha0, 'h77, 'hde, 'h31, 'h64, 'h46, 'h59, 'h58, 'h9c, 'h63, 'hde, 'h34, 'h85, 'h5a, 'h98, 'hf, 'h7f, 'he3, 'h36, 'ha7, 'h9, 'h8e, 'h96, 'h34, 'he7, 'h2d, 'h21, 'hb6, 'h22, 'h15, 'h56, 'hab, 'h4b, 'h93, 'hee, 'h84, 'h9a, 'h80, 'h6, 'h90, 'ha1, 'hb5, 'ha8, 'h7, 'h9e, 'haf, 'hcb, 'h88, 'he1, 'h5d, 'hdd, 'h23, 'h83, 'h81, 'hf4, 'h21, 'hb4, 'hdc, 'h8f, 'h5b, 'h83, 'hdf, 'hf9, 'h54, 'hc0, 'h97, 'h35, 'h2b, 'he0, 'h1, 'h3c, 'hb4, 'he3, 'h80, 'h46, 'h5, 'h46, 'hb, 'h91, 'h1, 'ha6, 'hf0, 'hd6, 'hb9, 'hdb, 'h7f, 'h8, 'h54, 'h7c, 'hdc, 'h1e, 'hfa, 'hcb, 'h83, 'he8, 'hfc, 'ha6, 'h48, 'he5, 'h42, 'h66, 'he9, 'h95, 'h15, 'h90, 'h52, 'h62, 'hd2, 'h22, 'h5a, 'h6f, 'h5b, 'h1d, 'h5e, 'h9d, 'h15, 'h61, 'hea, 'h0, 'h88, 'h22, 'h2, 'hea, 'hc0, 'h9d, 'hb5, 'hd9, 'h87, 'h27, 'h4d, 'h2e, 'h3e, 'hac, 'h3c, 'h61, 'hd0, 'h89, 'h1d, 'h77, 'hb3, 'h82, 'hc8, 'hc2, 'hfb, 'hc7, 'h67, 'h18, 'h45, 'hb2, 'h2e, 'h24, 'hf, 'h4d, 'h2b, 'hc0, 'hbc, 'he4, 'ha2, 'hd9, 'hfc, 'h6f, 'h80, 'hbf, 'h9a, 'hda, 'h7d, 'hbb, 'hcf, 'hc1, 'haa, 'hb4, 'h91, 'hac, 'h13, 'h44, 'hf2, 'ha4, 'hc, 'h4b, 'h22, 'hc3, 'hfa, 'ha6, 'h58, 'h8f, 'hae, 'ha, 'h72, 'h19, 'h22, 'h81, 'hf6, 'h8b, 'h95, 'h70, 'h26, 'h6c, 'hd5, 'h3b, 'hde, 'h45, 'h1, 'h19, 'h93, 'hb6, 'h63, 'h67, 'h5d, 'he0, 'h17, 'h8c, 'h1f, 'h1f, 'h4d, 'h84, 'h18, 'hba, 'he5, 'ha9, 'hac, 'h69, 'h10, 'h3a, 'h2d, 'h3d, 'hce, 'h5c, 'h65, 'h6c, 'h56, 'hc3, 'hf8, 'hf7, 'h1e, 'hb1, 'h11, 'hb, 'h7c, 'he2, 'h52, 'h4e, 'h70, 'h46, 'h29, 'hbd, 'hae, 'h7a, 'h70, 'h6d, 'hf, 'h8d, 'h5c, 'hc1, 'hf6, 'h2a, 'hb4, 'hf0, 'hf8, 'ha, 'h99, 'hd0, 'h38, 'hf0, 'hb9, 'h58, 'hd7, 'h70, 'h5e, 'hf9, 'hd5, 'hc1, 'hdf, 'h8d, 'hf6, 'haf, 'hb7, 'h27, 'hfb, 'ha9, 'he6, 'hd0, 'h65, 'ha6, 'hc5, 'h1f, 'h5d, 'hcc, 'h5, 'hf7, 'h20, 'h36, 'h81, 'h93, 'h49, 'h66, 'h13, 'hf, 'h57, 'ha1, 'h8a, 'h63, 'hd3, 'h26, 'h28, 'hd0, 'hf9, 'hcb, 'h9c, 'h1a, 'had, 'h7b, 'he8, 'h2c, 'hb, 'h3d, 'h24, 'h47, 'h8d, 'ha4, 'h64, 'h61, 'h4, 'hf3, 'h53, 'hf, 'hb2, 'h2c, 'hf3, 'hb8, 'hfc, 'h2b, 'h19, 'h77, 'ha4, 'h9b, 'h4d, 'h9e, 'h1e, 'hbf, 'h97, 'hdd, 'hf8, 'h8f, 'h36, 'haf, 'hd5, 'hb5, 'h5e, 'h69, 'h5d, 'h4f, 'hc5, 'h98, 'hff, 'h80, 'h32}",
            0xB3B2F35D9CB5B33FB2973CF9518FA4DB2242AD577A275144D9918C685CE4C249,
            id="seed=964134",
        ),
        pytest.param(
            0x7D,
            0x2B5545CB07808CEDEBB9016116CA187A162C546CF9C87B191922A9B60EFFFAEE,
            "'{'h82, 'h59, 'h46, 'hea, 'h78, 'hec, 'h91, 'h3c, 'hb8, 'hda, 'h98, 'hd3, 'h59, 'h25, 'h2, 'h88, 'h29, 'hf, 'hc1, 'ha5, 'h5b, 'h81, 'h18, 'hb0, 'hc9, 'h9, 'hf8, 'h75, 'h6d, 'hd5, 'h45, 'h45, 'h75, 'hb2, 'h46, 'h20, 'h56, 'h9d, 'hc, 'hfe, 'hda, 'hf0, 'h74, 'hb1, 'h93, 'hb2, 'h15, 'h5e, 'hd5, 'h4c, 'hb1, 'hb4, 'h4f, 'haa, 'h1f, 'h18, 'h2f, 'h26, 'h75, 'h60, 'hbf, 'hac, 'ha0, 'h5e, 'hf2, 'h65, 'h50, 'h8f, 'h1e, 'hb0, 'hed, 'hd3, 'h64, 'had, 'h94, 'h45, 'h21, 'hfd, 'h59, 'h5f, 'hd3, 'hdd, 'h59, 'h8, 'h46, 'he4, 'he5, 'h26, 'hda, 'h3c, 'hc, 'h5c, 'ha7, 'h45, 'h15, 'h81, 'h85, 'h54, 'hb5, 'h57, 'h45, 'h19, 'h23, 'ha2, 'h45, 'h6c, 'h0, 'h7a, 'h5a, 'hf8, 'ha0, 'hdd, 'h3e, 'h22, 'h1f, 'he, 'hee, 'h7, 'h64, 'h55, 'hab, 'h32, 'h5, 'hcf, 'hf2, 'h6a, 'hc, 'hbc, 'h3d, 'h39, 'h6, 'hcd, 'hfa, 'h33, 'hf8, 'h8, 'hb3, 'h8d, 'h2b, 'hf, 'h7a, 'h2a, 'hbc, 'h67, 'h35, 'he1, 'h69, 'h48, 'h30, 'h5d, 'h4, 'hf0, 'hb3, 'h7b, 'hac, 'h9f, 'hc5, 'h89, 'hba, 'hb3, 'h1f, 'h9d, 'hf6, 'h57, 'h7c, 'hca, 'hbf, 'h8c, 'h4b, 'h33, 'hd1, 'h34, 'h3c, 'h7c, 'h10, 'h81, 'ha7, 'h61, 'h4e, 'h39, 'h79, 'h12, 'h37, 'hdb, 'hba, 'hf1, 'h5d, 'h65, 'hb2, 'h6b, 'h44, 'hfb, 'h4f, 'he3, 'h82, 'h88, 'hba, 'h45, 'h22, 'h5e, 'hd5, 'hce, 'h1f, 'h6c, 'h5c, 'h1, 'h8c, 'hf9, 'h8a, 'h94, 'he6, 'h3b, 'hf9, 'h57, 'h4f, 'h49, 'hd8, 'hb3, 'h3c, 'h79, 'h72, 'h3f, 'hd0, 'h9b, 'h36, 'ha3, 'ha0, 'h7f, 'h9d, 'hf7, 'h4b, 'hdb, 'h26, 'h75, 'ha4, 'h73, 'h30, 'hd8, 'h57, 'hcf, 'h3a, 'h8e, 'hc6, 'hc, 'h5, 'h29, 'hee, 'h35, 'hfe, 'h46, 'h46, 'h42, 'h74, 'h95, 'had, 'h51, 'hc6, 'h2c, 'hd8, 'h25, 'hd, 'hd6, 'hb6, 'hf7, 'h9b, 'h1f, 'hc2, 'hb6, 'h9, 'h2b, 'h5, 'h50, 'h26, 'ha0, 'hdb, 'h91, 'h9e, 'h5c, 'h8b, 'hfa, 'ha8, 'hf1, 'haf, 'h7d, 'hf7, 'h11, 'h3c, 'h3b, 'hb5, 'hd8, 'hfd, 'hb5, 'h83, 'h27, 'he1, 'h2, 'h33, 'h1e, 'hdb, 'ha5, 'h2f, 'h99, 'hc, 'h3, 'h44, 'h6a, 'h38, 'hb0, 'h79, 'h6f, 'hdb, 'h64, 'h7a, 'h3, 'hb3, 'h30, 'h65, 'h7e, 'h2a, 'hdf, 'h45, 'h42, 'hba, 'h13, 'h40, 'h7, 'h97, 'h36, 'h99, 'hf4, 'h4e, 'hc4, 'hf2, 'hc6, 'h35, 'h9e, 'h20, 'h3c, 'h66, 'h6e, 'hd9, 'he, 'h1d, 'heb, 'h74, 'h98, 'h67, 'hef, 'h9b, 'h54, 'hc9, 'h4c, 'h2a, 'h4, 'h1f, 'hfc, 'hfc, 'ha4, 'h15, 'h41, 'h1f, 'he8, 'h2f, 'h52, 'hae, 'h93, 'he2, 'h52, 'h7a, 'hf5, 'h97, 'h95, 'hd, 'had, 'h36, 'h4f, 'h93, 'hc7, 'h1f, 'h7d, 'h1d, 'hc3, 'haf, 'h23, 'h99, 'he0, 'h7e, 'he1, 'had, 'h79, 'hc0, 'hfa, 'hbc, 'hbb, 'hb1, 'hb4, 'hfa, 'h42, 'hf6, 'h52, 'h7b, 'h5a, 'h59, 'hb6, 'hdf, 'hee, 'h53, 'h49, 'h3f, 'h3, 'h9e, 'h22, 'hbf, 'h9d, 'h66, 'hcc, 'h80, 'h67, 'hf6, 'hf9, 'h9b, 'he0, 'h40, 'hc0, 'hd, 'hbb, 'he9, 'h1c, 'hd2, 'hed, 'h15, 'h7e, 'h3, 'ha4, 'h80, 'h3b, 'h69, 'he4, 'h65, 'h70, 'h2, 'h58, 'hc8, 'h79, 'ha1, 'h3d, 'h5, 'hd5, 'h97, 'h43, 'h6, 'hec, 'he6, 'h5c, 'he8, 'h6a, 'h18, 'h9b, 'hce, 'hc8, 'h20, 'hc9, 'h7c, 'h44, 'h39, 'h4e, 'he3, 'hb9, 'hbb, 'h91, 'h60, 'h8b, 'h8a, 'hc5, 'h7b, 'h25, 'h1d, 'h9a, 'hdb, 'h97, 'h41, 'haa, 'h92, 'h37, 'hd4, 'hbb, 'ha7, 'h25, 'h18, 'h25, 'h6a, 'h7a, 'hbb, 'h41, 'had, 'hf2, 'h0, 'h4, 'hcc, 'haa, 'h85, 'ha9, 'h67, 'h70, 'h6e, 'hc6, 'h5b, 'h3d, 'h8d, 'hf0, 'h2e, 'hcd, 'h99, 'hb5, 'h59, 'h5e, 'he6, 'hf3, 'h59, 'h46, 'h73, 'h25, 'hfb, 'h4b, 'h31, 'h19, 'h8a, 'h72, 'h50, 'h1e, 'hee, 'h18, 'h2f, 'h28, 'h46, 'h3a, 'h87, 'h70, 'hff, 'ha6, 'h76, 'h11, 'h77, 'h8e, 'h10, 'hb8, 'hbb, 'h8c, 'hba, 'h22, 'h81, 'h1f, 'h70, 'hb8, 'he2, 'hd1, 'hc6, 'hb, 'hbb, 'hf7, 'hef, 'hab, 'h51, 'hee, 'h3e, 'h2e, 'h81, 'hae, 'h21, 'h9c, 'h8, 'haf, 'h37, 'hb9, 'h1c, 'h1f, 'h25, 'he2, 'h96, 'hd4, 'hd, 'h55, 'hcb, 'hf4, 'h81, 'hf2, 'hcd, 'h3c, 'h4a, 'h8e, 'hca, 'h83, 'h42, 'h3e, 'hd3, 'h15, 'h57, 'h65, 'h22, 'ha4, 'ha5, 'he7, 'hf8, 'h22, 'h21, 'haf, 'h4d, 'hb3, 'h5b, 'he5, 'hf9, 'h95, 'h44, 'hc3, 'h42, 'hdc, 'h83, 'h4e, 'h3d, 'hb, 'h6f, 'h37, 'hb9, 'h58, 'h77, 'he2, 'h6c, 'h7, 'ha3, 'h5c, 'h9c, 'had, 'hcf, 'hfd, 'h9f, 'h31, 'h35, 'h29, 'hf2, 'hf3, 'hf0, 'hb7, 'h9a, 'h51, 'h26, 'h1, 'hbb, 'heb, 'h4f, 'h8a, 'hb6, 'hb8, 'h9, 'hdb, 'h13, 'had, 'h1a, 'h16, 'hf7, 'h81, 'h37, 'h97, 'h56, 'hc7, 'hfb, 'hc5, 'he7, 'h4b, 'hf1, 'hcc, 'ha6, 'hb, 'hf0, 'hfe, 'h57, 'hed, 'h77, 'h4c, 'h5c, 'h88, 'h95, 'h9b, 'h72, 'h4a, 'h58, 'h77, 'h5c, 'he9, 'h6c, 'h2b, 'hf0, 'hd7, 'h9f, 'h93, 'he3, 'hb2, 'h74, 'h77, 'hdf, 'h23, 'h93, 'hde, 'he5, 'h18, 'h18, 'h30, 'h77, 'h95, 'hd2, 'h3a, 'hde, 'h91, 'hc9, 'h39, 'hfd, 'hc2, 'h12, 'h4, 'ha3, 'h42, 'hb3, 'hef, 'hc1, 'h3e, 'h72, 'h3c, 'hbc, 'h72, 'h5a, 'h97, 'h4e, 'hc1, 'h38, 'hf2, 'h66, 'h3f, 'hd5, 'h93, 'h30, 'hf4, 'h78, 'h6e, 'hd0, 'h20, 'h9b, 'hb7, 'h6f, 'h16, 'h46, 'ha5}",
            0xC756EF866D77C401E0DFD8181DA8712044E8C21E9A5F462F7B2D77F43D279EA8,
            id="seed=991159",
        ),
    ],
)
def test_tmac(nonce: int, key: int, input_data: str, expected_data: int):
    assert tmac(
        __int_to_bytes(key, length=32),
        __sv_str_to_py_bytes(input_data),
        __int_to_bytes(nonce),
    ) == __int_to_bytes(expected_data)
