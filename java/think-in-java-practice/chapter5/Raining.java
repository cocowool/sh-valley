// package chapter5;

class Cloud {
    void rain(){
        sunshine();
        this.sunshine();
    }

    void sunshine(){
        System.out.println("Rain is over.");
    }
}

public class Raining {
    public static void main(String[] args){
        Cloud c = new Cloud();
        c.rain();
    }
}
