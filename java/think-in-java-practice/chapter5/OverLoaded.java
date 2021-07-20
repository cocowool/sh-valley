// package chapter5;

class Pet {
    Pet(String i){
        System.out.println("string is " + i);
    }

    Pet(String i, int m){
        System.out.println("string is " + i + " and age is " + m);
    }
}

public class OverLoaded {
    public static void main(String[] args){
        Pet a = new Pet("dog");
        Pet b = new Pet("bird", 5);
    }
}
