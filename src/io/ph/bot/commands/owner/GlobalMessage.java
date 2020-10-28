package io.ph.bot.commands.owner;

import io.ph.bot.commands.Command;
import io.ph.bot.commands.CommandCategory;
import io.ph.bot.commands.CommandData;
import io.ph.bot.jobs.StatusChangeJob;
import io.ph.bot.model.Permission;
import io.ph.util.Util;
import io.ph.bot.Bot;

import net.dv8tion.jda.api.entities.Message;
import net.dv8tion.jda.api.EmbedBuilder;

import java.awt.Color;
import java.util.List;
import java.util.Date;
import java.text.SimpleDateFormat;
import java.lang.StringBuilder;

/**
 * Sends a DM to all guild owners WIth great power comes great responcibility
 * @author Nick
 */

@CommandData (
        defaultSyntax = "globalmessage",
        aliases = {},
        category = CommandCategory.BOT_OWNER,
        permission = Permission.BOT_OWNER,
        description = "Messages all users that own a guild the bot is a part of.",
        example = "*content* will send *content* to every guild owner"
        )

public class GlobalMessage extends Command {

    @Override
    public void executeCommand(Message msg) {
        String timeStamp = new SimpleDateFormat("yyyy.MM.dd HH:mm:ss").format(new Date());
        EmbedBuilder em = new EmbedBuilder();
        StringBuilder stringBuilder = new StringBuilder();
        Bot.getInstance().getBots()
        .forEach(j -> {
            j.getGuilds()
            .forEach(g -> {
                stringBuilder.append("> Guild: " + g.getName() + "\n>> User: " + g.getOwner().getUser().getName() + "#" + g.getOwner().getUser().getDiscriminator() + "\n");
                g.getOwner().getUser().openPrivateChannel().queue(ch -> {
                    em.setTitle("Message from Bot Owner/Developer:", null)
                    .setColor(Color.YELLOW)
                    .setDescription(Util.getCommandContents(msg)+"\nPlease reply to: " +  msg.getAuthor().getName() + "#" + msg.getAuthor().getDiscriminator())
                    .setFooter("Message was sent Local time "+timeStamp, null);
                    g.getOwner().getUser().openPrivateChannel().complete().sendMessage(em.build()).queue();
                });
            });
        });
        String finalString = stringBuilder.toString();
        em.clearFields();
        em.setTitle(msg.getAuthor().getName() + " sent a Global Message to the following:\n", null)
        .setColor(Color.GREEN)
        .setDescription(finalString);
        msg.getChannel().sendMessage(em.build()).queue(success -> {msg.delete().queue();});
    }
}