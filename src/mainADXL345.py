import spidev
import time

# ADXL345 Register Addresses
REG_BW_RATE = 0x2C
REG_POWER_CTL = 0x2D
REG_DATA_FORMAT = 0x31
REG_DATAX0 = 0x32
REG_OFSZ = 0x20

# Initialize SPI
spi = spidev.SpiDev()
spi.open(0, 0)  # Open SPI bus 0, device 0
spi.max_speed_hz = 281000*2  # Set SPI speed

def write_register(register, value):
    """Write a value to a specific register."""
    spi.xfer2([register, value])

def read_register(register):
    """Read a value from a specific register."""
    response = spi.xfer2([register | 0x80, 0])  # Set MSB to 1 for read
    return response[1]

def read_accelerometer():
    """Read acceleration data from the ADXL345."""
    x0 = read_register(REG_DATAX0)
    x1 = read_register(REG_DATAX0 + 1)
    y0 = read_register(REG_DATAX0 + 2)
    y1 = read_register(REG_DATAX0 + 3)
    z0 = read_register(REG_DATAX0 + 4)
    z1 = read_register(REG_DATAX0 + 5)
    
    # Combine high and low bytes
    x = (x1 << 8) | x0
    y = (y1 << 8) | y0
    z = (z1 << 8) | z0

    # Convert to signed 16-bit values
    if x > 32767:
        x -= 65536
    if y > 32767:
        y -= 65536
    if z > 32767:
        z -= 65536

    return x, y, z

def read_accelerometer_z():
    """Read acceleration data from the ADXL345."""
    # Read raw bytes from the Z-axis registers
    z0 = read_register(REG_DATAX0 + 4)  # Low byte
    z1 = read_register(REG_DATAX0 + 5)  # High byte

    # # Print raw register values for Z-axis, including binary representation
    # print(f"Raw Z-axis bytes: z0={z0} (binary: {bin(z0)}), z1={z1} (binary: {bin(z1)})")

    # Combine high and low bytes
    z = (z1 << 8) | z0
    # print(f"Combined 16-bit Z value (before sign conversion): {z} (binary: {bin(z)})")

    # Convert to signed 16-bit values
    if z > 32767:
        z -= 65536
    # print(f"Signed 16-bit Z value: {z} (binary: {bin(z & 0xFFFF)})")  # Mask to keep 16-bit representation

    # Scale the output to m/s^2
    scaled_z = z * 9.8 * .0039 # 9.8 m/s2 per g, .0039 g per LSB
    # print(f"Scaled Z value (m/s^2): {scaled_z}")


    return scaled_z



# sample_t = 1/500

# # Initialize ADXL345
# write_register(REG_POWER_CTL, 0x08)  # Measure mode
# write_register(REG_DATA_FORMAT, 0x00)  # +/- 2g, full resolution

# try:
#     while True:
#         x, y, z = read_accelerometer()
#         print(f"X: {x}, Y: {y}, Z: {z}")
#         time.sleep(sample_t)  # Delay for 500ms
# except KeyboardInterrupt:
#     print("Exiting...")
# finally:
#     spi.close()
