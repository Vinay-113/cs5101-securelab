#include <stdio.h>
#include <string.h>
/* The probe always reports both paths and fails unless the required access
 * pattern is observed. DAC deliberately permits both in the AppArmor lesson. */
int main(int argc, char **argv) {
    int expect_denied=argc==2 && strcmp(argv[1],"confined")==0;
    const char *paths[]={"/opt/securelab/apparmor/allowed.txt","/opt/securelab/apparmor/denied.txt"};
    int opened[2];
    for(int i=0;i<2;i++) {
        FILE *f=fopen(paths[i],"r"); opened[i]=(f!=NULL);
        printf("%s: %s\n",paths[i],f ? "ALLOWED" : "DENIED");
        if(f) fclose(f);
    }
    return opened[0] && (expect_denied ? !opened[1] : opened[1]) ? 0 : 1;
}
