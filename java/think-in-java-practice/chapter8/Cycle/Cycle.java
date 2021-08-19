public class Cycle {
    public String name;

    public Cycle(){
        this.name = "Cycle";
    }

    public String toString(){
        return this.name;
    }

    public void wheels(Cycle c){
        System.out.println( c.toString() + "'s wheels is .");
    }

    public void ride(Cycle c){
        this.wheels(c);
        System.out.println( c.toString() + " is riding.");
    }
}
