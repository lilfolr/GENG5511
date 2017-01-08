#include <stdio.h>
#include <fcntl.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/stat.h>

#define INGOING "traffic.fifo"
#define BUFFER 200

int generate(){
    printf("Generating\n");
    ///Generate random traffic to fifo file
    mkfifo(INGOING, 0666);
    printf("Made fifo\n");
    int out_fd=open(INGOING, O_WRONLY);
    printf("opened fifo for writing\n");
    if (out_fd==-1) {
        perror("open error");
    }
    pid_t pid = fork();
    if (pid == 0){
        // child process
        while (1) {
            printf("Writing to fifo\n");
            char* input = "Hello World";
            if (write(out_fd, input, strlen(input))==-1) {
                perror("write error");
            }
        }
    }
    else if (pid > 0){
        // parent
        return 0;
    }
    else{
        // fork failed
        printf("fork() failed!\n");
        return 1;
    }
    
}
