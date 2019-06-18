import copy
import typing
import readline
import shlex

from pytoolcore import style
from pytoolcore import command
from pytoolcore import exception


# ----------------------------------------------------------------------------------------------#
#                                       Data structures                                         #
# ----------------------------------------------------------------------------------------------#

class Option:
    def __init__(self, optname: str, value: str, desc: str = "") -> None:
        self.__optname__: str = optname
        self.__value__: str = value
        self.__desc__: str = desc

    @property
    def value(self) -> str:
        return self.__value__

    @value.setter
    def value(self, value: str) -> None:
        self.__value__ = value

    @property
    def desc(self) -> str:
        return self.__desc__


class CommandSlot:
    def __init__(self, cmd: command.Command, fct: typing.Callable,
                 helpstr: str) -> None:
        self.__cmd__: command.Command = cmd
        self.__fct__: typing.Callable = fct
        self.__help__: str = helpstr

    def getfct(self) -> typing.Callable:
        return self.__fct__

    def getcmd(self) -> command.Command:
        return self.__cmd__

    def gethelp(self) -> str:
        return self.__help__

    fct = property(getfct)
    cmd = property(getcmd)
    cmdhelp = property(gethelp)


# --------------------------------------------------------------------------------------------------#
#                                   Framework command line engine                                   #
# --------------------------------------------------------------------------------------------------#

