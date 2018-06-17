
import copy
import typing

from pytoolcore import exception


class Argument:

    def __init__(self, argname: str, hasvalue: bool, optional: bool,
                 value: str=None, substitutes: typing.List[str]=None)->None:
        self.__argname__: str = argname.lower()
        self.__hasvalue__: bool = hasvalue
        self.__optional__: bool = optional
        self.__value__: typing.Optional[str] = value
        self.__present__: bool = False
        self.__substitutes__: typing.Optional[typing.List[str]] = substitutes

    def clone(self):
        return copy.deepcopy(self)


class Command:

    def __init__(self, cmdname: str, nargslist: typing.List[Argument]=None,
                 nbpositionals: int=0, completionlist: typing.List[str] = None)->None:
        self.__cmdname__: str = cmdname.lower()
        self.__args__: typing.List[str] = []
        self.__nbpositionals__: int = nbpositionals
        self.__kwargs__: typing.Dict[str, Argument] = {}
        if nargslist is not None:
            for narg in nargslist:
                self.__kwargs__[narg.__argname__] = narg.clone()
        self.__completionlist__: typing.List[str] = list(self.__kwargs__.keys())
        if not completionlist:
            completionlist: typing.List[str] = []
        self.__completionlist__ += completionlist

    def clone(self):
        # return a deep copy of the command object
        return copy.deepcopy(self)

    def __findarg__(self, argname)->typing.Optional[Argument]:
        try:
            return self.__kwargs__[argname.lower()]
        except KeyError:
            return None

    def __validate__(self)->None:
        # check if all positionals arguments are present
        if len(self.__args__) != self.__nbpositionals__:
            raise exception.CException("Command " + self.__cmdname__ +
                                       " missing mandatory argument(s)")
        # check if all mandatory named arguments are present
        for argname, arg in self.__kwargs__.items():
            # check only if the argument is mandatory
            if not arg.__optional__:
                if arg.__present__:
                    continue
                if arg.__substitutes__:
                    bfound: bool = False
                    for substitute in arg.__substitutes__:
                        sarg = self.__findarg__(substitute)
                        if sarg and sarg.__present__:
                            bfound = True
                            break
                    if not bfound:
                        raise exception.CException("Command " + self.__cmdname__ +
                                                   " missing mandatory keyword argument(s)")
                else:
                    raise exception.CException("Command" + self.__cmdname__ +
                                               " missing mandatory keyword argument(s)")

    def parse(self, cmdline)-> typing.Tuple[typing.List[str], typing.Dict[str, str]]:
        wordslist: typing.List[str] = cmdline.split()
        # remove 1st element since it's the command name
        wordslist = wordslist[1:]
        i: int = 0
        while i < len(wordslist):
            arg = self.__findarg__(wordslist[i].lower())
            if arg is not None:
                arg.__present__ = True
                if arg.__hasvalue__:
                    # it's an argument name
                    i += 1
                    if i < len(wordslist):
                        arg.__value__ = wordslist[i]
                    else:
                        # Wrong number of arguments, raise error
                        raise exception.CException("Wrong number of " +
                                                   "arguments for the command " +
                                                   self.__cmdname__)
            else:
                # it's not an argument name
                # maybe an positional argument
                if len(self.__args__) < self.__nbpositionals__:
                    self.__args__.append(wordslist[i])
                else:
                    # Not even an cmd input, just exit
                    raise exception.CException("Unexpected argument " +
                                               wordslist[i] + " for the command " +
                                               self.__cmdname__)
            i += 1  # next step
        self.__validate__()
        args: typing.List[str] = self.__args__
        kwargs: typing.Dict[str, str] = {}
        # parse the named arguments
        for key, arg in self.__kwargs__.items():
            if arg.__present__:
                if arg.__value__:
                    kwargs[key] = arg.__value__
                else:
                    kwargs[key] = "true"
        return args, kwargs
