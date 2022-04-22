f4 = open('words_1.txt', 'r')
a = []
for line in f4:
    a.append(line.split())
f4.close()

f7 = open('words_2.txt', 'r')
b = []
for line in f7:
    b.append(line.split())
f7.close()

cl = open("class.txt", 'r')
c = []
for line in cl:
    c.append(line)
cl.close()
