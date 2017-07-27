# coding:utf-8
"""
code
name
changepercent
trade
open
high
low
settlement
volume
turnoverratio
amount
per
pb
mktcap
nmc
"""


def longup(data, percent):
	code_list = []
	for idx in xrange(len(data)-1):
		_open = data['open'][idx]
		_close = data['trade'][idx]
		_high = data['high'][idx]
		_low = data['low'][idx]
		_last = data['settlement'][idx]
		_code = data['code'][idx]
		if '300' in _code:
			continue
		if _close < 5.0:
			continue
		if (float(_high) / max(float(_open), float(_close))) < percent:
			continue
		print _open, _close, _high, _low, _last
		code_list.append(_code)
	return code_list

def star(data):
	code_list=[]
	for idx in xrange(len(data)-1):
		_open=data['open'][idx]
		_close=data['trade'][idx]
		_high=data['high'][idx]
		_low=data['low'][idx]
		_last=data['settlement'][idx]
		_code=data['code'][idx]
		if '300' in _code:
			continue
		if _close < 5.0:
			continue
		if abs(_open / _close) > 0.005:
			continue
		if (_low / min(_open, _close)) < 0.005:
			continue
		if (_high / max(_open, _close)) < 0.005:
			continue
		print _open, _close, _high, _low, _last
		code_list.append(_code)
	return code_list

def down(data, max_percent=0.05, min_percent=-0.05):
	code_list=[]
	for idx in xrange(len(data)-1):
		_percent=data['changepercent'][idx]
		_code=data['code'][idx]
		if '300' in _code:
			continue
		if _percent < min_percent:
			continue
		if _percent > max_percent:
			continue
		code_list.append(_code)
	return code_list
