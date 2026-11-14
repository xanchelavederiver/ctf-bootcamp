/* «Пропуск» (reverse) — СГЕНЕРИРОВАНО src/generate.py, править генератор.
 *
 * Утилита читает строку со stdin. Если она совпадает с одним из трёх
 * пропусков (флагов) — печатает "Access granted", иначе "Access denied".
 * Три проверки независимы и демонстрируют три приёма обратной разработки.
 *
 * Сборка:  gcc -O0 -no-pie -fno-stack-protector -o access-check check.c
 */
#include <stdio.h>
#include <string.h>

/* --- Флаг 1: открытая константа, сверяется strcmp (находится strings). --- */
static const char *FLAG1 = "BootCTF{str1ngs_unlock_the_d00r}";

/* --- Флаг 2: хранится XOR-шифрованным; расшифровывается до main. --- */
static unsigned char enc2[] = { 0x18, 0x35, 0x35, 0x2e, 0x19, 0x0e, 0x1c, 0x21, 0x3d, 0x3e, 0x38, 0x05, 0x29, 0x3f, 0x3f, 0x29, 0x05, 0x2e, 0x32, 0x3f, 0x05, 0x39, 0x6a, 0x34, 0x29, 0x2e, 0x28, 0x2f, 0x39, 0x2e, 0x6a, 0x28, 0x27 };
static char dec2[sizeof(enc2) + 1];

__attribute__((constructor))
static void unlock_badge(void)
{
    unsigned int i;
    for (i = 0; i < sizeof(enc2); i++)
        dec2[i] = (char)(enc2[i] ^ 0x5a);
    dec2[sizeof(enc2)] = '\0';
}

/* Ручной побайтовый цикл вместо strcmp/memcmp: ltrace ничего не покажет. */
static int check2(const char *s)
{
    unsigned int i;
    for (i = 0; i < sizeof(enc2); i++) {
        if (s[i] != dec2[i]) return 0;
    }
    return s[sizeof(enc2)] == '\0';
}

/* --- Флаг 3: цепочка if-ов, по одному символу, перемешанный порядок. --- */
static int check3(const char *s)
{
    int bad = 0;
    if (strlen(s) != 33) return 0;
    if (s[32] != '}') bad = 1;
    if (s[28] != 'h') bad = 1;
    if (s[17] != '_') bad = 1;
    if (s[16] != 'f') bad = 1;
    if (s[8] != 's') bad = 1;
    if (s[7] != '{') bad = 1;
    if (s[19] != 'a') bad = 1;
    if (s[1] != 'o') bad = 1;
    if (s[5] != 'T') bad = 1;
    if (s[0] != 'B') bad = 1;
    if (s[4] != 'C') bad = 1;
    if (s[15] != '1') bad = 1;
    if (s[18] != 'l') bad = 1;
    if (s[21] != 'd') bad = 1;
    if (s[14] != '_') bad = 1;
    if (s[29] != '0') bad = 1;
    if (s[2] != 'o') bad = 1;
    if (s[22] != 'e') bad = 1;
    if (s[13] != 'c') bad = 1;
    if (s[3] != 't') bad = 1;
    if (s[30] != 'm') bad = 1;
    if (s[6] != 'F') bad = 1;
    if (s[27] != '_') bad = 1;
    if (s[9] != 't') bad = 1;
    if (s[11] != 't') bad = 1;
    if (s[25] != 'a') bad = 1;
    if (s[20] != 'd') bad = 1;
    if (s[12] != 'i') bad = 1;
    if (s[31] != 'e') bad = 1;
    if (s[26] != 't') bad = 1;
    if (s[24] != '_') bad = 1;
    if (s[10] != 'a') bad = 1;
    if (s[23] != 'r') bad = 1;
    return bad == 0;
}

int main(void)
{
    char buf[256];
    if (!fgets(buf, sizeof(buf), stdin)) return 1;
    buf[strcspn(buf, "\n")] = '\0';

    if (strcmp(buf, FLAG1) == 0 || check2(buf) || check3(buf))
        puts("Access granted");
    else
        puts("Access denied");
    return 0;
}
