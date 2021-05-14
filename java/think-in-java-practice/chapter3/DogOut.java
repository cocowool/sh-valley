import static net.mindview.util.Print.*;
// package chapter3;

class Dog {
    String name;
    String says;
}

public class DogOut {
    public static void main(String[] args){
        Dog a = new Dog();
        a.name = "spot";
        a.says = "Ruff! ";

        Dog b = new Dog();
        b.name = "scruffy";
        b.says = "Wurf! ";

        print("Dog a.name " + a.name + ", a.syas " + a.says);
        print("Dog b.name " + b.name + ", b.syas " + b.says);

        print(a.equals(b));
    }
}
