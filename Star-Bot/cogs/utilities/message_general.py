"""General Message Hub."""

# internal modules

# external modules

# relative modules

# global attributes
__all__ = ('test', 'main', 'Default')
__filename__ = __file__.split('/')[-1].strip('.py')
__path__ = __file__.strip('.py').strip(__filename__)


def generic_message(ctx, channel, message: str, delete: int):
    """Generic message builder.

    Parameters
    ----------
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
    messages = split_message(message, 500)
    for message in messages:
        try:
            for channel in ctx.message.channel_mentions:
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
                if '. ' in tmpv:
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
