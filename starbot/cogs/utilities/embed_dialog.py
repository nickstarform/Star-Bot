"""General Embed Dialog Hub."""

# internal modules

# external modules
import discord
import asyncio
from discord.ext import commands

# relative modules
from .colours import Colours
from .embed_general import generic_embed
from .functions import current_time

# global attributes
__all__ = ('iterator',
           'confirm',
           'respond')
__filename__ = __file__.split('/')[-1].strip('.py')
__path__ = __file__.strip('.py').strip(__filename__)


async def iterator(ctx: commands.Context, step: dict,
                   timeout: int, with_confirm: bool=False):
    """Generic iterator embedder.

    Will ask a series of questions and save the results

    Parameters
    ----------
    ctx: :func: commands.Context
        the context command object
    step: dict
        dictionary of key='question to display', value=blank (to be populated)
    timeout: int
        the timeout in seconds before cancel for any subcommand

    Returns
    -------
    dict
        the same dictionary with value overriden
    """
    message = generic_embed(title=f'Please answer these questions.',
        desc=f'Type `cancel` or `exit` to cancel. Type `-1` to keep original/default value (in square brackets)\n**({timeout}s timer)**:',
        fields=[],
        colours=Colours.DIALOG_T,
        footer=current_time())[0]
    request = await ctx.send(embed=message)
    failed = False
    original = step.copy()

    for question in step.keys():
        tmp_r = await ctx.send(f'{question} [{step[question]}]')
        try:
            tmp_m = await ctx.bot.wait_for("message",
                                           timeout=timeout,
                                           check=lambda message:
                                           message.author == ctx.message.author)  # noqa
            if ('-1' != step[question][:2]):
                step[question] = tmp_m.content
            else:
                continue
            if ('cancel' == step[question][:6].lower()) or\
               ('exit' == step[question][:4].lower()):
                failed = True
                break
        except asyncio.TimeoutError:
            failed = True
            break
        except Exception as e:
            print(f'Error in parsing message: {e}')
            await ctx.send(embed=eembed.internalerrorembed(f'Error in parsing message: {e}'), delete_after=5)
            break
        try:
            await tmp_r.delete()
            await tmp_m.delete()
        except Exception as e:
            print(f'Error in deleting message: {e}')
            await ctx.send(embed=eembed.internalerrorembed(f'Error in deleting message: {e}'), delete_after=5)
        if failed:
            break

    try:
        await request.delete()
        if not failed:
            await respond(ctx, True)
        else:
            await respond(ctx, False)
            return False
    except Exception as e:
        print(f'Error in deleting/reacting to message: {e}')
        await ctx.send(embed=eembed.internalerrorembed(f'Error in deleting/reacting to message: {e}'), delete_after=5)
    return step


async def confirm(ctx: commands.Context, message: str, timeout: int):
    """Generic confirmation embedder.

    Serves as a confirm/deny embed builder with a Xs timeout

    Parameters
    ----------
    ctx: :func: commands.Context
        the context command object
    message: str
        the message to display
    timeout: int
        the timeout in seconds before cancel

    Returns
    -------
    bool
        success true false
    """
    confirmdialog = f'\nAttempting to **{ctx.command}**:\n'\
                    f'{message}'\
                    f'\n➡️ Type `confirm` to **{ctx.command}**'\
                    ' or literally anything else to cancel.'\
                    f'\n\n**You have {timeout}s...**'
    message = generic_embed(title=r'❗ Confirmation Request ❗',
                            desc=confirmdialog,
                            fields=[], footer=current_time(),
                            colors=Colours.DIALOG_T)[0]
    request = await ctx.send(embed=message, delete_after=timeout)
    try:
        message = await ctx.bot.wait_for("message",
                                         timeout=timeout,
                                         check=lambda message:
                                         message.author == ctx.message.author)
    except asyncio.TimeoutError:
        await respond(ctx, False)
        return False
    if message.content.lower() != 'confirm':
        await request.delete()
        await respond(ctx, False)
        await message.delete()
        return False
    try:
        await request.delete()
        await message.delete()
        await respond(ctx, True)
    except Exception as e:
        print(f'Error in deleting message: {e}')
    return True


async def respond(ctx: commands.Context, status: bool):
    """Respond/react to message.

    Parameters
    ----------
    ctx: :func: commands.Context
        the context command object
    status: bool
        status to react with

    Returns
    -------
    bool
        success true false
    """
    try:
        if status:
            await ctx.message.add_reaction(r'✅')
        else:
            await ctx.message.add_reaction(r'❌')
        return True
    except Exception as e:
        print(f'Error in responding to message message: {e}')
        return False
        pass

# end of code

# end of file
