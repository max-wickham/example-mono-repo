with open('/home/max/Downloads/data.bin', 'rb') as f:
    count = 0
    # Read the binary file byte by byte
    while (byte := f.read(1)):
        count += 1
        # Convert the byte to an integer and print it
        print(int.from_bytes(byte, byteorder='little'))
    print(count)
