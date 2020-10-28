package io.ph.bot.commands.general;

import io.ph.bot.Bot;
import io.ph.bot.commands.Command;
import io.ph.bot.commands.CommandCategory;
import io.ph.bot.commands.CommandData;
import io.ph.bot.model.Permission;
import net.dv8tion.jda.api.entities.Message;

/**
 * Send the invite link for Bot
 * @author Nick
 *
 */
@CommandData (
        defaultSyntax = "invitebot",
        aliases = {"botinvite"},
        category = CommandCategory.UTILITY,
        permission = Permission.NONE,
        description = "Send a link to invite me to a server",
        example = "(no parameters)"
        )
public class InviteBot extends Command {

    @Override
    public void executeCommand(Message msg) {
        if(Bot.getInstance().getConfig().getBotInviteBotLink() == null)
            return;
        msg.getChannel().sendMessage(Bot.getInstance().getConfig().getBotInviteBotLink()).queue(success -> {msg.delete().queue();});
    }
}
