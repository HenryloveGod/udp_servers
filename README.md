# udp_servers


P2P通信，游戏服务器通信，UDP比TCP更胜一筹


# PYTHON TWISTED SERVER

<b color="red">协议格式</b>   
```
协议        4字节
数据长度    4字节
校验        4字节
数据        x 字节
```

<b color="red">协议protocol = 1 格式</b>   
```
协议        4字节  值为1 protocol = 1
数据长度    4字节
校验        4字节
数据        x 字节   此数据为字符串数据，可转化为json
```

<b color="red">协议protocol = 2 格式</b>   
```
协议        4字节  值为2 protocol = 2
数据长度     4字节
校验        4字节
json数据长度 4字节
json数据    x 字节  此数据为字符串数据，可转化为json
stream数据长度 4字节
stream数据  y 字节  此数据为二进制流，代表任意类型数据

```


## Client 注册：

```
发送数据：b'\x00\x00\x00\x01\x00\x00\x00A\x00\x00\x00\x00{"uid": 1, "method": "register", "auth_value": 0, "channel": 123}'


解析：
0-3字节：协议 = 0x00000001
4-7字节：数据长度 0x000000A0
8-11字节：校验位 = 0x00000000

数据：{"uid": 1, "method": "register", "auth_value": 0, "channel": 123}
```

SERVER回复：
```
b'ok'
```
## Client 咨询用户信息：
```
b'\x00\x00\x00\x01\x00\x00\x00\x1a\x00\x00\x00\x00{"method": "ask_user_all"}'

```
SERVER回复：
```
b'{"1": {"addr": ["127.0.0.1", 35661], "channel": 123}}'
```

## Client 中转数据：

```
b'\x00\x00\x00\x02\x00\x00\x00W\x00\x00\x00\x00\x00\x00\x00A{"from_uid": [2, 123], "method": "turn_data", "to_uid": [1, 123]}\x00\x00\x00\x16HELLO ! TEST TURN DATA'

```

服务端，找到对应to_uid，原始数据转发给对应to_uid



