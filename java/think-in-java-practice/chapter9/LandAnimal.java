//Page 174, Practice 7
import java.util.*;

interface Rodent {
    public String name = "Rodent";

    // Rodent(){
    //     this.name = "Rodent";
    // }

    public void craw(Rodent r);

    public void color(Rodent c);

    public abstract void sound();

    public String toString();
}

class Mouse implements Rodent {
    // Mouse(){
    //     this.name = "Mouse";
    // }
    public void craw(Rodent c){
        System.out.println(c + "' craw.");
    }

    public void color(Rodent c){
        System.out.println(c + "'s color is gray.");
    }

    public void sound(){
        System.out.println(this.name + " sounds jijiji.");
    }
}

class Gerbil implements Rodent {
    // Gerbil(){
    //     this.name = "Gerbil";
    // }
    public void craw(Rodent c){
        System.out.println(c + "' craw.");
    }

    public void color(Rodent c){
        System.out.println(c + "'s color is black.");
    }

    public void sound(){
        System.out.println(this.name + " sounds gagaga.");
    }
}

class Hamster implements Rodent {
    // Hamster(){
    //     this.name = "Hamster";
    // }
    public void craw(Rodent c){
        System.out.println(c + "' craw.");
    }

    public void color(Rodent c){
        System.out.println(c + "'s color is gray.");
    }

    public void sound(){
        System.out.println(this.name + " sounds hahaha.");
    }
}

public class LandAnimal {
    private Random rand = new Random(100);

    public Rodent rodentGenerator(){
        switch(rand.nextInt(3)){
            default:
            case 0: return new Mouse();
            case 1: return new Gerbil();
            case 2: return new Hamster();
        }
    }

    public static void main(String[] args){
        LandAnimal a = new LandAnimal();

        System.out.println("Test Program:");
        Rodent[] r = new Rodent[10];
        for(int i = 0 ; i < r.length; i++ ){
            r[i] = a.rodentGenerator();
        }

        for(Rodent t: r){
            System.out.println("Print Color");
            System.out.println(t.name);
            t.sound();
            t.color(t);
        }
    }
}
