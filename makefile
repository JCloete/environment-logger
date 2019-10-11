.RECIPEPREFIX +=
CC = gcc
CFLAGS = -Wall -lm -lrt -lwiringPi -lpthread

PROG = bin/*
OBJS = obj/*

default:
    mkdir -p bin obj
    $(CC) $(CFLAGS) -c src/main.c -o obj/main
    $(CC) $(CFLAGS) -c src/sensors.c -o obj/sensors
    $(CC) $(CFLAGS) -c src/network.c -o obj/network
    $(CC) $(CFLAGS) obj/main obj/sensors obj/network -o bin/main

run:
    sudo ./bin/main

clean:
    rm $(PROG) $(OBJS)