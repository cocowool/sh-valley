public class Shapes {
    private static RandomShapeGenerator gen = new RandomShapeGenerator();

    public static void main(String[] args){
        Shape[] s = new Shape[9];
        for(int i = 0; i < s.length; i++){
            s[i] = gen.next();
        }

        for(Shape shp : s ){
            shp.draw();
            shp.size();
        }

        System.out.println("================");

        Shape[] x = new Shape[5];
        for(int i = 0; i < x.length; i++){
            x[i] = gen.next();
        }

        for(Shape shp : x ){
            shp.draw();
            shp.size();
        }
    }
}
