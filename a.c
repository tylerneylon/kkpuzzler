#include <stdio.h>

// How to print a division sign.
// This works in iTerm2 and the default Terminal app.

int main() {
    printf("%c%c%c\n", 0xc3, 0xb7, 0x0a);
    return 0;
}