class Engine:

    # -------------------------------------------------------------------------------------------#
    #                                       Private section                                      #
    # -------------------------------------------------------------------------------------------#

    def __init__(self, moduleref: str, modulename: str, author: str) -> None:
        self.__moduleref__: str = moduleref
        self.__modulename__: str = modulename
        self.__author__: str = author
        self.__dictoptions__: typing.Dict[str, Option] = {}
        self.__running__: bool = False

        cmdhelp: command.Command = command.Command(cmdname="help", nbpositionals=1)
        cmdset: command.Command = command.Command(cmdname="set", nbpositionals=2)
        cmdreset: command.Command = command.Command(cmdname="reset", nbpositionals=1)
        cmdshow: command.Command = command.Command(cmdname="show", nbpositionals=1,
                                                   completionlist=["commands", "name", "author", "options"])
        cmdexit: command.Command = command.Command(cmdname="exit")
        cmdclear: command.Command = command.Command(cmdname="clear")
        self.__dictcmd__: typing.Dict[str, CommandSlot] = \
            {"help": CommandSlot(fct=self.__help__,
                                 cmd=cmdhelp,
                                 helpstr="Oh, please man... >_>"
                                 ),
             "set": CommandSlot(fct=self.__set__,
                                cmd=cmdset,
                                helpstr="Description : set an option with a value\n" +
                                        "Usage : set {variable} {value}\n" +
                                        "Note : Use 'show options' to display available options"
                                ),
             "reset": CommandSlot(fct=self.__reset__, cmd=cmdreset,
                                  helpstr="Description : reset a variable\n" +
                                          "Usage : reset {options}\n" +
                                          "Note : " +
                                          "Use 'show options' to display available options"
                                  ),
             "show": CommandSlot(fct=self.__show__, cmd=cmdshow,
                                 helpstr="Description : display option(s) and command(s)\n" +
                                         "Usage : show {keyword} \n" +
                                         "Note :\n" +
                                         "\tuse 'show name' to display module's name\n" +
                                         "\tuse 'show author' to display module's author\n" +
                                         "\tuse 'show commands' to display the module's commands\n"
                                         "\tuse 'show options' to display other valid keywords"
                                 ),
             "exit": CommandSlot(fct=self.__exit__, cmd=cmdexit,
                                 helpstr="Description : exit the current module\n" +
                                         "Usage : exit"
                                 ),
             "clear":
                 CommandSlot(fct=Engine.__clear__,
                             cmd=cmdclear, helpstr="Description : clean the terminal\n" +
                                                   "Usage : clear"
                             )
             }

    def __autoupdatehelp__(self):
        self.__dictcmd__["help"].cmd.__completionlist__ = list(self.__dictcmd__.keys())

    def __exit__(self) -> bool:
        self.__running__ = False
        return True

    def __help__(self, cmd: str) -> bool:
        try:
            print(style.Style.info("{0}'s help\n{1}".format(cmd, self.__dictcmd__[cmd].__help__)))
        except KeyError:
            print(style.Style.error("Keyword {0} isn't a defined command.".format(cmd)))
        return True

    def __set__(self, optname: str, value: str, verbose: bool = True) -> None:
        optname = optname.lower()
        try:
            self.__dictoptions__[optname].value = value
            if not value:
                value = '""'
            if verbose:
                print(style.Style.success("Option {0} set at {1}".format(optname, str(value))))
        except exception.ErrorException:
            if verbose:
                print(style.Style.failure("Impossible to assign {0} to {1} with set command".format(
                    optname, str(value))))
        except KeyError:
            if verbose:
                print(style.Style.error(str.format("Option {0} isn't defined.", optname)))

    def __reset__(self, optname: str) -> None:
        optname = optname.lower()
        if optname == "all" or optname == "*":
            for option in self.getoptnames():
                self.__set__(option, "", False)
        else:
            self.__set__(optname, "", False)

    def __show__(self, keyword: str) -> None:
        keyword = keyword.lower()
        if keyword == "options":
            print(style.Style.info("{0}'s options".format(self.name)))
            headers: typing.List[str] = ["Option", "Current setting", "Description"]
            table: typing.List[typing.List[str]] = []
            for optname, opt in self.__dictoptions__.items():
                table.append([optname, opt.value, opt.desc])
            print(style.Style.tabulate(headers, table))
            print()
        elif keyword == "commands":
            print(style.Style.info("{0}'s commands".format(self.name)))
            headers: typing.List[str] = ["Command", "Help"]
            table: typing.List[typing.List[str]] = []
            for cmdname, cmd in self.__dictcmd__.items():
                table.append([cmdname, cmd.cmdhelp])
            print(style.Style.tabulate(headers, table, True))
            print()
        elif keyword == "author":
            print(style.Style.info("{0}'s author".format(self.name)))
            print(style.Style.tabulate(["Author"], [[self.author]]))
            print()
        elif keyword == "name":
            print(style.Style.info("{0}'s name".format(self.name)))
            print(style.Style.tabulate(["Name"], [[self.name]]))
            print()
        else:
            try:
                print(style.Style.tabulate(["Option", "Current Setting", "Description"],
                                           [[keyword, self.getoptionvalue(keyword), self.getoptiondesc(keyword)]]))
                print()
            except KeyError:
                print(style.Style.error("Option {0} isn't defined.".format(keyword)))

    @staticmethod
    def __clear__() -> None:
        style.clear()

    def __call__(self, cmdline) -> bool:
        # unpack arguments and call function
        try:
            cmdname: str = shlex.split(cmdline)[0].lower()  # trigger exception if empty cmdline
            try:
                # Make a copy of the command to avoid modifying the model
                try:
                    cmd: command.Command = self.__dictcmd__[cmdname].cmd.clone()
                except KeyError:
                    raise exception.ErrorException(str.format("Command {0} not found", cmdname))
                args, kwargs = cmd.parse(cmdline)
                return self.__dictcmd__[cmdname].fct(*args, **kwargs)
            except KeyError as err:
                print(style.Style.error(str.format("Key {0} not found", str(err))))
            except (exception.ErrorException, exception.FailureException, exception.WarningException,
                    exception.InfoException, exception.SuccessException) as err:
                print(str(err))
        except IndexError:
            # empty input
            pass
        return True

    # ------------------------------------------------------------------------------------------#
    #                                       Public section                                      #
    # ------------------------------------------------------------------------------------------#

    @property
    def modulename(self) -> str:
        return self.__modulename__

    @property
    def moduleref(self) -> str:
        return self.__moduleref__

    def addcmd(self, cmd: command.Command, fct: typing.Callable,
               helpstr: str) -> None:
        try:
            self.removecmd(cmd.__cmdname__)
        except KeyError:
            pass
        self.__dictcmd__[cmd.__cmdname__] = CommandSlot(fct=fct, cmd=cmd,
                                                        helpstr=str(helpstr))
        self.__autoupdatehelp__()

    def removecmd(self, cmdname: str) -> None:
        try:
            del self.__dictcmd__[cmdname]
        except KeyError:
            pass

    def getcmd(self, cmdname: str) -> CommandSlot:
        return self.__dictcmd__[cmdname]

    def getoptnames(self) -> typing.List[str]:
        optnames: typing.List[str] = []
        for optname, var in self.__dictoptions__.items():
            optnames.append(optname)
        return optnames

    def addoption(self, optname: str, description: str, value="") -> None:
        if optname:
            optname = optname.lower()
            try:
                del self.__dictoptions__[optname]
            except KeyError:
                pass
            self.__dictoptions__[optname] = Option(optname=optname, value=value, desc=description)
        else:
            print(style.Style.error("Option must have a name"))

    def removeoption(self, optname: str) -> None:
        try:
            del self.__dictoptions__[optname]
        except KeyError:
            pass

    def getoption(self, optname: str) -> Option:
        # return the option object
        optname = optname.lower()
        return self.__dictoptions__[optname]

    def getoptiondesc(self, optname: str):
        return self.__dictoptions__[optname].desc

    def getoptionvalue(self, optname: str) -> str:
        return self.__dictoptions__[optname].value

    def setvar(self, optname: str, value: str, verbose: bool = True) -> None:
        optname = optname.lower()
        self.__set__(optname, value, verbose)

    def show(self, keyword: str) -> None:
        self.__show__(keyword)

    def splash(self) -> None:
        print("\n\t{0} module by {1} \n".format(self.__modulename__, self.author))

    def run(self) -> None:
        readline.set_completer_delims('\t')
        readline.parse_and_bind("tab: complete")
        self.__running__ = True
        while self.__running__:
            readline.set_completer(self.completer)
            try:
                cmdline = input(self.ref + " > ")
                self.__call__(cmdline=cmdline)
            except (KeyboardInterrupt, SystemExit):
                print()
                break
            except(KeyError, ValueError) as err:
                print(style.Style.error(str(err)))
            except exception.ErrorException as err:
                print(str(err))
                break
        self.stop()
        return

    def stop(self) -> None:
        pass

    def completer(self, text: str, state: int) -> str:
        subtext: str = text.split(" ")[-1].lower()
        if len(text.split(" ")) == 1:
            wordslist: typing.List[str] = list(self.__dictcmd__.keys())
        else:
            cmdname: str = text.split(" ")[0].lower()
            wordslist = self.__dictcmd__[cmdname].cmd.__completionlist__
        retlist: typing.List[str] = text.split(" ")[:-1]
        retlist.append([x for x in wordslist if x.lower().startswith(subtext, 0) and
                        x.lower() not in text.lower().split(" ") and
                        (subtext.strip() != "")][state])
        return " ".join(retlist)

    @property
    def ref(self) -> str:
        return self.__moduleref__

    @property
    def name(self) -> str:
        return self.__modulename__

    @property
    def author(self) -> str:
        return self.__author__
