class practice1 {
    int i;
    char x;

    public int getI() {
        return i;
    }

    public char getX(){
        return x;
    }

    public static void main(String args[]){

        System.out.println( new practice1().getI() );
        System.out.println( new practice1().getX() );
    }
}