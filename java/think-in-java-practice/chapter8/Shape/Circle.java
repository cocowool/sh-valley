public class Circle extends Shape {
    @Override void draw() {
        System.out.println("Circle.draw()");
    }
    @Override void erase() {
        System.out.println("Circle.erase()");
    }

    public void size() {
        System.out.println("Circle's size is 5.");
    }
}
