public class Outer {
    class Inner {
        void saySomthing(){
            System.out.println("I'm inner.");
        }
    }

    public Inner getInner(){
        return new Inner();
    }

    public static void main(String[] args){
        System.out.println("Outer Program:");
        Outer o = new Outer();
        o.getInner().saySomthing();
    }
}
