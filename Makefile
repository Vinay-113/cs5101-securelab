CC ?= cc
CFLAGS := -std=c11 -D_POSIX_C_SOURCE=200809L -Wall -Wextra -Wpedantic -g
HARDEN := -O2 -fstack-protector-strong -fPIE
LDFLAGS := -pie -Wl,-z,relro,-z,now,-z,noexecstack
PROGRAMS := identity syscall_demo address_space pipe_ipc shared_ipc bounded_copy confinement_probe
BINS := $(addprefix bin/,$(PROGRAMS)) bin/race_unsafe bin/race_mutex
.PHONY: all clean test unsafe
all: $(BINS)
bin:
	mkdir -p $@
bin/%: src/%.c | bin
	$(CC) $(CFLAGS) $(HARDEN) $< -o $@ $(LDFLAGS) -pthread
bin/race_unsafe: src/race_demo.c | bin
	$(CC) $(CFLAGS) -O0 -pthread $< -o $@ $(LDFLAGS)
bin/race_mutex: src/race_demo.c | bin
	$(CC) $(CFLAGS) -O0 -DUSE_MUTEX -pthread $< -o $@ $(LDFLAGS)
unsafe: bin/memory_protected bin/memory_unprotected bin/memory_asan
bin/memory_protected: src/memory_overflow_demo.c | bin
	$(CC) $(CFLAGS) -O0 -fstack-protector-all -fPIE $< -o $@ $(LDFLAGS)
bin/memory_unprotected: src/memory_overflow_demo.c | bin
	$(CC) $(CFLAGS) -O0 -fno-stack-protector -fno-pie -no-pie $< -o $@ -Wl,-z,noexecstack
bin/memory_asan: src/memory_overflow_demo.c | bin
	$(CC) $(CFLAGS) -O0 -fsanitize=address -fno-omit-frame-pointer $< -o $@ $(LDFLAGS)
test: all unsafe
	python3 tests/test_programs.py
clean:
	rm -rf bin
