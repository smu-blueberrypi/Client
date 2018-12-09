import librtmp

conn = librtmp.RTMP("rtmp://118.217.34.116:live/s", live = True)
conn.connect()
stream = conn.create_stream()
data = stream.read(1024)
