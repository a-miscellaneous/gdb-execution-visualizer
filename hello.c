#include <stdio.h>

int a = 1;
int b = 2;

int main() {
    int num = 12345;
    int rev = 0;
    int rem = 0;

    while (num != 0) {
        rem = num % 10;
        rev = rev * 10 + rem;
        num /= 10;
    }

    printf("Reversed = %d \n", rev);

    return 0;
}