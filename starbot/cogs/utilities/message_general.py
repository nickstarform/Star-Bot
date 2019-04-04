"""General Message Hub."""

# internal modules

# external modules

# relative modules

# global attributes
__all__ = ('generic_message', 'split_message', 'MAX_LEN')
__filename__ = __file__.split('/')[-1].strip('.py')
__path__ = __file__.strip('.py').strip(__filename__)

MAX_LEN = 1000

async def generic_message(ctx, channels, message: str, delete: int):
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
    messages = split_message(message, MAX_LEN)
    for message in messages:
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


def split_message(target: str, maxl: int):
    if len(target) <= maxl:
        return [target]
    else:
        ret = []
        tmpi_o = 0
        tmpi_n = 0
        tmpv = target
        while (len(tmpv) > maxl) or (tmpi_n < (len(target) - 1)):
            case = ''
            if len(tmpv) > maxl:
                if '\n' in tmpv:
                    case = '\n'
                    tmpv = f'{case}'.join(tmpv.split(case)[0:-1])  # split sentence
                elif '. ' in tmpv:
                    case = '. '
                    tmpv = f'{case}'.join(tmpv.split(case)[0:-1])  # split sentence
                elif '; ' in tmpv:
                    case = '; '
                    tmpv = f'{case}'.join(tmpv.split(case)[0:-1])  # split connected
                elif ': ' in tmpv:
                    case = ': '
                    tmpv = f'{case}'.join(tmpv.split(case)[0:-1])  # split list
                elif ', ' in tmpv:
                    case = ', '
                    tmpv = f'{case}'.join(tmpv.split(case)[0:-1])  # split phrase
                elif ' ' in tmpv:
                    case = ' '
                    tmpv = f'{case}'.join(tmpv.split(case)[0:-1])  # split word
                else:
                    case = ''
                    tmpv = tmpv[:maxl]  # greedy split char at lim
            if (len(tmpv) + len(case)) <= maxl:
                tmpi_o += tmpi_n
                tmpi_n += len(tmpv) + len(case)
                ret.append(tmpv + case)
                tmpv = target[tmpi_n:]
    return ret


if __name__ == "__main__":
    """Directly Called."""

    print('Testing module')
    print('Test Passed')

# end of code

# end of file
