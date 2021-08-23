package cn.edulinks.life;
//jar -cvf cn.edulinks.code.jar cn/edulinks/code/*class
//jar -cvf cn.edulinks.life.jar cn/edulinks/life/*class
//java -classpath cn.edulinks.code.jar:cn.edulinks.life.jar cn.edulinks.life.Wang

import cn.edulinks.code.Coding;

public class Wang {
    public static void main(String[] args){
        Coding c = new Worker();
        c.codeJava();
        c.codePython();
        c.codeNode();
    }
}
