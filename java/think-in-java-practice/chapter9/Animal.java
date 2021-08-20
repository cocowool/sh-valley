//Page 155, Practice 9
import java.util.*;

abstract class Rodent {
    public String name;

    Rodent(){
        this.name = "Rodent";
    }

    public void craw(Rodent r) {
        System.out.println( r + " is crawing.");
    }

    public void color(Rodent c){};

    public abstract void sound();

    public String toString(){
        return this.name;
    }
}

class Mouse extends Rodent {
    Mouse(){
        this.name = "Mouse";
    }

    public void color(Mouse c){
        System.out.println(c + "'s color is gray.");
    }

    public void sound(){
        System.out.println(this.name + " sounds jijiji.");
    }
}

class Gerbil extends Rodent {
    Gerbil(){
        this.name = "Gerbil";
    }

    public void color(Gerbil c){
        System.out.println(c + "'s color is black.");
    }

    public void sound(){
        System.out.println(this.name + " sounds gagaga.");
    }
}

class Hamster extends Rodent {
    Hamster(){
        this.name = "Hamster";
    }

    public void color(Hamster c){
        System.out.println(c + "'s color is gray.");
    }

    public void sound(){
        System.out.println(this.name + " sounds hahaha.");
    }
}

public class Animal {
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
        Animal a = new Animal();

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
