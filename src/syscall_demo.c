#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <unistd.h>
int main(void) {
    int fd = open("hello.txt", O_CREAT | O_WRONLY | O_TRUNC | O_NOFOLLOW, 0644);
    if (fd < 0) { perror("open"); return 1; }
    const char msg[] = "Hello from user space!\n";
    size_t off = 0;
    while (off < sizeof(msg)-1) {
        ssize_t n = write(fd, msg+off, sizeof(msg)-1-off);
        if (n < 0 && errno == EINTR) continue;
        if (n <= 0) { perror("write"); close(fd); return 1; }
        off += (size_t)n;
    }
    if (close(fd) < 0) { perror("close"); return 1; }
    return 0;
}
