#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/wait.h>
int main(void) {
    int fd[2];
    if (pipe(fd)<0) { perror("pipe"); return 1; }
    pid_t pid=fork();
    if(pid<0) { perror("fork"); close(fd[0]); close(fd[1]); return 1; }
    if(pid==0) {
        close(fd[1]);
        char buffer[128]; size_t used=0;
        while (used<sizeof(buffer)-1) {
            ssize_t n=read(fd[0], buffer+used, sizeof(buffer)-1-used);
            if(n<0 && errno==EINTR) continue;
            if(n<0) { perror("read"); _exit(1); }
            if(n==0) break;
            used+=(size_t)n;
        }
        buffer[used]='\0';
        printf("Child received: %s\n",buffer);
        close(fd[0]); return 0;
    }
    close(fd[0]);
    const char msg[]="Hello from the parent";
    size_t off=0;
    while(off<strlen(msg)) {
        ssize_t n=write(fd[1],msg+off,strlen(msg)-off);
        if(n<0 && errno==EINTR) continue;
        if(n<=0) { perror("write"); close(fd[1]); waitpid(pid,NULL,0); return 1; }
        off+=(size_t)n;
    }
    close(fd[1]);
    int status;
    while(waitpid(pid,&status,0)<0) { if(errno!=EINTR) { perror("waitpid"); return 1; } }
    return WIFEXITED(status) ? WEXITSTATUS(status) : 1;
}
