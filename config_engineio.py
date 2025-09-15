# 配置 engineio 以增加最大数据包限制
import engineio

# 增加最大数据包限制（默认为16）
engineio.payload.max_decode_packets = 1000  # 设置为一个较大的值

# 可选：增加最大 payload 大小
engineio.async_server.AsyncServer.max_http_buffer_size = 100000000  # 100MB