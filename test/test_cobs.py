def test_cobs():
    import sys
    import os
    
    # Add the parent directory to sys.path to import lib.cobs
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from lib.cobs import cobs_encode, cobs_decode
    import cobs.cobs

    # Test data
    test_data = [1, 2, 3, 0, 4, 5, 6, 0, 7, 8, 9, 0]
    for i in range(256):
        test_data.append(i)
    test_data.extend([4, 5, 6, 0, 7, 8, 9, 0, 10, 11, 12, 0])


    for i in range(len(test_data)-1):
        for j in range(i+1, len(test_data)):
            # Create a sublist for testing
            sub_test_data = test_data[i:j]
 
            # Encode the sublist
            encoded_data = cobs_encode(sub_test_data)
            assert encoded_data == list(cobs.cobs.encode(bytearray(sub_test_data))+b'\x00'), "Encoding mismatch!"

            # Decode the encoded data
            decoded_data, _ = cobs_decode(encoded_data)
            assert decoded_data == list(cobs.cobs.decode(bytearray(encoded_data[:len(encoded_data)-1]))), "Decoding mismatch!"

            # Check if the decoded data matches the original sublist
            assert decoded_data == sub_test_data, "Decoded data does not match original data!"

    # Encode the test data
    encoded_data = cobs_encode(test_data)
    print(f'Encoded Data: {encoded_data}')

    # Decode the encoded data
    decoded_data, _ = cobs_decode(encoded_data)
    print(f'Decoded Data: {decoded_data}')

    # Check if the decoded data matches the original test data
    assert decoded_data == test_data, "Decoded data does not match original data!"