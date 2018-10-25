
package proto;

import java.nio.CharBuffer;  
import java.lang.reflect.*;
import java.util.*;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.net.InetAddress;
import java.lang.reflect.Method;
import org.omg.CORBA.Object;
import org.omg.CORBA.PUBLIC_MEMBER;
import javax.xml.bind.DatatypeConverter;

class base_utils{

    /*备注：ByteOrder.BIG_ENDIAN 还是LITTLE_ENDIAN，要先进行系统判断 */
    public static final ByteOrder byte_order = ByteOrder.BIG_ENDIAN;
    


    public byte[] int_to_byte(int myInteger){
        return ByteBuffer.allocate(4).order(byte_order).putInt(myInteger).array();
    }
    public byte[] char_to_byte(char myChar){
        return ByteBuffer.allocate(2).order(byte_order).putChar(myChar).array();
    }
    public byte[] short_to_byte(short myShort){
        return ByteBuffer.allocate(2).order(byte_order).putShort(myShort).array();
    }
    public char  bytes_to_one_char(byte[] buf){
        try{
            String text1 = new String(buf, "UTF-8");
            return text1.toCharArray()[0];
        }catch(Exception e){
            System.out.print(e);
            return 0;
        }
    }

    public byte  bytes_to_one_byte(byte[] buf){
        return buf[0];
    }


    public short bytes_to_short(byte[] arr) {
        return (short)( arr[0]*256 + arr[1]);
    } 


}


class estun_stream extends estun_define{
    public byte[] buffer = new byte[MESSAGE_MAX_LENGTH]; 
    public int end_len;
}

class estun_define extends base_utils{


    public static final short MESSAGE_MAX_LENGTH = 2048;
    public static final int MESSAGE_HEADER_LENGTH = 20;


    // METHOD 方法定义
    public static final byte STUN_METHOD_ALLOCATE = 0x03;
    public static final byte STUN_METHOD_REFRESH =0x04;           //用户刷新，相当于心跳
    public static final byte STUN_METHOD_EOTU_ASK_USER =0x05 ;    //请求对方信息
    public static final byte STUN_METHOD_SEND =0x06 ;            //用户转发数据到服务器
    public static final byte STUN_METHOD_DATA =0x07 ;            //服务器转发数据给用户

    // ATTRIBUTE 数据类型 定义

    public static final short STUN_ATTRIBUTE_ERROR_CODE = 0x0009;
    public static final short STUN_ATTRIBUTE_XOR_PEER_ADDRESS = 0x0012;           //需要中转的peer addr
    public static final short STUN_ATTRIBUTE_DATA = 0x0013;                        //需要中转的数据
    public static final short STUN_ATTRIBUTE_XOR_RELAYED_ADDRESS = 0x0016;         //服务器返回NAT地址
    public static final short STUN_ATTRIBUTE_LIFETIME = 0x000d;
    public static final short STUN_ATTRIBUTE_REQUESTED_ADDRESS_FAMILY = 0x0017;    //ipv4 默认值 0x001
    public static final short STUN_ATTRIBUTE_REQUESTED_TRANSPORT = 0x0019;         //udp 通信默认17
    public static final short STUN_ATTRIBUTE_XOR_MAPPED_ADDRESS = 0x0020;          //服务器返回的客户端映射地址
    public static final short STUN_ATTRIBUTE_EOTU_LOCAL_ADDR = (0x0e03) ;          //用户上报ip port
    public static final short STUN_ATTRIBUTE_ASK_USERID_INFO = 0x0e11  ;           //咨询某用户信息
    public static final short STUN_ATTRIBUTE_RES_USERID_INFO = (0x0e12)  ;         //服务器返回用户信息
    public static final short STUN_ATTRIBUTE_RES_USER_INFO_MAPEED_ADDR = (0x0e13);  //服务器返回咨询用户的本地地址，服务器检测的反射地址
    public static final short STUN_ATTRIBUTE_RES_USER_INFO_RELAYED_ADDR = (0x0e14);   //服务器返回用户NAT地址
    public static final short STUN_ATTRIBUTE_RES_USER_INFO_REAL_ADDR = (0x0e15)  ; //服务器返回用户上报的本地地址
    public static final short STUN_ATTRIBUTE_SEND_DATA_TYPE = 0x0e16   ;           //发送的数据类型
    public static final short STUN_ATTRIBUTE_SEND_IS_RESPONSE = 0x0e17 ;           //发送的数据是否需要回复


