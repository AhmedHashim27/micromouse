import uasyncio
from machine import Pin, I2C
import math
from ustruct import pack
from array import array


class HMC5883L:
    __gain__ = {
        '0.88': (0 << 5, 0.73),
        '1.3':  (1 << 5, 0.92),
        '1.9':  (2 << 5, 1.22),
        '2.5':  (3 << 5, 1.52),
        '4.0':  (4 << 5, 2.27),
        '4.7':  (5 << 5, 2.56),
        '5.6':  (6 << 5, 3.03),
        '8.1':  (7 << 5, 4.35)
    }

    def __init__(self, scl=5, sda=4, address=30, gauss='1.9', declination=(4, 45)):
        self.i2c = i2c = I2C(scl=Pin(scl), sda=Pin(sda), freq=100000)
        self.address = address
        # Initialize sensor.
        i2c.start()

        # Configuration register A:
        #   0bx11xxxxx  -> 8 samples averaged per measurement
        #   0bxxx100xx  -> 15 Hz, rate at which data is written to output registers
        #   0bxxxxxx00  -> Normal measurement mode
        i2c.writeto_mem(self.address, 0x00, pack('B', 0b111000))

        # Configuration register B:
        reg_value, self.gain = self.__gain__[gauss]
        i2c.writeto_mem(self.address, 0x01, pack('B', reg_value))

        # Set mode register to continuous mode.
        i2c.writeto_mem(self.address, 0x02, pack('B', 0x00))
        i2c.stop()

        # Convert declination (tuple of degrees and minutes) to radians.
        self.declination = (declination[0] + declination[1] / 60) * math.pi / 180

        # Reserve some memory for the raw xyz measurements.
        self.data = array('B', [0] * 6)

    def read(self):
        data = self.data
        gain = self.gain

        self.i2c.readfrom_mem_into(self.address, 0x03, data)

        x = (data[0] << 8) | data[1]
        z = (data[2] << 8) | data[3]
        y = (data[4] << 8) | data[5]

        x = x - (1 << 16) if x & (1 << 15) else x
        y = y - (1 << 16) if y & (1 << 15) else y
        z = z - (1 << 16) if z & (1 << 15) else z

        x = x * gain
        y = y * gain
        z = z * gain

        #x = x * 1 - 46.36
        #y = y * 1.01 + 105.53

        return x, y, z

    def heading(self, x, y):
        heading_rad = math.atan2(y, x)
        heading_rad += self.declination

        # Correct reverse heading.
        if heading_rad < 0:
            heading_rad += 2 * math.pi

        # Compensate for wrapping.
        elif heading_rad > 2 * math.pi:
            heading_rad -= 2 * math.pi

        # Convert from radians to degrees.
        heading = heading_rad * 180 / math.pi
        return heading 

    def format_result(self, x, y, z):
        x_degrees = self.heading(x, y)
        y_degrees = self.heading(x, z)
        z_degrees = self.heading(y, z)
        return x_degrees, y_degrees, z_degrees
        return 'X: {:.4f}, Y: {:.4f}, Z: {:.4f}, Heading: {}° {}′ '.format(x, y, z, degrees, minutes)

if(__name__ == "__main__"):
    print('[Press CTRL + C to end the script!]')
    comp = HMC5883L()
    try:
        while True:
            x,y,z = comp.read()
            print(comp.format_result(x,y,z))
    except KeyboardInterrupt:
        print("End Script")
