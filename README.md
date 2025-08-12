# Cirebon
> Cirebon esolang in one file.
## Introduction
This is not a real assembly lang. It's just an educational project!
Nothing :D
Search info in Internet, else send an issue or a pull request.
## Installation
1. First you need to install the interpreter.
`wget`:
```bash
wget https://raw.githubusercontent.com/48Hz-Minetest/Cirebon/main/cirebon.py
```
`curl`:
```bash
curl -o cirebon.py https://raw.githubusercontent.com/48Hz-Minetest/Cirebon/main/cirebon.py
```
(NEW) `git`:
```bash
git clone https://github.com/48Hz-Minetest/Cirebon.git
cp cirebon.py ..
cd ..
rm -rf Cirebon
```
2. Then you need to write a programm on it
```bash
nano my_first_programm.cire
```
Paste this code in `nano`
```cirebon
const MSG "Hello, World!"
prt_str MSG
```
And execute it
```bash
python cirebon.py test.cire
```
Or just type this and it will print the usage:
```bash
python cirebon.py
```
## Contributing
To contribute send an issue or a pull request with label `contribute`.