    HashMap<Short,String> attr_map = new HashMap<Short,String>();
    HashMap<Byte,String> method_map = new HashMap<Byte,String>();

    public static int bytes_to_short(byte[] bytes, int offset) {
        int ret = 0;
        for (int i=0; i<2 && i+offset<bytes.length; i++) {
          ret <<= 8;
          ret |= (int)bytes[i] & 0xFF;
        }
        return ret;
      }
      public static int bytes_to_int(byte[] bytes, int offset) {
        int ret = 0;
        for (int i=0; i<4 && i+offset<bytes.length; i++) {
          ret <<= 8;
          ret |= (int)bytes[i] & 0xFF;
        }
        return ret;
      }
    public String get_attr_addr_string(byte[] buf){
        int pp = bytes_to_short(new byte[]{buf[2],buf[3]},0);

        String ipStr = String.format("%d.%d.%d.%d:%d",buf[4] & 0xff,buf[5] & 0xff,buf[6]& 0xff,buf[7] & 0xff,pp);
        return ipStr;
    }

    public String get_attr_byte_string(byte[] buf){

        return javax.xml.bind.DatatypeConverter.printHexBinary(buf);
    }

    public String get_attr_byte_user_info(byte[] buf){

        if(buf.length != 8){
            return "error user id/channel";
        }

        byte[] uid = new byte[4];
        byte[] channel = new byte[4];

        System.arraycopy(buf,0,uid,0,4);
        System.arraycopy(buf,4,channel,0,4);

        return DatatypeConverter.printHexBinary(uid) + ":" +DatatypeConverter.printHexBinary(channel);

    }


    public estun_define(){
        attr_map.put(STUN_ATTRIBUTE_ERROR_CODE,"STUN_ATTRIBUTE_ERROR_CODE");
        attr_map.put(STUN_ATTRIBUTE_XOR_PEER_ADDRESS,"STUN_ATTRIBUTE_XOR_PEER_ADDRESS");
        attr_map.put(STUN_ATTRIBUTE_DATA,"STUN_ATTRIBUTE_DATA");
        attr_map.put(STUN_ATTRIBUTE_XOR_RELAYED_ADDRESS,"STUN_ATTRIBUTE_XOR_RELAYED_ADDRESS");
        attr_map.put(STUN_ATTRIBUTE_LIFETIME,"STUN_ATTRIBUTE_LIFETIME");
        attr_map.put(STUN_ATTRIBUTE_REQUESTED_ADDRESS_FAMILY,"STUN_ATTRIBUTE_REQUESTED_ADDRESS_FAMILY");
        attr_map.put(STUN_ATTRIBUTE_REQUESTED_TRANSPORT,"STUN_ATTRIBUTE_REQUESTED_TRANSPORT");
        attr_map.put(STUN_ATTRIBUTE_XOR_MAPPED_ADDRESS,"STUN_ATTRIBUTE_XOR_MAPPED_ADDRESS");
        attr_map.put(STUN_ATTRIBUTE_EOTU_LOCAL_ADDR,"STUN_ATTRIBUTE_EOTU_LOCAL_ADDR");
        attr_map.put(STUN_ATTRIBUTE_ASK_USERID_INFO,"STUN_ATTRIBUTE_ASK_USERID_INFO");
        attr_map.put(STUN_ATTRIBUTE_RES_USERID_INFO,"STUN_ATTRIBUTE_RES_USERID_INFO");
        attr_map.put(STUN_ATTRIBUTE_RES_USER_INFO_MAPEED_ADDR,"STUN_ATTRIBUTE_RES_USER_INFO_MAPEED_ADDR");
        attr_map.put(STUN_ATTRIBUTE_RES_USER_INFO_RELAYED_ADDR,"STUN_ATTRIBUTE_RES_USER_INFO_RELAYED_ADDR");
        attr_map.put(STUN_ATTRIBUTE_RES_USER_INFO_REAL_ADDR,"STUN_ATTRIBUTE_RES_USER_INFO_REAL_ADDR");
        attr_map.put(STUN_ATTRIBUTE_SEND_DATA_TYPE,"STUN_ATTRIBUTE_SEND_DATA_TYPE");
        attr_map.put(STUN_ATTRIBUTE_SEND_IS_RESPONSE,"STUN_ATTRIBUTE_SEND_IS_RESPONSE");

        method_map.put(STUN_METHOD_ALLOCATE,"STUN_METHOD_ALLOCATE");
        method_map.put(STUN_METHOD_REFRESH,"STUN_METHOD_REFRESH");
        method_map.put(STUN_METHOD_EOTU_ASK_USER,"STUN_METHOD_EOTU_ASK_USER");
        method_map.put(STUN_METHOD_SEND,"STUN_METHOD_SEND");
        method_map.put(STUN_METHOD_DATA,"STUN_METHOD_DATA");
        

    }

