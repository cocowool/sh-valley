class Room {
    private String s;
    Room(){
        System.out.println("Room class initializing...");
        s = "I'm a room.";
    }

    public String toString(){
        return s;
    }
}

public class Building {
    private Room r;

    public String toString(){
        if( r == null){
            r = new Room();
        }

        return "Building includes " + r;
    }

    public static void main(String[] args){
        System.out.println("Main in Building class");
        Building b = new Building();
        System.out.println(b);
    }
}
