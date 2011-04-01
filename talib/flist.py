from talib import TA_LIB

tl = TA_LIB()

for g in tl.group_list():
    print("\nGroup: %s" % g)
    for f in tl.func_list(g):
        print("%s" % str(tl.func(f)))

