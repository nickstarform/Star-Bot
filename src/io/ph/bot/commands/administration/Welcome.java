package io.ph.bot.commands.administration;

import io.ph.bot.commands.Command;
import io.ph.bot.commands.CommandCategory;
import io.ph.bot.commands.CommandData;
import io.ph.bot.model.GuildObject;
import io.ph.bot.model.Permission;
import io.ph.util.Util;
import io.ph.util.MessageUtils;
import io.ph.bot.Bot;
import net.dv8tion.jda.core.entities.Message;
import net.dv8tion.jda.core.entities.Member;
import net.dv8tion.jda.core.entities.Guild;
import net.dv8tion.jda.core.entities.TextChannel;
import java.lang.StringBuilder;

/**
 * Echo the welcome message
 * @author Nick
 *
 */
@CommandData (
        defaultSyntax = "welcome",
        aliases = {"welcomemessage"},
        category = CommandCategory.ADMINISTRATION,
        permission = Permission.MANAGE_SERVER,
        description = "Have the bot demo the welcome message.",
	example = ""
        )
public class Welcome extends Command {

    @Override
    public void executeCommand(Message msg) {
        Guild guild = msg.getGuild();
        GuildObject g = GuildObject.guildMap.get(guild.getId());
        String ret;
        StringBuilder stringBuilder = new StringBuilder();

        // Welcome message
        if (!g.getConfig().getWelcomeMessage().isEmpty()) {
            // weird instance to get the botinvitelink, split and just get the botidlong
            String botIDlong = Bot.getInstance().getConfig().getBotInviteBotLink().split("\\=")[1].split("\\&")[0];
            Member bot = Util.resolveUserFromMessage(botIDlong, guild.getId());
            if (g.getConfig().isPmWelcomeMessage()) {
                stringBuilder.append("Will PM the user.\n");
            }
            if (!g.getSpecialChannels().getWelcome().equals("")) {
                TextChannel chanName = guild.getTextChannelById(g.getSpecialChannels().getRulesChannel());
                stringBuilder.append("Will send a message to the channel: <#" + chanName.getId() + ">\n");
            }

            ret = g.getConfig().getWelcomeMessage();
            System.out.println("BotID: "+ botIDlong);
            ret = ret.replaceAll("\\$user\\$", bot.getAsMention());
            ret = ret.replaceAll("\\$server\\$", guild.getName());

            if (!g.getSpecialChannels().getWelcome().equals("")) {
                TextChannel chanName = guild.getTextChannelById(g.getSpecialChannels().getRulesChannel());
                ret = ret.replaceAll("\\$channel\\$", "<#" + chanName.getId() + ">");
            }
        } else {
            ret = "No message has been set, use the `changewelcome` command to set it.";
        }
        stringBuilder.append(ret);
        String finalString = stringBuilder.toString();
        MessageUtils.sendMessage(msg.getChannel().getId(), finalString);
    }
}
