// import java.util.concurrent.CyclicBarrier;
public class Tricycle extends Cycle{
    public Tricycle(){
        this.name = "Tricycle";
    }
    
    public void color(){
        System.out.println("Tricycle color is white.");
    }

    public void roadRide(Cycle c){
        c.ride(c);
    }

    public static void main(String[] args){
        System.out.println("Tricycle is coming.");
        Tricycle b = new Tricycle();
        b.color();
        b.roadRide(b);
    }
}