    public String get_attr_string(short attr_short,byte[] buf){

        switch(attr_short){
            case STUN_ATTRIBUTE_XOR_PEER_ADDRESS:
            case STUN_ATTRIBUTE_XOR_RELAYED_ADDRESS:
            case STUN_ATTRIBUTE_XOR_MAPPED_ADDRESS:
            case STUN_ATTRIBUTE_EOTU_LOCAL_ADDR:
            case STUN_ATTRIBUTE_RES_USER_INFO_MAPEED_ADDR:
            case STUN_ATTRIBUTE_RES_USER_INFO_RELAYED_ADDR:
            case STUN_ATTRIBUTE_RES_USER_INFO_REAL_ADDR:
                return get_attr_addr_string(buf);
            case STUN_ATTRIBUTE_ERROR_CODE:
            case STUN_ATTRIBUTE_DATA:
                String response;
                response =  buf.toString() +":" + get_attr_byte_string(buf);
                return response;
            case STUN_ATTRIBUTE_LIFETIME:
            case STUN_ATTRIBUTE_REQUESTED_ADDRESS_FAMILY:
            case STUN_ATTRIBUTE_REQUESTED_TRANSPORT:

            case STUN_ATTRIBUTE_SEND_DATA_TYPE:
            case STUN_ATTRIBUTE_SEND_IS_RESPONSE:
                return get_attr_byte_string(buf);
            case STUN_ATTRIBUTE_ASK_USERID_INFO:
            case STUN_ATTRIBUTE_RES_USERID_INFO:
                return get_attr_byte_user_info(buf);
            default:
                return "unknow method";
        }
    }
}

public class estun extends estun_define {

    public estun_stream MSG; 
    public static int user_me  ;
    public static int channel  ; 

    /************************************************************
     * INTERFACE
    **************************************************************/


    /************************************************************
     *  初始化
     * 
     * @user_me 用户ID
     * @channel 双方约定的通信通道
    **************************************************************/

    public estun(int user_me ,int channel){
        estun.user_me = user_me;
        estun.channel = channel;
        MSG = new estun_stream();
    }

    /************************************************************
     *  报文头部 初始化 
     * 
     * 共20字节
     * ×××××××××××××××××××××××××××××××××××××××××××××××××××××××××××
     * 0x00 1字节+消息类型1字节，合并2字节         报文长度 2字节
     * ×××××××××××××××××××××××××××××××××××××××××××××××××××××××××××
     * 待定义 4字节
     * ×××××××××××××××××××××××××××××××××××××××××××××××××××××××××××
     * 随机数 4字节
     * ×××××××××××××××××××××××××××××××××××××××××××××××××××××××××××
     * 用户ID 4字节
     * ×××××××××××××××××××××××××××××××××××××××××××××××××××××××××××
     * 通信通道 4字节
     * ×××××××××××××××××××××××××××××××××××××××××××××××××××××××××××
    **************************************************************/
    private void msg_header_init(int user_me, int channel,byte stun_method , int random){
        MSG.buffer[0] = 0;
        MSG.buffer[1] = stun_method; 
        System.arraycopy(int_to_byte(random),0,MSG.buffer,8,4);
        System.arraycopy(int_to_byte(user_me),0,MSG.buffer,12,4);
        System.arraycopy(int_to_byte(channel),0,MSG.buffer,16,4);
        MSG.end_len = 20;
    }
    /*报文组装完毕后，设定报文长度*/
    private void set_msg_stream_size(){
        short len = (short)(MSG.end_len - MESSAGE_HEADER_LENGTH);
        System.arraycopy(short_to_byte(len),0,MSG.buffer,2,2);
    }

