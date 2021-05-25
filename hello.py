def app(environ, start_response):
	data = '\n'.join(environ['QUERY_STRING'].split('&'))
	data = bytes(data, 'utf-8')
	status = '200 OK'
	response_headers = [
		('Content-Type', 'text/plain'),
		('Content-Length', str(len(data)))
	]
	start_response(status, response_headers)
	return iter([data])
