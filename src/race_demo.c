#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
/* Intentionally a C data race without USE_MUTEX: undefined behavior.
 * -O0 makes lost updates easier to observe; it does not make them guaranteed. */
static long counter;
#ifdef USE_MUTEX
static pthread_mutex_t lock = PTHREAD_MUTEX_INITIALIZER;
static void checked(int e) { if (e) { fprintf(stderr, "pthread: %s\n", strerror(e)); exit(1); } }
#endif
static void *worker(void *arg) {
    (void)arg;
    for (long i = 0; i < 1000000; ++i) {
#ifdef USE_MUTEX
        checked(pthread_mutex_lock(&lock));
#endif
        /* CRITICAL SECTION: read -> add -> write shared state. */
        counter++;
#ifdef USE_MUTEX
        checked(pthread_mutex_unlock(&lock));
#endif
    }
    return NULL;
}
int main(void) {
    pthread_t t[2];
    for (int i=0; i<2; ++i) {
        int e=pthread_create(&t[i], NULL, worker, NULL);
        if(e) { fprintf(stderr,"pthread_create: %s\n",strerror(e)); exit(1); }
    }
    for (int i=0; i<2; ++i) {
        int e=pthread_join(t[i],NULL);
        if(e) { fprintf(stderr,"pthread_join: %s\n",strerror(e)); return 1; }
    }
    printf("Expected: 2000000\nActual  : %ld\n",counter);
#ifdef USE_MUTEX
    checked(pthread_mutex_destroy(&lock));
    return counter == 2000000 ? 0 : 1;
#else
    return 0;
#endif
}
