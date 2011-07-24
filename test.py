class Foo(object):
    def bar(self):
        self.__baz()

    def __baz(self):
        print('baz')

f=Foo()
f.bar()
