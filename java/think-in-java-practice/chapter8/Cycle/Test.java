public class Test {
    public static void main(String[] args){
        Bicycle b = new Bicycle();
        b.color();
        b.roadRide(b);

        Unicycle u = new Unicycle();
        u.color();
        u.roadRide(u);

        Tricycle t = new Tricycle();
        t.color();
        t.roadRide(t);
    }
}
