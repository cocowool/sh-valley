package com.edulinks.testproject.controller;

import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;


@RestController
@RequestMapping(value = "demo")
public class MyFirstSpringBootController {
    @RequestMapping(value = "hello")
    public String hello(){
        return "Hello World";
    }
}