    /************************************************************
     *  ATTRIBUTE  数据格式
     * 
     * ×××××××××××××××××××××××××××××××××××××××××××××××××××××××××××
     *  数据属性key 2字节    长度 2字节
     * ×××××××××××××××××××××××××××××××××××××××××××××××××××××××××××
     *  数据value   字节X
     * ×××××××××××××××××××××××××××××××××××××××××××××××××××××××××××
    **************************************************************/
    private void set_attr_value(short attr_key,byte[] attr_value,short attr_len){
     
        System.arraycopy(short_to_byte(attr_key),0,MSG.buffer,MSG.end_len,2);
        System.arraycopy(short_to_byte(attr_len),0,MSG.buffer,MSG.end_len+2,2);
        System.arraycopy(attr_value,0,MSG.buffer,MSG.end_len+4,attr_len);
        MSG.end_len = MSG.end_len + 4 + attr_len;
    }

    /************************************************************
     *  ATTRIBUTE   ADDRESS 地址数据格式
     * 
     * *****************************************
     * FAMILY 字节2   PORT 字节2
     * *****************************************
     *      ADDR 字节4
     * *****************************************
    **************************************************************/

    public byte[] get_attr_addr_buf(String ip,short port,short family){
        byte[] data_buf = new byte[8];
        
        try{
            byte[] ip_buf = InetAddress.getByName(ip).getAddress();
            if(family == 2 || family == 0){
   
                System.arraycopy(short_to_byte(family),0,data_buf,0,2);
                System.arraycopy(short_to_byte(port),0,data_buf,2,2);
                System.arraycopy(ip_buf,0,data_buf,4,4);
            }else{
                System.out.print("ipv6 not support now");
                return null;
            }
        }catch(Exception e){
            System.out.print(e);
            return null;
        }

        return data_buf;
    }

    /************************************************************
     *  ATTRIBUTE   ASK_USER_INFO 地址数据格式
     * 
     * *****************************************
     * USER ID  字节4
     * *****************************************
     * CHANNEL   字节4
     * *****************************************
    **************************************************************/
    public byte[] get_ask_user_info_buf(int user_id,int channel){
        byte[] data_buf = new byte[8];
        System.arraycopy(int_to_byte(user_id),0,data_buf,0,4);
        System.arraycopy(int_to_byte(channel),0,data_buf,4,4);
        return data_buf;
    }


    /**============================================================================= **/
    /**========================组装报文      ======================================== **/
    /**============================================================================= **/


    public byte[] msg_resize(){
   
        byte[] result = new byte[MSG.end_len];
        System.arraycopy(MSG.buffer,0,result,0,MSG.end_len);
        return result;
    }

    /**ALLOCATION 上线，请求服务器分配资源**/
    public byte[] allocate_base(String ip,short port,short family){
   
        msg_header_init(estun.user_me,estun.channel,STUN_METHOD_ALLOCATE,0xffffffff) ;
        set_attr_value( STUN_ATTRIBUTE_EOTU_LOCAL_ADDR,get_attr_addr_buf(ip,port,family),(short)8);
        set_attr_value( STUN_ATTRIBUTE_REQUESTED_TRANSPORT,int_to_byte(0x11000000),(short) 4);
        set_attr_value( STUN_ATTRIBUTE_REQUESTED_ADDRESS_FAMILY,int_to_byte(0x01000000),(short) 4);
        set_msg_stream_size();
        return msg_resize();

    }
    /**ALLOCATION 上线，请求服务器分配资源**/
    public byte[] beat_heart_base(){
     
        msg_header_init(estun.user_me,estun.channel,STUN_METHOD_REFRESH,0);
        set_msg_stream_size();
        return msg_resize();
    }
    /**ASK_USER_INFO 请求对方信息 **/
    public byte[] ask_user_info_base(int user_id,int channel){
        //报头的 estun.channel 应该与 请求的 channel 一致，否则 服务器拒绝
        msg_header_init(estun.user_me,estun.channel,STUN_METHOD_EOTU_ASK_USER,123) ;
        set_attr_value( STUN_ATTRIBUTE_ASK_USERID_INFO,get_ask_user_info_buf(user_id,channel),(short)8);
        set_msg_stream_size();
        return msg_resize();
    }
    /**TURN 中转 **/
    public byte[] turn_base(int user_id,int channelid,byte[] data_buf,short data_len){
        //报头的 estun.channel 应该与 请求的 channel 一致，否则 服务器拒绝
        msg_header_init(estun.user_me,estun.channel,STUN_METHOD_SEND,123) ;
        set_attr_value( STUN_ATTRIBUTE_ASK_USERID_INFO,get_ask_user_info_buf(user_id,channelid),(short)8); 
        set_attr_value( STUN_ATTRIBUTE_DATA,data_buf,data_len);
        set_msg_stream_size();
        return msg_resize();
    }


