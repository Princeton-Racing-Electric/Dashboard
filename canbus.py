import can
import logging


def _get_message(msg):

    return msg


class PCANBus(object):

    RX_SDO = 0x600
    TX_SDO = 0x580
    RX_PDO = 0x200
    TX_PDO = 0x0160

    id_unit_a = [120, 121, 122, 123]
    id_unit_b = [124, 125, 126, 127]

    def __init__(self):

        logging.info("Initializing CANbus")

        self.bus = can.Bus(channel="PCAN_USBBUS1", bustype="pcan")
        self.buffer = can.BufferedReader()
        self.notifier = can.Notifier(self.bus, [_get_message, self.buffer])

    def send_message(self, message):

        try:
            self.bus.send(message)
            return True
        except can.CanError:
            logging.error("message not sent!")
            return False

    def read_input(self, id):

        msg = can.Message(arbitration_id=self.RX_PDO + id,
                          data=[0x00],
                          is_extended_id=False)

        self.send_message(msg)
        return self.buffer.get_message()

    def flush_buffer(self):

        msg = self.buffer.get_message()
        while (msg is not None):
            msg = self.buffer.get_message()

    def cleanup(self):

        self.notifier.stop()
        self.bus.shutdown()

    def disable_update(self):

        for i in [50, 51, 52, 53]:

            msg = can.Message(arbitration_id=0x600 + i,
                              data=[0x23, 0xEA, 0x5F, 0x00, 0x00, 0x00, 0x00, 0x00],
                              is_extended_id=False)

            self.send_message(msg)

# To use in main code:
# pcan = PCANBus()
# msg = Message(arbitration_id=pcan.RX_PDO + 50, is_extended_id=False, data=[0x4F, 0x00])
# pcan.send_message(msg)
# ret = pcan.read_input(0x78)
# pcan.cleanup()