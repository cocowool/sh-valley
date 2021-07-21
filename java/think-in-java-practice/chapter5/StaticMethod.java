// package chapter5;

class StaticItem {
    static int i = 5;
    static int x;
    static {
        x = 10;
    }
    StaticItem(){
        System.out.println("Static i = " + i + " , x = " + x);
    }
}

public class StaticMethod {
    public static void main(String[] args){
        StaticItem s = new StaticItem();
    }
}
