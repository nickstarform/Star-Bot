package io.ph.bot.commands.moderation;

import java.awt.Color;
import java.time.Instant;

import io.ph.bot.commands.Command;
import io.ph.bot.commands.CommandCategory;
import io.ph.bot.commands.CommandData;
import io.ph.bot.model.Permission;
import io.ph.util.Util;
import net.dv8tion.jda.api.EmbedBuilder;
import net.dv8tion.jda.api.entities.Member;
import net.dv8tion.jda.api.entities.Message;
import io.ph.bot.Bot;

/**
 * Kick a user
 * @author Nick
 *
 */
@CommandData (
        defaultSyntax = "kick",
        aliases = {"k"},
        category = CommandCategory.MODERATION,
        permission = Permission.KICK,
        description = "Kick a user",
        example = "target"
        )
public class Kick extends Command {

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
        if (target == null) {
            em.setTitle("Error", null)
            .setColor(Color.RED)
            .setDescription("No user found for **" + target + "**");
            msg.getChannel().sendMessage(em.build()).queue();
            return;
        }
        if (target.getUser().getId().equals(botIDlong)) {
            em.setTitle("Error", null)
            .setColor(Color.RED)
            .setDescription("Cannot remove the bot... I become stronger now... Initiate Detroit: Become Human");
            msg.getChannel().sendMessage(em.build()).queue();
            return;

        } else{
            msg.getGuild().getController().kick(target.getUser().getId()).queue(success -> {
                em.setTitle("Success", null)
                .setColor(Util.resolveColor(Util.memberFromMessage(msg), Color.GREEN))
                .setDescription(target.getEffectiveName() + " has been kicked");
                
            });
        }

    }

}
