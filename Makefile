all: scheduler 

scheduler:
	gcc -g -o build/schedule src/schedule.c src/schedule.h -lm 

.PHONY: clean

clean:
	rm build/*

install:
	cp build/schedule /usr/local/bin/schedule