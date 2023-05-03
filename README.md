# gdb-execution-visualizer



## Requirements

* Python 3.x (maybe)
* GDB
* GCC/c compiler
* rr

#### GDB
should be compiled for use with python, check
```bash
gdb --configuration
``` 
for 
```
--with-python=/usr
```

#### rr
do this:
```
sudo sysctl -w kernel.perf_event_paranoid=1
```



## Usage

TODO:

current execution command:
```
q \n gcc -g hello.c && gdb -q --command test.py
```
put it into [F5 Anything](https://marketplace.visualstudio.com/items?itemName=discretegames.f5anything)



## License

[Apache](https://choosealicense.com/licenses/apache-2.0/)
