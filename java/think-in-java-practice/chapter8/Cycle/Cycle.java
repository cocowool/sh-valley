public class Cycle {
    public String name;

    public Cycle(){
        this.name = "Cycle";
    }

    public String toString(){
        return this.name;
    }    

    public void ride(Cycle c){
        System.out.println( c.toString() + " is riding.");
    }
}
