#include<stdio.h>
#include<stdlib.h>
#include<unistd.h>
#include<sys/types.h>

int main(){
    pid_t pid;

    printf("Process Start\n");

    pid = fork();

    if(pid > 0){
        printf("parent\n");
        execl("/home/pi/.virtualenvs/openvino/bin/python3","python3","/home/pi/infant_accident_prevention_system_development/smartmobile_first_client.py", 0);
    }else if(pid == 0){

        pid_t ppid = fork();
        if(ppid > 0){
            printf("son\n");
            execl("kinesis_video_gstreamer_sample_app","./kinesis_video_gstreamer_sample_app","KINESSIS STREAM ID",0);
        }
        else if(ppid == 0){
            printf("baby\n");
            execl("/bin/bash","bash","/home/pi/infant_accident_prevention_system_development/process_check.sh",0);
        }else{
            printf("error\n");
        }
    }else{
        printf("error fork()\n");
    }
    return 0;
}
