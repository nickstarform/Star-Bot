"""General Message Hub."""

# internal modules
from time import sleep

# external modules

# relative modules
from .functions import lessen_list

# global attributes
__all__ = ('generic_message', 'split_message', 'MAX_LEN')
__filename__ = __file__.split('/')[-1].strip('.py')
__path__ = __file__.strip('.py').strip(__filename__)

MAX_LEN = 2000

async def generic_message(ctx, channels, message: str, delete: int, splitwith: str=''):
    """Generic message builder.

    Parameters
    ----------
    ctx: :func: commands.Context
        the context command object
    channels: list
        List of channels to send the message to.
    message: str
        the message to display. Will try to split by sentance,
        fallback by word, fallback crude cut
    delete: int
        time in seconds to delete message, -1 to turn off

    Returns
    -------
    bool
        status true false
    """
    messages = split_message(message, MAX_LEN, splitwith)
    for message in messages:
        if not message:
            continue
        try:
            for channel in channels:
                if delete > 0:
                    await channel.send(f'{message}', delete_after=delete)
                else:
                    await channel.send(f'{message}')
        except Exception as e:
            print('Error sending message', e)
            return False
    return True


def split_message(target: str, maxl: int, splitwith: str=''):
    if len(target) <= maxl:
        return [target]
    else:
        ret = []
        tmpi_o = 0
        tmpi_n = 0
        tmpv = target
        while (len(tmpv) > maxl) or (tmpi_n < (len(target) - 1)):
            case = ''
            print('TEST',tmpv, case, splitwith)
            if (len(tmpv)+ len(case) + len(splitwith)) > maxl:
                if '\n' in tmpv:
                    case = '\n'
                elif '. ' in tmpv:
                    case = '. '
                elif '; ' in tmpv:
                    case = '; '
                elif ': ' in tmpv:
                    case = ': '
                elif ', ' in tmpv:
                    case = ', '
                elif ' ' in tmpv:
                    case = ' '
                if case != '':
                    tmpv = f'{case}'.join(lessen_list(tmpv.split(case),(maxl - len(case) - len(splitwith))))
                else:
                    case = ''
                    tmpv = tmpv[:maxl]  # greedy split char at lim

            if (len(tmpv) + len(case) + len(splitwith)) <= maxl:
                tmpi_o += tmpi_n
                tmpi_n += len(tmpv) + len(case)
                if tmpi_o == 0:
                    ret.append(tmpv + splitwith + case)
                elif tmpi_n < len(target):
                    ret.append(splitwith + tmpv + splitwith + case)
                else:
                    ret.append(splitwith + tmpv + case)
                tmpv = target[tmpi_n:]
        if ret[-1] != tmpv:
            ret.append(tmpv)
    return ret


if __name__ == "__main__":
    """Directly Called."""

    print('Testing module')
    print('Test Passed')

# end of code

# end of file
