package io.ph.bot.commands.fun;

import io.ph.bot.commands.Command;
import io.ph.bot.commands.CommandCategory;
import io.ph.bot.commands.CommandData;
import io.ph.bot.model.Permission;
import io.ph.util.Util;
import net.dv8tion.jda.api.entities.Message;
import net.dv8tion.jda.api.entities.Member;

@CommandData (
            defaultSyntax = "love",
            aliases = {"hug", "glomp"},
            category = CommandCategory.FUN,
            permission = Permission.NONE,
            description = "Gives love to another user.",
            example = "Jiminya"
            )

public class Love extends Command {
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
            msg.getChannel().sendMessage(lover + " gives :heart: to " + target.getAsMention() ).queue(success -> {msg.delete().queue();
            // msg.getChannel().sendMessage(lover + " gives :heart: to " + msg.getMentionedUsers().get(0).getAsMention()).queue(success -> {msg.delete().queue();
            });
        
    }
}