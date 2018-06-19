import copy
import sys
import typing
import readline

from pytoolcore import style
from pytoolcore import command
from pytoolcore import exception


# ----------------------------------------------------------------------------------------------#
#                                       Data structures                                         #
# ----------------------------------------------------------------------------------------------#

class VariableSlot:
    def __init__(self, varname: str, value: str, settable: str, desc: str = "") -> None:
        self.__varname__: str = varname
        self.__value__: str = value
        self.__settable__: str = settable
        self.__desc__: str = desc

    def setvalue(self, value: str) -> None:
        if self.__settable__:
            self.__value__ = value
        else:
            raise exception.CException("Variable not settable")

    def getvalue(self) -> str:
        return self.__value__

    def getdesc(self) -> str:
        return self.__desc__

    def getsettable(self) -> str:
        return self.__settable__

    value = property(getvalue, setvalue)
    desc = property(getdesc)
    settable = property(getsettable)


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
        self.__dictvar__: typing.Dict[str, VariableSlot] = {}
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
                                helpstr="Description : set a variable with a value\n" +
                                        "Usage : set {variable} {value}\n" +
                                        "Note : Use 'show options' to display " +
                                        "settable variable"
                                ),
             "reset": CommandSlot(fct=self.__reset__, cmd=cmdreset,
                                  helpstr="Description : reset a variable\n" +
                                          "Usage : reset {variable}\n" +
                                          "Note : " +
                                          "Use 'show options' to display " +
                                          "resettable variable" +
                                          "Use 'reset all' to reset " +
                                          "all variables"
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
            print(style.Style.info("Here is " + cmd + "'s help\n" +
                                   self.__dictcmd__[cmd].__help__))

        except KeyError:
            print(style.Style.error("Keyword " + cmd + " isn't a defined command."))
        return True

    def __set__(self, varname: str, value: str) -> None:
        varname = varname.upper()
        try:
            self.__dictvar__[varname].value = value
            if not value:
                value = '""'
            print(style.Style.success("Variable " + varname +
                                      " set to " + str(value)))
        except exception.CException:
            print(style.Style.failure("Impossible to assign " + varname +
                                      " to " + str(value) + " with set command"))
        except KeyError:
            print(style.Style.error("Variable " + varname + " isn't defined."))

    def __reset__(self, varname: str) -> None:
        varname = varname.upper()
        if varname == "ALL" or varname == "*":
            for _, var in self.__dictvar__.items():
                try:
                    var.value = ""
                except exception.CException:
                    pass
        else:
            self.__set__(varname, "")

    def __show__(self, keyword: str) -> None:
        keyword = keyword.upper()
        if keyword == "OPTIONS":
            infotext: str = style.Style.info(self.ref + "'s options")
            print(infotext)
            print(len(infotext) * "=" + "\n")
            print("| Option\t| Current setting\t\t| Settable\t\t| Description")
            print("---------\t-------------------\t\t------------\t\t" +
                  "--------------")
            for varname, var in self.__dictvar__.items():
                value: str = var.value
                description: str = var.desc
                settable: str = var.settable
                setpadding: str = "\t\t\t"
                print("| " + style.Style.varnamepadding(varname) +
                      "| " + style.Style.valuepadding(value) +
                      "| " + settable + setpadding + "| " + description)
            print()
        elif keyword == "COMMANDS":
            print(style.Style.info(self.__moduleref__ + " commands"))
            for cmdname in self.__dictcmd__.keys():
                print(cmdname)
        elif keyword == "AUTHOR":
            print(style.Style.info(self.author))
        elif keyword == "NAME":
            print(style.Style.info(self.name))
        else:
            try:
                print(self.__dictvar__[keyword].value)
            except KeyError:
                print(style.Style.error("Variable " + keyword + " isn't defined."))

    @staticmethod
    def __clear__() -> None:
        style.clear()

    def __call__(self, cmdline) -> bool:
        # unpack arguments and call function
        try:
            cmdname: str = cmdline.split()[0].lower()  # trigger exception if empty cmdline
            try:
                # Make a copy of the command to avoid modifying the model
                try:
                    cmd: command.Command = self.__dictcmd__[cmdname].cmd.clone()
                except KeyError:
                    raise exception.CException("Command " + cmdname + " not found")
                args, kwargs = cmd.parse(cmdline)
                return self.__dictcmd__[cmdname].fct(*args, **kwargs)
            except KeyError as err:
                print(style.Style.error("Key " + str(err) + " not found"))
            except exception.CException as err:
                print(str(err))
        except IndexError:
            # empty input
            pass
        return True

    # ------------------------------------------------------------------------------------------#
    #                                       Public section                                      #
    # ------------------------------------------------------------------------------------------#

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
        del self.__dictcmd__[cmdname]

    def getvarnames(self) -> typing.List[str]:
        varnames: typing.List[str] = []
        for varname, var in self.__dictvar__.items():
            varnames.append(varname)
        return varnames

    def addvar(self, varname: str, description: str,
               settable: bool, value="") -> None:
        if varname:
            varname = varname.upper()
            try:
                del self.__dictvar__[varname]
            except KeyError:
                pass
            self.__dictvar__[varname] = VariableSlot(varname=varname, value=value,
                                                     desc=description,
                                                     settable=str(bool(settable)).lower())
        else:
            print(style.Style.error("Variable must have a name"))

    def getvar(self, varname: str) -> str:
        # return the variable
        varname = varname.upper()
        return self.__dictvar__[varname].value

    def getval(self, varname: str) -> str:
        # return a copy of the variable
        return copy.deepcopy(self.getvar(varname))

    def setvar(self, varname, value) -> None:
        varname = varname.upper()
        self.__set__(varname, value)

    def show(self, keyword) -> None:
        self.__show__(keyword)

    def splash(self) -> None:
        print("\n\t" + self.__modulename__ + " module by " + self.author + "\n")

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
            except exception.CException as err:
                print(str(err))
                break
        self.stop()
        return

    def stop(self) -> None:
        pass

    def completer(self, text: str, state: int)->str:
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

    def moduleref(self) -> str:
        return self.__moduleref__

    def modulename(self) -> str:
        return self.__modulename__

    def authorname(self) -> str:
        return self.__author__

    ref = property(moduleref)
    name = property(modulename)
    author = property(authorname)
