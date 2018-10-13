import struct



'''
    int类型转化为unsigned char array
@num    int位数
@value  int值
'''

def int_to_unsiged_array(value,num=1):
    pack_type = {
        1:">B",
        2:">H",
        4:">L",
        8:">Q"
    }
    if not num in pack_type:
        return None

    if not isinstance(value,int):
        print("error !!!!!!!!!!!!!!!!!")
        print(value)

    return struct.pack(pack_type[num], value)    


'''
任意长度bytes转发为 int -->不要太大～～
'''

def bytes_to_int(data_bytes):
    r = 0
    for i in data_bytes:
        r = r * 256 + i

    return r

'''
    拼接一个int到msg_buf，int位数由bit_num决定
@msg_buf
@sttp       msg_buf起始位置
@endp       msg_buf结束位置
@src        要拼接的int
@bit_num    int的位数
'''
def set_int_to_msg_buf(msg_buf,sttp,src,bit_num):
    src_array = int_to_unsiged_array(src,bit_num)
    for i in range(0,bit_num,1):
        msg_buf[sttp+i]=src_array[i]
    return msg_buf

'''
拼接buf到msg_buf中，
@msg_buf    
@sttp       msg_buf起始位置
@src        要拼接的内容
@bit_num    要拼接内容的长度 
'''
def set_buf_to_msg_buf(msg_buf,sttp,src,bit_num):
    for i in range(bit_num):
        msg_buf[sttp+i]=src[i]
    return msg_buf

