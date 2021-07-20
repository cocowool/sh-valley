// package chapter5;
import java.util.*;

class MyCar {
    //构造器没有返回值
    MyCar(String color){
        System.out.println("Car color is " + color);
    }

    MyCar(String color, int weight){
        this(color);
        System.out.println("Car weight is " + weight);
    }
}

public class Traffic {
    public static void main(String[] args){
        MyCar c = new MyCar("benz", 1000);
    }
}
