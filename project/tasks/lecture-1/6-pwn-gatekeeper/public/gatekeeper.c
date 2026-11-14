/*
 * «Турникет» — демонстрационное задание категории pwn (мини-курс «Введение в CTF»).
 *
 * Сборка (воспроизводимо, в Docker):
 *   gcc -fno-stack-protector -no-pie -O0 -o gatekeeper gatekeeper.c
 */

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>

void win(void) {
    const char *flag = getenv("PWN_FLAG_1");
    if (!flag) flag = "BootCTF{PWN_FLAG_1_not_set}";
    write(1, "Турникет открыт. Пропуск: ", 27);
    write(1, flag, strlen(flag));
    write(1, "\n", 1);
    fflush(stdout);
}

void check(void) {
    char buf[64];
    puts("Поднесите пропуск к турникету:");
    fflush(stdout);
    read(0, buf, 256);
    puts("Пропуск не распознан. Доступ запрещён.");
    fflush(stdout);
}

int main(void) {
    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stdin, NULL, _IONBF, 0);
    check();
    return 0;
}
