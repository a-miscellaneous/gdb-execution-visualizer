#include <stdio.h>

int a = 1;
int b = 2;

int main() {
    int num = 12345;
    int rev = 1;
    int rem = 1;

    while (num != 0) {
        //int test = 1;
        rem = num % 10;
        rev = rev * 10 + rem;
        num /= 10;
    }

    printf("////////////////////////////////////Reversed = %d \n", rev);

    return 0;
}