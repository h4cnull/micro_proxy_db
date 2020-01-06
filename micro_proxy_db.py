#coding=utf-8

import re
import os
import sys
import sqlite3
import argparse
import sqlfunc
import requests
from concurrent.futures import ThreadPoolExecutor

def get_parser():
	parser = argparse.ArgumentParser(description="[+] micro_proxy_db manage a micro socks proxy pool")
	group = parser.add_mutually_exclusive_group()
	group.add_argument("--find", action='store_true', help="find valid proxy by proxybroker cmd")
	group.add_argument("--get", metavar='n/*', type=str, help="get n records or all from database")
	group.add_argument("--update", action='store_true', help="check the proxy from database and update it state")
	group.add_argument("--hisfind", action='store_true', help="find valid proxy from history in tmp/history.txt")
	return parser

def his_find_proxies():
	with open('tmp/history.txt','r') as f:
		proxies = format_proxies(f.read())
		return proxies

def find_proxies():
	print("[+] Finding proxies")
	r = os.popen("proxybroker find --types SOCKS4 SOCKS5 --lvl High --countries CN --format default --limit 50")
	text = r.read()
	with open('tmp/history.txt','a+') as f:
		f.write(text)
	proxies = format_proxies(text)
	r.close()
	return proxies

def format_proxies(text):
	proxies = []
	unformat_proxies = [line.strip() for line in text.split('>')]
	for line in unformat_proxies:
		if 'SOCKS5' in line:
			ip_port = line.split()[-1].split(':')
			proxies.append({'protocol':'socks5','ip':ip_port[0],'port':ip_port[1]})
			continue
		if 'SOCKS4' in line:
			ip_port = line.split()[-1].split(':')
			proxies.append({'protocol':'socks4','ip':ip_port[0],'port':ip_port[1]})
	return remove_duplicate(proxies)

def remove_duplicate(tmplist):
	rst = []
	for item in tmplist:
		if item not in rst:
			rst.append(item)
	return rst

def check_proxy(proxy):
	proxystr = proxy['protocol'] + '://' + proxy['ip'] + ":" + proxy['port']
	try:
		r = requests.get('https://www.example.com',timeout=3,proxies={'https':proxystr})
		sys.stdout.write("[+] Found a valid proxy: %s\n" % proxystr)
		proxy['quality'] = "%.2fs" % r.elapsed.total_seconds()
		return proxy	#valid proxy
	except:
		return proxy	#invalid proxy

def check_thread(proxies):
	check_pool = []
	thread = 10 if len(proxies) >= 10 else len(proxies)
	check_executor = ThreadPoolExecutor(max_workers=thread)
	for proxy in proxies:
		c_p = check_executor.submit(check_proxy, proxy)
		check_pool.append(c_p)
	result = []
	for c_p in check_pool:
		rst = c_p.result()
		result.append(rst)
	return result

if __name__ == '__main__':

	args = get_parser().parse_args()
	if not (args.get or args.find or args.update or args.hisfind):
		get_parser().print_help()
		sys.exit(0)

	if not os.path.exists('proxies.db'):
		sqlfunc.create_db()
	conn = sqlite3.connect('proxies.db')

	if args.get:
		proxies = []
		num = None
		if re.match("^\d+$",args.get):
			num = int(args.get)
			proxies = sqlfunc.get_proxy(conn, num=num)
		elif re.match("^\*$",args.get):
			proxies = sqlfunc.get_proxy(conn)
		else:
			print("[!] Please specify a valid number or *")
			get_parser().print_help()
			sys.exit(0)
		for proxy in proxies:
			print("%s %s %s	#%s %s %s"%(proxy[0],proxy[1],proxy[2],proxy[3],proxy[4],proxy[5]))

	if args.update:
		proxies = []
		tmpproxies = sqlfunc.get_proxy(conn,col='protocol,ip,port')
		for proxy in tmpproxies:
			proxies.append({'protocol':proxy[0],'ip':proxy[1],'port':proxy[2]})
		proxies = check_thread(proxies)
		for proxy in proxies:
			if 'quality' in proxy:
				#print("[!] Update db. update valid proxy %s://%s:%s" % (proxy['protocol'], proxy['ip'], proxy['port']))
				sqlfunc.update_proxy(conn, proxy)
			else:
				print("[!] Delete invalid proxy %s://%s:%s" % (proxy['protocol'], proxy['ip'], proxy['port']))
				sqlfunc.del_proxy(conn, proxy)
	
	proxies = []
	if args.find:
		proxies = find_proxies()
	if args.hisfind:
		proxies = his_find_proxies()
	if proxies:
		proxies = check_thread(proxies)
		exists_ip = [proxy[0] for proxy in sqlfunc.get_proxy(conn,col='ip')]
		for proxy in proxies:
			if 'quality' not in proxy:	#invalid proxy
				continue
			if proxy['ip'] not in exists_ip:
				sqlfunc.insert_proxy(conn,proxy)
			else:
				print("[+] Proxy already exists %s://%s:%s" % (proxy['protocol'], proxy['ip'], proxy['port']))
				sqlfunc.update_proxy(conn,proxy)
	conn.close()