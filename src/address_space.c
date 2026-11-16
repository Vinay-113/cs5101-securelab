#include <stdio.h>
#include <unistd.h>
int main(void) {
    int secret = 12345;
    printf("PID = %ld\n&secret = %p\nsecret = %d\n", (long)getpid(), (void *)&secret, secret);
    puts("Inspect this process's maps for 30 seconds.");
    fflush(stdout);
    sleep(30);
    return 0;
}
