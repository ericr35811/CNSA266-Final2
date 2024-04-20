from obd import commands as obd_commands

# Lookup table of PIDs which are used for live data, with their min/max values and units
# from https://www.csselectronics.com/pages/obd2-pid-table-on-board-diagnostics-j1979

CMD = 0
MIN = 1
MAX = 2
UNIT = 3

pids = {
	4:  [None,	0,		100,	'%'		],
	5:  [None,	-40,	215,	'°C'	],
	6:  [None,	-100,	99,		'%'		],
	7:  [None,	-100,	99,		'%'		],
	8:  [None,	-100,	99,		'%'		],
	9:  [None,	-100,	99,		'%'		],
	10: [None,	0,		765,	'kPa'	],
	11: [None,	0,		255,	'kPa'	],
	12: [None,	0,		16384,	'rpm'	],
	13: [None,	0,		255,	'km/h'	],
	14: [None,	-64,	64,		'deg'	],
	15: [None,	-40,	215,	'°C'	],
	16: [None,	0,		655,	'grams/sec'	],
	17: [None,	0,		100,	'%'		],
	20: [None,	0,		1,		'volts'	],
	21: [None,	0,		1,		'volts'	],
	22: [None,	0,		1,		'volts'	],
	23: [None,	0,		1,		'volts'	],
	24: [None,	0,		1,		'volts'	],
	25: [None,	0,		1,		'volts'	],
	26: [None,	0,		1,		'volts'	],
	27: [None,	0,		1,		'volts'	],
	31: [None,	0,		65535,	'seconds'	],
	33: [None,	0,		65535,	'km'	],
	34: [None,	0,		5177,	'kPa'	],
	35: [None,	0,		655350,	'kPa'	],
	36: [None,	0,		2,		''	],
	37: [None,	0,		2,		''	],
	38: [None,	0,		2,		''	],
	39: [None,	0,		2,		''	],
	40: [None,	0,		2,		''	],
	41: [None,	0,		2,		''	],
	42: [None,	0,		2,		''	],
	43: [None,	0,		2,		''	],
	44: [None,	0,		100,	'%'		],
	45: [None,	-100,	99,		'%'		],
	46: [None,	0,		100,	'%'		],
	47: [None,	0,		100,	'%'		],
	49: [None,	0,		65535,	'km'	],
	50: [None,	-8192,	8192,	'Pa'	],
	51: [None,	0,		255,	'kPa'	],
	52: [None,	0,		2,		''	],
	53: [None,	0,		2,		''	],
	54: [None,	0,		2,		''	],
	55: [None,	0,		2,		''	],
	56: [None,	0,		2,		''	],
	57: [None,	0,		2,		''	],
	58: [None,	0,		2,		''	],
	59: [None,	0,		2,		''	],
	60: [None,	-40,	6514,	'°C'	],
	61: [None,	-40,	6514,	'°C'	],
	62: [None,	-40,	6514,	'°C'	],
	63: [None,	-40,	6514,	'°C'	],
	66: [None,	0,		66,		'V'		],
	67: [None,	0,		25700,	'%'		],
	68: [None,	0,		2,		''	],
	69: [None,	0,		100,	'%'		],
	70: [None,	-40,	215,	'°C'	],
	71: [None,	0,		100,	'%'		],
	72: [None,	0,		100,	'%'		],
	73: [None,	0,		100,	'%'		],
	74: [None,	0,		100,	'%'		],
	75: [None,	0,		100,	'%'		],
	76: [None,	0,		100,	'%'		],
	77: [None,	0,		65535,	'minutes'	],
	78: [None,	0,		65535,	'minutes'	],
	79: [None,	0,		255,	''	],
	80: [None,	0,		2550,	'g/s'	],
	82: [None,	0,		100,	'%'		],
	83: [None,	0,		328,	'kPa'	],
	84: [None,	-32767,	32768,	'Pa'	],
	85: [None,	-100,	99,		'%'		],
	86: [None,	-100,	99,		'%'		],
	87: [None,	-100,	99,		'%'		],
	88: [None,	-100,	99,		'%'		],
	89: [None,	0,		655350,	'kPa'	],
	90: [None,	0,		100,	'%'		],
	91: [None,	0,		100,	'%'		],
	92: [None,	-40,	215,	'°C'	],
	93: [None,	-210,	302,	'deg'	],
	94: [None,	0,		3277,	'L/h'	],
	97: [None,	-125,	130,	'%'		],
	98: [None,	-125,	130,	'%'		],
	99: [None,	0,		65535,	'Nm'	],
	100: [None,	-125,	130,	'%'		],
	102: [None,	0,		2048,	'grams/sec'	],
	103: [None,	-40,	215,	'°C'	],
	104: [None,	-40,	215,	'°C'	],
	124: [None,	-40,	6514,	'°C'	],
	141: [None,	0,		100,	'%'		],
	142: [None,	-125,	130,	'%'		],
	162: [None,	0,		2048,	'mg/stroke'	],
	164: [None,	0,		66,		''	],
	165: [None,	0,		128,	'%'		]
}

# associate each PID with an OBDCommand object from the library
# some are not supported by the PyOBD library, ignore them
temp = {}
for pid, values in pids.items():
	try:
		values[0] = obd_commands[1][pid]
	except IndexError:
		pass
	else:
		temp[pid] = values

pids = temp

for p, v in pids.items():
	print(p, v)