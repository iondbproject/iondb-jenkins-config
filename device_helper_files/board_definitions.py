from collections import namedtuple

id_pair = namedtuple("id_pair", ["vid", "pid"])

ftdi = 0x0403

boards = \
{
    'yun':          [id_pair(0x2341, 0x0041), id_pair(0x2341, 0x8041), id_pair(0x2A03, 0x0041),
                     id_pair(0x2A03, 0x8041)],
    'uno':          [id_pair(0x2341, 0x0043), id_pair(0x2341, 0x0001), id_pair(0x2A03, 0x0043),
                     id_pair(0x2341, 0x0243)],
    'diecimila':    [],
    'nano':         [],
    'mega':         [id_pair(0x2341, 0x0010), id_pair(0x2341, 0x0042), id_pair(0x2A03, 0x0010),
                     id_pair(0x2A03, 0x0042), id_pair(0x2341, 0x0210), id_pair(0x2341, 0x0242)],
    'megaADK':      [id_pair(0x2341, 0x003f), id_pair(0x2341, 0x0044), id_pair(0x2A03, 0x003f),
                     id_pair(0x2A03, 0x0044)],
    'leonardo':     [id_pair(0x2341, 0x0036), id_pair(0x2341, 0x8036), id_pair(0x2A03, 0x0036),
                     id_pair(0x2A03, 0x8036)],
    'micro':        [id_pair(0x2341, 0x0037), id_pair(0x2341, 0x8037), id_pair(0x2A03, 0x0037),
                     id_pair(0x2A03, 0x8037), id_pair(0x2341, 0x0237), id_pair(0x2341, 0x8237)],
    'esplora':      [id_pair(0x2341, 0x003C), id_pair(0x2341, 0x803C), id_pair(0x2A03, 0x003C),
                     id_pair(0x2A03, 0x803C)],
    'mini':         [],
    'ethernet':     [],
    'fio':          [],
    'bt':           [],
    'LilyPadUSB':   [id_pair(0x1B4F, 0x9207), id_pair(0x1B4F, 0x9208)],
    'lilypad':      [],
    'pro':          [],
    'atmegang':     [],
    'robotControl': [id_pair(0x2341, 0x0038), id_pair(0x2341, 0x8038), id_pair(0x2A03, 0x0038),
                     id_pair(0x2A03, 0x8038)],
    'robotMotor':   [id_pair(0x2341, 0x0039), id_pair(0x2341, 0x8039), id_pair(0x2A03, 0x0039),
                     id_pair(0x2A03, 0x8039)],
    'gemma':        [id_pair(0x2341, 0x0c9f)]
}

processors = \
{
    'diecimila':    ['atmega328p', 'atmega168'],
    'nano':         ['atmega328p', 'atmega168'],
    'mega':         ['atmega2560', 'atmega1280'],
    'mini':         ['atmega328p', 'atmega168'],
    'bt':           ['atmega328p', 'atmega168'],
    'lilypad':      ['atmega328p', 'atmega168'],
    'pro':          ['atmega328p', 'atmega168'],
    'atmegang':     ['atmega168', 'atmega8']
}