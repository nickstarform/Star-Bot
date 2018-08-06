package io.ph.bot.commands.fun;

import io.ph.bot.commands.Command;
import io.ph.bot.commands.CommandCategory;
import io.ph.bot.commands.CommandData;
import io.ph.bot.model.Permission;
import io.ph.util.Util;
import net.dv8tion.jda.core.entities.Message;
import net.dv8tion.jda.core.entities.Member;

@CommandData (
            defaultSyntax = "cookie",
            aliases = {"cookies", "snack"},
            category = CommandCategory.FUN,
            permission = Permission.NONE,
            description = "Gives cookies to another user.",
            example = "Jiminya"
            )

public class Cookie extends Command {
    @Override
    public void executeCommand(Message msg) {

            String t = Util.getCommandContents(msg);
            Member target = null;
            String lover = msg.getAuthor().getName();
            if (msg.getMentionedUsers().size() > 0) {
                target = msg.getGuild().getMember(msg.getMentionedUsers().get(0));
            } else
                target = Util.resolveMemberFromMessage(t, msg.getGuild());
            //String loved = msg.getMentionedUsers().size() > 0 ? msg.getMentionedUsers().get(0).getName() : Util.getCommandContents(msg);
            msg.getChannel().sendMessage("I, " + lover + ", offer this in peace to " + target.getAsMention() + "\n" + "     (V)" + "\n" + "    (* *)" + "\n" + "    ( > >:cookie:" + "\n" + " C('')('')").queue(success -> {msg.delete().queue();
            });
        
    }
}