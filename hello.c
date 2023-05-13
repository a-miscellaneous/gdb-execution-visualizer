#include <stdio.h>



int mod(int a, int b) {
    a = a % b;
    return a;
}

int main() {
    int num = 12345;
    int rev = 1;
    int rem = 1;

    while (num != 0) {

        int test = 1;
        rem = mod(num, 10);
        rem = num % 10;
        rev = rev * 10 + rem;
        num /= 10;
    }

    printf("////Reversed = %d \n", rev);

    return 0;
}