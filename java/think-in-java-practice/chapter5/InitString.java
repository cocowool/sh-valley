import java.util.*;

class Stone {
    Stone(String i){
        System.out.println("string i is " + i);
    }

    String i;   //不初始化将被默认设置为null
}

public class InitString{
    public static void  main(String[] args){
        Stone s = new Stone("a");
        System.out.println(s.i);
    }
}