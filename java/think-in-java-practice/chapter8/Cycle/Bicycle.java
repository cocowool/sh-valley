// import java.util.concurrent.CyclicBarrier;
public class Bicycle extends Cycle{
    public Bicycle(){
        this.name = "Bicycle";
    }
    
    public void color(){
        System.out.println("Bicycle color is red.");
    }

    public void roadRide(Cycle c){
        c.ride(c);
    }

    public static void main(String[] args){
        System.out.println("Bicycle is coming.");
        Bicycle b = new Bicycle();
        b.color();
        b.roadRide(b);
    }
}
