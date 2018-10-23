

#           suma(10)
#           /    \
#         suma(9) + 10
#         /      \
#       suma(8) + 9
#       /      \
#     suma(7) + 8
#     /      \
# suma(6)     +7



def suma(n):
    if n == 1:
        return 1
    return suma(n-1) + n

# suma(10) => suma(9) + 10 => suma(8) + 9 + 10 => suma(7) + 8 + 9 + 10 ... => 1 + 2 + 3 ... 10 

 suma(4) = > 6 + 4

 suma(3) = > 3 + 3 = 6
 
 suma(2) = > 1 + 2 = 3
 
 suma(1) = > 1

