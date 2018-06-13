
class Style:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    BOLDEND = '\033[22m'
    UNDERLINEEND = '\033[24m'

    @staticmethod
    def purple(string: str)-> str:
        return Style.PURPLE + string + Style.END

    @staticmethod
    def cyan(string: str)-> str:
        return Style.CYAN + string + Style.END

    @staticmethod
    def darkcyan(string: str)-> str:
        return Style.DARKCYAN + string + Style.END

    @staticmethod
    def blue(string: str)-> str:
        return Style.BLUE + string + Style.END

    @staticmethod
    def green(string: str)-> str:
        return Style.GREEN + string + Style.END

    @staticmethod
    def yellow(string: str)-> str:
        return Style.YELLOW + string + Style.END

    @staticmethod
    def red(string: str)-> str:
        return Style.RED + string + Style.END

    @staticmethod
    def bold(string)-> str:
        return Style.BOLD + string + Style.BOLDEND

    @staticmethod
    def underline(string)-> str:
        return Style.UNDERLINE + string + Style.UNDERLINEEND

    @staticmethod
    def error(string: str)-> str:
        return Style.red("(!) Error: ") + string

    @staticmethod
    def warning(string: str)-> str:
        return Style.yellow(Style.underline("/!\\")) + Style.yellow(" Warning: ") + string

    @staticmethod
    def info(string: str)-> str:
        return Style.darkcyan("(i) Information: ") + string

    @staticmethod
    def failure(string: str)-> str:
        return Style.red("[-] Failure: ") + string

    @staticmethod
    def success(string: str)-> str:
        return Style.green("[+] Success: ") + string

    @staticmethod
    def valuepadding(value: str)-> str:
        padding = "\t"
        if len(value) <= 5:
            padding = "\t\t\t\t"
        elif len(value) <= 13:
            padding = "\t\t\t"
        elif len(value) <= 21:
            padding = "\t\t"
        return padding + value

    @staticmethod
    def varnamepadding(varname: str)-> str:
        padding = "\t"
        if len(varname) <= 5:
            padding = "\t\t"
        return padding + varname


def clear()-> None:
    print("\x1b[2J\x1b[H")
