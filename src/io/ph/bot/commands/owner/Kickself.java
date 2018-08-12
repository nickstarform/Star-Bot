package io.ph.bot.commands.owner;

import java.awt.Color;
import java.time.Instant;

import io.ph.bot.commands.Command;
import io.ph.bot.commands.CommandCategory;
import io.ph.bot.commands.CommandData;
import io.ph.bot.model.Permission;
import io.ph.util.Util;
import net.dv8tion.jda.core.EmbedBuilder;
import net.dv8tion.jda.core.entities.Guild;
import net.dv8tion.jda.core.entities.Member;
import net.dv8tion.jda.core.entities.Message;
import io.ph.bot.Bot;

/**
 * Kick the bot
 * @author Nick
 *
 */
@CommandData (
        defaultSyntax = "kickself",
        aliases = {""},
        category = CommandCategory.BOT_OWNER,
        permission = Permission.BOT_OWNER,
        description = "Kick the bot from server",
        example = "@bot ------- *kick the bot from the current server*\n"
                + "@bot guildID *kick the bot from this server*\n"
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
        Member target = Util.resolveMemberFromMessage(msg);
        String contents = Util.getCommandContents(Util.getCommandContents(msg));
        if (target == null) {
            em.setTitle("Error", null)
            .setColor(Color.RED)
            .setDescription("No user found for **" + target + "**");
            msg.getChannel().sendMessage(em.build()).queue();
            return;
        }
        if (target.getUser().getId().equals(botIDlong)) {
            if (!contents.equals("")){
                Bot.getInstance().shards.getGuildById(contents).getController().kick(target.getUser().getId()).queue(success -> {
                        em.setTitle("Success", null)
                        .setColor(Util.resolveColor(Util.memberFromMessage(msg), Color.GREEN))
                        .setDescription(target.getEffectiveName() + " has been kicked");
                });
            } else {
                    msg.getGuild().getController().kick(target.getUser().getId()).queue(success -> {
                        em.setTitle("Success", null)
                        .setColor(Util.resolveColor(Util.memberFromMessage(msg), Color.GREEN))
                        .setDescription(target.getEffectiveName() + " has been kicked");
                    });
                }
        }
        return;
    }

}
