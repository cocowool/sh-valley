import java.util.*;

public class CompareRandom {
    public static void main(String[] args){
        int a = (int)(Math.random()*100);
        int i = 0;
        do {
            int b = (int)(Math.random()*100);
            if( a > b ){
                System.out.println("Number a : " + a + " is bigger than Number b : " + b);
            }else if ( a < b ){
                System.out.println("Number a : " + a + " is lower than Number b : " + b);
            }else{
                System.out.println("Number a : " + a + " equal than Number b : " + b);
            }
            a = b;
            i++;
        }while(i < 25);
    }
}
