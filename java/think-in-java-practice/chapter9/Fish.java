// Try to make the interface class to private, compile error.
interface Animal {
    private void Swim();
    void Color();
}

public class Fish implements Animal{
    private void Color(){
        System.out.println("Fish color is red.");
    }

    public static void main(String[] args){
        Animal a = new Fish();
    }
}
