package io.ph.bot.commands.owner;

import java.awt.Color;
import java.time.Instant;

import io.ph.bot.commands.Command;
import io.ph.bot.commands.CommandCategory;
import io.ph.bot.commands.CommandData;
import io.ph.bot.model.Permission;
import io.ph.util.Util;
import net.dv8tion.jda.api.EmbedBuilder;
import net.dv8tion.jda.api.entities.Guild;
import net.dv8tion.jda.api.entities.Member;
import net.dv8tion.jda.api.entities.Message;
import io.ph.bot.Bot;

/**
 * Kick the bot
 * @author Nick
 *
 */
@CommandData (
        defaultSyntax = "kickself",
        aliases = {},
        category = CommandCategory.BOT_OWNER,
        permission = Permission.BOT_OWNER,
        description = "Kick the bot from server",
        example = "botId ------- *kick the bot from the current server*\n"
                + "botId guildID *kick the bot from this server*\n"
        )

public class Kickself extends Command {

    @Override
    public void executeCommand(Message msg) {
        EmbedBuilder em = new EmbedBuilder().setTimestamp(Instant.now());
        // weird instance to get the botinvitelink, split and just get the botidlong
        String botIDlong = Bot.getInstance().getConfig().getBotInviteBotLink().split("\\=")[1].split("\\&")[0];
        if (Util.getCommandContents(msg).isEmpty()) {
            em.setTitle("Error", null)
            .setColor(Color.RED)
            .setDescription("No target specified");
            msg.getChannel().sendMessage(em.build()).queue();
            return;
        }
        String target = "";
        String contents = "";
        String temp = Util.getCommandContents(msg);
        String[] tempB = temp.split(" ");
        if (tempB.length > 1){
            target = tempB[0];
            contents = tempB[1];
            System.out.println("Contents: "+contents);
        } else {
            target = tempB[0];
        }

        if (target == null) {
            em.setTitle("Error", null)
            .setColor(Color.RED)
            .setDescription("No user found for **" + target + "**");
            msg.getChannel().sendMessage(em.build()).queue();
            return;
        }
        System.out.println("All contents: "+temp);
        System.out.println("Target: "+target);
        System.out.println("ID: "+botIDlong);
        if (target.equals(botIDlong)) {
            if (!contents.equals("")){

                Bot.getInstance().shards.getGuildById(contents).leave().queue(
                success -> {}, failure -> {
                    em.setTitle("Error", null)
                    .setColor(Color.RED)
                    .setDescription(failure.getMessage());
                    msg.getChannel().sendMessage(em.build()).queue();
                });

            } else {

                msg.getGuild().leave().queue(
                success -> {}, failure -> {
                    em.setTitle("Error", null)
                    .setColor(Color.RED)
                    .setDescription(failure.getMessage());
                    msg.getChannel().sendMessage(em.build()).queue();
                });
            }
        } else {
            em.setTitle("Can only remove self bot", null)
            .setColor(Util.resolveColor(Util.memberFromMessage(msg), Color.GREEN))
            .setDescription("Failed to kick bot. Invalid ID");
            msg.getChannel().sendMessage(em.build()).queue();
        }
    }

}
