abstract class People {
    People(){
        print();
    }

    public abstract void print();
}

class BlackPeople extends People {
    int i;

    BlackPeople(){
        this.i = 10;
    }

    public void print(){
        System.out.println("BlackPeople print " + this.i);
    }
}

public class Life {
    public static void main(String[] args){
        BlackPeople b = new BlackPeople();
        b.print();
    }
}
