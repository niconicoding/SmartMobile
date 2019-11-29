#include <sys/socket.h>
#include<sys/types.h>
#include <unistd.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>


int main(int argc, char **argv)
{

    int client_len;
    int client_sockfd;

    char buf_get[255];
    char buf_in[7] = "second";


    struct sockaddr_in clientaddr;

    if (argc != 2)
    {
        printf("Usage : ./client [port]\n");
        printf("예    : ./client 4444\n");
        exit(0);
    }

    client_sockfd = socket(AF_INET, SOCK_STREAM, 0);
    clientaddr.sin_family = AF_INET;
    clientaddr.sin_addr.s_addr = inet_addr("INSERT SERVER ADDRESS");
    clientaddr.sin_port = htons(atoi(argv[1]));

    client_len = sizeof(clientaddr);

    if (connect(client_sockfd, (struct sockaddr *)&clientaddr, client_len) < 0)
    {
        perror("Connect error: ");
        exit(0);
    }
    write(client_sockfd, buf_in, 7);
    read(client_sockfd, buf_get, 255);

    pid_t pid = fork();
    if(pid>0){
        close(client_sockfd);
        exit(0);
    }else if(pid == 0){

        pid_t ppid = fork();
        if(ppid > 0){
            printf("son\n");
            execl("kinesis_video_gstreamer_sample_app","./kinesis_video_gstreamer_sample_app","KINESIS STREAM ID",0);
        }
        else if(ppid == 0){
            printf("baby\n");
            execl("/bin/bash","bash","/home/pi/infant_accident_prevention_system_development/smartmobile.py",0);
        }else{
            printf("error\n");
        }
    }else{
        printf("error fork()\n");
    }
    return 0;
}
