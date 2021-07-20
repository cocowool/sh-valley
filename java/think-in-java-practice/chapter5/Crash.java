// package chapter5;

class DigitalCar {
    boolean energy = true;
    int fuels = 100;

    DigitalCar(int fuel){
        this.fuels = fuel;
        if(fuel > 0){
            energy = true;
        }else{
            energy = false;
        }
    }

    void goaround(){
        this.fuels--;
        System.out.println("fuel is " + this.fuels);
        System.out.println("energy is " + this.energy);
        if(this.fuels > 0){
            energy = true;
        }else{
            energy = false;
        }
    }

    protected void finalize(){
        if( ! energy ){
            System.out.println("Digital Car run out energy");
        }
    }
}

public class Crash {
    public static void main(String[] args){
        DigitalCar d = new DigitalCar(11);
        d.goaround();

        DigitalCar dd = new DigitalCar(0);
        dd.goaround();

        System.gc();

    }
}
