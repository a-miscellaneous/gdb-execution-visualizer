#include <stdio.h>
#include <stdlib.h>
#include <string.h>



int mod(int a, int b) {
    a = a % b;
    return a;
}

int main() {
    int num;
    num = 12345;
    int rev = 1;
    int rem = 1;
    char *str = "Hello World";
    char *str2 = (char*)malloc(100);
    strcpy(str2, str);

    while (num != 0) {
        int test = 1;
        rem = mod(num, 10);
        rem = num % 10;
        rev = rev * 10 + rem;
        num /= 10;
    }

    printf("////Reversed = %d \n", rev);

    exit(0);
}