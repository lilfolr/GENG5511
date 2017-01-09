#include <printf.h>
#include <stdbool.h>
#include "generator.c"

#define BUFFER 200

int main(int argc, char *argv[]) {
    printf("Starting\n");
    typedef struct config config;
    struct config {
    	bool is_simulator;
    };
    config settings = {false};
    int opt;
    while ((opt = getopt(argc, argv, "s"))!=-1){
    	switch (opt){
			case 's':{
				settings.is_simulator = true;
			}
    	}
    }

    if (settings.is_simulator){
		generate();
		char in[BUFFER];

		int in_fd=open(INGOING, O_RDONLY);
		if (in_fd==-1) {
			perror("open error");
			exit(-1);
		}
		while (read(in_fd, in, BUFFER)>0) {
			printf("Received data %s\n", in);
		}
    }
    return 0;
}
