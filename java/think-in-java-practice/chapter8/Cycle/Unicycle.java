// import java.util.concurrent.CyclicBarrier;
public class Unicycle extends Cycle{
    public Unicycle(){
        this.name = "Unicycle";
    }
    
    public void color(){
        System.out.println("Unicycle color is black.");
    }

    public void roadRide(Cycle c){
        c.ride(c);
    }

    public static void main(String[] args){
        System.out.println("Unicycle is coming.");
        Unicycle b = new Unicycle();
        b.color();
        b.roadRide(b);
    }
}
