#include <stdio.h>
#include <string.h>
int main(int argc, char **argv) {
    char buffer[16];
    if(argc!=2) { fprintf(stderr,"Usage: %s TEXT\n",argv[0]); return 2; }
    size_t n=strlen(argv[1]);
    if(n>=sizeof(buffer)) { fprintf(stderr,"Rejected: input plus terminator exceeds %zu bytes\n",sizeof(buffer)); return 1; }
    memcpy(buffer,argv[1],n+1);
    printf("Accepted: %s\n",buffer);
    return 0;
}
