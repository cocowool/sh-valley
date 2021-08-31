//: innerclasses/Sequence.java
// Holds a sequence of Objects.

interface Selector {
    boolean end();
    Object current();
    void next();
}

class Animal {
    private String name;
    Animal(Integer i){
        switch (i) {
            case 0:
                name = "Dog";
                break;
            case 1:
                name = "Cock";
                break;
            case 2:
                name = "Bird";
                break;
            case 3:
                name = "Cat";
                break;
            case 4:
                name = "Goat";
                break;
            case 5:
                name = "Mouse";
                break;
            case 6:
                name = "Panda";
                break;
            case 7:
                name = "Cow";
                break;
            case 8:
                name = "Penguin";
                break;        
            default:
                name = "Pig";
                break;
        }
    }

    public String toString(){
        return name;
    }
}


public class Sequence {
    private Object[] items;
    private int next = 0;
    public Sequence(int size) { items = new Object[size]; }
    public void add(Object x) {
        if(next < items.length)
        items[next++] = x;
    }
    private class SequenceSelector implements Selector {
        private int i = 0;
        public boolean end() { return i == items.length; }
        public Object current() { return items[i]; }
        public void next() { if(i < items.length) i++; }
    }
    public Selector selector() {
        return new SequenceSelector();
    }	
    public static void main(String[] args) {
        Sequence sequence = new Sequence(10);
        for(int i = 0; i < 10; i++)
        // sequence.add(Integer.toString(i));
        sequence.add( new Animal(i) );
        Selector selector = sequence.selector();
        while(!selector.end()) {
        System.out.println(selector.current() + " ");
        selector.next();
        }
    }
} /* Output:
0 1 2 3 4 5 6 7 8 9
*///:~
