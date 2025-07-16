######################################
##### Parse COBS                ######
######################################

def cobs_decode(enc_data:list[int], index:int=0):
    """ COBSデコードを行う。
    COBSエンコードされたデータをデコードし、元のデータと残りのエンコードデータを返す。
    Args:
        enc_data (list[int]): COBSエンコードされたデータのリスト。
        index (int): デコードを開始するインデックス。デフォルトは0。
    Returns:
        (dec_data, rest_index) ((list[int], int)): 
            dec_data: デコードされたデータのリスト。

            rest_index: 残りのエンコードデータの開始インデックス。
    """
    dec_data:list[int] = []
    enc_idx = index

    next_0x00 = 0
    next_is_overhead = True
    is_end = False

    while enc_idx < len(enc_data):
        if next_0x00 != 0:
            dec_data.append(enc_data[enc_idx])
            enc_idx += 1
        else:
            if enc_data[enc_idx] == 0x00:
                is_end = True
                # 終端コード(0x00)発見時は処理を終了する。
                break

            if next_is_overhead == True:
                pass
            else:
                dec_data.append(0)

            next_0x00 = enc_data[enc_idx]
            enc_idx += 1

            if next_0x00 == 0xff:
                next_is_overhead = True
            else:
                next_is_overhead = False
        next_0x00 -= 1

    if is_end == False:
        # 終端コード(0x00)が見つからなかった場合は、
        # []を返す。
        print("COBS decode error: no end code found")
        return [], enc_idx+1
    return dec_data, enc_idx+1


def cobs_encode(data:list[int]):
    encoded_data:list[int] = []
    encoding_block:list[int] = [0x00]

    for byte in data:
        if len(encoding_block) == 255:
            # エンコードブロックが255バイト(すなわち、254個連続して0x00を含まない)場合は、
            # 現在のエンコードブロックを追加し、新しいブロックを開始する。
            encoding_block[0] = len(encoding_block)
            encoded_data.extend(encoding_block)
            encoding_block = [0x00]

        if byte == 0x00:
            encoding_block[0] = len(encoding_block)
            encoded_data.extend(encoding_block)
            encoding_block = [0x00]
        else:
            encoding_block.append(byte)


    # 最後にencoding_blockを流し、終端コード(0x00)を追加する。
    encoding_block[0] = len(encoding_block)
    encoded_data.extend(encoding_block)
    encoded_data.append(0)

    return encoded_data