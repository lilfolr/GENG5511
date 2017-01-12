#include<stdio.h> 			//For standard things
#include<stdlib.h>    		//malloc
#include<string.h>    		//memset
#include<netinet/ip_icmp.h>   //Provides declarations for icmp header
#include<netinet/udp.h>   //Provides declarations for udp header
#include<netinet/tcp.h>   //Provides declarations for tcp header
#include<netinet/ip.h>    //Provides declarations for ip header
#include<sys/socket.h>
#include<arpa/inet.h>

char *ProcessPacket(unsigned char* buffer, int size);

unsigned int sock_raw;
int tcp=0,udp=0,icmp=0,others=0,igmp=0,total=0,i,j;

int sniff_packets(){
    unsigned int saddr_size;
	int data_size;
    struct sockaddr saddr;
    unsigned char *buffer = (unsigned char *)malloc(65536); //Its Big!

    int sock_raw_signed = socket(AF_INET , SOCK_RAW , IPPROTO_TCP);
	if(sock_raw_signed < 0)
	{
		printf("Socket Error\n");
	}
	sock_raw = sock_raw_signed;
    mkfifo(INGOING, 0666);
    printf("Made fifo\n");
    pid_t pid = fork();
    if (pid == 0){
        // child process
        int out_fd=open(INGOING, O_WRONLY);
        printf("opened fifo for writing\n");
        if (out_fd==-1) {
            perror("open error");
        }
        while (1) {
			saddr_size = (unsigned int) sizeof saddr;
			//Receive a packet
			data_size = recvfrom(sock_raw , buffer , 65536 , 0 , &saddr , &saddr_size);
			if(data_size <0 ){
				printf("Recv from error , failed to get packets\n");
			}
			//Now process the packet
            printf("Writing to fifo\n");
            char* input = ProcessPacket(buffer , data_size);
            if (write(out_fd, input, strlen(input))==-1) {
                perror("write error");
            }
        }
    }
    else if (pid > 0){
        return 0;
    }
    else{
        printf("fork() failed!\n");
        return -1;
    }
}

char* ProcessPacket(unsigned char* buffer, int size)
{
	//Get the IP Header part of this packet
	struct iphdr *iph = (struct iphdr*)buffer;
	++total;
	switch (iph->protocol) //Check the Protocol and do accordingly...
	{
		case 1:  //ICMP Protocol
			++icmp;
			break;

		case 2:  //IGMP Protocol
			++igmp;
			break;

		case 6:  //TCP Protocol
			++tcp;
			break;

		case 17: //UDP Protocol
			++udp;
			break;

		default: //Some Other Protocol like ARP etc.
			++others;
			break;
	}
	char *return_data = (char*)malloc(30 * sizeof(char));
	sprintf(return_data, "TCP : %d   UDP : %d   ICMP : %d   IGMP : %d   Others : %d   Total : %d\n",tcp,udp,icmp,igmp,others,total);
	return return_data;
}
