#include <stdio.h>
#include <stdlib.h>
#include <string.h>



int mod(int a, int b) {
    int c = a / b;
    a = a % b;
    return a;
}

int main() {
    int num;
    num = 123;
    int rev = 0;
    int rem = 0;
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

    for (int i = 0; i < 4; i++) {
        printf("Hello World\n");
    }

    int ss = 0;
    do {
        int x = 0;
        ss++;
    } while (ss < 4);

    printf("////Reversed = %d \n", rev);

    exit (0);
}