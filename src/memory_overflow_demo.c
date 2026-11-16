/* INTENTIONALLY UNSAFE. Fixed teaching input, lab VM only. No exploit payload. */
#include <stdio.h>
#include <string.h>
int main(int argc, char **argv) {
    char buffer[16];
    const char *input=(argc==2 && strcmp(argv[1],"short")==0) ? "short" : "THIS_INPUT_IS_LONGER_THAN_SIXTEEN";
    printf("Copying %zu bytes into a 16-byte buffer...\n", strlen(input)+1);
    fflush(stdout);
    memcpy(buffer,input,strlen(input)+1);
    /* Consume the buffer so the demonstration cannot be optimized away. */
    printf("Buffer: %s\n",buffer);
    return 0;
}
