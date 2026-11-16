/* Self-contained comparison when no instructor shared-memory code is supplied.
 * Linux anonymous MAP_SHARED; process-shared semaphore prevents stale reads. */
#define _GNU_SOURCE
#include <errno.h>
#include <semaphore.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <sys/mman.h>
#include <sys/wait.h>
struct message { sem_t ready; char text[128]; };
int main(void) {
    struct message *m=mmap(NULL,sizeof(*m),PROT_READ|PROT_WRITE,MAP_SHARED|MAP_ANONYMOUS,-1,0);
    if(m==MAP_FAILED) { perror("mmap"); return 1; }
    if(sem_init(&m->ready,1,0)<0) { perror("sem_init"); munmap(m,sizeof(*m)); return 1; }
    pid_t pid=fork();
    if(pid<0) { perror("fork"); sem_destroy(&m->ready); munmap(m,sizeof(*m)); return 1; }
    if(pid==0) {
        while(sem_wait(&m->ready)<0) { if(errno!=EINTR) { perror("sem_wait"); _exit(1); } }
        printf("Shared-memory child received: %s\n",m->text);
        munmap(m,sizeof(*m)); return 0;
    }
    snprintf(m->text,sizeof(m->text),"Hello through a synchronized shared mapping");
    if(sem_post(&m->ready)<0) { perror("sem_post"); return 1; }
    int status;
    while(waitpid(pid,&status,0)<0) { if(errno!=EINTR) { perror("waitpid"); return 1; } }
    int failed=sem_destroy(&m->ready)<0;
    if(munmap(m,sizeof(*m))<0) failed=1;
    return !failed && WIFEXITED(status) && WEXITSTATUS(status)==0 ? 0 : 1;
}
