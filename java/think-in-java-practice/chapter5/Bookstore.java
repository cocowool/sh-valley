// package chapter5;

class Booklist {
    public enum FamousBook {
        JANE, FRENCH, CHINA 
    }

    Booklist(String... args){

        for(String x : args){
            System.out.println("bookname is " + x);
        }
    }


}

public class Bookstore {
    public static void main(String[] args){
        Booklist b = new Booklist("Great Wall","Love Story","Children");

        for(String x : args){
            System.out.println("The argument is " + x);
        }

        for(Booklist.FamousBook x : Booklist.FamousBook.values()){
            System.out.println("famous book is " + x);
        }

        
    }

}
