#include <stdio.h>
#include <unistd.h>
int main(void) {
    printf("Real UID       : %lu\nEffective UID  : %lu\n", (unsigned long)getuid(), (unsigned long)geteuid());
    printf("Real GID       : %lu\nEffective GID  : %lu\n", (unsigned long)getgid(), (unsigned long)getegid());
    return 0;
}
