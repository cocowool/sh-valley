// package chapter5;
import java.util.*;

class Pills {
    String[] a = new String[]{
        "Long", 
        "Short", 
        "Red", 
        "Yellow"
    };

    String[] b = {
        "Wide", 
        "Short", 
        "Red", 
        "Yellow"
    };

    // String[] c;
    
    // c = {
    //     "Black",
    //     "Short",
    //     "Red", 
    //     "Yellow"
    // };

    
    Pills(String i){
        System.out.println("string parameter x = " + i);

        for(String x : a){
            System.out.println(x);
        }

        System.out.println("-------");

        for(String x : b){
            System.out.println(x);
        }

        // System.out.println("-------");

        // for(String x : c){
        //     System.out.println(x);
        // }
    }
}

public class WordsArray {
    public static void main(String[] args){
        System.out.println("Words Array");
        Pills p = new Pills("a");

        Pills[] x;
        Pills[] y;

        x = new Pills[]{
            new Pills("A"),
            new Pills("B"),
            new Pills("C")
        };

        y = x;
    }
}
