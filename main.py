#coding:utf-8
import tushare as ts
from utils import star, down, longup

def main():
	data = ts.get_today_all()
	print down(data, -0.05, -0.07)
	print longup(data,percent=1.05)


if __name__ == '__main__':
	main()