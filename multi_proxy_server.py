#!/usr/bin/env python3
import socket, time, sys
from multiprocessing import Process

HOST = ""
PORT = 8001
BUFFER_SIZE = 1024

#get ip
def get_remote_ip(host):
	print(f'Getting IP for {host}')
	try:
		remote_ip = socket.gethostbyname( host )
	except socket.gaierror:
		print('Hostname could not be resolved. Exiting')
		sys.exit()

	print(f'Ip address of {host} is {remote_ip}')
	return remote_ip

def handle_request(addr, conn, proxy_end):
	print("Connected by", addr)

	send_full_data = conn.recv(BUFFER_SIZE)
	print(f"Sending recieved data {send_full_data} to google")
	proxy_end.sendall(send_full_data)
	proxy_end.shutdown(socket.SHUT_WR)
	data = proxy_end.recv(BUFFER_SIZE)
	print(f"Sending recieved data {data} to client")
	conn.send(data)
	# conn.shutdown(socket.SHUT_RDWR)
	# conn.close()

def main():
	extern_host = 'www.google.com'
	port = 80

	#establish "start" of proxy (connects to localhost)
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as proxy_start:
		print("Starting proxy server")
		#allow resued addresses, bind, and set to listening mode
		proxy_start.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		proxy_start.bind((HOST, PORT))
		proxy_start.listen(2)

		while True:
			#connect proxy_start
			conn, addr = proxy_start.accept()
			print("Connected by", addr)

			#while True:
			#establish "end" of proxy (connects to google)
			with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as proxy_end:
				print("Connected to Google")
				remote_ip = get_remote_ip(extern_host)

				#connect proxy_end
				proxy_end.connect((remote_ip, port))

				#accept connections and start a Process daemon for handling multiple connections
				# conn, addr = proxy_start.accept()
				p = Process(target=handle_request, args=(addr, conn, proxy_end))
				p.daemon = True
				p.start()
				print("Started process ", p)

				# #send data
				# send_full_data = conn.recv(BUFFER_SIZE)
				# print(f"Sending recieved data {send_full_data} to google")
				# proxy_end.sendall(send_full_data)

				# #remember to shut down!!
				# proxy_end.shutdown(socket.SHUT_WR) #shutdown() is different from close()

				# data = proxy_end.recv(BUFFER_SIZE)
				# print(f"Sending recieved data {data} to client")
				# #send data back
				# conn.send(data)

			conn.close()



if __name__ == '__main__':
	main()