    /**============================================================================= **/
    /**========================解析报文      ======================================== **/
    /**============================================================================= **/

  
    
    public HashMap<String,String> depose_msg(byte[] buf){

        HashMap<String,String> msg_map = new HashMap<String,String>();


        if(buf.length < MESSAGE_HEADER_LENGTH){
            System.out.print("message length error ! return null");
            return null;
        }
  
        byte[] uid = new byte[4];
        byte[] channelid = new byte[4];
        byte[] msg_len = new byte[2];
        byte[] attr = new byte[2];
        byte[] attr_len = new byte[2];

        System.arraycopy(buf,2,msg_len,0,2);
        System.arraycopy(buf,12,uid,0,4);
        System.arraycopy(buf,16,channelid,0,4);
        short msg_l = bytes_to_short(msg_len);

        msg_map.put("method",method_map.get(buf[1]));
        msg_map.put("uid",DatatypeConverter.printHexBinary(uid));
        msg_map.put("channelid",DatatypeConverter.printHexBinary(channelid));
        // msg_map.put("msg_len",String.valueOf(msg_l));


        int remain = MESSAGE_HEADER_LENGTH  ;
        short attr_l ;

        while(remain + 4  < msg_l + MESSAGE_HEADER_LENGTH){
            System.arraycopy(buf,remain,attr,0,2);
            System.arraycopy(buf,remain + 2 ,attr_len,0,2);
            attr_l = bytes_to_short(attr_len);
            //System.out.println("remain:" +  remain + " attr_l:" + attr_l  + " msg_l :" + msg_l);
            if(attr_l >0 && remain + 4 + attr_l <= msg_l + MESSAGE_HEADER_LENGTH ){
                Short attr_short = bytes_to_short(attr);
                String attr_des = attr_map.get(attr_short);
                byte[] attr_value = new byte[attr_l];
                //System.out.println(javax.xml.bind.DatatypeConverter.printHexBinary(attr_value));
                System.arraycopy(buf,remain + 4 ,attr_value,0,attr_l);
                String attr_v = get_attr_string(attr_short,attr_value);
                //System.out.println(attr_des + ":" + attr_v);
                msg_map.put(attr_des,attr_v);

            }
            remain = remain + attr_l + 4;
        }
        return msg_map;   
    }
}



// class test{

//     public static void test_print(estun_stream estream){
//         byte[] result = new byte[estream.end_len];
//         System.arraycopy(estream.buffer,0,result,0,estream.end_len);

//         System.out.println(javax.xml.bind.DatatypeConverter.printHexBinary(result));
//     }

//     public static void main(String[] args){

//         estun e = new estun(11,15);

//         //上线测试
//         estun_stream allcation = e.allocate_base("192.168.1.1",54321,2);
//         if(allcation != null){
//             test_print(allcation);
//         }
        

//         //心跳数据测试
//         estun_stream beat = e.beat_heart_base();
//         if(beat != null){
//             test_print(beat);
//         }

//         //请求对方信息测试
//         estun_stream ask_user_info = e.ask_user_info_base(10,15);
//         if(ask_user_info != null){
//             test_print(ask_user_info);
//         }

//         //中转测试 1
//         String test_string = "nihao";
//         byte[] turn_data = test_string.getBytes();
//         estun_stream turn= e.turn_base(10,15,turn_data,(short)test_string.length());
//         if(turn != null){
//             test_print(turn);
//         }

//         //中转测试 2
//         turn= e.turn_base(10,15,ask_user_info.buffer,(short)ask_user_info.end_len);
//         if(turn != null){
//             test_print(turn);
//         }
//     }

// }